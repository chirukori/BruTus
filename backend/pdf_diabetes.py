"""
PDF Report Generator for Diabetes Risk Assessments.
Generates comprehensive clinical diagnostic dossiers using ReportLab.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def generate_diabetes_pdf(output_pdf_path, record):
    """
    Creates a formal clinical PDF report for a diabetes risk prediction.
    """
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
    
    # Obsidian & Axiom Palette
    obsidian_dark = colors.HexColor("#080808")
    primary_navy = colors.HexColor("#141313")
    accent_emerald = colors.HexColor("#10B981")
    accent_amber = colors.HexColor("#F59E0B")
    accent_rose = colors.HexColor("#EF4444")
    border_color = colors.HexColor("#262626")
    bg_subtle = colors.HexColor("#f8fafc")
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    
    is_diabetic = record.get('prediction', 0) == 1
    prob_diabetic = float(record.get('probability_diabetic', 0))
    risk_level = record.get('risk_level', 'Low Risk')
    
    if prob_diabetic >= 60:
        badge_bg = accent_rose
    elif prob_diabetic >= 35:
        badge_bg = accent_amber
    else:
        badge_bg = accent_emerald

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_navy,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_muted
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_navy,
        spaceBefore=10,
        spaceAfter=6
    )
    
    normal_text = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )
    
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#991b1b")
    )

    story = []

    # Header with Axiom Branding
    header_data = [
        [
            Paragraph("<b>AXIOM HEALTH &bull; AI DIABETES RISK ASSESSMENT</b>", title_style),
            Paragraph(f"<b>CASE DOSSIER:</b> #{record.get('id', 1):05d}<br/><b>TIMESTAMP:</b> {record.get('created_at', datetime.now().strftime('%d %b %Y, %H:%M'))}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceBefore=4, spaceAfter=8))

    # Patient & Specimen Info Table
    patient_info = [
        [
            Paragraph("<b>Patient Identifier:</b>", normal_text),
            Paragraph(str(record.get('patient_id', 'ANON-PATIENT')), normal_text),
            Paragraph("<b>Analysis Model:</b>", normal_text),
            Paragraph("Axiom PIMA Ensemble (Random Forest)", normal_text),
        ],
        [
            Paragraph("<b>Patient Name:</b>", normal_text),
            Paragraph(str(record.get('patient_name', 'Anonymous Patient')), normal_text),
            Paragraph("<b>Model Benchmarks:</b>", normal_text),
            Paragraph("74.68% Test Acc | 0.8154 ROC-AUC", normal_text),
        ]
    ]
    patient_table = Table(patient_info, colWidths=[120, 160, 110, 150])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_subtle),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 10))

    # Primary Finding Banner
    pred_label = record.get('prediction_label', 'Non-Diabetic')
    finding_text = f"<font size='14'><b>DIAGNOSTIC STATUS: {pred_label.upper()} ({risk_level.upper()})</b></font><br/><font size='10'>Calculated Diabetes Risk Probability: <b>{prob_diabetic:.1f}%</b> &nbsp;|&nbsp; Non-Diabetic Probability: <b>{float(record.get('probability_non_diabetic', 100 - prob_diabetic)):.1f}%</b></font>"
    finding_data = [[Paragraph(finding_text, ParagraphStyle('Finding', parent=normal_text, textColor=colors.white, alignment=1))]]
    finding_table = Table(finding_data, colWidths=[540])
    finding_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), badge_bg),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(finding_table)
    story.append(Spacer(1, 10))

    # Biometric Measurements Table
    story.append(Paragraph("<b>Patient Biometric Profiles (8 Standard Features)</b>", section_heading))
    bio_rows = [["Biometric Clinical Parameter", "Patient Value", "Standard Clinical Reference", "Evaluation"]]
    
    biometric_defs = [
        ("Pregnancies", record.get('pregnancies', 0), "count", "0 - 4 count"),
        ("Fasting Plasma Glucose", record.get('glucose', 0), "mg/dL", "70 - 99 mg/dL"),
        ("Diastolic Blood Pressure", record.get('blood_pressure', 0), "mm Hg", "60 - 80 mm Hg"),
        ("Triceps Skin Fold Thickness", record.get('skin_thickness', 0), "mm", "10 - 25 mm"),
        ("2-Hour Serum Insulin", record.get('insulin', 0), "μU/mL", "16 - 166 μU/mL"),
        ("Body Mass Index (BMI)", record.get('bmi', 0), "kg/m²", "18.5 - 24.9 kg/m²"),
        ("Diabetes Pedigree Function", record.get('diabetes_pedigree', 0), "score", "0.08 - 0.50 score"),
        ("Patient Age", record.get('age', 0), "years", "21 - 45 years")
    ]
    
    for label, val, unit, ref in biometric_defs:
        status_text = "Normal"
        status_color = "#10b981"
        v = float(val)
        if label == "Fasting Plasma Glucose" and v >= 100:
            status_text = "Elevated (Pre-Diabetic)" if v < 126 else "Critical (Diabetic Range)"
            status_color = "#f59e0b" if v < 126 else "#ef4444"
        elif label == "Body Mass Index (BMI)" and v >= 25.0:
            status_text = "Overweight" if v < 30.0 else "Obese (High Risk)"
            status_color = "#f59e0b" if v < 30.0 else "#ef4444"
        elif label == "Diastolic Blood Pressure" and v >= 80:
            status_text = "Stage 1/2 Hypertension"
            status_color = "#f59e0b"
            
        bio_rows.append([
            label,
            f"<b>{val}</b> {unit}",
            ref,
            f"<font color='{status_color}'><b>{status_text}</b></font>"
        ])
        
    bio_table = Table(bio_rows, colWidths=[180, 110, 130, 120])
    bio_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_navy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_subtle]),
    ]))
    story.append(bio_table)
    story.append(Spacer(1, 10))

    # Clinical Care Recommendations
    story.append(Paragraph("<b>Clinical Pathways & Preventive Action Plan</b>", section_heading))
    if prob_diabetic >= 60.0:
        rec_text = (
            "&bull; <b>Urgent Laboratory Confirmation:</b> Schedule venous plasma glucose and HbA1c test.<br/>"
            "&bull; <b>Endocrinology Consultation:</b> Rule out metabolic decompensation and diabetic ketoacidosis.<br/>"
            "&bull; <b>Comprehensive Ophthalmic Retinopathy Exam:</b> Dilated fundus examination is strongly advised to detect early microvascular retinal changes."
        )
    elif prob_diabetic >= 35.0:
        rec_text = (
            "&bull; <b>Targeted Lifestyle Modification:</b> Target 5-7% total body weight reduction via calorie deficit and structured exercise.<br/>"
            "&bull; <b>Dietary Adjustments:</b> Restrict refined carbohydrates and high-fructose corn syrups.<br/>"
            "&bull; <b>Follow-up Screening:</b> Re-evaluate fasting plasma glucose and oral glucose tolerance in 6 months."
        )
    else:
        rec_text = (
            "&bull; <b>Routine Health Maintenance:</b> Maintain nutritious low-glycemic dietary intake and cardiovascular fitness.<br/>"
            "&bull; <b>Annual Screening:</b> Routine annual wellness checkups recommended for monitoring metabolic profiles."
        )
    story.append(Paragraph(rec_text, normal_text))
    story.append(Spacer(1, 12))

    # Mandatory Legal & Medical Disclaimer
    disclaimer_box = [
        [Paragraph(
            "<b>MANDATORY RESEARCH DISCLAIMER:</b> "
            "This application is an experimental AI decision-support research prototype. Its predictions are not a medical diagnosis "
            "and must not replace clinical examination or laboratory blood testing by a qualified physician. "
            "Model confidence scores represent statistical machine learning approximations based on the PIMA Indians Diabetes cohort.",
            disclaimer_style
        )]
    ]
    disclaimer_table = Table(disclaimer_box, colWidths=[540])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef2f2")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#fca5a5")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(KeepTogether(disclaimer_table))

    doc.build(story)
    return output_pdf_path

