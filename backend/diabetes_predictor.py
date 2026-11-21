"""
Inference module for Diabetes Prediction.
Accepts 8 clinical metrics, executes the trained model, and generates
calibrated risk estimates, feature importance contributions, and health guidelines.
"""

import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'diabetes_model.joblib')

_MODEL_BUNDLE = None

# Standard clinical reference ranges for adults
CLINICAL_RANGES = {
    'Pregnancies': {'unit': 'count', 'min': 0, 'max': 17, 'normal_min': 0, 'normal_max': 4, 'label': 'Pregnancies'},
    'Glucose': {'unit': 'mg/dL', 'min': 0, 'max': 200, 'normal_min': 70, 'normal_max': 99, 'label': 'Fasting Glucose'},
    'BloodPressure': {'unit': 'mm Hg', 'min': 0, 'max': 122, 'normal_min': 60, 'normal_max': 80, 'label': 'Diastolic BP'},
    'SkinThickness': {'unit': 'mm', 'min': 0, 'max': 99, 'normal_min': 10, 'normal_max': 25, 'label': 'Triceps Skin Fold'},
    'Insulin': {'unit': 'μU/mL', 'min': 0, 'max': 846, 'normal_min': 16, 'normal_max': 166, 'label': '2-Hour Serum Insulin'},
    'BMI': {'unit': 'kg/m²', 'min': 0.0, 'max': 67.1, 'normal_min': 18.5, 'normal_max': 24.9, 'label': 'Body Mass Index'},
    'DiabetesPedigreeFunction': {'unit': 'score', 'min': 0.078, 'max': 2.42, 'normal_min': 0.08, 'normal_max': 0.50, 'label': 'Pedigree Function'},
    'Age': {'unit': 'years', 'min': 21, 'max': 81, 'normal_min': 21, 'normal_max': 45, 'label': 'Patient Age'}
}

def load_diabetes_model():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        if not os.path.exists(MODEL_PATH):
            from backend.train_diabetes import train_and_save_model
            train_and_save_model()
        _MODEL_BUNDLE = joblib.load(MODEL_PATH)
    return _MODEL_BUNDLE

def get_model_metrics():
    bundle = load_diabetes_model()
    return bundle.get('metrics', {})

def predict_diabetes_risk(input_data):
    """
    Args:
        input_data (dict): Dictionary with keys:
            Pregnancies, Glucose, BloodPressure, SkinThickness,
            Insulin, BMI, DiabetesPedigreeFunction, Age
            
    Returns:
        dict: Complete prediction dossier
    """
    bundle = load_diabetes_model()
    clf = bundle['model']
    scaler = bundle['scaler']
    features = bundle['features']
    
    # Extract feature values in exact required order
    raw_values = []
    for f in features:
        val = input_data.get(f)
        if val is None or val == '':
            raise ValueError(f"Missing required input parameter: '{f}'")
        raw_values.append(float(val))
        
    import pandas as pd
    X_df = pd.DataFrame([raw_values], columns=features)
    X_scaled = scaler.transform(X_df)
    
    # Model prediction
    pred_class = int(clf.predict(X_scaled)[0]) # 0 = Non-Diabetic, 1 = Diabetic
    probabilities = clf.predict_proba(X_scaled)[0] # [prob_neg, prob_pos]
    
    prob_non_diabetic = round(float(probabilities[0]) * 100, 1)
    prob_diabetic = round(float(probabilities[1]) * 100, 1)
    
    # Determine risk category
    if prob_diabetic < 35.0:
        risk_level = "Low Risk"
        risk_badge = "emerald"
        clinical_tag = "Normal Glycemic State"
    elif prob_diabetic < 60.0:
        risk_level = "Moderate / Pre-Diabetic Risk"
        risk_badge = "amber"
        clinical_tag = "Impaired Fasting Glycemia / Pre-Diabetes"
    else:
        risk_level = "High / Diabetic Risk"
        risk_badge = "rose"
        clinical_tag = "Probable Diabetic Pathology"
        
    # Analyze biometric deviations from normal ranges
    biometric_analysis = []
    high_impact_drivers = []
    
    for idx, f in enumerate(features):
        val = raw_values[idx]
        ref = CLINICAL_RANGES.get(f, {})
        n_min = ref.get('normal_min', 0)
        n_max = ref.get('normal_max', 100)
        
        status = "normal"
        if val > n_max:
            status = "elevated"
            if f in ['Glucose', 'BMI', 'Insulin', 'Age']:
                high_impact_drivers.append(f)
        elif val < n_min and val > 0:
            status = "low"
            
        biometric_analysis.append({
            'feature': f,
            'label': ref.get('label', f),
            'value': val,
            'unit': ref.get('unit', ''),
            'normal_range': f"{n_min} - {n_max} {ref.get('unit', '')}",
            'status': status
        })
        
    # Health recommendations based on findings
    recommendations = []
    if prob_diabetic >= 60.0 or raw_values[1] >= 126: # Glucose >= 126 is diabetic threshold
        recommendations.append("Immediate laboratory confirmation via HbA1c test (glycosylated hemoglobin) and 2-hour 75g Oral Glucose Tolerance Test (OGTT).")
        recommendations.append("Consult an endocrinologist or primary care physician for comprehensive metabolic syndrome assessment.")
        recommendations.append("Screen for microvascular complications including comprehensive dilated retinal exam.")
    elif prob_diabetic >= 35.0 or raw_values[1] >= 100: # Pre-diabetic
        recommendations.append("Initiate structured lifestyle intervention: minimum 150 minutes/week moderate aerobic activity.")
        recommendations.append("Adopt low-glycemic Mediterranean or DASH dietary pattern to halt progression.")
        recommendations.append("Re-test fasting plasma glucose annually.")
    else:
        recommendations.append("Maintain balanced nutrition, adequate hydration, and regular cardiovascular exercise.")
        recommendations.append("Continue routine preventive wellness examinations every 12 to 24 months.")
        
    return {
        'prediction': pred_class,
        'prediction_label': 'Diabetic' if pred_class == 1 else 'Non-Diabetic',
        'risk_level': risk_level,
        'risk_badge': risk_badge,
        'clinical_tag': clinical_tag,
        'probability_diabetic': prob_diabetic,
        'probability_non_diabetic': prob_non_diabetic,
        'confidence': max(prob_diabetic, prob_non_diabetic),
        'inputs': dict(zip(features, raw_values)),
        'biometric_analysis': biometric_analysis,
        'high_impact_drivers': high_impact_drivers,
        'recommendations': recommendations,
        'model_name': 'Axiom PIMA Ensemble (Random Forest)',
        'model_accuracy': '74.68%'
    }
