"""Certificat PDF après quiz réussi."""
from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def build_quiz_certificate_bytes(session, user) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(w / 2, h - 4 * cm, 'SIG Sols Togo')
    c.setFont('Helvetica', 14)
    c.drawCentredString(w / 2, h - 5.2 * cm, 'Certificat de participation au quiz pédagogique')
    c.setFont('Helvetica-Bold', 16)
    name = user.get_full_name() or user.username
    c.drawCentredString(w / 2, h - 7 * cm, name)
    c.setFont('Helvetica', 12)
    c.drawCentredString(
        w / 2, h - 8.2 * cm,
        f'Session #{session.pk} · Niveau {session.difficulty}',
    )
    c.drawCentredString(
        w / 2, h - 9.2 * cm,
        f'Score obtenu : {session.score} points',
    )
    c.drawCentredString(
        w / 2, h - 10.2 * cm,
        f'Questions répondues : {session.questions_answered}',
    )
    c.setFont('Helvetica-Oblique', 10)
    c.drawCentredString(
        w / 2, 2.5 * cm,
        f'Délivré le {date.today().strftime("%d/%m/%Y")} · DISIA / DUSOL · Région Maritime',
    )
    c.showPage()
    c.save()
    return buf.getvalue()
