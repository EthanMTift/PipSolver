import cv2
from pipClicksShared import clicks
from pipClickEvent import click_event

def get_two_clicks(img, instr="Click TOP-LEFT and BOTTOM-RIGHT"):
    """
    Let the user click two points on the image.
    Returns a list of two (x, y) tuples.
    Window closes automatically after 2 clicks.
    """
    # clear shared list instead of redefining it locally
    clicks.clear()

    window_name = "Select Two Points"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, click_event)

    while True:
        display = img.copy()
        for (x, y) in clicks:
            cv2.circle(display, (x, y), 6, (0, 255, 0), -1)
        cv2.putText(display, instr, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow(window_name, display)

        if len(clicks) >= 2:
            break  # Exit loop after two clicks

        key = cv2.waitKey(50) & 0xFF
        if key == 27:  # ESC cancels
            clicks.clear()
            break

    cv2.destroyWindow(window_name)
    return clicks.copy()
