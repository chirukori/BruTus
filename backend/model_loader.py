"""
Model Loader for Retinal Fundus Diabetic Retinopathy Vision AI.
Loads and caches the fine-tuned MobileNetV2 model.
"""

import os
import tensorflow as tf
import keras

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'MobileNetV2_Final_Model.keras')

if not os.path.exists(MODEL_PATH):
    alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MobileNetV2_Final_Model.keras')
    if os.path.exists(alt_path):
        MODEL_PATH = alt_path

_CACHED_MODEL = None

CLASS_NAMES = {
    0: "No DR",
    1: "Mild DR",
    2: "Moderate DR",
    3: "Severe DR",
    4: "Proliferative DR"
}

CLASS_DESCRIPTIONS = {
    0: "No visible signs of diabetic retinopathy. Retinal blood vessels, macula, and optic disc appear healthy.",
    1: "Mild Non-Proliferative DR (NPDR). Presence of microaneurysms only.",
    2: "Moderate Non-Proliferative DR (NPDR). Microaneurysms, dot-and-blot hemorrhages, and hard lipid exudates.",
    3: "Severe Non-Proliferative DR (NPDR). 4-2-1 rule multi-quadrant hemorrhages and venous beading.",
    4: "Proliferative Diabetic Retinopathy (PDR). Neovascularization and vitreous hemorrhage."
}

MODEL_METRICS = {
    "model_name": "MobileNetV2 Fine-Tuned",
    "test_accuracy": "77.82%",
    "macro_f1": "0.55",
    "macro_roc_auc": "0.9137",
    "num_classes": 5,
    "input_resolution": "224 x 224 x 3"
}

def load_dr_model():
    global _CACHED_MODEL
    if _CACHED_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        _CACHED_MODEL = keras.models.load_model(MODEL_PATH, compile=False)
    return _CACHED_MODEL

def get_class_info(class_id):
    return {
        "id": class_id,
        "name": CLASS_NAMES.get(class_id, "Unknown"),
        "description": CLASS_DESCRIPTIONS.get(class_id, "")
    }

