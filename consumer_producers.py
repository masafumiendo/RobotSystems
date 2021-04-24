"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class
"""
import time
from threading import Lock

from picarx_organized import PicarX
from sensing import Sensor
from interpretation import Interpretor
from controller import Controller
from integration import Integrator

lock = Lock()
sensor = Sensor()
interpretor = Interpretor()
controller = Controller()

def producer(message_bus, delay_time):

    while True:
        with lock:
            message = sensor.sensor_reading()
            message_bus.write(message)
        time.sleep(delay_time)

def consumer_producer(message_bus, delay_time):

    while True:
        message = message_bus.read()
        message = interpretor.calc_relative_pos(message)
        message_bus.write(message)
        time.sleep(delay_time)

def consumer(message_bus, delay_time):

    while True:
        message = message_bus.read()
