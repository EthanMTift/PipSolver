import cv2
from pipClickEvent import click_event
from pipClicksShared import clicks
def get_four_clicks(img, instr="Click LEFT, RIGHT, TOP, BOTTOM edges"):
    
    clicks.clear()

    window_name = instr
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, click_event)

    while len(clicks) < 4:
        display = img.copy()
        for (x, y) in clicks:
            cv2.circle(display, (x, y), 6, (0, 255, 0), -1)
        cv2.imshow(window_name, display)
        key = cv2.waitKey(50) & 0xFF
        if key == 27:  # ESC cancels
            break

    cv2.destroyWindow(window_name)
    return clicks.copy()