"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: classes for camera sensing and interpretation (3.5)
"""

import numpy as np
import cv2

class CameraSensor:

    # initialization
    def __init__(self, camera):
        self.camera = camera
        self.resolution = (640, 480)

    def sensor_reading(self, image):
        return image

class CameraInterpretor:

    # initialization
    def __init__(self):
        self.lower_blue = np.array([])
        self.upper_blue = np.array([])

    def calc_relative_pos(self, image):

        # create binary image from raw frame
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        ret, th = cv2.threshold(mask, 0, 255, cv2.THRESH_OTSU)

        # identify moment of line
        mu = cv2.moments(th)
        x, _ = int(mu["m10"]/mu["m00"]) , int(mu["m01"]/mu["m00"])

        # based on the identified relative position, calculate relative position
        pos = (320 - x) / 320

        return pos