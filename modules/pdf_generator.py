from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_pdf(filename, score, results, ai_report, text, output_path):

    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>AI-Assisted Pharmaceutical Label Compliance Report</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    elements.append(
        Paragraph(f"<b>File Name:</b> {filename}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"<b>Compliance Score:</b> {score}%", styles["Normal"])
    )

    elements.append(
        Paragraph("<br/><b>Rule Validation</b>", styles["Heading2"])
    )

    for rule, status in results.items():
        mark = "PASS" if status else "FAIL"
        elements.append(
            Paragraph(f"{rule}: {mark}", styles["Normal"])
        )

    elements.append(
        Paragraph("<br/><b>AI Analysis</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(ai_report.replace("\n", "<br/>"), styles["Normal"])
    )

    elements.append(
        Paragraph("<br/><b>OCR Extracted Text</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(text.replace("\n", "<br/>"), styles["Normal"])
    )

    doc.build(elements)

    return output_path