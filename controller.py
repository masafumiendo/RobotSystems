"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for controller (3.3)
"""

import time

class Controller:

    # initialization
    def __init__(self, type_c="pd"):

        self.type_c = type_c

        # PID gain
        self.kp = 10
        self.ki = 1
        self.kd = 2

        # I controller
        self.integral = 0

        self.t_prev = 0
        self.e_prev = None

        # limit of steering angle
        self.steer_angle_th = 20

    def controller(self, e_curr):

        # current values
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
            if self.type_c == "pid":
                res = p + i + d
            elif self.type_c == "pd":
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
