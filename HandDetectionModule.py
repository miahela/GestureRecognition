import solution.HandTrackingModule as trackingModule
import solution.GestureRecognitionModule2 as gestureRecognition
from solution.FingerCounterModule import get_fingers
import cv2

tracker = trackingModule.HandTrackingModule()
recognize = gestureRecognition.GestureRecognitionModule()


def get_sign(img, draw=False):

    landmarks = tracker.detect_hand(img, draw)

    h, w, c = img.shape

    fingers = get_fingers(landmarks)

    if draw is True:
        cv2.putText(img, fingers, (w - 200, 30), cv2.FONT_ITALIC, 1, (0, 0, 255), 1)

    if len(landmarks) != 0:
        pointer = landmarks[8][0]
    else:
        pointer = 0

    sign = recognize.get_gesture(fingers, pointer)

    return sign
