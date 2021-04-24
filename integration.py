"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for integration (3.4)
"""

import time

class Integrator:

    # initialization
    def __init__(self, car, sensor, interpretor, controller, speed=30, type_c="pd"):
        self.sensor = sensor
        self.interpretor = interpretor
        self.controller = controller

        self.car = car

        self.speed = speed
        self.type_c = type_c

    def feedback_controller(self):
        vals = self.sensor.sensor_reading()
        e_curr = self.interpretor.calc_relative_pos(vals)
        steer_angle = self.controller.controller(e_curr, self.type_c)
        self.car.forward(self.speed, steer_angle)

    def line_trace(self):
        # trace line while controlling steering angle
        while True:
            self.feedback_controller()
            time.sleep(0.01)