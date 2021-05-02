"""
Authors: Masafumi Endo
Date: 05/01/2021
Content: main function to execute multimodal control
"""

import sys
sys.path.append('..')

import concurrent.futures

from picarx_organized import PicarX
from photosensing import PhotoSensor, PhotoInterpretor
from ultrasonicsensing import UltrasonicSensor, UltrasonicInterpretor
from controller import Controller

from busses import MessageBus
from multimodal_executer import MultimodalExecuter

if __name__ == '__main__':

    # initialization
    photo_producer = MessageBus()
    photo_consumer = MessageBus()
    ultra_producer = MessageBus()
    ultra_consumer = MessageBus()

    photosensor = PhotoSensor()
    photointerpretor = PhotoInterpretor()
    ultrasonicsensor = UltrasonicSensor()
    ultrasonicinterpretor = UltrasonicInterpretor()
    controller = Controller()
    car = PicarX()

    multimodal_executor = MultimodalExecuter(photosensor, photointerpretor, controller, car, ultrasonicsensor, ultrasonicinterpretor)

    delay_time = 0.01
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        executor.submit(multimodal_executor.photosensor, photo_producer, delay_time)
        executor.submit(multimodal_executor.photointerpretor, photo_consumer, photo_producer, delay_time)
        executor.submit(multimodal_executor.steer_control, photo_consumer, delay_time)
        executor.submit(multimodal_executor.ultrasonicsensor, ultra_producer, delay_time)
        executor.submit(multimodal_executor.ultrasonicinterpretor, ultra_consumer, ultra_producer, delay_time)
        executor.submit(multimodal_executor.collision_avoidance, ultra_consumer, delay_time)