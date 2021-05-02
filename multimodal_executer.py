"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class
"""
import time
from threading import Lock

from concurrent_executor import ConcurrentExecuter

class MultimodalExecuter(ConcurrentExecuter):

    def __init__(self, photosensor, photointerpretor, controller, car, ultrasonicsensor, ultrasonicinterpretor):
        super().__init__(photosensor, photointerpretor, controller, car)
        self.ultrasonicsensor = ultrasonicsensor
        self.ultrasonicinterpretor = ultrasonicinterpretor

    def ultrasonic_sensing(self, bus_producer, delay_time):

        lock = Lock()

        while True:
            with lock:
                vals = self.ultrasonicsensor.sensor_reading()
                bus_producer.write(vals)
            time.sleep(delay_time)

    def ultrasonic_interpretation(self, bus_consumer, bus_producer, delay_time):

        while True:
            val = bus_producer.read()
            pos = self.ultrasonicinterpretor.calc_relative_pos(val)
            bus_consumer.write(pos)
            time.sleep(delay_time)

    def collision_avoidance(self, bus_consumer, delay_time):

        while True:
            pos = bus_consumer.read()
            if pos < 10:
                self.car.forward(0, 0)
            time.sleep(delay_time)