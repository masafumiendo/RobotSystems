"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class
"""
import time
from threading import Lock
import concurrent.futures

from picarx_organized import PicarX
from sensing import Sensor
from interpretation import Interpretor
from controller import Controller

from busses import MessageBus

lock = Lock()
sensor = Sensor()
interpretor = Interpretor()
controller = Controller()
car = PicarX()

def producer(bus_producer, delay_time):

    while True:
        with lock:
            vals = sensor.sensor_reading()
            bus_producer.write(vals)
        time.sleep(delay_time)

def consumer_producer(bus_consumer, bus_producer, delay_time):

    while True:
        vals = bus_producer.read()
        pos = interpretor.calc_relative_pos(vals)
        bus_consumer.write(pos)
        time.sleep(delay_time)

def consumer(bus_consumer, delay_time):

    while True:
        e_curr = bus_consumer.read()
        steer_angle = controller.controller(e_curr)
        car.forward(30, steer_angle)

def main():

    # initialization
    bus_producer = MessageBus()
    bus_consumer = MessageBus()

    delay_time = 0.01
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        eSencer = executor.submit(producer, bus_producer, delay_time)
        eInterpretor = executor.submit(consumer_producer, bus_consumer, bus_producer, delay_time)
        eController = executor.submit(consumer, bus_consumer, delay_time)

        eSencer.result()
        eInterpretor.result()

if __name__ == '__main__':
    main()