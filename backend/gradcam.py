"""
Explainable AI (Grad-CAM) module for Retinal Fundus Deep Learning.
"""

import os
import numpy as np
import tensorflow as tf
import keras
import cv2
from PIL import Image
from backend.model_loader import load_dr_model

_GRADCAM_FEATURE_EXTRACTOR = None
_GRADCAM_HEAD_MODEL = None

def _get_gradcam_submodels(model=None):
    global _GRADCAM_FEATURE_EXTRACTOR, _GRADCAM_HEAD_MODEL
    if _GRADCAM_FEATURE_EXTRACTOR is None or _GRADCAM_HEAD_MODEL is None:
        if model is None:
            model = load_dr_model()
            
        base_model = model.get_layer("mobilenetv2_1.00_224")
        target_layer = base_model.get_layer("out_relu")
        
        _GRADCAM_FEATURE_EXTRACTOR = keras.Model(
            inputs=base_model.inputs,
            outputs=target_layer.output,
            name="gradcam_feature_extractor"
        )
        
        head_in = keras.Input(shape=(7, 7, 1280), name="gradcam_head_input")
        h = head_in
        for layer in model.layers[3:]:
            h = layer(h)
        _GRADCAM_HEAD_MODEL = keras.Model(
            inputs=head_in,
            outputs=h,
            name="gradcam_head_model"
        )
        
    return _GRADCAM_FEATURE_EXTRACTOR, _GRADCAM_HEAD_MODEL

def generate_gradcam(image_path, target_class_id=None, model=None, output_dir=None):
    if model is None:
        model = load_dr_model()
        
    feature_extractor, head_model = _get_gradcam_submodels(model)
    
    pil_orig = Image.open(image_path).convert('RGB')
    orig_w, orig_h = pil_orig.size
    
    pil_resized = pil_orig.resize((224, 224), Image.Resampling.BILINEAR)
    img_array = np.array(pil_resized, dtype=np.float32)
    preprocessed_input = keras.applications.mobilenet_v2.preprocess_input(img_array)
    input_tensor = tf.convert_to_tensor(np.expand_dims(preprocessed_input, axis=0))
    
    with tf.GradientTape() as tape:
        conv_outputs = feature_extractor(input_tensor, training=False)
        tape.watch(conv_outputs)
        predictions = head_model(conv_outputs, training=False)
        
        if target_class_id is None:
            target_class_id = int(tf.argmax(predictions[0]))
            
        class_output = predictions[:, target_class_id]

    grads = tape.gradient(class_output, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    conv_outputs_val = conv_outputs[0]
    heatmap = conv_outputs_val @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.math.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    heatmap = heatmap.numpy()

    heatmap_resized = cv2.resize(heatmap, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
    heatmap_uint8 = np.uint8(255 * np.clip(heatmap_resized, 0, 1))
    
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    orig_rgb_arr = np.array(pil_orig)
    overlay = cv2.addWeighted(orig_rgb_arr, 0.65, heatmap_colored_rgb, 0.35, 0)

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    heatmap_filename = f"{base_name}_gradcam_heatmap.jpg"
    overlay_filename = f"{base_name}_gradcam_overlay.jpg"
    
    heatmap_out_path = os.path.join(output_dir, heatmap_filename)
    overlay_out_path = os.path.join(output_dir, overlay_filename)
    
    Image.fromarray(heatmap_colored_rgb).save(heatmap_out_path, quality=95)
    Image.fromarray(overlay).save(overlay_out_path, quality=95)
    
    return {
        "heatmap_path": heatmap_out_path,
        "overlay_path": overlay_out_path,
        "heatmap_filename": heatmap_filename,
        "overlay_filename": overlay_filename,
        "target_class_id": target_class_id
    }

