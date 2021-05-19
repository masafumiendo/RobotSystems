import cv2
import numpy as np
import sys
sys.path.append('/home/pi/ArmPi/')
import LABConfig as lbc
import CameraCalibration.CalibrationConfig as cconf
import math
from ArmIK.Transform import *


# Find the contour with the largest area
# The parameter is a list of contours to be compared
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # Traverse all contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate the contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # Only accept contours with area larger than 300
                area_max_contour = c

    return area_max_contour, contour_area_max  # Return the largest contour

class ColorPerception():
    # constructor
    # @param
    def __init__(self, target_colors, min_box_area=2500, color_range=lbc.color_range, \
                 size=(640, 480), square_length=cconf.square_length):
        self.min_box_area = min_box_area
        self.color_range = color_range

        self.size = size
        self.square_length = square_length

        self.target_colors = target_colors

        self.color_list = []
        self.start_count_t1 = True
        self.count = 0

        self.last_x = 0
        self.last_y = 0

    # Perform bit operations on the original image and mask
    def thresh_image(self, image, low_color, high_color):
        return cv2.inRange(image, low_color, high_color)

    def fill_image(self, image):
        opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # Closed operation
        return closed

    def get_contours(self, image):
        return cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the outline

    def get_larget_contour(self, contours):
        return getAreaMaxContour(contours)  # Find the largest contour

    def fit_box(self, contour):
        rect = cv2.minAreaRect(contour)
        box = np.int0(cv2.boxPoints(rect))

        roi = getROI(box) #Get roi area
        return rect, roi, box

    def get_center_box(self, rect, roi):
        img_centerx, img_centery = getCenter(rect, roi, self.size, self.square_length)  # Get the center coordinates of the block
        return img_centerx, img_centery

    def convert_world_frame(self, x, y):
        world_x, world_y = convertCoordinate(x, y, self.size) #Convert to real world coordinates
        return world_x, world_y

    def preprocess(self, img):
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        #if not __isRunning:
        #    return img



        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #If an area is detected with a recognized object, it will continue to detect the area until there is none
        #if get_roi and start_pick_up:
        #    get_roi = False
        #    frame_gb = getMaskROI(frame_gb, roi, size)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        return frame_lab

    def perception(self, img, start_pick_up):
        img_copy = img.copy()
        frame_lab = self.preprocess(img_copy)


        max_area = 0
        areaMaxContour = 0
        color_area_max = None

        if not start_pick_up:
            for i in self.color_range:
                if i in self.target_colors:
                    detect_color = i
                    frame_mask = self.thresh_image( frame_lab, \
                                                    self.color_range[detect_color][0], \
                                                    self.color_range[detect_color][1])
                    closed = self.fill_image(frame_mask)
                    contours = self.get_contours(closed)
                    areaMaxContour, area_max = self.get_larget_contour(contours)

                    if areaMaxContour is not None:
                        if area_max > max_area:  # Find the largest area of all of the colors
                            max_area = area_max
                            color_area_max = i
                            areaMaxContour_max = areaMaxContour


            if max_area > self.min_box_area:  # Have found the largest area
                rect, roi, box = self.fit_box(areaMaxContour)

                get_roi = True

                img_centerx, img_centery = self.get_center_box(rect, roi)
                world_x, world_y = self.convert_world_frame(img_centerx, img_centery)


                cv2.drawContours(img, [box], -1, self.range_rgb[detect_color], 2)
                cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1) #Draw center point
                self.distance = math.sqrt(pow(world_x - self.last_x, 2) + pow(world_y - self.last_y, 2)) #Compare the last coordinate to determine whether to move
                last_x, last_y = world_x, world_y

                if color_area_max == 'red':  # red largest
                    color = 1
                elif color_area_max == 'green':  # green largest
                    color = 2
                elif color_area_max == 'blue':  # blue largest
                    color = 3
                else:
                    color = 0
                self.color_list.append(color)
                # cumulative judgement
                if distance < 0.5:
                    count += 1
                    center_list.extend((world_x, world_y))
                    if self.start_count_t1:
                        self.start_count_t1 = False
                        t1 = time.time()
                    if time.time() - t1 > 1:
                        rotation_angle = rect[2]
                        self.start_count_t1 = True
                        world_X, world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                        center_list = []
                        count = 0
                        start_pick_up = True
                else:
                    t1 = time.time()
                    self.start_count_t1 = True
                    center_list = []
                    count = 0

                if len(color_list) == 3:  # Multiple judgements
                    # take the average
                    color = int(round(np.mean(np.array(color_list))))
                    self.color_list = []
                    if color == 1:
                        detect_color = 'red'
                        draw_color = self.range_rgb["red"]
                    elif color == 2:
                        detect_color = 'green'
                        draw_color = self.range_rgb["green"]
                    elif color == 3:
                        detect_color = 'blue'
                        draw_color = self.range_rgb["blue"]
                    else:
                        detect_color = 'None'
                        draw_color = self.range_rgb["black"]
            else:
                if not start_pick_up:
                    draw_color = (0, 0, 0)
                    detect_color = "None"

                # end if for max area
        cv2.putText(img, "Color: " + detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2)
        return img

if __name__ == '__main__':
    import sys
    sys.path.append('/home/pi/ArmPi/')
    from CameraCalibration.CalibrationConfig import *
    import Camera
    import time
    import threading


    target_color = ('red', 'green', 'blue')
    my_camera = Camera.Camera()
    my_camera.camera_open()

    perception = ColorPerception(target_color)

    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = perception.perception(frame, start_pick_up=False)
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()