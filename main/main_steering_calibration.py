"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: main function to calibrate steering angle
"""

import sys
sys.path.append('..')

from picarx_improved import *

if __name__ == '__main__':

    is_calibrated = False
    while is_calibrated == False:
        print('please enter the value for steering calibration!')
        angle = input('input angle: ')

        # calibrate servo based on input value
        angle = int(angle)
        dir_servo_angle_calibration(angle)

        print('please enter y or n to see calibration angle is ok!')
        ans = input('input your answer: ')

        if ans == "y":
            break
        elif ans == "n":
            continue
