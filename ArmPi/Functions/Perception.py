# Author: Masafumi Endo
# Objective: Perceive color blocks

#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import color_range
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
from ArmIK.Transform import getMaskROI, getROI, getCenter, convertCoordinate
from CameraCalibration.CalibrationConfig import square_length
import numpy as np
import math

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

class Perception:

    def __init__(self):

        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255)
        }

        self.size = (640, 480)
        self.roi = None
        self.get_roi = False
        self.detected_color = None

    def perception(self, img, target_color, start_pick_up):

        img_copy = img.copy()
        frame_lab = self.__image_converter(img_copy)

        max_area_max = 0
        areaMaxContour_max = 0
        self.detected_color = "None"
        draw_color = "black"
        world_x, world_y, rotation = None, None, None
        if not start_pick_up:
            for color in color_range:
                if color in target_color:
                    areaMaxContour, area_max = self.__get_max_area_contour(frame_lab, color)

                    if areaMaxContour is not None:
                        if area_max > max_area_max:
                            areaMaxContour_max = areaMaxContour
                            max_area_max = area_max
                            self.detected_color = color
                            draw_color = color
            if max_area_max > 2500:
                world_x, world_y, rotation = self.__coordinates_converter(areaMaxContour_max, display_img=img)
            else:
                self.detected_color = "None"
        print(max_area_max)
        cv2.putText(img, "Color: " + self.detected_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.range_rgb[draw_color], 2)

        return world_x, world_y, rotation, self.detected_color

    def __image_converter(self, img):

        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert images to LAB space

        return frame_lab

    def __get_max_area_contour(self, frame_lab, color):

        frame_mask = cv2.inRange(frame_lab, color_range[color][0], color_range[color][1])  # Bitwise operations on the original image and mask
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open Arithmetic
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operations
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] # Find the outline
        areaMaxContour, area_max = self.__getAreaMaxContour(contours)  # Find the maximum profile

        return areaMaxContour, area_max

    def __getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:
                    area_max_contour = c

        return area_max_contour, contour_area_max

    def __coordinates_converter(self, contour, display_img=None):

        rect = cv2.minAreaRect(contour)
        rotation_angle = rect[2]
        box = np.int0(cv2.boxPoints(rect))

        self.roi = getROI(box) #Get roi area
        self.get_roi = True

        img_centerx, img_centery = getCenter(rect, self.roi, self.size, square_length)  # Get the coordinates of the center of the block
        world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # Convert to real world coordinates

        if display_img is not None:
            cv2.drawContours(display_img, [box], -1, self.range_rgb[self.detected_color], 2)

            cv2.putText(display_img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[self.detected_color], 1)

        return world_x, world_y, rotation_angle

if __name__ == "__main__":

    target_color = ("red")
    my_camera = Camera.Camera()
    my_camera.camera_open()

    perception = Perception()

    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            world_x, world_y, rotation_angle, color = perception.perception(frame, target_color, start_pick_up=False)
            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
