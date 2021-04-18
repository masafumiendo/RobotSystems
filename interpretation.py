"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for interpretation (3.2)
"""

class Interpretor:

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