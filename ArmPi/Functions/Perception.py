#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

import LABConfig as labconf
import CameraCalibration.CalibrationConfig as cameraconf

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

class Perception:

    def __init__(self, target_color):
        self.__target_color = target_color
        self.color_range = labconf.color_range
        self.range_rgb = {
            'red':   (0, 0, 255),
            'blue':  (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }

        self.size = (640, 480)
        self.square_length = cameraconf.square_length

        self.last_x = 0
        self.last_y = 0

        self.center_list = []
        self.color_list = []
        self.count = 0

        self.detect_color = 'None'

    def perception(self, img, start_pick_up):
        """
        function to perceive objects (same role as run() function of original codes)
        :return: image w/ identified color of block's information
        """

        img_copy = img.copy()
        frame_lab = self.__image_converter(img_copy)

        color_area_max = None
        max_area = 0
        areaMaxContour_max = 0

        if not start_pick_up:
            for i in self.color_range:
                if i in self.__target_color:
                    frame_mask = cv2.inRange(frame_lab, self.color_range[i][0], self.color_range[i][1])  #对原图像和掩模进行位运算
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #开运算
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) #闭运算
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #找出轮廓
                    areaMaxContour, area_max = self.__get_max_area_contour(contours)  #找出最大轮廓
                    if areaMaxContour is not None:
                        if area_max > max_area:#找最大面积
                            max_area = area_max
                            color_area_max = i
                            areaMaxContour_max = areaMaxContour

            if max_area > 2500:  # 有找到最大面积
                rect = cv2.minAreaRect(areaMaxContour_max)
                box = np.int0(cv2.boxPoints(rect))

                roi = getROI(box) #获取roi区域
                get_roi = True
                img_centerx, img_centery = getCenter(rect, roi, self.size, self.square_length)  # 获取木块中心坐标

                world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) #转换为现实世界坐标

                cv2.drawContours(img, [box], -1, self.range_rgb[color_area_max], 2)
                cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[color_area_max], 1) #绘制中心点

                distance = math.sqrt(pow(world_x - self.last_x, 2) + pow(world_y - self.last_y, 2)) #对比上次坐标来判断是否移动
                last_x, last_y = world_x, world_y
                if not start_pick_up:
                    if color_area_max == 'red':  #红色最大
                        color = 1
                    elif color_area_max == 'green':  #绿色最大
                        color = 2
                    elif color_area_max == 'blue':  #蓝色最大
                        color = 3
                    else:
                        color = 0
                    self.color_list.append(color)
                    # 累计判断
                    if distance < 0.5:
                        self.count += 1
                        self.center_list.extend((world_x, world_y))
                        if self.start_count_t1:
                            self.start_count_t1 = False
                            t1 = time.time()
                        if time.time() - t1 > 1:
                            rotation_angle = rect[2]
                            self.start_count_t1 = True
                            world_X, world_Y = np.mean(np.array(self.center_list).reshape(self.count, 2), axis=0)
                            self.center_list = []
                            self.count = 0
                            start_pick_up = True
                    else:
                        t1 = time.time()
                        self.start_count_t1 = True
                        self.center_list = []
                        self.count = 0

                    if len(self.color_list) == 3:  #多次判断
                        # 取平均值
                        color = int(round(np.mean(np.array(self.color_list))))
                        self.color_list = []
                        if color == 1:
                            self.detect_color = 'red'
                            draw_color = self.range_rgb["red"]
                        elif color == 2:
                            self.detect_color = 'green'
                            draw_color = self.range_rgb["green"]
                        elif color == 3:
                            self.detect_color = 'blue'
                            draw_color = self.range_rgb["blue"]
                        else:
                            self.detect_color = 'None'
                            draw_color = self.range_rgb["black"]
            else:
                if not start_pick_up:
                    draw_color = (0, 0, 0)
                    self.detect_color = "None"

        cv2.putText(img, "Color: " + self.detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.range_rgb[self.detect_color], 2)
        return img

    def __image_converter(self, img):

        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        frame_resize = cv2.resize(img, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert images to LAB space

        return frame_lab

    def __get_max_area_contour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # Go through all contours
            contour_area_temp = math.fabs(cv2.contourArea(c)) # Calculate the contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # The contour of the maximum area is valid only when the area is greater than 300 to filter the interference
                    area_max_contour = c

        return area_max_contour, contour_area_max  # Returns the largest profile

if __name__ == '__main__':

    __target_color = ('red')
    my_camera = Camera.Camera()
    my_camera.camera_open()

    perception = Perception(__target_color)

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