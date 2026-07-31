from flask import Flask, render_template, request, send_file, redirect
from werkzeug.utils import secure_filename
import os
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

# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

# ============================================================
# HELPER FUNCTION
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# HOME PAGE
# ============================================================

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


# ============================================================
# UPLOAD
# ============================================================

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

        # ====================================================
        # PDF OR IMAGE
        # ====================================================

        if filename.lower().endswith(".pdf"):

            ocr_image = pdf_to_image(filepath)
            image_path = "/" + ocr_image.replace("\\", "/")

        else:

            ocr_image = filepath
            image_path = "/" + filepath.replace("\\", "/")

        # ====================================================
        # OCR
        # ====================================================

        text = extract_text(ocr_image)

        # ====================================================
        # RULE VALIDATION
        # ====================================================

        results = validate_label(text)

        # ====================================================
        # AI ANALYSIS
        # ====================================================

        ai_report = analyze_label(text)

        # ====================================================
        # SCORE
        # ====================================================

        passed = sum(results.values())
        total = len(results)

        score = round(
            (passed / total) * 100
        ) if total > 0 else 0

        # ====================================================
        # SAVE HISTORY
        # ====================================================

        current_date = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        save_result(
            filename,
            score,
            current_date
        )

        current_time = datetime.now().strftime(
            "%d %B %Y, %I:%M %p"
        )

        # ====================================================
        # RESULT PAGE
        # ====================================================

        return render_template(
            "result.html",
            filename=filename,
            image_path=image_path,
            text=text,
            results=results,
            ai_report=ai_report,
            score=score,
            passed=passed,
            total=total,
            moment=current_time
        )

    except Exception as e:

        return f"""
        <h2>Application Error</h2>
        <pre>{str(e)}</pre>
        """, 500
        # ============================================================
# HISTORY
# ============================================================

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


# ============================================================
# DELETE HISTORY
# ============================================================

@app.route("/delete/<int:record_id>")
def delete(record_id):

    delete_history(record_id)

    return redirect("/history")


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================

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


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "413.html"
    ), 413


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "500.html"
    ), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=False
    )