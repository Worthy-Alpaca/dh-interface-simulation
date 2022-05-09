from pathlib import Path
import tkinter as tk
from types import FunctionType
import configparser
from os.path import exists
from numpy import product
import requests

import sys
import os
import json

PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from gui.parent.canvas import Canvas
from gui.misc.errorhandler import ErrorHandler
from gui.controller.controller import Controller
from simulation.dataloader import DataLoader
from simulation.manufacturing import Manufacturing
from simulation.machine import Machine
from tkinter import filedialog, PhotoImage, ttk, messagebox
from tkcalendar import Calendar

class Interface:
    def __init__(self) -> None:
        self.mainframe = tk.Tk()
        self.mainframe.protocol("WM_DELETE_WINDOW", self.__onClose)
        self.mainframe.title('SMD Produktion')
        self.mainframe.geometry('1200x750')
        photo = PhotoImage(file = os.getcwd() + os.path.normpath('/src/assets/logo.png'))
        self.mainframe.iconphoto(True, photo)
        self.calDate = {}
        self.machines = {}
        self.dateLabel1 = tk.Label(self.mainframe).grid(row=1, column=3)
        self.dateLabel2 = tk.Label(self.mainframe).grid(row=1, column=5)
        self.config = configparser.ConfigParser()
        self.__configInit()

        """ Create interface elements"""
        menubar = tk.Menu(self.mainframe)
        fileMenu = {
            'New': self.__new,
            'Load': self.__openNew,
            'Save': self.__saveAs,
            'seperator': '',
            'Exit': self.__onClose
        }
        setupMenu = {
            'Add Machine': self.__setupMachines,
            'View Machines': self.__viewMachines
        }
        self.__createMenu(menubar, 'File', fileMenu)
        self.__createMenu(menubar, 'Setup', setupMenu)
        self.__createOptionsMenu(menubar)
        self.mainframe.config(menu=menubar)
        Canvas(self.mainframe)
        self.__createButton(8, 0, text='Compare', function=self.__dummy)
        self.__createButton(2, 0, text='Simulate', function=self.__simulate)
        self.__createForms()
        self.__loadConfig()

        """ Create error handling capabilities """
        self.errors = ErrorHandler(self.mainframe)

    def __configInit(self) -> (list[str] | None):
        path = os.getcwd() + os.path.normpath('/data/settings/settings.ini')
        if exists(path):
            return self.config.read(path)
        
        self.config.add_section('default')
        self.config.set('default', 'randomInterruptMax', '0')
        self.config.set('default', 'randomInterruptMin', '0')
        self.config.set('default', 'multithreading', 'false')
        self.config.set('default', 'randomInterrupt', 'false')
    
    def __call__(self, *args: any, **kwds: any) -> None:
        self.mainframe.mainloop()
    
    def __onClose(self) -> None:
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            with open(os.getcwd() + os.path.normpath('/data/settings/settings.ini'), 'w') as configfile:
                self.config.write(configfile)
            self.mainframe.destroy()

    def __dummy(self, text = '') -> None:
        print(text)

    def __loadConfig(self) -> None:
        data = self.__openNew()
        if data == None:
            return
        for i in data['machines']:
            self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'], i['SMD'], i['offsets'])
        self.__viewMachines()

    def __createMenu(self, menubar: tk.Menu, label: str, data: dict) -> None:
        filemenu = tk.Menu(menubar, tearoff=0)
        for key in data:
            if key == 'seperator':
                filemenu.add_separator()
            else:
                filemenu.add_command(label=key, command=data[key])
        menubar.add_cascade(label=label, menu=filemenu)

    def __createOptionsMenu(self, menubar: tk.Menu) -> tk.Menu:
        filemenu = tk.Menu(menubar, tearoff=0)
        self.multithread = tk.BooleanVar()
        self.multithread.set(self.config.getboolean('default', 'multithreading'))
        filemenu.add_checkbutton(label='Use Multithreading', var=self.multithread, command=lambda: self.config.set('default', 'multithreading', str(self.multithread.get())))
        self.randomInterupt = tk.BooleanVar()
        self.randomInterupt.set(self.config.getboolean('default', 'randomInterrupt'))
        filemenu.add_checkbutton(label='Use Random Interuptions', var=self.randomInterupt, command=lambda: self.config.set('default', 'randomInterrupt', str(self.randomInterupt.get())))
        filemenu.add_separator()
        filemenu.add_command(label='Options', command=self.__setOptions)
        menubar.add_cascade(label='Options', menu=filemenu)

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

    def __createForms(self) -> None:
        tk.Label(self.mainframe, text='Program:').grid(row=0, column=0)
        tk.Label(self.mainframe, text='Parts to manufacture:').grid(row=1, column=0)
        tk.Label(self.mainframe, text='Start Date:').grid(row=0, column=4)
        tk.Label(self.mainframe, text='End Date:').grid(row=0, column=6)

        #self.product = tk.Entry(self.mainframe)
        #self.product.grid(row=0, column=1)
        self.numManu = tk.Entry(self.mainframe)
        self.numManu.insert('end', 1)
        self.numManu.grid(row=1, column=1)

        OptionList = os.listdir(os.getcwd() + os.path.normpath('/data/'))

        self.product = tk.StringVar(self.mainframe)
        option = tk.OptionMenu(self.mainframe, self.product, *OptionList)
        option.grid(row=0, column=1)

        self.date1 = self.__createButton(5, 0, 'Select', function=lambda: self.__showCal('start', 5, 1))
        self.date2 = self.__createButton(7, 0, 'Select', function=lambda: self.__showCal('end', 7, 1))

    def __showCal(self, i: str, posX: int, posY: int) -> tk.Toplevel:
        top = tk.Toplevel(self.mainframe)
        cal = Calendar(top, font="Arial 14", selectmode='day')

        def getDate(cal: Calendar):
            top.withdraw()
            self.calDate[i] = cal.selection_get()
            self.__createLabel(posX, posY, self.calDate[i])
        
        cal.pack(fill='both', expand=True)
        ttk.Button(top, text='ok', command=lambda: getDate(cal)).pack()

    def __setupMachines(self) -> tk.Toplevel:
        top = tk.Toplevel(self.mainframe)
        #top.geometry('300x300')
        top.title('Add Machine')
        menubar = tk.Menu(top)
        tk.Label(top, text='Machine Name:').grid(row=0, column=0)
        nameEntry = tk.Entry(top)
        nameEntry.grid(row=0, column=1)

        tk.Label(top, text='CPH:').grid(row=1, column=0)
        cphEntry = tk.Entry(top)
        cphEntry.insert('end', '1')
        cphEntry.grid(row=1, column=1)
        
        tk.Label(top, text='Nozzle Heads:').grid(row=2, column=0)
        nozHeads = tk.Entry(top)
        nozHeads.insert('end', '1')
        nozHeads.grid(row=2, column=1)
        self.button_pressed = tk.StringVar()
        smdMachine = tk.BooleanVar()
        smdMachine.set(False)
        tk.Label(top, text='SMD Machine:').grid(row=3, column=0)

        """ Offset entries """
        tk.Label(top, text='Offsets').grid(row=4, column=0)
        tk.Label(top, text='X').grid(row=4, column=1)
        tk.Label(top, text='Y').grid(row=4, column=2)
        tk.Label(top, text='Checkpoint:').grid(row=5, column=0)
        checkpointX = tk.Entry(top)
        checkpointX.insert('end', '0')
        checkpointX.grid(row=5, column=1)
        checkpointY = tk.Entry(top)
        checkpointY.insert('end', '0')
        checkpointY.grid(row=5, column=2)

        tk.Label(top, text='PCB:').grid(row=6, column=0)
        pcbX = tk.Entry(top)
        pcbX.insert('end', '0')
        pcbX.grid(row=6, column=1)
        pcbY = tk.Entry(top)
        pcbY.insert('end', '0')
        pcbY.grid(row=6, column=2)

        """ feedercart 1"""
        row1 = 7
        tk.Label(top, text='Feedercart Front Left:').grid(row=row1, column=0)
        feedercart_1x = tk.Entry(top)
        feedercart_1x.insert('end', '0')
        feedercart_1x.grid(row=row1, column=1)
        feedercart_1y = tk.Entry(top)
        feedercart_1y.insert('end', '0')
        feedercart_1y.grid(row=row1, column=2)
        """ feedercart 2"""
        row2 = 8
        tk.Label(top, text='Feedercart Back Left:').grid(row=row2, column=0)
        feedercart_2x = tk.Entry(top)
        feedercart_2x.insert('end', '0')
        feedercart_2x.grid(row=row2, column=1)
        feedercart_2y = tk.Entry(top)
        feedercart_2y.insert('end', '0')
        feedercart_2y.grid(row=row2, column=2)
        """ feedercart 3"""
        row3 = 9
        tk.Label(top, text='Feedercart Front Right:').grid(row=row3, column=0)
        feedercart_3x = tk.Entry(top)
        feedercart_3x.insert('end', '0')
        feedercart_3x.grid(row=row3, column=1)
        feedercart_3y = tk.Entry(top)
        feedercart_3y.insert('end', '0')
        feedercart_3y.grid(row=row3, column=2)
        """ feedercart 4"""
        row4 = 10
        tk.Label(top, text='Feedercart Back Right:').grid(row=row4, column=0)
        feedercart_4x = tk.Entry(top)
        feedercart_4x.insert('end', '0')
        feedercart_4x.grid(row=row4, column=1)
        feedercart_4y = tk.Entry(top)
        feedercart_4y.insert('end', '0')
        feedercart_4y.grid(row=row4, column=2)

        
        machineType = tk.Checkbutton(top, var=smdMachine)
        machineType.grid(row=3, column=1)

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
                if smdMachine.get() == False:
                    self.machines[name] = Machine(name, cph, noz, smdMachine.get())
                    return close()
                args = {
                    "checkpoint": [int(checkpointX.get()), int(checkpointY.get())],
                    "pcb": [int(pcbX.get()), int(pcbY.get())],
                    "feedercarts": [
                        {"ST-FL": [int(feedercart_1x.get()), int(feedercart_1y.get())]},
                        {"ST-RL": [int(feedercart_2x.get()), int(feedercart_2y.get())]},
                        {"ST-FR": [feedercart_3x.get(), feedercart_3y.get()]},
                        {"ST-RR": [feedercart_4x.get(), feedercart_4y.get()]}
                    ]
                }
                self.machines[name] = Machine(name, cph, noz, smdMachine.get(), offsets=args)
                close()
            except Exception as e:
                tk.Label(top, text='Please only use Numbers for CPH and Nozzle Heads').grid(row=51, column=1)
            
        def load():
            self.machines.clear()
            data = self.__openNew()
            if data == None:
                return
            for i in data['machines']:
                self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'], i['SMD'], i['offsets'])
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
        self.conButton.grid(row=50, column=0)
        nextButton = ttk.Button(top, text='Add another', command=nextMachine)
        nextButton.grid(row=50, column=1)
        self.__createMenu(menubar, 'File', fileMenu)
        top.config(menu=menubar)

    def __viewMachines(self) -> tk.Toplevel:
        top = tk.Toplevel(self.mainframe)
        top.geometry('300x200')
        top.title('Machines')
        menubar = tk.Menu(top)
        scrollbar = tk.Scrollbar(top)
        scrollbar.pack(side = 'right', fill = 'y')
        mylist = tk.Listbox(top, yscrollcommand = scrollbar.set )
        def createEntry(machine: Machine):
            mylist.insert('end', f'Machine: {machine.machineName} ')
            mylist.insert('end', f'CPH: {machine.cph} ')
            mylist.insert('end', f'Velocity: {machine.velocity} ')
            mylist.insert('end', f'Nozzle Heads: {machine.nozHeads} ')
            mylist.insert('end', f'Offsets: {machine.offsets} ')
            mylist.insert('end', f'-------------')
        for key in self.machines:
            createEntry(self.machines[key])
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
        
        def load():
            self.machines.clear()
            data = self.__openNew()
            if data == None:
                return
            for i in data['machines']:
                self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'], i['SMD'], i['offsets'])
            close()
            self.__viewMachines()


        fileMenu = {
            'Clear': clearMachines,
            'Save': save,
            'Load': load,
            'Exit': close
        }
        self.__createMenu(menubar, 'File', fileMenu)
        top.config(menu=menubar)
        ttk.Button(top, text='ok', command=close).pack()

    def __setOptions(self) -> tk.Toplevel:
        top = tk.Toplevel(self.mainframe)
        top.geometry('300x150')
        top.title('Options')
        
        def callback():
            max = randominterruptmax.get()
            min = randominterruptmin.get()
            if min > max:
                return tk.Label(top, text='The maximum interrupt value needs to be higher then the minimum!', foreground='red', wraplengt=200).pack()
            self.config.set('default', 'randominterruptmax', str(max))
            self.config.set('default', 'randominterruptmin', str(min))
            top.withdraw()
            return True
        tk.Label(top, text='Random Interruptions Max').pack()
        randominterruptmax = tk.IntVar()
        randominterruptmax.set(self.config.getint('default', 'randominterruptmax'))
        tk.Entry(top, textvariable=randominterruptmax).pack()
        tk.Label(top, text='Random Interruptions Min').pack()
        randominterruptmin = tk.IntVar()
        randominterruptmin.set(self.config.getint('default', 'randominterruptmin'))
        tk.Entry(top, textvariable=randominterruptmin).pack()

        ttk.Button(top, text='OK', command=callback).pack()

    def __new(self) -> None:
        self.numManu.delete(0, 'end')

    def __saveAs(self, data: dict) -> None:
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

    def __parseInputSimulation(self) -> Path:
        if self.product.get() == '':
            return None
        path = Path(os.getcwd() + os.path.normpath('/data/' + self.product.get()))
        return path

    def __simulate(self) -> None:

        machineTime = {}
        coords = {}
        for i in self.machines:
            machine = self.machines[i]
            product_id = self.product.get()
            data = machine.getData()
            type = 'manufacturing'
            if self.machines[i].SMD == False:
                type = 'coating'
            request = requests.put(f'http://127.0.0.1:5000/simulate/{type}/{product_id}', data = json.dumps(data) )
            if request.status_code != 200:
                return self.errors.handle(request.status_code)
            requestData = request.json()
            machineTime[self.machines[i].machineName] = requestData['time']
            if 'plot_x' in requestData:
                coords[self.machines[i].machineName] = {
                        'X': requestData['plot_x'],
                        'Y': requestData['plot_y']
                    }
        
        randomInterrupt = (0, 0) if self.randomInterupt.get() == False else (self.config.getint('default', 'randominterruptmin'), self.config.getint('default', 'randominterruptmax'))
        controller = Controller(self.mainframe)
        #controller(coordX, coordY, machineTime, int(self.numManu.get()), randomInterrupt, prodName=self.product.get())
        controller(coords=coords, time=machineTime, numParts=int(self.numManu.get()), randomInterupt=randomInterrupt, prodName=self.product.get())
        





if __name__ == '__main__':
    Interface()()