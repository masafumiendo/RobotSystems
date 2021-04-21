"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class for handle I/O
"""

class SensorBus:

    # initialization
    def __init__(self):
        self.message = 0

    def write(self):
        pass

    def read(self):
        return self.message