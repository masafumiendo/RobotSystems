"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for interpretation (3.2)
"""

class Interpretor:

    # initialization
    def __init__(self, sensitivity, polarity):
        """
        :param sensitivity: value from 0 to 1
        :param polarity: value of 0 (follow darker color) or 1 (follow lighter color)
        """
        self.sensitivity = sensitivity
        self.polarity = polarity

    def calc_relative_pos(self, vals):
        return