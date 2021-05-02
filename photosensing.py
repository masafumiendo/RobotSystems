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

class PhotoSensor:

    # initialization
    def __init__(self):
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')
        self.sensors = [self.S0, self.S1, self.S2]

    def sensor_reading(self):
        return [sensor_.read() for sensor_ in self.sensors]

class PhotoInterpretor:

    # initialization
    def __init__(self, sensitivity=1e-2, polarity=0):
        """
        :param sensitivity: value from 0 to 1
        :param polarity: value of 0 (follow darker color) or 1 (follow lighter color)
        """
        self.sensitivity = sensitivity
        self.polarity = polarity

    def calc_relative_pos(self, vals):

        # set target value
        if self.polarity == 0:
            val_t = min(vals)
        elif self.polarity == 1:
            val_t = max(vals)

        # calculate relative differences against target value
        diff_l = vals[0] - val_t
        diff_r = vals[2] - val_t
        pos = self.sensitivity * (diff_l - diff_r)

        if pos > 1:
            pos = 1
        elif pos < -1:
            pos = -1

        return pos