"""
Retinal Vision AI PDF Report Generator.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)

def generate_pdf_report(
    output_pdf_path,
    patient_id,
    prediction_id,
    predicted_stage_name,
    predicted_stage_id,
    confidence,
    probabilities,
    original_img_path=None,
    gradcam_overlay_path=None,
    model_name="MobileNetV2 Fine-Tuned",
    notes=""
):
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#080808")
    accent_color = colors.HexColor("#10B981")
    border_color = colors.HexColor("#e2e8f0")
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=primary_color)
    subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#64748b"))
    normal_text = ParagraphStyle('NormalText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"))
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=primary_color, spaceBefore=8, spaceAfter=4)

    story = []

    header_data = [
        [
            Paragraph("<b>AXIOM HEALTH &bull; RETINAL FUNDUS VISION AI</b>", title_style),
            Paragraph(f"<b>CASE:</b> #{prediction_id:05d}<br/><b>DATE:</b> {datetime.now().strftime('%d %b %Y, %H:%M')}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=4, spaceAfter=8))

    patient_info = [
        [Paragraph("<b>Patient Identifier:</b>", normal_text), Paragraph(str(patient_id), normal_text),
         Paragraph("<b>Analysis Model:</b>", normal_text), Paragraph(str(model_name), normal_text)],
        [Paragraph("<b>Modality:</b>", normal_text), Paragraph("Retinal Fundus (224x224 RGB)", normal_text),
         Paragraph("<b>Benchmark:</b>", normal_text), Paragraph("77.82% Test Accuracy", normal_text)]
    ]
    pt_table = Table(patient_info, colWidths=[120, 160, 110, 150])
    pt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(pt_table)
    story.append(Spacer(1, 10))

    finding_text = f"<font size='14'><b>PREDICTED: {predicted_stage_name.upper()} (STAGE {predicted_stage_id})</b></font><br/><font size='10'>Confidence: <b>{confidence:.2f}%</b> &nbsp;|&nbsp; Grad-CAM XAI Localized</font>"
    finding_table = Table([[Paragraph(finding_text, ParagraphStyle('F', parent=normal_text, textColor=colors.white, alignment=1))]], colWidths=[540])
    finding_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#10B981") if predicted_stage_id == 0 else colors.HexColor("#ef4444")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(finding_table)
    story.append(Spacer(1, 10))

    img_cells = []
    if original_img_path and os.path.exists(original_img_path):
        img_cells.append(Image(original_img_path, width=180, height=180))
    if gradcam_overlay_path and os.path.exists(gradcam_overlay_path):
        img_cells.append(Image(gradcam_overlay_path, width=180, height=180))
    if len(img_cells) == 2:
        img_table = Table([[img_cells[0], img_cells[1]],
                           [Paragraph("<b>Original Retinal Fundus</b>", normal_text), Paragraph("<b>Grad-CAM Heatmap Overlay</b>", normal_text)]], colWidths=[270, 270])
        img_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('TOPPADDING', (0,0), (-1,-1), 4)]))
        story.append(img_table)
        story.append(Spacer(1, 10))

    disclaimer_table = Table([[Paragraph("<b>RESEARCH DISCLAIMER:</b> Experimental decision support prototype. Does not replace examination by an ophthalmologist.", ParagraphStyle('D', parent=normal_text, textColor=colors.HexColor("#991b1b"), fontSize=8))]], colWidths=[540])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef2f2")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#fca5a5")),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether(disclaimer_table))

    doc.build(story)
    return output_pdf_path

