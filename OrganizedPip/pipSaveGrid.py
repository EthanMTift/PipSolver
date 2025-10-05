import json

def save_grid_json(img, anchor_x, anchor_y, tile_w, tile_h, image_path, json_path, ROWS, COLS):
    h, w = img.shape[:2]
    grid_data = {
        "image_path": image_path,
        "image_width": w,
        "image_height": h,
        "rows": ROWS,
        "cols": COLS,
        "tile_width": tile_w,
        "tile_height": tile_h,
        "anchor_x": anchor_x,
        "anchor_y": anchor_y
    }

    with open(json_path, "w") as f:
        json.dump(grid_data, f, indent=4)
    print(f"Saved grid data to {json_path}")