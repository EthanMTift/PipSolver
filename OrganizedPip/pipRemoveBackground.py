import cv2
import numpy as np

def remove_white_background(img, tol=240):
    """
    Turn the white-ish background of an image to black,
    without affecting isolated white symbols.

    Parameters:
        img (numpy.ndarray): Input image (BGR, already loaded with cv2.imread)
        tol (int): Tolerance for considering a pixel as white (default 240)

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
    floodfill_mask = np.zeros((h+2, w+2), np.uint8)

    # Flood fill from all corners (background assumed connected to corners)
    corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
    for corner in corners:
        cv2.floodFill(flood_mask, floodfill_mask, corner, 0)

    # Replace background pixels in original image with black
    result = img.copy()
    result[flood_mask == 0] = [0, 0, 0]

    return result