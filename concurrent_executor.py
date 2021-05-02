"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class
"""
import time
from threading import Lock


class ConcurrentExecuter:

    def __init__(self, photosensor, photointerpretor, controller, car):
        self.photosensor = photosensor
        self.photointerpretor = photointerpretor
        self.controller = controller
        self.car = car

    def photo_sensing(self, bus_producer, delay_time):

        lock = Lock()

        while True:
            with lock:
                vals = self.photosensor.sensor_reading()
                bus_producer.write(vals)
            time.sleep(delay_time)

    def photo_interpretation(self, bus_consumer, bus_producer, delay_time):

        while True:
            vals = bus_producer.read()
            pos = self.photointerpretor.calc_relative_pos(vals)
            bus_consumer.write(pos)
            time.sleep(delay_time)

    def steer_control(self, bus_consumer, delay_time):

        while True:
            e_curr = bus_consumer.read()
            steer_angle = self.controller.controller(e_curr)
            self.car.forward(30, steer_angle)
            time.sleep(delay_time)