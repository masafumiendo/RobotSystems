"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: main function to sense line and follow it by PID controller
"""

import sys
sys.path.append('..')

from picarx_organized import PicarX
from sensing import Sensor
from interpretation import Interpretor
from controller import Controller

if __name__ == '__main__':
    car = PicarX()
    sensor = Sensor(car)