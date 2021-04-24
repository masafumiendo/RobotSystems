"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class
"""
import time
from threading import Lock


class ConcurrentExecuter:

    def __init__(self, sensor, interpretor, controller, car):
        self.sensor = sensor
        self.interpretor = interpretor
        self.controller = controller
        self.car = car

    def producer(self, bus_producer, delay_time):

        lock = Lock()

        while True:
            with lock:
                vals = self.sensor.sensor_reading()
                bus_producer.write(vals)
            time.sleep(delay_time)

    def consumer_producer(self, bus_consumer, bus_producer, delay_time):

        while True:
            vals = bus_producer.read()
            pos = self.interpretor.calc_relative_pos(vals)
            bus_consumer.write(pos)
            time.sleep(delay_time)

    def consumer(self, bus_consumer, delay_time):

        while True:
            e_curr = bus_consumer.read()
            steer_angle = self.controller.controller(e_curr)
            self.car.forward(30, steer_angle)
            time.sleep(delay_time)