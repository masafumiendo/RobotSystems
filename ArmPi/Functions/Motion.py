
#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
from ArmIK.Transform import getAngle
from ArmIK.ArmMoveIK import ArmIK
import HiwonderSDK.Board as Board

from Perception import Perception

class Motion:

    def __init__(self):

        self.AK = ArmIK()
        self.servo1 = 500
        self.base_z = 1.5
        self.block_height = 2.5
        self.num_stacked = 0

        self.coordinates = {
            'red':    (-15 + 0.5, 12 - 0.5, 1.5),
            'green':  (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':   (-15 + 0.5, 0 - 0.5,  1.5),
            'pallet': (-15 + 1, -7 - 0.5, 1.5),
        }

    def stacking(self, world_x, world_y, rotation_angle, color):

        if color == 'red':
            print('first floor detected!')
            # register 1st floor's information
            self.color_prev = color
            self.target_x = world_x
            self.target_y = world_y
            self.target_z = self.base_z
            self.target_angle = rotation_angle
            self.num_stacked += 1
            self.num_stacked %= 3
            return
        else:
            print('try stacking!')
            self.target_z += self.block_height * self.num_stacked
            self.__pick(world_x, world_y, self.base_z, rotation_angle)
            self.__place(self.target_x, self.target_y, self.target_z)
            self.__initMove()

    def sort(self, block_x, block_y, block_rotation, block_color):

        if not block_color in ['red', 'green', 'blue']:
            raise Exception("Bad color :(")

        place_x, place_y, place_z = self.coordinates[block_color]

        if not self.__check_reachable(block_x, block_y):
            return False

        self.__pick(block_x, block_y, self.base_z, block_rotation)

        self.__place(place_x, place_y, place_z)

        self.__initMove()

    def palletize(self, block_x, block_y, block_rotation):

        place_x, place_y, place_z = self.coordinates["pallet"]

        place_z += self.block_height * self.num_stacked

        if not self.__check_reachable(block_x, block_y):
            return False

        self.__pick(block_x, block_y, self.base_z, block_rotation)

        self.__place(place_x, place_y, place_z)

        self.__initMove()
        self.num_stacked += 1
        self.num_stacked %= 3

    def __pick(self, x, y, z, rotation):

        servo2_angle = getAngle(x, y, rotation)
        Board.setBusServoPulse(1, self.servo1 - 280, 500)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        if not self.__check_reachable(x, y, z):
            print("could not pick the target!")
            return

        Board.setBusServoPulse(1, self.servo1, 500)
        time.sleep(0.8)

        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((x, y, 12), -90, -90, 0, 1000)
        time.sleep(1)

    def __place(self, x, y, z, rotation=-90):

        if not self.__check_reachable(x, y, z + 6):
            print("could not reach the position!")
            return

        servo2_angle = getAngle(x, y, rotation)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.5)

        self.AK.setPitchRangeMoving((x, y, z + 3), -90, -90, 0, 500)
        time.sleep(0.5)

        self.AK.setPitchRangeMoving((x, y, z), -90, -90, 0, 1000)
        time.sleep(0.8)

        Board.setBusServoPulse(1, self.servo1 - 200, 500)
        time.sleep(0.8)

        self.AK.setPitchRangeMoving((x, y, 12), -90, -90, 0, 800)
        time.sleep(0.8)

    def __check_reachable(self, x, y, z=7):
        result = self.AK.setPitchRangeMoving((x, y, z), -90, -90, 0)
        if result == False:
            reachable = False
        else:
            time.sleep(result[2]/1000)
            reachable = True

        return reachable

    def __initMove(self):
        Board.setBusServoPulse(1, self.servo1 - 250, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.5)

if __name__ == "__main__":

    my_camera = Camera.Camera()
    my_camera.camera_open()

    target_color = ("red", "blue", "green")
    perception = Perception()

    motion = Motion()
    cnt_img = 0
    floor = 0
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            frame_checked_ = img.copy()
            world_x, world_y, rotation_angle, color = perception.perception(frame, target_color[floor], start_pick_up=False)
            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1)
            if key == 27:
                break
            if world_x is not None and cnt_img >= 1:
                motion.stacking(world_x, world_y, rotation_angle, color)
                floor += 1

            cnt_img += 1

    my_camera.camera_close()
    cv2.destroyAllWindows()