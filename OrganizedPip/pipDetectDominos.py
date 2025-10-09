import cv2
import numpy as np

def detect_dominos(img, domino_area, tile_w, tile_h, debug_out="domino_debug.png"):
    # Parse domino area
    if isinstance(domino_area, dict):
        top_left = tuple(map(int, domino_area["top_left"]))
        bottom_right = tuple(map(int, domino_area["bottom_right"]))
    else:
        top_left, bottom_right = domino_area
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))

    crop = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]].copy()

    # Convert to grayscale and blur
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Canny edges
    edges = cv2.Canny(blur, 50, 150)

    # Dilate edges slightly to close tiny gaps
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # Debug: save edges to inspect
    cv2.imwrite("debug_edges.png", edges)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dominos = []

    # --- SCALE-BASED THRESHOLD ---
    # A domino covers roughly 2 tiles
    min_area = tile_w * tile_h  # adjust factor if needed
    aspect_ratio_min = 1.5
    aspect_ratio_max = 2.5

    for cnt in contours:
        epsilon = 0.03 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)

            # Use scaled area instead of hardcoded 1000
            if aspect_ratio_min < aspect_ratio < aspect_ratio_max and w * h > min_area / 2:
                domino_crop = crop[y:y + h, x:x + w]
                left_half = domino_crop[:, :w // 2]
                right_half = domino_crop[:, w // 2:]

                # --- PIP COUNTING (unchanged) ---
                def count_pips(half):
                    gray_half = cv2.cvtColor(half, cv2.COLOR_BGR2GRAY)
                    _, thresh_half = cv2.threshold(gray_half, 200, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    return len([c for c in contours if cv2.contourArea(c) > 30])

                left_pips = count_pips(left_half)
                right_pips = count_pips(right_half)

                # Store domino info
                dominos.append({
                    "x": x + top_left[0],
                    "y": y + top_left[1],
                    "w": w,
                    "h": h,
                    "left_pips": left_pips - 1,
                    "right_pips": right_pips - 1
                })

                # Draw debug rectangles and pip counts
                cv2.rectangle(crop, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(crop, f"{left_pips}|{right_pips}", 
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            0.6, (0, 0, 255), 2, cv2.LINE_AA)

    # Save debug image
    cv2.imwrite(debug_out, crop)
    print(f"Debug domino image saved to {debug_out}")
    print(f"Detected {len(dominos)} domino(s)")

    return dominos