"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for sensing (3.1)
"""

### begin 2.5.3
try:
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print("This computer does not appear to be a PiCar-X system(/opt/ezblock is not present). Shadowing hardware calls with substitute functions")
    from sim_ezblock import *
### end 2.5.3

from picarx_organized import PicarX

class Sensor:

    # initialization
    def __init__(self):
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')
        self.sensors = [self.S0, self.S1, self.S2]

    def sensor_reading(self):
        return [sensor_.read() for sensor_ in self.sensors]

if __name__ == '__main__':
    car = PicarX()
    sensor = Sensor()
    while True:
        print(sensor.sensor_reading())