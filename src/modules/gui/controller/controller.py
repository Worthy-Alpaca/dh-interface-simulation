

import os
import sys

from gui.parent.canvas import Canvas

class Controller(Canvas):
    """ Draws PCB on canvas """
    def __init__(self, frame) -> None:
        super().__init__(frame)

    def __call__(self, data_x, data_y) -> any:
        self.figure.clear()
        plot = self.figure.add_subplot(111)
        plot.scatter(data_x, data_y)
        self.canvas.draw()