"""
Authors: Masafumi Endo
Date: 05/01/2021
Content: class for sensing (5.2)
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

class UltrasonicSensor:

    # initialization
    def __init__(self):
        self.trig = Pin("D0")
        self.echo = Pin("D1")
        self.sensor = Ultrasonic(self.trig, self.echo)

    def sensor_reading(self):
        return self.sensor.read()

class UltrasonicInterpretor:

    # initialization
    def __init__(self, th):
        self.th = th

    def detect_obstacle(self, val):
        if val < self.th:
            flag = 1
        else:
            flag = 0
        return flag