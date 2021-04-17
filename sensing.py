"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for sensing (3.1)
"""

from picarx_organized import PicarX

class Sensor:

    # initialization
    def __init__(self, car):
        self.car = car
        self.sensors = [self.car.S0, self.car.S1, self.car.S2]

    def sensor_reading(self):
        return [sensor_.read() for sensor_ in self.sensors]

if __name__ == '__main__':
    car = PicarX()
    sensor = Sensor(car)
    while True:
        print(sensor.sensor_reading())