"""
Generates 5 realistic sample retinal fundus images for instant demo and evaluation:
- sample_0_no_dr.jpg (No DR)
- sample_1_mild_dr.jpg (Mild DR)
- sample_2_moderate_dr.jpg (Moderate DR)
- sample_3_severe_dr.jpg (Severe DR)
- sample_4_proliferative_dr.jpg (Proliferative DR)
"""

import os
import numpy as np
import cv2
from PIL import Image

def create_base_fundus(size=512):
    img = np.zeros((size, size, 3), dtype=np.uint8)
    center = (size // 2, size // 2)
    radius = int(size * 0.46)
    
    # Create smooth circular mask with soft edge
    Y, X = np.ogrid[:size, :size]
    dist = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    
    # Base orange-red retinal color gradient
    base_r = np.clip(210 - dist * 0.15, 60, 220).astype(np.uint8)
    base_g = np.clip(100 - dist * 0.15, 20, 110).astype(np.uint8)
    base_b = np.clip(50 - dist * 0.12, 10, 60).astype(np.uint8)
    
    img[:, :, 0] = base_r
    img[:, :, 1] = base_g
    img[:, :, 2] = base_b
    
    # Optic disc (yellowish-bright circle around x=160, y=256)
    disc_center = (int(size * 0.32), int(size * 0.5))
    disc_radius = int(size * 0.08)
    cv2.circle(img, disc_center, disc_radius, (245, 220, 140), -1)
    # Optic cup
    cv2.circle(img, disc_center, int(disc_radius * 0.55), (255, 245, 190), -1)
    
    # Macula / Fovea (darker reddish circular zone around x=340, y=256)
    macula_center = (int(size * 0.65), int(size * 0.51))
    macula_radius = int(size * 0.09)
    macula_overlay = img.copy()
    cv2.circle(macula_overlay, macula_center, macula_radius, (140, 45, 20), -1)
    cv2.addWeighted(macula_overlay, 0.45, img, 0.55, 0, img)
    # Foveal reflex
    cv2.circle(img, macula_center, int(size * 0.015), (105, 30, 15), -1)
    
    # Main retinal blood vessels branching out from optic disc
    vessel_color = (130, 30, 20)
    # Superior temporal arcade
    pts_sta = np.array([
        disc_center,
        (int(size * 0.38), int(size * 0.32)),
        (int(size * 0.52), int(size * 0.22)),
        (int(size * 0.70), int(size * 0.25)),
        (int(size * 0.82), int(size * 0.38))
    ], np.int32)
    cv2.polylines(img, [pts_sta], False, vessel_color, thickness=int(size*0.015), lineType=cv2.LINE_AA)
    
    # Inferior temporal arcade
    pts_ita = np.array([
        disc_center,
        (int(size * 0.38), int(size * 0.68)),
        (int(size * 0.52), int(size * 0.78)),
        (int(size * 0.70), int(size * 0.75)),
        (int(size * 0.82), int(size * 0.62))
    ], np.int32)
    cv2.polylines(img, [pts_ita], False, vessel_color, thickness=int(size*0.015), lineType=cv2.LINE_AA)
    
    # Superior & Inferior nasal vessels
    pts_sn = np.array([disc_center, (int(size * 0.22), int(size * 0.30)), (int(size * 0.15), int(size * 0.20))], np.int32)
    pts_in = np.array([disc_center, (int(size * 0.22), int(size * 0.70)), (int(size * 0.15), int(size * 0.80))], np.int32)
    cv2.polylines(img, [pts_sn], False, vessel_color, thickness=int(size*0.012), lineType=cv2.LINE_AA)
    cv2.polylines(img, [pts_in], False, vessel_color, thickness=int(size*0.012), lineType=cv2.LINE_AA)
    
    # Smaller vessel branches
    cv2.line(img, (int(size * 0.52), int(size * 0.22)), (int(size * 0.58), int(size * 0.34)), vessel_color, 2, cv2.LINE_AA)
    cv2.line(img, (int(size * 0.52), int(size * 0.78)), (int(size * 0.58), int(size * 0.66)), vessel_color, 2, cv2.LINE_AA)
    
    # Soft circular aperture crop (black background outside fundus disc)
    mask = (dist <= radius).astype(np.float32)
    feather = np.clip((radius - dist) / 6.0, 0.0, 1.0)
    for c in range(3):
        img[:, :, c] = (img[:, :, c] * feather).astype(np.uint8)
        
    return img

def add_dr_lesions(base_img, stage):
    img = base_img.copy()
    np.random.seed(42 + stage)
    size = img.shape[0]
    center = (size // 2, size // 2)
    radius = int(size * 0.40)
    
    def random_retina_point():
        while True:
            x = np.random.randint(int(size * 0.15), int(size * 0.85))
            y = np.random.randint(int(size * 0.15), int(size * 0.85))
            if np.sqrt((x - center[0])**2 + (y - center[1])**2) < radius:
                return (x, y)
                
    if stage >= 1:
        # Microaneurysms: small dark red dots (2-4 px)
        num_ma = 12 if stage == 1 else (30 if stage == 2 else 60)
        for _ in range(num_ma):
            pt = random_retina_point()
            cv2.circle(img, pt, np.random.randint(2, 4), (110, 15, 10), -1)
            
    if stage >= 2:
        # Dot and blot hemorrhages + Hard exudates (yellowish deposits)
        for _ in range(25):
            pt = random_retina_point()
            cv2.circle(img, pt, np.random.randint(3, 7), (100, 10, 8), -1)
        for _ in range(20):
            pt = random_retina_point()
            cv2.circle(img, pt, np.random.randint(2, 5), (245, 240, 160), -1)
            
    if stage >= 3:
        # Severe: Cotton wool spots & large flame hemorrhages
        for _ in range(8):
            pt = random_retina_point()
            cws = img.copy()
            cv2.circle(cws, pt, np.random.randint(10, 18), (240, 235, 220), -1)
            cv2.addWeighted(cws, 0.4, img, 0.6, 0, img)
        for _ in range(45):
            pt = random_retina_point()
            axes = (np.random.randint(5, 12), np.random.randint(3, 8))
            angle = np.random.randint(0, 180)
            cv2.ellipse(img, pt, axes, angle, 0, 360, (90, 8, 5), -1)
            
    if stage >= 4:
        # Proliferative DR: Neovascularization
        disc_center = (int(size * 0.32), int(size * 0.5))
        for _ in range(25):
            dx = np.random.randint(-35, 35)
            dy = np.random.randint(-35, 35)
            start_p = (disc_center[0] + dx, disc_center[1] + dy)
            end_p = (start_p[0] + np.random.randint(-15, 15), start_p[1] + np.random.randint(-15, 15))
            cv2.line(img, start_p, end_p, (140, 20, 15), 2, cv2.LINE_AA)
        vitreous_pt = (int(size * 0.55), int(size * 0.42))
        axes = (int(size * 0.16), int(size * 0.08))
        cv2.ellipse(img, vitreous_pt, axes, 25, 0, 360, (75, 5, 5), -1)
        
    return img

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static', 'images', 'samples')
    os.makedirs(out_dir, exist_ok=True)

    stage_labels = [
        ("sample_0_no_dr.jpg", 0, "Stage 0 - No DR (Healthy Retina)"),
        ("sample_1_mild_dr.jpg", 1, "Stage 1 - Mild DR (Microaneurysms)"),
        ("sample_2_moderate_dr.jpg", 2, "Stage 2 - Moderate DR (Exudates & Hemorrhages)"),
        ("sample_3_severe_dr.jpg", 3, "Stage 3 - Severe NPDR (Extensive Lesions)"),
        ("sample_4_proliferative_dr.jpg", 4, "Stage 4 - Proliferative DR (Neovascularization)")
    ]

    base = create_base_fundus(size=448)
    for filename, stage, title in stage_labels:
        img = add_dr_lesions(base, stage)
        img = cv2.GaussianBlur(img, (3, 3), 0.5)
        save_path = os.path.join(out_dir, filename)
        Image.fromarray(img).save(save_path, quality=95)
        print(f"Generated sample [{stage}]: {save_path}")

