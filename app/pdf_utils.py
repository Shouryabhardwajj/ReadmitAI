from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf(data, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont("Helvetica", 11)

    c.drawString(50, 800, "Heart Failure Readmission Report")
    c.line(50, 790, 550, 790)

    y = 760
    for key, value in data.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 18

    c.save()
