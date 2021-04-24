"""
Authors: Masafumi Endo
Date: 04/23/2021
Content: main function to sense line and follow it while concurrent processing
"""

import sys
sys.path.append('..')

import concurrent.futures

from picarx_organized import PicarX
from sensing import Sensor
from interpretation import Interpretor
from controller import Controller

from busses import MessageBus
from consumer_producers import ConcurrentExecuter


if __name__ == '__main__':

    # initialization
    bus_producer = MessageBus()
    bus_consumer = MessageBus()

    sensor = Sensor()
    interpretor = Interpretor()
    controller = Controller()
    car = PicarX()

    concurrent_executor = ConcurrentExecuter(sensor, interpretor, controller, car)

    delay_time = 0.01
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(concurrent_executor.producer, bus_producer, delay_time)
        executor.submit(concurrent_executor.consumer_producer, bus_consumer, bus_producer, delay_time)
        executor.submit(concurrent_executor.consumer, bus_consumer, delay_time)