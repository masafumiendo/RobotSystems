"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for controller (3.3)
"""

import time

class Controller:

    # initialization
    def __init__(self, sensor, interpretor):
        self.sensor = sensor
        self.interpretor = interpretor

        # PID gain
        self.kp = 10
        self.ki = 0
        self.kd = 5

        # I controller
        self.integral = 0

        self.t_prev = 0
        self.e_prev = None

        # limit of steering angle
        self.steer_angle_th = 20

    def controller(self, type_c):

        # current values
        vals = self.sensor.sensor_reading()
        e_curr = self.interpretor.calc_relative_pos(vals)
        t_curr = time.time()

        if self.e_prev != None:
            dt = t_curr - self.t_prev
            # integration
            self.integral += (e_curr + self.e_prev) / 2. * dt
            # differentiation
            diff = (e_curr - self.e_prev) / dt

            p = self.kp * e_curr
            i = self.ki * self.integral
            d = self.kd * diff

            # PID or PD controller
            if type_c == "pid":
                res = p + i + d
            elif type_c == "pd":
                res = p + d
        else:
            # P controller for the initial loop
            p = self.kp * e_curr
            res = p

        # limit steering angle
        if res >= self.steer_angle_th:
            res = self.steer_angle_th
        if res <= - self.steer_angle_th:
            res = - self.steer_angle_th

        # update variables
        self.t_prev = t_curr
        self.e_prev = e_curr

        return res