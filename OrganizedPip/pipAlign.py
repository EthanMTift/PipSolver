import cv2
import json
from pipClickQuice import get_four_clicks
from pipClickTwice import get_two_clicks
from pipDrawGrid import draw_grid_overlay
from pipSaveGrid import save_grid_json
from pipSaveDominoArea import save_domino_area_json
from pipDetectDominos import detect_dominos



def align(img, ROWS, COLS, OUT_PATH, DOMINO_JSON_PATH, json_path, img_path):

    # --- Step 1: User selects grid ---
    while True:
        clicks = get_four_clicks(img, instr="Click LEFT, RIGHT, TOP, BOTTOM edges of the board")
        if len(clicks) < 4:
            print("Selection cancelled. Exiting.")
            return

        left_x, right_x, top_y, bottom_y = clicks
        min_x = min(left_x[0], right_x[0])
        max_x = max(left_x[0], right_x[0])
        min_y = min(top_y[1], bottom_y[1])
        max_y = max(top_y[1], bottom_y[1])

        tile_w = (max_x - min_x) / COLS
        tile_h = (max_y - min_y) / ROWS
        anchor_x, anchor_y = min_x, min_y

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
                break
            elif key in (ord('q'), ord('Q'), 27):
                print("Quitting without saving.")
                cv2.destroyAllWindows()
                return

        # Exit outer loop if confirmed
        if key in (ord('c'), ord('C')):
            break

    # --- Step 2: User selects domino area ---
    print("Now select the domino area")
    domino_clicks = get_two_clicks(img, instr="Click TOP-LEFT, BOTTOM-RIGHT of domino area")
    if len(domino_clicks) < 2:
        print("Domino selection cancelled. Exiting.")
        return
    top_left = domino_clicks[0]
    bottom_right = domino_clicks[1]
    save_domino_area_json(top_left, bottom_right, DOMINO_JSON_PATH)

    # --- Step 3: Detect dominos ---
    with open(DOMINO_JSON_PATH) as f:
        domino_area = json.load(f)
    dominos = detect_dominos(img, domino_area, tile_w, tile_h)
    print(f"Detected {len(dominos)} domino(s):", dominos)
    return dominos