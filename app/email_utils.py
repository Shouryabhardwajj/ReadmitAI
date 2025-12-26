import smtplib
import os
from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo  
from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(to_email: str, pdf_path: str, record: dict):
    msg = EmailMessage()
    msg["Subject"] = "Heart Failure 30‑Day Readmission Risk Report"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    patient_id = record.get("id", "N/A")
    raw_created = record.get("created_at")

    dt_utc = None
    if isinstance(raw_created, str):
        dt_utc = datetime.fromisoformat(raw_created.split("+")[0])
    elif isinstance(raw_created, datetime):
        dt_utc = raw_created

    if dt_utc is not None:
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        dt_ist = dt_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        created_str = dt_ist.strftime("%d-%m-%Y %H:%M")
    else:
        created_str = "N/A"

    prob = float(record.get("probability", 0.0))
    risk_pct = f"{prob * 100:.6f}%"  

    html_body = f"""
    <p>Dear Sir/Madam,</p>

    <p><b>Key information:</b><br>
    • <b>Patient ID:</b> {patient_id}<br>
    • <b>Time of Report Generation:</b> {created_str}<br>
    • <b>Chances of Readmission:</b> {risk_pct}
    </p>

    <p>This report is a decision‑support tool and does not replace clinical judgment.</p>

    <p>Regards,<br>
    ReadmitAI Team</p>
    """

    msg.add_alternative(html_body, subtype="html")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename="heart_failure_readmission_report.pdf",
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)
