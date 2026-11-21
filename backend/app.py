"""
Axiom Health &bull; Autonomous Diabetes Prediction & Clinical Intelligence Platform
Flask Web Application providing RESTful prediction endpoints, telemetry, and PDF reporting.
"""

import os
import uuid
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for,
    send_from_directory, flash, abort
)
from werkzeug.utils import secure_filename

# Backend modules
from backend.diabetes_predictor import predict_diabetes_risk, get_model_metrics
from backend.pdf_diabetes import generate_diabetes_pdf
from backend.database import (
    init_db,
    insert_diabetes_prediction, update_diabetes_pdf_path,
    get_diabetes_prediction_by_id, get_all_diabetes_predictions,
    get_diabetes_stats, delete_diabetes_prediction, clear_all_diabetes_predictions,
    # Retinopathy functions
    insert_prediction, update_pdf_path, get_prediction_by_id,
    get_all_predictions, get_dashboard_stats, delete_prediction
)
from backend.model_loader import load_dr_model, MODEL_METRICS, CLASS_NAMES
from backend.prediction import predict_retinopathy, validate_image_file
from backend.gradcam import generate_gradcam
from backend.pdf_report import generate_pdf_report

# Initialize directories
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
STATIC_FOLDER = os.path.join(BASE_DIR, 'frontend', 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'frontend', 'templates')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=TEMPLATE_FOLDER,
    static_folder=STATIC_FOLDER
)

app.config['SECRET_KEY'] = 'axiom-health-secret-key-2026'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

# Initialize SQLite tables on startup
init_db()

# Pre-load models
try:
    load_dr_model()
except Exception as e:
    print(f"[Warning] MobileNetV2 could not be pre-loaded: {e}")

@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'dr_metrics': MODEL_METRICS,
        'class_names': CLASS_NAMES
    }

# ----------------- PAGE ROUTES ----------------- #

@app.route('/')
def index():
    """Axiom Landing Page with telemetry terminal, metrics, and architecture overview."""
    stats = get_diabetes_stats()
    return render_template('index.html', stats=stats)

@app.route('/predict')
def predict_page():
    """8-Biometric Clinical Diabetes Prediction Terminal."""
    return render_template('predict.html')

@app.route('/results/<int:record_id>')
def results_page(record_id):
    """Clinical Diabetes Assessment Dossier."""
    record = get_diabetes_prediction_by_id(record_id)
    if not record:
        flash("Case record not found in audit registry.", "danger")
        return redirect(url_for('analytics_page'))
        
    # Reconstruct biometric deviations and recommendations from input values
    CLINICAL_RANGES = {
        'Glucose': {'label': 'Fasting Glucose', 'unit': 'mg/dL', 'normal_min': 70, 'normal_max': 99},
        'BMI': {'label': 'Body Mass Index', 'unit': 'kg/m²', 'normal_min': 18.5, 'normal_max': 24.9},
        'BloodPressure': {'label': 'Blood Pressure', 'unit': 'mm Hg', 'normal_min': 60, 'normal_max': 80},
        'Insulin': {'label': 'Serum Insulin', 'unit': 'μU/mL', 'normal_min': 16, 'normal_max': 166},
        'SkinThickness': {'label': 'Skin Thickness', 'unit': 'mm', 'normal_min': 10, 'normal_max': 25},
        'DiabetesPedigreeFunction': {'label': 'Diabetes Pedigree', 'unit': 'score', 'normal_min': 0.08, 'normal_max': 0.50},
        'Pregnancies': {'label': 'Pregnancies', 'unit': 'count', 'normal_min': 0, 'normal_max': 4},
        'Age': {'label': 'Patient Age', 'unit': 'years', 'normal_min': 21, 'normal_max': 65}
    }
    
    val_map = {
        'Glucose': record['glucose'],
        'BMI': record['bmi'],
        'BloodPressure': record['blood_pressure'],
        'Insulin': record['insulin'],
        'SkinThickness': record['skin_thickness'],
        'DiabetesPedigreeFunction': record['diabetes_pedigree'],
        'Pregnancies': record['pregnancies'],
        'Age': record['age']
    }
    
    deviations = []
    for f, ref in CLINICAL_RANGES.items():
        v = val_map.get(f, 0)
        n_min = ref['normal_min']
        n_max = ref['normal_max']
        status = "Optimal"
        if v > n_max:
            status = "Elevated"
        elif v < n_min and v > 0:
            status = "Low"
        deviations.append({
            'feature': ref['label'],
            'value': v,
            'unit': ref['unit'],
            'normal': f"{n_min}–{n_max}",
            'status': status
        })
    record['deviations'] = deviations
    
    recs = []
    if record['probability_diabetic'] >= 60.0 or record['glucose'] >= 126:
        recs.append("Immediate laboratory confirmation via HbA1c test and 2-hour 75g Oral Glucose Tolerance Test (OGTT).")
        recs.append("Consult an endocrinologist or primary care physician for comprehensive metabolic syndrome assessment.")
        recs.append("Screen for microvascular complications including comprehensive dilated retinal exam.")
    elif record['probability_diabetic'] >= 35.0 or record['glucose'] >= 100:
        recs.append("Initiate structured lifestyle intervention: minimum 150 minutes/week moderate aerobic activity.")
        recs.append("Adopt low-glycemic Mediterranean or DASH dietary pattern to halt progression.")
        recs.append("Re-test fasting plasma glucose annually.")
    else:
        recs.append("Maintain balanced nutrition, adequate hydration, and regular cardiovascular exercise.")
        recs.append("Continue routine preventive wellness examinations every 12 to 24 months.")
        recs.append("Annual metabolic risk screening for early detection.")
    record['recommendations'] = recs
    
    return render_template('results.html', record=record)

