"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for integration (3.4)
"""

from picarx_organized import PicarX

class Integrator:

    # initialization
    def __init__(self, sensor, controller, speed=30, type_c="pd"):
        self.sensor = sensor
        self.controller = controller

        self.car = PicarX()

        self.speed = speed
        self.type_c = type_c

    def feedback_controller(self):
        steer_angle = self.controller.controller(self.type_c)
        self.car.forward(self.speed, steer_angle)

    def line_trace(self):
        # trace line while controlling steering angle
        while True:
            self.feedback_controller()