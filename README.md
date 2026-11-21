# BruTus &bull; Autonomous Medical Intelligence Platform

BruTus is a medical AI web application that performs dual-modality clinical diagnostic triage:
1. **Retinal Vision AI**: Convolutional deep learning model (fine-tuned MobileNetV2) for automated classification of Diabetic Retinopathy severity stages (No DR, Mild NPDR, Moderate NPDR, Severe NPDR, Proliferative DR) paired with Explainable AI (Grad-CAM) visual attention heatmaps.
2. **Clinical Diabetes Risk Prediction Engine**: Multi-variable machine learning classifier (Random Forest Ensemble) analyzing 8 canonical metabolic biometrics from the PIMA dataset.
3. **Interactive 3D Anatomical Human Eye**: 3D biological exploration component rendered with Three.js featuring 360° orbital rotation, microvascular textures, and layer peeling.
4. **Clinical Dossier Generation**: Automated generation of clinical PDF medical diagnostic reports.

---

## Architecture & Technology Stack

- **Backend**: Python 3, Flask, SQLite
- **Machine Learning & Deep Learning**: TensorFlow / Keras (MobileNetV2), Scikit-Learn (Random Forest Ensemble), NumPy, OpenCV, Pillow
- **Explainability (XAI)**: Grad-CAM (Gradient-weighted Class Activation Mapping)
- **Frontend**: HTML5, Modern CSS3, JavaScript (ES6+), Bootstrap 5, Three.js (3D Anatomical Visualization), FontAwesome 6
- **Reporting**: ReportLab (High-resolution Clinical PDF generation)

---

## Directory Structure

```
├── backend/
│   ├── app.py                     # Flask application & routing
│   ├── diabetes_predictor.py      # Random Forest inference engine & feature attributions
│   ├── retinopathy_detector.py    # MobileNetV2 inference & Grad-CAM heatmap generator
│   ├── report_generator.py        # ReportLab clinical PDF generator
│   └── database.py                # SQLite clinical audit registry
├── frontend/
│   ├── templates/
│   │   ├── base.html              # Obsidian UI master template & navigation
│   │   ├── index.html             # Hero viewport with interactive 3D human eye
│   │   ├── predict.html           # 8-Parameter Biometric Prediction Terminal
│   │   ├── results.html           # Diagnostic risk dossier & biometric breakdown
│   │   ├── retinopathy.html       # Fundus image upload & analysis terminal
│   │   ├── retinopathy_results.html # Grad-CAM tri-view & severity staging
│   │   └── analytics.html         # Longitudinal clinical registry & cohort metrics
│   └── static/
│       ├── css/axiom.css          # Axiom Obsidian dark design system
│       └── js/
│           ├── axiom.js           # Interactive UI controllers
│           └── eye3d.js           # Three.js interactive 3D anatomical eye
├── models/
│   ├── diabetes_model.joblib      # Calibrated Random Forest model
│   └── MobileNetV2_Final_Model.keras # Fine-tuned MobileNetV2 deep learning model
├── reports/                       # Generated clinical PDF dossiers
├── uploads/                       # Retinal fundus scans and Grad-CAM overlays
├── run.py                         # Application entrypoint
└── test_axiom_platform.py         # Autonomous verification test suite
```

---

## Quickstart

### 1. Prerequisites
Ensure Python 3.10+ is installed.

### 2. Install Dependencies
```bash
pip install flask tensorflow scikit-learn numpy opencv-python pillow reportlab joblib
```

### 3. Launch Application
```bash
python run.py
```
Open your browser at `http://127.0.0.1:5000/`.

### 4. Run Test Suite
```bash
python test_axiom_platform.py
```

---

## License
Proprietary clinical research protocol.
