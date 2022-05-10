from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk


class Canvas(tk.Canvas):
    def __init__(self, frame) -> tk.Canvas:
        """Creates the canvas on which to draw"""
        self.mainframe = frame
        self.figure = Figure(figsize=(11.6, 6.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.mainframe)
        self.canvas.draw()
        self.__tools()

    def __tools(self):
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=10, rowspan=10, padx=(20, 20))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.mainframe, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=13, column=0, columnspan=10, rowspan=10, padx=(20, 20))
