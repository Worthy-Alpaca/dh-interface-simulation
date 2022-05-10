from matplotlib import style

try:
    from src.modules.gui.parent.canvas import Canvas
except:
    from modules.gui.parent.canvas import Canvas

import string
import os
import random


class ErrorHandler(Canvas):
    """Class to handle any errors"""

    def __init__(self, frame) -> None:
        super().__init__(frame)

    def handle(self, error):
        self.figure.clear()
        errorPlot = self.figure.add_subplot(312)

        style.use("ggplot")
        errorPlot.axis("off")

        errorCode = self.__errorCode()
        errorPlot.set_title(f"An error occured: {error}", color="C7")
        self.canvas.draw()

    def __errorCode(self, length=8):
        letters = string.ascii_lowercase
        result = "".join(random.choice(letters) for i in range(length))
        return result
