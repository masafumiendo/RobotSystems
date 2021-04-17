"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: main function to check PicarX class
"""

import sys
sys.path.append('..')

### begin 2.5.3
try:
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print("This computer does not appear to be a PiCar-X system(/opt/ezblock is not present). Shadowing hardware calls with substitute functions")
    from sim_ezblock import *
### end 2.5.3

from picarx_organized import PicarX
from sensing import Sensor

if __name__ == '__main__':
    car = PicarX()
    sensor = Sensor(car=car)
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