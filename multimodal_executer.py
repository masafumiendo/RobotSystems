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
                val = self.ultrasonicsensor.sensor_reading()
                bus_producer.write(val)
            time.sleep(delay_time)

    def ultrasonic_interpretation(self, bus_consumer, bus_producer, delay_time):

        while True:
            val = bus_producer.read()
            print(val)
            flag = self.ultrasonicinterpretor.detect_obstacle(val)
            bus_consumer.write(flag)
            time.sleep(delay_time)

    def collision_avoidance(self, bus_consumer, delay_time):

        while True:
            flag = bus_consumer.read()
            time.sleep(delay_time)