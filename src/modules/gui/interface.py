
from pathlib import Path
import tkinter as tk
from tkinter import font
from types import FunctionType

import sys
import os



PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from gui.parent.canvas import Canvas
from gui.misc.errorhandler import ErrorHandler
from gui.controller.controller import Controller
from simulation.dataloader import DataLoader
from simulation.manufacturing import Manufacturing
from tkinter import filedialog, PhotoImage, ttk
from tkcalendar import Calendar

class Interface:
    def __init__(self) -> None:
        self.mainframe = tk.Tk()
        self.mainframe.title('SMD Produktion')
        self.mainframe.geometry('1200x750')
        photo = PhotoImage(file = os.getcwd() + os.path.normpath('/src/assets/logo.png'))
        self.mainframe.iconphoto(True, photo)
        self.calDate = {}
        self.dateLabel1 = tk.Label(self.mainframe).grid(row=1, column=3)
        self.dateLabel2 = tk.Label(self.mainframe).grid(row=1, column=5)

        """ Create interface elements"""
        self.__createMenu()
        Canvas(self.mainframe)
        self.__createButton(8, 0, text='Compare', function=self.__dummy)
        self.__createButton(2, 0, text='Simulate', function=self.__simulate)
        self.__createForms()

        """ Create error handling capabilities """
        self.errors = ErrorHandler(self.mainframe)

    
    def __call__(self, *args: any, **kwds: any) -> any:
        self.mainframe.mainloop()

    def __close(self):
        self.mainframe.quit()

    def __dummy(self, text = ''):
        print(text)

    def __createMenu(self):
        """ creates the file menu """
        menubar = tk.Menu(self.mainframe)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='New', command=self.__new)
        filemenu.add_command(label='Load', command=self.__openNew)
        filemenu.add_command(label='Save', command=self.__saveAs)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.__close)
        menubar.add_cascade(label='File', menu=filemenu)
        self.mainframe.config(menu=menubar)

    def __createButton(self, posX: int, posY: int, text: str, function: FunctionType, margin: int = None) -> tk.Button:
        """ Create a button at specified position"""
        if margin == None:
            margin = 30
        button = tk.Button(master=self.mainframe, height=1, width=10, text=text, command=function)
        button.grid(column=posX, row=posY, padx=(margin, 0))

    def __createLabel(self, posX: int, posY: int, text: str) -> tk.Label:
        """ Create a label at specified position"""
        label = tk.Label(master=self.mainframe, text=text)
        label.grid(column=posX, row=posY)

    def __createForms(self):
        tk.Label(self.mainframe, text='Program:').grid(row=0, column=0)
        tk.Label(self.mainframe, text='Parts to manufacture:').grid(row=1, column=0)
        tk.Label(self.mainframe, text='Start Date:').grid(row=0, column=4)
        tk.Label(self.mainframe, text='End Date:').grid(row=0, column=6)

        self.product = tk.Entry(self.mainframe)
        self.product.grid(row=0, column=1)
        self.numManu = tk.Entry(self.mainframe)
        self.numManu.grid(row=1, column=1)

        self.date1 = self.__createButton(5, 0, 'Select', function=lambda: self.__showCal('start', 5, 1))
        self.date2 = self.__createButton(7, 0, 'Select', function=lambda: self.__showCal('end', 7, 1))

    def __showCal(self, i, posX, posY):
        top = tk.Toplevel(self.mainframe)
        cal = Calendar(top, font="Arial 14", selectmode='day')

        def getDate(cal):
            top.withdraw()
            self.calDate[i] = cal.selection_get()
            self.__createLabel(posX, posY, self.calDate[i])
        
        cal.pack(fill='both', expand=True)
        ttk.Button(top, text='ok', command=lambda: getDate(cal)).pack()

    def __new(self):
        self.product.delete(0, 'end')
        self.numManu.delete(0, 'end')

    def __saveAs(self):
        pass

    def __openNew(self):
        pass

    def __parseInputSimulation(self):
        if self.product.get() == '':
            return None
        path = Path(os.getcwd() + os.path.normpath('/data/' + self.product.get()))
        return path

    def __simulate(self):
        try:
            path = self.__parseInputSimulation()
            data = DataLoader(path)
            manufacturing = Manufacturing(data(), machine='M20')
            simulationData = manufacturing(plotPCB=True)
            avg = simulationData['time'] * int(self.numManu.get())
            self.__createLabel(2, 1, avg)
            Controller(self.mainframe)(simulationData['plot_x'], simulationData['plot_y'])
        except Exception as e:
            print(e)
            #return self.errors.handle(e)
        





if __name__ == '__main__':
    Interface()()