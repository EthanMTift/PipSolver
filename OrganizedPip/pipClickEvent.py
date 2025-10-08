import cv2
from pipClicksShared import clicks

def click_event(event, x, y, flags, param):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append((x, y))
        print("Clicked:", (x, y))