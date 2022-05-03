
from pathlib import Path
import tkinter as tk
from tkinter import font
from types import FunctionType

import sys
import os
import json

from pyparsing import col



PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from gui.parent.canvas import Canvas
from gui.misc.errorhandler import ErrorHandler
from gui.controller.controller import Controller
from simulation.dataloader import DataLoader
from simulation.manufacturing import Manufacturing
from simulation.machine import Machine
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
        self.machines = {}
        self.dateLabel1 = tk.Label(self.mainframe).grid(row=1, column=3)
        self.dateLabel2 = tk.Label(self.mainframe).grid(row=1, column=5)

        """ Create interface elements"""
        menubar = tk.Menu(self.mainframe)
        #self.__createFileMenu(menubar)
        fileMenu = {
            'New': self.__new,
            'Load': self.__openNew,
            'Save': self.__saveAs,
            'seperator': '',
            'Exit': self.__close()
        }
        setupMenu = {
            'Add Machine': self.__setupMachines,
            'View Machines': self.__viewMachines
        }
        self.__createMenu(menubar, 'File', fileMenu)
        self.__createMenu(menubar, 'Setup', setupMenu)
        self.mainframe.config(menu=menubar)
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

    def __createMenu(self, menubar: tk.Menu, label: str, data: dict):
        filemenu = tk.Menu(menubar, tearoff=0)
        for key in data:
            if key == 'seperator':
                filemenu.add_separator()
            else:
                filemenu.add_command(label=key, command=data[key])
        menubar.add_cascade(label=label, menu=filemenu)

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
        self.numManu.insert('end', 1)
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

    def __setupMachines(self):
        top = tk.Toplevel(self.mainframe)
        top.geometry('300x300')
        menubar = tk.Menu(top)
        tk.Label(top, text='Machine Name:').pack()
        nameEntry = tk.Entry(top)
        nameEntry.pack()

        tk.Label(top, text='CPH').pack()
        cphEntry = tk.Entry(top)
        cphEntry.pack()
        
        tk.Label(top, text='Nozzle Heads').pack()
        nozHeads = tk.Entry(top)
        nozHeads.pack()
        self.button_pressed = tk.StringVar()
        tk.Label(top, text='SMD Machine').pack()
        machineType = tk.Checkbutton(top)
        machineType.pack()

        

        def clearMachine():
            nameEntry.delete(0, 'end')
            cphEntry.delete(0, 'end')
            nozHeads.delete(0, 'end')
        
        def close():
            top.withdraw()
        
        def confirm():
            try:
                self.button_pressed.set("button pressed")
                name = nameEntry.get()
                cph = int(cphEntry.get())
                noz = int(nozHeads.get())
                self.machines[name] = Machine(name, cph, noz)
                close()
            except Exception as e:
                tk.Label(top, text='Please only use Numbers for CPH and Nozzle Heads').pack()
            
        def load():
            data = self.__openNew()
            if data == None:
                return
            for i in data['machines']:
                self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'])
            close()

        def nextMachine():
            confirm()
            self.__setupMachines()


        fileMenu = {
            'New': clearMachine,
            'Load': load,
            'Exit': close
        }
        self.conButton = ttk.Button(top, text='OK', command=confirm)
        self.conButton.pack(side='left')
        nextButton = ttk.Button(top, text='Add another', command=nextMachine)
        nextButton.pack(side='right')
        self.__createMenu(menubar, 'File', fileMenu)
        top.config(menu=menubar)

    def __viewMachines(self):
        top = tk.Toplevel(self.mainframe)
        top.geometry('300x150')
        menubar = tk.Menu(top)
        scrollbar = tk.Scrollbar(top)
        scrollbar.pack(side = 'right', fill = 'y')
        mylist = tk.Listbox(top, yscrollcommand = scrollbar.set )
        offset = 0
        def createEntry(machine: Machine):
            mylist.insert('end', f'Machine: {machine.machineName} ')
            mylist.insert('end', f'CPY: {machine.cph} ')
            mylist.insert('end', f'Velocity: {machine.velocity} ')
            mylist.insert('end', f'Nozzle Heads: {machine.nozHeads} ')
            mylist.insert('end', f'-------------')
        for key in self.machines:
            createEntry(self.machines[key])
            offset = offset + 5
        mylist.pack( side = 'top', fill = 'both' )
        scrollbar.config( command = mylist.yview )
        def close():
            top.withdraw()

        def clearMachines():
            close()
            self.machines.clear()

        def save():
            machines = []
            for key in self.machines:
                machines.append(self.machines[key].getData())

            data = {
                "machines": machines
            }
            self.__saveAs(data)


        fileMenu = {
            'Clear': clearMachines,
            'Save': save,
            'Exit': close
        }
        self.__createMenu(menubar, 'File', fileMenu)
        top.config(menu=menubar)

    def __new(self):
        self.product.delete(0, 'end')
        self.numManu.delete(0, 'end')

    def __saveAs(self, data: dict):
        file_opt = options = {}
        options['filetypes'] = [('JSON files', '.json'), ('all files', '.*')]
        options['initialdir'] = os.getcwd() + os.path.normpath("/data/presets")

        filename = filedialog.asksaveasfile(defaultextension=".json", **file_opt)
        if filename is None:  
            return
            
        json.dump(data, filename)

    def __openNew(self) -> (None | dict):
        file_opt = options = {}
        options['filetypes'] = [('JSON files', '.json'), ('all files', '.*')]
        options['initialdir'] = os.getcwd() + os.path.normpath("/data/presets")
        filename = filedialog.askopenfilename(**file_opt)
        if filename == None or filename == '':
            return
        with open(filename) as file:
            data = json.load(file)

        return data

    def __parseInputSimulation(self):
        if self.product.get() == '':
            return None
        path = Path(os.getcwd() + os.path.normpath('/data/' + self.product.get()))
        return path

    def __simulate(self):
        #try:
            path = self.__parseInputSimulation()
            if len(self.machines) == 0:
                self.__setupMachines()
                self.conButton.wait_variable(self.button_pressed)
            print(self.machines)
            data = DataLoader(path)
            manufacturing = Manufacturing(data(), list(self.machines.values())[0] )
            simulationData = manufacturing(plotPCB=True)
            print(simulationData['time'])
            avg = simulationData['time'] * int(self.numManu.get())
            self.__createLabel(2, 1, avg)
            Controller(self.mainframe)(simulationData['plot_x'], simulationData['plot_y'])
        #except Exception as e:
            #return self.errors.handle(e)
        





if __name__ == '__main__':
    Interface()()