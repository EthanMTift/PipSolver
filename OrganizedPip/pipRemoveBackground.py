import cv2
import numpy as np

def remove_white_background(img, tile_w, tile_h, tol=240):
    """
    Turn the white-ish background of an image to black,
    without affecting isolated white symbols. Also fills any
    large white holes inside the board (e.g., missing background
    in the middle of the image).

    Parameters:
        img (numpy.ndarray): Input image (BGR)
        tol (int): Tolerance for considering a pixel as white
        tile_w, tile_h (int): Approximate tile dimensions, used
                              to find interior white holes

    Returns:
        result (numpy.ndarray): Image with white background turned to black
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to get white-ish areas
    _, white_mask = cv2.threshold(gray, tol, 255, cv2.THRESH_BINARY)

    # Copy mask for flood fill
    flood_mask = white_mask.copy()
    h, w = flood_mask.shape

    # Create mask for floodFill (needs 2 pixels larger)
    floodfill_mask = np.zeros((h + 2, w + 2), np.uint8)

    # Flood fill from all corners (background assumed connected to corners)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for corner in corners:
        cv2.floodFill(flood_mask, floodfill_mask, corner, 0)

    # === NEW SECTION: detect large internal white patches ===
    if tile_w is not None and tile_h is not None:
        sub_w = tile_w // 2
        sub_h = tile_h // 2

        # Loop over quarter-tiles
        for y in range(0, h, sub_h):
            for x in range(0, w, sub_w):
                x2 = min(x + sub_w, w)
                y2 = min(y + sub_h, h)
                region = flood_mask[y:y2, x:x2]

                # If the region is mostly white, flood fill it black
                white_ratio = np.mean(region == 255)
                if white_ratio > 0.95:  # almost entirely white
                    cv2.floodFill(flood_mask, floodfill_mask, (x + sub_w // 2, y + sub_h // 2), 0)

    # Replace background pixels in original image with black
    result = img.copy()
    result[flood_mask == 0] = [0, 0, 0]

    return result
