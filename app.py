from flask import Flask, render_template, request, send_file, redirect
from werkzeug.utils import secure_filename
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

# ---------------- CONFIG ---------------- #

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db()


# ---------------- HELPER FUNCTIONS ---------------- #

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


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

    if "label" not in request.files:
        return "No file uploaded.", 400

    file = request.files["label"]

    if file.filename == "":
        return "No file selected.", 400

    if not allowed_file(file.filename):
        return "Only PNG, JPG, JPEG and PDF files are allowed.", 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    try:

        # -------- Handle PDF or Image -------- #

        if filename.lower().endswith(".pdf"):

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

ai_report = analyze_label(text)

# -------- Calculate Compliance Score -------- #

passed = sum(results.values())
total = len(results)

if total > 0:
    score = round((passed / total) * 100)
else:
    score = 0

        # -------- Save History -------- #

        current_date = datetime.now().strftime("%d-%m-%Y %H:%M")

        save_result(
            filename,
            score,
            current_date
        )

        return render_template(
            "result.html",
            filename=filename,
            image_path=image_path,
            text=text,
            results=results,
            ai_report=ai_report,
            score=score
        )

    except Exception as e:

        return f"""
        <h2>Application Error</h2>
        <pre>{str(e)}</pre>
        """, 500


# ---------------- HISTORY ---------------- #

@app.route("/history")
def history():

    keyword = request.args.get("search", "").strip()

    if keyword:
        history = search_history(keyword)
    else:
        history = get_history()

    return render_template(
        "history.html",
        history=history,
        keyword=keyword
    )


# ---------------- DELETE ---------------- #

@app.route("/delete/<int:record_id>")
def delete(record_id):

    delete_history(record_id)

    return redirect("/history")


# ---------------- PDF REPORT ---------------- #

@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    filename = request.form.get("filename", "")
    score = request.form.get("score", "")
    text = request.form.get("text", "")
    ai_report = request.form.get("ai_report", "")

    results = {}

    for key, value in request.form.items():

        if key.startswith("rule_"):

            rule = key.replace("rule_", "")
            results[rule] = (value == "True")

    output_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "Compliance_Report.pdf"
    )

    generate_pdf(
        filename=filename,
        score=score,
        results=results,
        ai_report=ai_report,
        text=text,
        output_path=output_path
    )

    return send_file(
        output_path,
        as_attachment=True,
        download_name="Compliance_Report.pdf"
    )


# ---------------- ERROR HANDLERS ---------------- #

@app.errorhandler(413)
def file_too_large(error):
    return (
        "<h3>File too large. Maximum upload size is 10 MB.</h3>",
        413
    )


@app.errorhandler(404)
def page_not_found(error):
    return (
        "<h3>404 - Page Not Found</h3>",
        404
    )


@app.errorhandler(500)
def internal_error(error):
    return (
        "<h3>500 - Internal Server Error</h3>",
        500
    )


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=False)