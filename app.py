from flask import Flask, render_template, request, send_file, redirect
import os
import re
from datetime import datetime

from modules.ocr import extract_text
from modules.validator import validate_label
from modules.groq_ai import analyze_label
from modules.pdf_generator import generate_pdf
from modules.pdf_reader import pdf_to_image

from modules.database import (
    init_db,
    save_result,
    get_history,
    get_dashboard_stats,
    search_history,
    delete_history,
    get_chart_data
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db()


# ---------------- HOME ---------------- #

@app.route("/")
def index():

    stats = get_dashboard_stats()
    history = get_history()[:5]
    chart = get_chart_data()

    return render_template(
        "index.html",
        stats=stats,
        history=history,
        chart=chart
    )


# ---------------- UPLOAD ---------------- #

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["label"]

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # -------- Handle PDF or Image -------- #

    if file.filename.lower().endswith(".pdf"):

        ocr_image = pdf_to_image(filepath)
        image_path = "/" + ocr_image.replace("\\", "/")

    else:

        ocr_image = filepath
        image_path = "/" + filepath.replace("\\", "/")

    # -------- OCR -------- #

    text = extract_text(ocr_image)

    # -------- Rule Validation -------- #

    results = validate_label(text)

    # -------- AI Analysis -------- #

    try:

        ai_report = analyze_label(text)

        score = 0

        match = re.search(
            r"Compliance Score[:\s]*(\d+)",
            ai_report
        )

        if match:
            score = int(match.group(1))

    except Exception as e:

        ai_report = f"AI Analysis Error:\n\n{str(e)}"
        score = 0

    # -------- Save History -------- #

    current_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    save_result(
        file.filename,
        score,
        current_date
    )

    return render_template(
        "result.html",
        filename=file.filename,
        image_path=image_path,
        text=text,
        results=results,
        ai_report=ai_report,
        score=score
    )


# ---------------- HISTORY ---------------- #

@app.route("/history")
def history():

    keyword = request.args.get("search")

    if keyword:
        history = search_history(keyword)
    else:
        history = get_history()

    return render_template(
        "history.html",
        history=history,
        keyword=keyword or ""
    )


# ---------------- DELETE ---------------- #

@app.route("/delete/<int:record_id>")
def delete(record_id):

    delete_history(record_id)

    return redirect("/history")


## ---------------- PDF REPORT ---------------- #

@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    filename = request.form.get("filename")
    score = request.form.get("score")
    text = request.form.get("text")
    ai_report = request.form.get("ai_report")

    # Collect rule validation results
    results = {}

    for key, value in request.form.items():

        if key.startswith("rule_"):

            rule = key.replace("rule_", "")
            results[rule] = (value == "True")

    # PDF output path
    output_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "Compliance_Report.pdf"
    )

    # Generate PDF
    generate_pdf(
        filename=filename,
        score=score,
        results=results,
        ai_report=ai_report,
        text=text,
        output_path=output_path
    )

    # Download PDF
    return send_file(
        output_path,
        as_attachment=True,
        download_name="Compliance_Report.pdf"
    )


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)