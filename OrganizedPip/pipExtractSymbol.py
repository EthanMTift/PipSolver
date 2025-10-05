import cv2
import json
import pytesseract
import os
import numpy as np




def extract_symbol(patch, json_path, conf_threshold=50, debug_folder=None, tile_idx=(0,0)):
    """
    Extract multi-character symbols from a patch using Tesseract.
    Returns symbol string and confidence.
    Applies fallback detection for '=' and '≠' using contours if OCR fails.
    Draws debug rectangles around detected bars if debug_folder is provided.
    Automatically reads tile_w and tile_h from the JSON file.
    """
    # --- Load tile size from JSON ---
    with open(json_path, "r") as f:
        grid_data = json.load(f)
    tile_w = grid_data["tile_width"]
    tile_h = grid_data["tile_height"]

    # --- Resize patch for OCR ---
    scale_factor = 4
    new_w = patch.shape[1] * scale_factor
    new_h = patch.shape[0] * scale_factor

    gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    thresh_inv = cv2.bitwise_not(thresh)  # symbols white (255), background black (0)
    gray_resized = cv2.resize(thresh_inv, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # --- OCR ---
    tesseract_config = r'-c tessedit_char_whitelist=0123456789<> --psm 6'
    text = pytesseract.image_to_string(gray_resized, config=tesseract_config).strip()

    data = pytesseract.image_to_data(gray_resized, config=tesseract_config, output_type=pytesseract.Output.DICT)
    confs = [c for c in data['conf'] if c >= 0]
    avg_conf = int(sum(confs)/len(confs)) if confs else 0

    # --- Save per-tile OCR debug ---
    if debug_folder:
        os.makedirs(debug_folder, exist_ok=True)
        debug_path = os.path.join(debug_folder, f"tile_{tile_idx[0]}_{tile_idx[1]}_ocr.png")
        cv2.imwrite(debug_path, gray_resized)

    # --- Return OCR result if confident ---
    if text and avg_conf >= conf_threshold:
        return text, avg_conf

    # --- Fallback detection for '=' and '≠' using contours ---
    black_pixels = np.sum(thresh_inv == 255)
    total_pixels = thresh_inv.size
    black_ratio = black_pixels / total_pixels

    # Find contours of white regions (the bars)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bars = []

    debug_patch = patch.copy()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)

        # Filter for horizontal bars using tile dimensions
        if w > tile_w * 0.1 and w < tile_w * 0.9 and aspect_ratio > 2:
            bars.append((x, y, w, h))
            # Draw a red rectangle around the detected bar for debug
            if debug_folder:
                cv2.rectangle(debug_patch, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Save debug image with bars drawn
    if debug_folder and bars:
        os.makedirs(debug_folder, exist_ok=True)
        debug_path = os.path.join(debug_folder, f"tile_{tile_idx[0]}_{tile_idx[1]}_bars.png")
        cv2.imwrite(debug_path, debug_patch)


    # If exactly two horizontal bars found → "="
    if len(bars) == 2:
        return "=", int(black_ratio*100)
    print(black_ratio)
    # If OCR failed and significant content remains → "≠"
    if black_ratio < .95:
        return "≠", int(black_ratio*100)

    # Nothing detected
    return None, avg_conf