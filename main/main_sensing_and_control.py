"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: main function to sense line and follow it by PID controller
"""

import sys
sys.path.append('..')

import time

from picarx_organized import PicarX
from sensing import Sensor
from interpretation import Interpretor
from controller import Controller
from integration import Integrator

if __name__ == '__main__':
    # call objects
    car = PicarX()
    sensor = Sensor()
    interpretor = Interpretor()
    controller = Controller()
    integrator = Integrator(car, sensor, interpretor, controller, speed=30, type_c="pd")

    integrator.line_trace()
