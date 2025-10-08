import cv2

def draw_grid_overlay(img, anchor_x, anchor_y, tile_w, tile_h, ROWS, COLS):
    overlay = img.copy()
    h, w = overlay.shape[:2]

    for r in range(ROWS):
        for c in range(COLS):
            x0 = int(anchor_x + c * tile_w)
            y0 = int(anchor_y + r * tile_h)
            x1 = int(anchor_x + (c+1) * tile_w)
            y1 = int(anchor_y + (r+1) * tile_h)
            cv2.rectangle(overlay, (x0, y0), (x1, y1), (128, 0, 255), 2)
            cv2.putText(overlay, f"{r},{c}", (x0 + 5, y0 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(overlay, f"{r},{c}", (x0 + 5, y0 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    instr = "C=confirm  R=redo  Q=quit  Arrows=move grid"
    cv2.rectangle(overlay, (5, h - 35), (520, h - 5), (0, 0, 0), -1)
    cv2.putText(overlay, instr, (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    return overlay