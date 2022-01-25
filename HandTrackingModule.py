import cv2
import mediapipe as mp
import time


class HandTrackingModule:

    def __init__(self,
                 static_image_mode=False,
                 max_num_hands=1,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode,
                                              max_num_hands,
                                              min_detection_confidence,
                                              min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    def detect_hand(self, img, draw=False):
        rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape


        result = self.hands.process(rgbImage)
        landmarks = []

        if result.multi_hand_landmarks:
            for coordinates in result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, coordinates, self.mpHands.HAND_CONNECTIONS)
                for id, lm in enumerate(coordinates.landmark):
                    landmarks.append((int(w*lm.x), int(h*lm.y)))
        return landmarks

