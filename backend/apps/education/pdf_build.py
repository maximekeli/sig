"""Génération de fiches pédagogiques PDF (ReportLab)."""
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from .manuscript_fr import BODY_ROTATION, CHAPTER_TITLES, INTRO_PARAS


def build_pedagogical_pdf_bytes(sheet) -> bytes:
    """Produit un PDF long (≈ 20+ pages) pour une fiche donnée."""
    theme = sheet.theme
    titles = CHAPTER_TITLES.get(theme, CHAPTER_TITLES['importance'])
    intros = INTRO_PARAS.get(theme, INTRO_PARAS['importance'])

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        name='PdfH1', parent=styles['Heading1'], fontSize=16, spaceAfter=14, leading=20,
    )
    h2 = ParagraphStyle(
        name='PdfH2', parent=styles['Heading2'], fontSize=11, spaceAfter=8, leading=14,
    )
    body = ParagraphStyle(
        name='PdfBody', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8,
    )
    small = ParagraphStyle(
        name='PdfSmall', parent=styles['Normal'], fontSize=8, leading=11, textColor=0x404040,
    )

    story = [
        Paragraph(escape(sheet.title), h1),
        Paragraph(
            escape(
                'SIG Sols Togo — DISIA / DUSOL · Document autogénéré · Données NASA citées selon '
                'les crédits missions (Earthdata / LP DAAC / NSIDC / GES DISC).',
            ),
            small,
        ),
        Spacer(1, 0.4 * cm),
    ]
    for para in intros:
        story.append(Paragraph(escape(para), body))
    story.append(Spacer(1, 0.5 * cm))
    # 48 chapitres courts × 3 paragraphes + sauts de page → volumétrie ≈ 22–32 pages
    n_cycles = 48
    for i in range(n_cycles):
        ch_title = titles[i % len(titles)]
        story.append(Paragraph(escape(f'Chapitre {i + 1} — {ch_title}'), h2))
        for k in range(3):
            b = BODY_ROTATION[(i * 3 + k) % len(BODY_ROTATION)]
            story.append(Paragraph(escape(b), body))
        if (i + 1) % 4 == 0:
            story.append(PageBreak())

    story.append(PageBreak())
    story.append(Paragraph(escape('Synthèse et références'), h2))
    story.append(Paragraph(
        escape(
            'Ce manuel synthétise des bonnes pratiques et des principes scientifiques généraux ; '
            'chaque situation locale doit être validée par un diagnostic de terrain. Pour les couches '
            'satellitaires NASA, consulter https://earthdata.nasa.gov/ et les guides produits MODIS, '
            'SMAP et GPM.',
        ),
        body,
    ))
    doc.build(story)
    return buf.getvalue()
