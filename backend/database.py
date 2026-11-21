"""
Database module for Axiom AI Healthcare & Diabetes Prediction Platform.
Manages persistent SQLite tables for:
1. Diabetes Tabular Predictions (8 clinical biometrics)
2. Retinal Fundus Deep Learning Predictions (Grad-CAM XAI)
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.sqlite')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Diabetes Tabular Risk Predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diabetes_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT DEFAULT 'AX-PATIENT',
            patient_name TEXT DEFAULT 'Anonymous Patient',
            pregnancies REAL NOT NULL,
            glucose REAL NOT NULL,
            blood_pressure REAL NOT NULL,
            skin_thickness REAL NOT NULL,
            insulin REAL NOT NULL,
            bmi REAL NOT NULL,
            diabetes_pedigree REAL NOT NULL,
            age REAL NOT NULL,
            prediction INTEGER NOT NULL,
            prediction_label TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            risk_badge TEXT NOT NULL,
            probability_diabetic REAL NOT NULL,
            probability_non_diabetic REAL NOT NULL,
            confidence REAL NOT NULL,
            high_impact_drivers TEXT,
            notes TEXT,
            pdf_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Retinal Fundus Vision Predictions (Preserved)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT DEFAULT 'ANON-PATIENT',
            image_filename TEXT NOT NULL,
            image_path TEXT NOT NULL,
            predicted_class_id INTEGER NOT NULL,
            predicted_class_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities TEXT NOT NULL,
            gradcam_heatmap_path TEXT,
            gradcam_overlay_path TEXT,
            pdf_report_path TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ----------------- DIABETES PREDICTION CRUD ----------------- #

def insert_diabetes_prediction(patient_id, patient_name, inputs, result, notes="", pdf_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    drivers_json = json.dumps(result.get('high_impact_drivers', []))
    
    cursor.execute('''
        INSERT INTO diabetes_predictions (
            patient_id, patient_name, pregnancies, glucose, blood_pressure,
            skin_thickness, insulin, bmi, diabetes_pedigree, age,
            prediction, prediction_label, risk_level, risk_badge,
            probability_diabetic, probability_non_diabetic, confidence,
            high_impact_drivers, notes, pdf_path, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        patient_id,
        patient_name,
        float(inputs['Pregnancies']),
        float(inputs['Glucose']),
        float(inputs['BloodPressure']),
        float(inputs['SkinThickness']),
        float(inputs['Insulin']),
        float(inputs['BMI']),
        float(inputs['DiabetesPedigreeFunction']),
        float(inputs['Age']),
        result['prediction'],
        result['prediction_label'],
        result['risk_level'],
        result['risk_badge'],
        result['probability_diabetic'],
        result['probability_non_diabetic'],
        result['confidence'],
        drivers_json,
        notes,
        pdf_path,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def update_diabetes_pdf_path(record_id, pdf_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE diabetes_predictions SET pdf_path = ? WHERE id = ?', (pdf_path, record_id))
    conn.commit()
    conn.close()

def get_diabetes_prediction_by_id(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diabetes_predictions WHERE id = ?', (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        try:
            item['high_impact_drivers'] = json.loads(item['high_impact_drivers'])
        except Exception:
            item['high_impact_drivers'] = []
        return item
    return None

def get_all_diabetes_predictions(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diabetes_predictions ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item['high_impact_drivers'] = json.loads(item['high_impact_drivers'])
        except Exception:
            item['high_impact_drivers'] = []
        results.append(item)
    return results

def get_diabetes_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM diabetes_predictions')
    total = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as diabetic_count FROM diabetes_predictions WHERE prediction = 1')
    diabetic_count = cursor.fetchone()['diabetic_count']
    
    cursor.execute('SELECT COUNT(*) as non_diabetic_count FROM diabetes_predictions WHERE prediction = 0')
    non_diabetic_count = cursor.fetchone()['non_diabetic_count']
    
    cursor.execute('SELECT AVG(confidence) as avg_conf, AVG(glucose) as avg_gluc, AVG(bmi) as avg_bmi FROM diabetes_predictions')
    row = cursor.fetchone()
    avg_conf = round(row['avg_conf'], 1) if row['avg_conf'] is not None else 0.0
    avg_gluc = round(row['avg_gluc'], 1) if row['avg_gluc'] is not None else 0.0
    avg_bmi = round(row['avg_bmi'], 1) if row['avg_bmi'] is not None else 0.0
    
    conn.close()
    return {
        'total': total,
        'diabetic_count': diabetic_count,
        'non_diabetic_count': non_diabetic_count,
        'avg_confidence': avg_conf,
        'avg_glucose': avg_gluc,
        'avg_bmi': avg_bmi
    }

def delete_diabetes_prediction(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM diabetes_predictions WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()

def clear_all_diabetes_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM diabetes_predictions')
    conn.commit()
    conn.close()

# ----------------- RETINAL (EXISTING) CRUD ----------------- #

def insert_prediction(image_filename, image_path, predicted_class_id, predicted_class_name, 
                      confidence, probabilities, gradcam_heatmap_path=None, 
                      gradcam_overlay_path=None, patient_id="ANON-PATIENT", notes=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    prob_json = json.dumps(probabilities) if isinstance(probabilities, (dict, list)) else str(probabilities)
    cursor.execute('''
        INSERT INTO predictions (
            patient_id, image_filename, image_path, predicted_class_id,
            predicted_class_name, confidence, probabilities,
            gradcam_heatmap_path, gradcam_overlay_path, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        patient_id, image_filename, image_path, predicted_class_id,
        predicted_class_name, float(confidence), prob_json,
        gradcam_heatmap_path, gradcam_overlay_path, notes,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def update_pdf_path(record_id, pdf_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE predictions SET pdf_report_path = ? WHERE id = ?', (pdf_path, record_id))
    conn.commit()
    conn.close()

def get_prediction_by_id(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE id = ?', (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        item['probabilities'] = json.loads(item['probabilities'])
        return item
    return None

def get_all_predictions(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item['probabilities'] = json.loads(item['probabilities'])
        except Exception:
            pass
        results.append(item)
    return results

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM predictions')
    total = cursor.fetchone()['total']
    
    stage_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    stage_names = {0: 'No DR', 1: 'Mild DR', 2: 'Moderate DR', 3: 'Severe DR', 4: 'Proliferative DR'}
    
    cursor.execute('SELECT predicted_class_id, COUNT(*) as count FROM predictions GROUP BY predicted_class_id')
    for row in cursor.fetchall():
        stage_counts[row['predicted_class_id']] = row['count']
        
    cursor.execute('SELECT AVG(confidence) as avg_conf FROM predictions')
    avg_conf_row = cursor.fetchone()
    avg_confidence = avg_conf_row['avg_conf'] if avg_conf_row['avg_conf'] is not None else 0.0
    
    conn.close()
    return {
        'total_analyzed': total,
        'stage_counts': stage_counts,
        'stage_names': stage_names,
        'avg_confidence': round(avg_confidence, 2)
    }

def delete_prediction(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()

def clear_all_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at", DB_PATH)

