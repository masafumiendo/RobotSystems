"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for sensing (3.1)
"""

try:
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print("This computer does not appear to be a PiCar-X system(/opt/ezblock is not present). Shadowing hardware calls with substitute functions")
    from sim_ezblock import *

from picarx_organized import PicarX

class Sensor:

    # initialization
    def __init__(self, car):
        self.car = car
        self.sensors = [ADC('A0'), ADC('A1'), ADC('A2')]

    def sensor_reading(self):
        return [sensor_.read() for sensor_ in self.sensors]

if __name__ == '__main__':
    car = PicarX()
    sensor = Sensor(car)
    while True:
        print(sensor.sensor_reading())