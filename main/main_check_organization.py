"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: main function to check PicarX class
"""

import sys
sys.path.append('..')

from picarx_organized import *

if __name__ == '__main__':
    car = PicarX
    while True:
        speed = input('input speed: ')
        steer_angle = input('input steer angle: ')
        time2drive = input('input time to drive: ')

        speed = float(speed)
        steer_angle = float(steer_angle)
        time2drive = float(time2drive)
        # drive the car
        car.basic_maneuvering(speed, steer_angle, time2drive)

        res = input('continue to drive? (y/n) : ')

        if res == 'y':
            continue
        else:
            break