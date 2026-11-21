"""
Comprehensive Test Suite for Axiom Health &bull; Autonomous Diabetes Prediction Platform.
Tests all web routes, tabular diabetes ML inference, Retinopathy Grad-CAM, PDF generation, and SQLite persistence.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app
from backend.database import get_db_connection, get_diabetes_prediction_by_id, get_diabetes_stats

def run_axiom_test_suite():
    print("===================================================================")
    print("  AXIOM HEALTH &bull; AUTONOMOUS PLATFORM VERIFICATION SUITE")
    print("===================================================================")
    
    app.config['TESTING'] = True
    client = app.test_client()
    
    # 1. Test Web Page Routes
    print("\n[Test 1] Testing Web Viewport Routes (Axiom Obsidian UI)...")
    routes = [
        ('/', 'BruTus Landing Page'),
        ('/predict', '8-Parameter Predictor Terminal'),
        ('/analytics', 'Clinical Analytics & Model Registry'),
        ('/retinopathy', 'Retinal Fundus Vision AI')
    ]
    for r, label in routes:
        resp = client.get(r)
        assert resp.status_code == 200, f"Route {r} failed with status {resp.status_code}"
        html = resp.get_data(as_text=True)
        assert 'BruTus' in html, f"Route {r} does not contain BruTus branding"
        print(f"  ✓ {label} ({r}) -> HTTP 200 OK (Obsidian UI active)")

    # Verify deprecated sections redirect safely without breaking routing
    for r in ['/about', '/contact']:
        resp = client.get(r, follow_redirects=True)
        assert resp.status_code == 200, f"Redirect for {r} failed with status {resp.status_code}"
        html = resp.get_data(as_text=True)
        assert 'BruTus' in html
        print(f"  ✓ Safe Deprecation Redirect ({r}) -> HTTP 200 OK (Routed to Home)")

    # 2. Test Diabetes Prediction on Low-Risk Profile
    print("\n[Test 2] Testing Diabetes ML Inference on Low-Risk Profile...")
    normal_payload = {
        'Pregnancies': 0,
        'Glucose': 85,
        'BloodPressure': 68,
        'SkinThickness': 20,
        'Insulin': 75,
        'BMI': 21.8,
        'DiabetesPedigreeFunction': 0.18,
        'Age': 24,
        'patient_id': 'AX-TEST-001',
        'patient_name': 'Sarah Connor (Test)'
    }
    resp = client.post('/api/predict_diabetes', json=normal_payload)
    assert resp.status_code == 200, f"Prediction failed: {resp.data}"
    data = resp.get_json()
    assert data['success'] is True
    rec_id_1 = data['record_id']
    res_1 = data['result']
    assert res_1['prediction'] == 0, f"Expected Non-Diabetic (0), got {res_1['prediction']}"
    assert res_1['prediction_label'] == 'Non-Diabetic'
    print(f"  ✓ Case #{rec_id_1:05d} successfully staged:")
    print(f"    - Classification: {res_1['prediction_label']} ({res_1['risk_level']})")
    print(f"    - Diabetic Probability: {res_1['probability_diabetic']}%")
    print(f"    - Confidence: {res_1['confidence']}%")

    # 3. Test Diabetes Prediction on High-Risk Profile
    print("\n[Test 3] Testing Diabetes ML Inference on High-Risk Profile...")
    highrisk_payload = {
        'Pregnancies': 5,
        'Glucose': 172,
        'BloodPressure': 88,
        'SkinThickness': 35,
        'Insulin': 240,
        'BMI': 38.6,
        'DiabetesPedigreeFunction': 0.88,
        'Age': 54,
        'patient_id': 'AX-TEST-002',
        'patient_name': 'Marcus Vance (Test)'
    }
    resp2 = client.post('/api/predict_diabetes', json=highrisk_payload)
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2['success'] is True
    rec_id_2 = data2['record_id']
    res_2 = data2['result']
    assert res_2['prediction'] == 1, f"Expected Diabetic (1), got {res_2['prediction']}"
    assert res_2['prediction_label'] == 'Diabetic'
    print(f"  ✓ Case #{rec_id_2:05d} successfully staged:")
    print(f"    - Classification: {res_2['prediction_label']} ({res_2['risk_level']})")
    print(f"    - Diabetic Probability: {res_2['probability_diabetic']}%")
    print(f"    - High Impact Drivers: {res_2['high_impact_drivers']}")

    # 4. Test Results Page Rendering
    print(f"\n[Test 4] Testing Diagnostic Results Page (/results/{rec_id_2})...")
    resp_view = client.get(f'/results/{rec_id_2}')
    assert resp_view.status_code == 200
    html_view = resp_view.get_data(as_text=True)
    assert 'Marcus Vance' in html_view
    assert 'Fasting Glucose' in html_view
    assert 'Clinical Care Recommendations' in html_view
    print(f"  ✓ Results dossier rendered with biometric breakdown and risk gauge.")

    # 5. Test PDF Report Generation & Serving
    print(f"\n[Test 5] Testing PDF Report Download (/api/download_pdf/{rec_id_2})...")
    pdf_resp = client.get(f'/api/download_pdf/{rec_id_2}')
    assert pdf_resp.status_code == 200
    assert 'application/pdf' in pdf_resp.content_type
    assert len(pdf_resp.data) > 1000, "PDF file is empty or corrupted"
    print(f"  ✓ PDF Dossier served successfully (Size: {len(pdf_resp.data)} bytes).")

    # 6. Test Retinopathy Vision AI module
    print("\n[Test 6] Testing Retinopathy Vision AI & Grad-CAM...")
    ret_resp = client.post('/api/predict_retinopathy', data={
        'sample_image': 'sample_0_no_dr.jpg',
        'patient_id': 'AX-RET-TEST'
    })
    assert ret_resp.status_code == 200
    ret_data = ret_resp.get_json()
    assert ret_data['success'] is True
    ret_id = ret_data['record_id']
    print(f"  ✓ Retinal fundus analyzed! Record ID: {ret_id}")
    
    ret_view = client.get(f'/retinopathy/results/{ret_id}')
    assert ret_view.status_code == 200
    print(f"  ✓ Retinopathy Grad-CAM tri-view rendered successfully.")

    # 7. Test SQLite Analytics Registry
    print("\n[Test 7] Testing SQLite Analytics Registry...")
    stats = get_diabetes_stats()
    assert stats['total'] >= 2
    assert stats['diabetic_count'] >= 1
    assert stats['non_diabetic_count'] >= 1
    print(f"  ✓ Audit registry validated: {stats['total']} total cases, {stats['diabetic_count']} diabetic, {stats['non_diabetic_count']} non-diabetic.")
    print(f"  ✓ Mean Cohort Glucose: {stats['avg_glucose']} mg/dL, Mean BMI: {stats['avg_bmi']}")

    print("\n===================================================================")
    print("  ALL 7 AXIOM INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("===================================================================")

if __name__ == '__main__':
    run_axiom_test_suite()

