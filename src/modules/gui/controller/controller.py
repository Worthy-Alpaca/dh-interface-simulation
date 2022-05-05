

import os
import random
import sys

from gui.parent.canvas import Canvas

class Controller(Canvas):
    """ Draws PCB on canvas """
    def __init__(self, frame) -> None:
        super().__init__(frame)

    def __call__(self, data_x, data_y, time, numParts, randomInterupt: tuple = (0, 0)) -> any:
        self.figure.clear()
        plot = self.figure.add_subplot(121)
        ax = self.figure.add_subplot(122)
        ax.axis('off')
        sumtime = []
        for i in range(numParts):
            sumtime.append(time + random.randint(randomInterupt[0], randomInterupt[1]))
        
        textstr = '\n'.join((
            f'Overall time needed: {round(sum(sumtime), 2)} Seconds',
            f'Average Time: {round(sum(sumtime) / numParts, 2)} Seconds ', 
            f'Highest time: {round(max(sumtime), 2)} Seconds',))
        props = dict(boxstyle='round', alpha=0.5)
        
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)
        plot.scatter(data_x, data_y)
        self.canvas.draw()