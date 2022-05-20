import os
import random
import sys
import tkinter as tk

try:
    from src.modules.gui.parent.canvas import MyCanvas
except:
    from modules.gui.parent.canvas import MyCanvas
from matplotlib.pyplot import style


class Controller(MyCanvas):
    """Draws PCB on canvas"""

    def __init__(self, frame: tk.Tk) -> None:
        super().__init__(frame)

    def __call__(
        self,
        coords: dict,
        mTime: dict,
        sTime: dict,
        numParts: int,
        randomInterupt: tuple = (0, 0),
        prodName: str = "",
    ) -> any:
        self.figure.clear()
        plot = self.figure.add_subplot(121)
        ax = self.figure.add_subplot(122)
        runtime = sum(list(mTime.values()))
        #setupTime = sum(list(sTime.values()))
        ax.axis("off")
        sumtime = []
        for i in range(numParts):
            sumtime.append(runtime + random.randint(randomInterupt[0], randomInterupt[1]))

        textstr = "\n".join(
            (
                f"Product: {prodName} ",
                "",
                f"Overall time needed: {round(sum(sumtime), 2)} Seconds",
                f"Average Time: {round(sum(sumtime) / numParts, 2)} Seconds ",
                f"Highest time: {round(max(sumtime), 2)} Seconds",
                "",
                "Machines",
            )
        )
        substr = ""
        for key in mTime:
            substr = substr + f"\n{key} Ideal: {round(mTime[key], 2)} Seconds \n{key} Setup Time: {round(sTime[key], 2)} Seconds\n"
        textstr = textstr + substr
        props = dict(boxstyle="round", alpha=0.5)

        ax.text(
            0.05,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props,
        )
        for key in coords:
            plot.scatter(coords[key]["X"], coords[key]["Y"])
        plot.legend(tuple(coords.keys()), loc="upper left")
        self.canvas.draw()

    def wait(self) -> any:
        self.figure.clear()
        waitPlot = self.figure.add_subplot(312)

        style.use("ggplot")
        waitPlot.axis("off")
        waitPlot.set_title("Loading...", color="green")
        self.canvas.draw()

    def error(self, error) -> any:
        self.figure.clear()
        waitPlot = self.figure.add_subplot(312)

        style.use("ggplot")
        waitPlot.axis("off")
        waitPlot.set_title(f"An error occured: {error} ", color="red")
        self.canvas.draw()
