"""
Prediction pipeline for Retinal Fundus Diabetic Retinopathy.
"""

import os
import numpy as np
from PIL import Image
import cv2
import keras
from backend.model_loader import load_dr_model, CLASS_NAMES, CLASS_DESCRIPTIONS

def validate_image_file(file_path_or_stream, filename=""):
    allowed_exts = {'.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(filename.lower())[1]
    if ext not in allowed_exts and filename != "":
        return False, f"Unsupported file type '{ext}'. Please upload JPG, JPEG, or PNG.", None
    
    try:
        if isinstance(file_path_or_stream, str):
            img = Image.open(file_path_or_stream)
        else:
            img = Image.open(file_path_or_stream)
            file_path_or_stream.seek(0)
            
        img.verify()
        
        if isinstance(file_path_or_stream, str):
            img = Image.open(file_path_or_stream)
        else:
            img = Image.open(file_path_or_stream)
            file_path_or_stream.seek(0)
            
        w, h = img.size
        if w < 100 or h < 100:
            return False, f"Image dimensions too small ({w}x{h}). Minimum required resolution is 100x100 pixels.", None
            
        return True, None, None
    except Exception as e:
        return False, f"Invalid or corrupted image file: {str(e)}", None

def preprocess_retinal_image(image_path, target_size=(224, 224)):
    pil_img = Image.open(image_path).convert('RGB')
    resized_img = pil_img.resize(target_size, Image.Resampling.BILINEAR)
    img_array = np.array(resized_img, dtype=np.float32)
    preprocessed_array = keras.applications.mobilenet_v2.preprocess_input(img_array)
    expanded_array = np.expand_dims(preprocessed_array, axis=0)
    return expanded_array, pil_img

def predict_retinopathy(image_path, model=None):
    if model is None:
        model = load_dr_model()
        
    processed_input, original_pil = preprocess_retinal_image(image_path)
    raw_preds = model(processed_input, training=False)
    probabilities_raw = raw_preds.numpy()[0]
    
    probabilities_dict = {}
    for idx, prob in enumerate(probabilities_raw):
        probabilities_dict[idx] = round(float(prob) * 100, 2)
        
    predicted_class_id = int(np.argmax(probabilities_raw))
    predicted_class_name = CLASS_NAMES.get(predicted_class_id, "Unknown")
    confidence = probabilities_dict[predicted_class_id]
    
    return {
        "predicted_class_id": predicted_class_id,
        "predicted_class_name": predicted_class_name,
        "confidence": confidence,
        "probabilities": probabilities_dict,
        "class_descriptions": CLASS_DESCRIPTIONS,
        "input_shape": list(processed_input.shape)
    }

