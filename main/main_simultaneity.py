"""
Authors: Masafumi Endo
Date: 04/23/2021
Content: main function to sense line and follow it while concurrent processing
"""

import sys
sys.path.append('..')

import concurrent.futures

from picarx_organized import PicarX
from photosensing import PhotoSensor, PhotoInterpretor
from controller import Controller

from busses import MessageBus
from concurrent_executor import ConcurrentExecuter


if __name__ == '__main__':

    # initialization
    bus_producer = MessageBus()
    bus_consumer = MessageBus()

    photosensor = PhotoSensor()
    photointerpretor = PhotoInterpretor()
    controller = Controller()
    car = PicarX()

    concurrent_executor = ConcurrentExecuter(photosensor, photointerpretor, controller, car)

    delay_time = 0.01
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(concurrent_executor.photo_sensing, bus_producer, delay_time)
        executor.submit(concurrent_executor.photo_interpretation, bus_consumer, bus_producer, delay_time)
        executor.submit(concurrent_executor.steer_control, bus_consumer, delay_time)