@app.route('/analytics')
def analytics_page():
    """Model Registry, Evaluation Metrics, and Ingestion Audit History."""
    stats = get_diabetes_stats()
    history = get_all_diabetes_predictions(limit=50)
    metrics = get_model_metrics()
    return render_template('analytics.html', stats=stats, history=history, metrics=metrics)

@app.route('/retinopathy')
def retinopathy_page():
    """Retinal Fundus Vision AI & Grad-CAM module."""
    return render_template('retinopathy.html')

@app.route('/retinopathy/results/<int:record_id>')
def retinopathy_results_page(record_id):
    """Grad-CAM Retinal Vision Results."""
    record = get_prediction_by_id(record_id)
    if not record:
        flash("Retinal record not found.", "danger")
        return redirect(url_for('retinopathy_page'))
    return render_template('retinopathy_results.html', record=record)

@app.route('/about')
def about_page():
    """Redirect deprecated methodology page to home."""
    return redirect(url_for('index'))

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    """Redirect deprecated contact page to home."""
    return redirect(url_for('index'))

# ----------------- DIABETES API ENDPOINTS ----------------- #

@app.route('/api/predict_diabetes', methods=['POST'])
def api_predict_diabetes():
    """
    Ingests the 8 clinical metrics, runs the trained Random Forest model,
    saves record in SQLite, generates clinical PDF, and returns redirection payload.
    """
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        if not data:
            return jsonify({'success': False, 'error': 'No input biometric payload received.'}), 400
            
        patient_id = data.get('patient_id', '').strip() or f"AX-{uuid.uuid4().hex[:6].upper()}"
        patient_name = data.get('patient_name', '').strip() or "Anonymous Patient"
        notes = data.get('notes', '').strip()
        
        # Execute trained machine learning model
        result = predict_diabetes_risk(data)
        
        # Insert into SQLite
        record_id = insert_diabetes_prediction(
            patient_id=patient_id,
            patient_name=patient_name,
            inputs=result['inputs'],
            result=result,
            notes=notes
        )
        
        # Generate official clinical PDF report
        pdf_filename = f"axiom_diabetes_report_CASE_{record_id:05d}.pdf"
        pdf_path = os.path.join(REPORT_FOLDER, pdf_filename)
        
        full_record = get_diabetes_prediction_by_id(record_id)
        generate_diabetes_pdf(pdf_path, full_record)
        update_diabetes_pdf_path(record_id, pdf_filename)
        
        return jsonify({
            'success': True,
            'record_id': record_id,
            'redirect_url': url_for('results_page', record_id=record_id),
            'result': result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download_pdf/<int:record_id>')
def download_diabetes_pdf(record_id):
    """Serves the generated Diabetes clinical PDF dossier."""
    record = get_diabetes_prediction_by_id(record_id)
    if not record or not record.get('pdf_path'):
        abort(404, description="PDF dossier not found.")
    return send_from_directory(REPORT_FOLDER, record['pdf_path'], as_attachment=True)

@app.route('/api/delete_diabetes/<int:record_id>', methods=['POST'])
def api_delete_diabetes_record(record_id):
    delete_diabetes_prediction(record_id)
    flash("Record removed from audit registry.", "info")
    return redirect(url_for('analytics_page'))

@app.route('/api/clear_diabetes_history', methods=['POST'])
def api_clear_diabetes_history():
    clear_all_diabetes_predictions()
    flash("Audit registry cleared.", "warning")
    return redirect(url_for('analytics_page'))

# ----------------- RETINOPATHY API ENDPOINTS ----------------- #

@app.route('/api/predict_retinopathy', methods=['POST'])
def api_predict_retinopathy():
    try:
        sample_name = request.form.get('sample_image')
        patient_id = request.form.get('patient_id', '').strip() or f"AX-RET-{uuid.uuid4().hex[:6].upper()}"
        clinical_notes = request.form.get('notes', '').strip()
        
        file_to_process = None
        if sample_name:
            sample_clean = os.path.basename(sample_name)
            sample_source = os.path.join(STATIC_FOLDER, 'images', 'samples', sample_clean)
            if not os.path.exists(sample_source):
                return jsonify({'success': False, 'error': 'Sample image not found.'}), 400
            uid = uuid.uuid4().hex[:8]
            saved_filename = f"sample_{uid}_{sample_clean}"
            dest_path = os.path.join(UPLOAD_FOLDER, saved_filename)
            import shutil
            shutil.copy(sample_source, dest_path)
            file_to_process = dest_path
        elif 'image' in request.files and request.files['image'].filename != '':
            uploaded_file = request.files['image']
            orig_filename = secure_filename(uploaded_file.filename)
            is_valid, err_msg, warn_msg = validate_image_file(uploaded_file, orig_filename)
            if not is_valid:
                return jsonify({'success': False, 'error': err_msg}), 400
            uid = uuid.uuid4().hex[:8]
            ext = os.path.splitext(orig_filename)[1].lower()
            file_to_process = os.path.join(UPLOAD_FOLDER, f"retina_{uid}{ext}")
            uploaded_file.save(file_to_process)
        else:
            return jsonify({'success': False, 'error': 'No image provided.'}), 400
            
        pred_result = predict_retinopathy(file_to_process)
        pred_class_id = pred_result['predicted_class_id']
        pred_class_name = pred_result['predicted_class_name']
        confidence = pred_result['confidence']
        probabilities = pred_result['probabilities']
        
        gradcam_res = generate_gradcam(file_to_process, pred_class_id, output_dir=UPLOAD_FOLDER)
        
        record_id = insert_prediction(
            image_filename=os.path.basename(file_to_process),
            image_path=file_to_process,
            predicted_class_id=pred_class_id,
            predicted_class_name=pred_class_name,
            confidence=confidence,
            probabilities=probabilities,
            gradcam_heatmap_path=gradcam_res['heatmap_filename'],
            gradcam_overlay_path=gradcam_res['overlay_filename'],
            patient_id=patient_id,
            notes=clinical_notes
        )
        
        pdf_filename = f"report_PAT_{patient_id}_REC_{record_id}.pdf"
        pdf_output_path = os.path.join(REPORT_FOLDER, pdf_filename)
        generate_pdf_report(
            output_pdf_path=pdf_output_path,
            patient_id=patient_id,
            prediction_id=record_id,
            predicted_stage_name=pred_class_name,
            predicted_stage_id=pred_class_id,
            confidence=confidence,
            probabilities=probabilities,
            original_img_path=file_to_process,
            gradcam_overlay_path=gradcam_res['overlay_path'],
            model_name="MobileNetV2 Fine-Tuned (77.82% Test Acc)",
            notes=clinical_notes
        )
        update_pdf_path(record_id, pdf_filename)
        
        return jsonify({
            'success': True,
            'record_id': record_id,
            'redirect_url': url_for('retinopathy_results_page', record_id=record_id)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download_retina_pdf/<int:record_id>')
def download_retina_pdf(record_id):
    record = get_prediction_by_id(record_id)
    if not record or not record.get('pdf_report_path'):
        abort(404, description="Report not found.")
    return send_from_directory(REPORT_FOLDER, record['pdf_report_path'], as_attachment=True)

# Static file serving
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory(REPORT_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

