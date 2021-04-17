"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for integration (3.4)
"""

from sensing import Sensor
from interpretation import Interpretor
from controller import Controller

class Integrator:

    # initialization
    def __init__(self, sensor, controller, speed, type_c):
        self.sensor = sensor
        self.controller = controller

        self.speed = speed
        self.type_c = type_c

    def feedback_controller(self):
        steer_angle = self.controller.controller(self.type_c)
        print(steer_angle)
        self.sensor.car.forward(self.speed, steer_angle)

    def line_trace(self):
        # trace line while controlling steering angle
        while True:
            self.feedback_controller()

if __name__ == '__main__':
    sensor = Sensor()
    interpretor = Interpretor()
    controller = Controller(sensor, interpretor)
    integrator = Integrator(sensor, controller, speed=20, type_c="pd")
    integrator.line_trace()