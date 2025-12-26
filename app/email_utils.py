from datetime import datetime
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, pdf_path, record):
    msg = EmailMessage()
    msg["Subject"] = "Heart Failure 30‑Day Readmission Risk Report"
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = to_email

    patient_id = record.get("id", "N/A")
    raw_created = record.get("created_at")

    if isinstance(raw_created, str):
        dt = datetime.fromisoformat(raw_created.split(".")[0])
    else:
        dt = raw_created 
    created_indian = dt.strftime("%d-%m-%Y %H:%M") if dt else "N/A"

    prob = float(record.get("probability", 0.0))
    risk_pct = f"{prob * 100:.1f}%"

    html_body = f"""
    <p>Dear Sir/Madam,</p>

    <p>
    Please find attached the latest Heart Failure 30‑Day Readmission Risk Report
    generated using the patient's discharge-time clinical details.
    </p>

    <p><b>Key information:</b><br>
    • <b>Patient ID:</b> {patient_id}<br>
    • <b>Time of Report Generation:</b> {created_indian}<br>
    • <b>Chances of Readmission:</b> {risk_pct}
    </p>

    <p>
    This analysis is intended only as a decision-support tool and should be interpreted
    along with your clinical assessment, medical history, and local protocols.
    It does not replace your professional judgement.
    </p>

    <p>
    Warm regards,<br>
    ReadmitAI Team
    </p>
    """

    msg.add_alternative(html_body, subtype="html")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename="heart_failure_readmission_report.pdf"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
