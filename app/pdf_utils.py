from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from zoneinfo import ZoneInfo 

def generate_pdf(record: dict, pdf_path: str = "prediction_report.pdf"):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Heart Failure Readmission Report")
    c.line(50, height - 60, width - 50, height - 60)

    c.setFont("Helvetica", 11)
    y = height - 90

    created_raw = record.get("created_at")
    dt_utc = None
    if isinstance(created_raw, str):
        dt_utc = datetime.fromisoformat(created_raw.split("+")[0])
    elif isinstance(created_raw, datetime):
        dt_utc = created_raw

    if dt_utc is not None:
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        dt_ist = dt_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        created_str = dt_ist.strftime("%d-%m-%Y %H:%M:%S")
    else:
        created_str = "N/A"

    for key in [
        "id",
        "age",
        "heart_rate",
        "systolic_bp",
        "diastolic_bp",
        "glucose",
        "creatinine",
        "troponin",
        "los",
        "prediction",
        "probability",
    ]:
        value = record.get(key, "")
        if key == "probability" and value is not None:
            value = f"{float(value):.6f}"
        if key == "probability":
            label = "probability"
        else:
            label = key
        c.drawString(50, y, f"{label}: {value}")
        y -= 18

    c.drawString(50, y, f"created_at_ist: {created_str}")

    c.showPage()
    c.save()

    return pdf_path
