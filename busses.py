"""
Authors: Masafumi Endo
Date: 04/21/2021
Content: class for handle I/O
"""

class MessageBus:

    # initialization
    def __init__(self):
        self.message = None

    def write(self, message):
        self.message = message

    def read(self):
        return self.message