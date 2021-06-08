
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

        self.coordinates = {
            'red':    (-15 + 0.5, 12 - 0.5, 1.5),
            'green':  (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':   (-15 + 0.5, 0 - 0.5,  1.5),
            'pallet': (-15 + 1, -7 - 0.5, 1.5),
        }

        self.target_x = 0
        self.target_y = 0
        self.target_z = 0
        self.num_stacked = 0

    def pick_and_place(self, world_x, world_y, rotation_angle):

        self.target_z = self.base_z
        self.target_z += self.block_height * self.num_stacked
        # execute pick and place
        self.__pick(world_x, world_y, self.base_z, rotation_angle)
        self.__place(self.target_x, self.target_y, self.target_z)

        self.__initMove()

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

def main():

    my_camera = Camera.Camera()
    my_camera.camera_open()

    target_color = ("red", "blue", "green")

    perception = Perception()
    motion = Motion()

    cnt_img = 0
    start_stacking = True
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            world_x, world_y, rotation_angle, color = perception.perception(frame, target_color[motion.num_stacked], start_pick_up=False)
            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1)
            if key == 27:
                break

            # start motion procedure
            if cnt_img >= 1:
                # register 1st floor's information
                print(motion.num_stacked)
                if motion.num_stacked == 0:
                    motion.target_x = world_x
                    motion.target_y = world_y
                    motion.num_stacked += 1
                # stack blue and green blocks
                else:
                    if start_stacking:
                        # pick and place
                        print('start pick and place!')
                        motion.pick_and_place(world_x, world_y, rotation_angle)
                        start_stacking = False
                    else:
                        # check the process is accomplished or not
                        frame_ = img.copy()
                        _, _, _, color_ = perception.perception(frame_, target_color[motion.num_stacked-1], start_pick_up=False)
                        print('check the process is accomplished!')
                        print(target_color[motion.num_stacked-1])
                        print(color_)
                        if color_ == "None":
                            print('success!')
                            motion.num_stacked += 1
                        elif color_ == target_color[motion.num_stacked-1]:
                            print('failed!')
                            motion.num_stacked -= 1

                        start_stacking = True

            cnt_img += 1

            if motion.num_stacked == 3:
                break

    my_camera.camera_close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()