"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: main function to sense line and follow it by PID controller
"""

import sys
sys.path.append('..')

import time

from picarx_organized import PicarX
from photosensing import PhotoSensor, PhotoInterpretor
from controller import Controller
from integration import Integrator

if __name__ == '__main__':
    # call objects
    car = PicarX()
    sensor = PhotoSensor()
    interpretor = PhotoInterpretor()
    controller = Controller()
    integrator = Integrator(car, sensor, interpretor, controller, speed=30)

    integrator.line_trace()
