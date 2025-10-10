import cv2
import json
from pipExtractSymbol import extract_symbol

DEBUG_FOLDER = 'symbol_debug'

def extract_tile_data(image, backgroundless_image, json_path, symbol_conf_threshold=50, debug=False, debug_folder=None):
    """
    Extract color and bottom-right symbol (with confidence) for each tile.
    Returns grid info and optional debug image.
    """
    with open(json_path, "r") as f:
        grid_data = json.load(f)

    rows = grid_data["rows"]
    cols = grid_data["cols"]
    tile_w = grid_data["tile_width"]
    tile_h = grid_data["tile_height"]
    anchor_x = grid_data["anchor_x"]
    anchor_y = grid_data["anchor_y"]

    h, w = image.shape[:2]
    grid_info = []
    debug_img = backgroundless_image.copy() if debug else None

    for r in range(rows):
        row_info = []
        for c in range(cols):
            # --- Color at tile center ---
            cx = int(anchor_x + c * tile_w + tile_w / 2)
            cy = int(anchor_y + r * tile_h + tile_h / 2)
            color = tuple(int(v) for v in image[cy, cx]) if 0 <= cx < w and 0 <= cy < h else None

            # --- Symbol patch ---
            br_x = int(anchor_x + (c + 1) * tile_w)
            br_y = int(anchor_y + (r + 1) * tile_h)
            # Patch size
            patch_w = int(tile_w / 1.5)
            patch_h = int(tile_h / 1.5)   # height shrink to 80%

            # Downward offset
            offset_y = int(tile_h * 0.1)

            # Coordinates
            x0 = br_x - patch_w // 2
            y0 = br_y - patch_h // 2 + offset_y
            x1 = x0 + patch_w
            y1 = y0 + patch_h

            # Lower bottom slightly
            bottom_lower = int(patch_h * .2)
            y1 = y1 - bottom_lower

            # Raise top slightly
            top_raise = int(patch_h * .08)
            y0 = y0 - top_raise

            # Clamp to image
            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(w, x1)
            y1 = min(h, y1)

            patch = backgroundless_image[y0:y1, x0:x1]

            # --- Detect symbol ---
            symbol, conf = extract_symbol(
                patch, json_path, conf_threshold=symbol_conf_threshold, debug_folder=DEBUG_FOLDER, tile_idx=(r,c)
            )

            # --- Debug visualization ---
            if debug and debug_img is not None:
                cv2.rectangle(debug_img, (x0, y0), (x1, y1), (0, 255, 0), 2)
                if symbol:
                    cv2.putText(debug_img, symbol, (x0, y0-2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)

            row_info.append({"color": color, "symbol": symbol, "conf": conf})
        grid_info.append(row_info)

    return (grid_info, debug_img) if debug else grid_info