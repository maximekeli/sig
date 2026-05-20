"""Génération de fiches PDF — présentation inspirée d'un document LaTeX (amsart / article)."""
from io import BytesIO
from datetime import date
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .manuscript_fr import BODY_ROTATION, CHAPTER_TITLES, INTRO_PARAS


def _footer(canvas, _doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    w, _h = A4
    y = 1.15 * cm
    canvas.setStrokeColor(HexColor('#333333'))
    canvas.setLineWidth(0.3)
    canvas.line(2 * cm, y + 0.45 * cm, w - 2 * cm, y + 0.45 * cm)
    canvas.drawCentredString(w / 2, y, f'— {canvas.getPageNumber()} —')
    canvas.setFont('Times-Roman', 7)
    canvas.drawCentredString(w / 2, y - 0.35 * cm, 'SIG Sols Togo · DISIA / DUSOL · Fiche pédagogique')
    canvas.restoreState()


def build_pedagogical_pdf_bytes(sheet) -> bytes:
    """Produit un PDF long, mise en page soignée (style académique / LaTeX)."""
    theme = sheet.theme
    titles = CHAPTER_TITLES.get(theme, CHAPTER_TITLES['importance'])
    intros = INTRO_PARAS.get(theme, INTRO_PARAS['importance'])

    buf = BytesIO()
    w, h = A4
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2.2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.4 * cm,
        rightMargin=2.4 * cm,
        title='SIG Sols — Fiche pédagogique',
        author='DISIA / DUSOL',
    )
    styles = getSampleStyleSheet()

    title_main = ParagraphStyle(
        name='LtxTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=HexColor('#0f172a'),
    )
    title_sub = ParagraphStyle(
        name='LtxSub',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=HexColor('#334155'),
    )
    meta_center = ParagraphStyle(
        name='LtxMeta',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=HexColor('#64748b'),
    )
    sect = ParagraphStyle(
        name='LtxSection',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        spaceBefore=14,
        spaceAfter=8,
        textColor=HexColor('#0f172a'),
        borderPadding=0,
    )
    body = ParagraphStyle(
        name='LtxBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        leading=14.5,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        firstLineIndent=0,
    )
    abstract_title = ParagraphStyle(
        name='LtxAbstractTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        spaceAfter=6,
        textColor=HexColor('#1e3a2f'),
    )
    abstract_body = ParagraphStyle(
        name='LtxAbstractBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=13.5,
        alignment=TA_JUSTIFY,
    )
    remark = ParagraphStyle(
        name='LtxRemark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        leftIndent=12,
        borderColor=HexColor('#cbd5e1'),
        borderWidth=0,
        borderPadding=8,
        backColor=None,
    )

    story = []
    # --- Page de titre (style LaTeX) ---
    story.append(Spacer(1, 2.8 * cm))
    story.append(Paragraph(escape(sheet.title), title_main))
    story.append(Paragraph(
        escape('Fiche pédagogique · Programme SIG Sols Togo'),
        title_sub,
    ))
    story.append(Spacer(1, 0.35 * cm))
    story.append(HRFlowable(width='80%', thickness=0.8, color=HexColor('#134e2a'), hAlign='CENTER'))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        escape(f'Thématique : {sheet.get_theme_display()}'),
        meta_center,
    ))
    story.append(Paragraph(escape(f'Généré le {date.today().strftime("%d/%m/%Y")}'), meta_center))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        escape(
            'Institutions partenaires : DISIA — Ministère de l’Agriculture (Togo), DUSOL. '
            'Références NASA : Earthdata, LP DAAC, NSIDC, GES DISC (domaines publics, citations requises).',
        ),
        meta_center,
    ))
    story.append(PageBreak())

    # --- Résumé (bloc type abstract) ---
    abstract_text = (
        f'{intros[0]} {intros[1]} Ce document complète la version synthétique affichée sur la plateforme ; '
        'les chapitres suivants développent les concepts, exemples de terrain et liens avec les données satellite.'
    )
    abst_tbl = Table(
        [[Paragraph('<b>Résumé</b>', abstract_title)],
         [Paragraph(escape(abstract_text), abstract_body)]],
        colWidths=[w - 4.8 * cm],
    )
    abst_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.6, HexColor('#94a3b8')),
        ('LINEBEFORE', (0, 0), (0, -1), 3, HexColor('#134e2a')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(abst_tbl)
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph(
        escape(
            '<b>Notation.</b> Les encadrés en marge gauche verte reprennent des remarques méthodologiques '
            'analogues aux environnements « remark » en LaTeX ; le corps du texte est justifié comme dans un article.',
        ),
        remark,
    ))
    story.append(Spacer(1, 0.5 * cm))

    # --- Corps : chapitres numérotés ---
    n_cycles = 48
    for i in range(n_cycles):
        ch_title = titles[i % len(titles)]
        num = i + 1
        story.append(Paragraph(escape(f'{num}. {ch_title}'), sect))
        for k in range(3):
            b = BODY_ROTATION[(i * 3 + k) % len(BODY_ROTATION)]
            story.append(Paragraph(escape(b), body))
        if (i + 1) % 3 == 0:
            story.append(Spacer(1, 0.2 * cm))

        if (i + 1) % 5 == 0:
            story.append(PageBreak())

    story.append(PageBreak())
    story.append(Paragraph(escape('Annexe — Synthèse et références documentaires'), sect))
    story.append(Paragraph(
        escape(
            'Ce manuel rassemble des principes généraux ; chaque recommandation doit être ajustée au diagnostic '
            'local (relief, pluviométrie, marchés, intrants disponibles). Pour les produits NASA (MODIS, SMAP, '
            'GPM), consulter https://earthdata.nasa.gov/ et la documentation officielle des instruments.',
        ),
        body,
    ))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
