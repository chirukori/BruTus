"""
Trainer and Serializer for Diabetes Prediction Machine Learning Model.
Trained on the 8-feature Pima Indians Diabetes Dataset.
Features: ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
Target: 'Outcome' (0 = Non-Diabetic, 1 = Diabetic)
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

def train_and_save_model():
    dataset_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'diabetes.csv'),
        r'E:\study\sem 5\sem5\AIML LAB\diabetes.csv',
        r'C:\Users\Chiranthan\Downloads\diabetes_dataset.csv'
    ]
    
    csv_path = None
    for p in dataset_paths:
        if os.path.exists(p):
            csv_path = p
            break
            
    if not csv_path:
        raise FileNotFoundError("Could not find diabetes.csv dataset.")
        
    print(f"[Trainer] Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    features = [
        'Pregnancies',
        'Glucose',
        'BloodPressure',
        'SkinThickness',
        'Insulin',
        'BMI',
        'DiabetesPedigreeFunction',
        'Age'
    ]
    
    X = df[features]
    y = df['Outcome']
    
    # Train-test split (80/20) with fixed seed for exact reproducibility
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # Optional standard scaler for robust normalization
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train high-performance Random Forest Ensemble
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42
    )
    clf.fit(X_train_scaled, y_train)
    
    # Evaluate model
    y_pred = clf.predict(X_test_scaled)
    y_probs = clf.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_probs)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    # Feature importances
    importances = dict(zip(features, [round(float(v), 4) for v in clf.feature_importances_]))
    
    metrics = {
        'accuracy': round(float(acc) * 100, 2),
        'precision': round(float(prec) * 100, 2),
        'recall': round(float(rec) * 100, 2),
        'f1_score': round(float(f1), 4),
        'roc_auc': round(float(auc), 4),
        'confusion_matrix': cm,
        'feature_importances': importances,
        'features': features,
        'model_name': 'Random Forest Classifier (PIMA Ensemble)'
    }
    
    print(f"[Trainer] Model Evaluation:")
    print(f"  Accuracy:  {metrics['accuracy']}%")
    print(f"  Precision: {metrics['precision']}%")
    print(f"  Recall:    {metrics['recall']}%")
    print(f"  F1-Score:  {metrics['f1_score']}")
    print(f"  ROC-AUC:   {metrics['roc_auc']}")
    print(f"  Confusion Matrix: {cm}")
    
    # Save bundle into models/
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'diabetes_model.joblib')
    
    bundle = {
        'model': clf,
        'scaler': scaler,
        'features': features,
        'metrics': metrics
    }
    
    joblib.dump(bundle, out_path)
    print(f"[Trainer] Trained model saved successfully to: {out_path}")
    return out_path

if __name__ == '__main__':
    train_and_save_model()

