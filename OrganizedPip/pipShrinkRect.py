import numpy as np

def refine_and_inset_rectangle(img, top_left, bottom_right, ROWS, COLS, target_color=(181, 190, 212), tolerance=10):
    """
    Shrinks the rectangle until it touches the target_color on all sides,
    then measures the border thickness from the LEFT side only and insets
    all sides by half that thickness.
    """
    x1, y1 = top_left
    x2, y2 = bottom_right

    h, w, _ = img.shape
    target_color = np.array(target_color, dtype=np.float32)
    white = np.array([255, 255, 255], dtype=np.float32)

    tile_w = (x2 - x1) / COLS
    tile_h = (y2 - y1) / ROWS

    def color_distance(c1, c2):
        return np.linalg.norm(c1.astype(np.float32) - c2)

    def is_target(px):
        return color_distance(px, target_color) < tolerance

    def is_white(px):
        return color_distance(px, white) < 25

    # --- Step 1: shrink rectangle inward until each side hits the color ---
    left_hit_y = None  # Store the y-coordinate of the first target pixel on the left
    while x1 < x2:
        col = img[y1:y2, x1]
        target_pixels = [i for i, px in enumerate(col) if is_target(px)]
        if target_pixels:
            left_hit_y = y1 + target_pixels[0]  # first target pixel in column
            break
        x1 += 1

    while x2 > x1:
        col = img[y1:y2, x2 - 1]
        if np.any([is_target(px) for px in col]):
            break
        x2 -= 1

    while y1 < y2:
        row = img[y1, x1:x2]
        if np.any([is_target(px) for px in row]):
            break
        y1 += 1

    while y2 > y1:
        row = img[y2 - 1, x1:x2]
        if np.any([is_target(px) for px in row]):
            break
        y2 -= 1

    rect_at_color = (x1, y1, x2, y2)

    # --- Step 2: measure border thickness from LEFT side using tile_h ---
    count = 0
    # Use the y of the first target pixel on the left side, then go half a tile down
    if left_hit_y is None:
        middle_y = int(y1 + tile_h / 2)
    else:
        middle_y = int(left_hit_y + tile_h / 2)
    middle_y = min(middle_y, y2 - 1)

    while True:
        x = x1 + count
        if x >= x2:
            break
        px = img[middle_y, x]
        if not (is_target(px) or is_white(px)):
            break
        count += 1

    border_thickness = count
    inset = border_thickness // 2

    # --- Step 3: inset all sides by half the measured thickness ---
    x1 += inset
    x2 -= inset
    y1 += inset
    y2 -= inset

    return (x1, y1), (x2, y2)
