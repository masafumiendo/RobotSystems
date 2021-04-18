"""
Authors: Masafumi Endo
Date: 04/15/2021
Content: class for interpretation (3.2)
"""

class Interpretor:

    # initialization
    def __init__(self, sensitivity=0.8, polarity=0):
        """
        :param sensitivity: value from 0 to 1
        :param polarity: value of 0 (follow darker color) or 1 (follow lighter color)
        """
        self.sensitivity = sensitivity
        self.polarity = polarity

    def calc_relative_pos(self, vals):

        # calculate relative differences against target (center) value
        diff_l = vals[1] - vals[0]
        diff_r = vals[1] - vals[2]
        print('left : {}, center : {}, right : {}'.format(vals[0], vals[1], vals[2]))
        print('diff of left : {}, diff of right {}'.format(diff_l, diff_r))
        # follow darker color
        pos = self.sensitivity * (diff_l - diff_r)
        print('relative pos : {}'.format(pos))
        if self.polarity == 1:
            # follow lighter color (change sign)
            pos = - 1 * pos
        if abs(pos) > 1:
            pos = float(pos / abs(pos))

        return pos