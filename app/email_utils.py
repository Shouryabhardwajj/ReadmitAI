from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ [web:123]

def send_email(to_email, pdf_path, record):
    msg = EmailMessage()
    msg["Subject"] = "Heart Failure 30‑Day Readmission Risk Report"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    patient_id = record.get("id", "N/A")
    raw_created = record.get("created_at")

    if isinstance(raw_created, str):
        dt_utc = datetime.fromisoformat(raw_created.replace("Z", ""))
    else:
        dt_utc = raw_created

    if dt_utc is not None:
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        dt_ist = dt_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        created_str = dt_ist.strftime("%d-%m-%Y %H:%M")
    else:
        created_str = "N/A"

    prob = float(record.get("probability", 0.0))
    risk_pct = f"{prob * 100:.6f}%"  # 6 decimal places [web:122][web:134]

    html_body = f"""
    <p>Dear Sir/Madam,</p>

    <p>
    Please find attached the latest <b>Heart Failure 30‑Day Readmission Risk Report</b>.
    </p>

    <p><b>Key information:</b><br>
    • <b>Patient ID:</b> {patient_id}<br>
    • <b>Time of Report Generation:</b> {created_str}<br>
    • <b>Chances of Readmission:</b> {risk_pct}
    </p>

    <p>
    This analysis is intended only as a decision-support tool and should be interpreted
    along with clinical assessment and local protocols.
    </p>

    <p>
    Regards,<br>
    ReadmitAI
    </p>
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