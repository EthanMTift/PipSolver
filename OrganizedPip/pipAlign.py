import cv2
import numpy as np
import json
from pipClickTwice import get_two_clicks
from pipDrawGrid import draw_grid_overlay
from pipSaveGrid import save_grid_json
from pipSaveDominoArea import save_domino_area_json
from pipDetectDominos import detect_dominos
from pipShrinkRect import refine_and_inset_rectangle





def align(img, ROWS, COLS, OUT_PATH, DOMINO_JSON_PATH, json_path, img_path):
    # --- Step 1: User selects approximate board area ---
    
    clicks = get_two_clicks(img, instr="Click TOP-LEFT and BOTTOM-RIGHT of board")

    if len(clicks) < 2:
        print("Selection cancelled.")
        return

    top_left = clicks[0]
    bottom_right = clicks[1]

    top_left, bottom_right = refine_and_inset_rectangle(img, top_left, bottom_right, ROWS, COLS)
    

    # Visualize detected region
    vis = img.copy()
    cv2.rectangle(vis, (top_left[0], top_left[1]), (bottom_right[0], bottom_right[1]), (0, 255, 0), 2)
    cv2.imshow("Detected Board Area", vis)
    cv2.waitKey(1000)
    cv2.destroyWindow("Detected Board Area")

    # --- Step 2: Compute grid geometry ---
    tile_w = (bottom_right[0] - top_left[0]) / COLS
    tile_h = (bottom_right[1] - top_left[1]) / ROWS
    anchor_x, anchor_y = top_left[0], top_left[1]

    # --- Step 3: Confirm and save grid overlay ---
    while True:
        overlay = draw_grid_overlay(img, anchor_x, anchor_y, tile_w, tile_h, ROWS, COLS)
        cv2.imshow("Grid Overlay", overlay)

        key = cv2.waitKey(0)
        if key in (ord('c'), ord('C')):
            cv2.imwrite(OUT_PATH, overlay)
            print("Saved grid overlay to", OUT_PATH)
            save_grid_json(img, anchor_x, anchor_y, tile_w, tile_h, img_path, json_path, ROWS, COLS)
            cv2.destroyAllWindows()
            break
        elif key in (ord('r'), ord('R')):
            cv2.destroyWindow("Grid Overlay")
            print("Redoing selection...")
            return align(img, ROWS, COLS, OUT_PATH, DOMINO_JSON_PATH, json_path, img_path)
        elif key in (ord('q'), ord('Q'), 27):
            print("Quitting without saving.")
            cv2.destroyAllWindows()
            return

    # --- Step 4: Domino area selection ---
    print("Now select the domino area")
    domino_clicks = get_two_clicks(img, instr="Click TOP-LEFT and BOTTOM-RIGHT of domino area")
    if len(domino_clicks) < 2:
        print("Domino selection cancelled.")
        return

    top_left = domino_clicks[0]
    bottom_right = domino_clicks[1]
    save_domino_area_json(top_left, bottom_right, DOMINO_JSON_PATH)

    # --- Step 5: Detect dominos ---
    with open(DOMINO_JSON_PATH) as f:
        domino_area = json.load(f)
    dominos = detect_dominos(img, domino_area, tile_w, tile_h)
    print(f"Detected {len(dominos)} domino(s):", dominos)
    return dominos




