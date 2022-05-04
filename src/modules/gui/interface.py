
from pathlib import Path
import tkinter as tk
from types import FunctionType

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
            'Exit': self.__close
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

    
    def __call__(self, *args: any, **kwds: any) -> any:
        self.mainframe.mainloop()

    def __close(self):
        self.mainframe.quit()

    def __dummy(self, text = ''):
        print(text)

    def __loadConfig(self):
        data = self.__openNew()
        if data == None:
            return
        for i in data['machines']:
            self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'], i['offsets'])
        self.__viewMachines()

    def __createMenu(self, menubar: tk.Menu, label: str, data: dict):
        filemenu = tk.Menu(menubar, tearoff=0)
        for key in data:
            if key == 'seperator':
                filemenu.add_separator()
            else:
                filemenu.add_command(label=key, command=data[key])
        menubar.add_cascade(label=label, menu=filemenu)

    def __createOptionsMenu(self, menubar: tk.Menu):
        filemenu = tk.Menu(menubar, tearoff=0)
        self.muiltthread = tk.BooleanVar()
        self.muiltthread.set(True)
        filemenu.add_checkbutton(label='Use Multithreading', var=self.muiltthread)
        self.randomInterupt = tk.BooleanVar()
        self.randomInterupt.set(True)
        filemenu.add_checkbutton(label='Use Random Interuptions', var=self.randomInterupt)
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

    def __createForms(self):
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
        #top.geometry('300x300')
        top.title('Add Machine')
        menubar = tk.Menu(top)
        tk.Label(top, text='Machine Name:').grid(row=0, column=0)
        nameEntry = tk.Entry(top)
        nameEntry.grid(row=0, column=1)

        tk.Label(top, text='CPH:').grid(row=1, column=0)
        cphEntry = tk.Entry(top)
        cphEntry.grid(row=1, column=1)
        
        tk.Label(top, text='Nozzle Heads:').grid(row=2, column=0)
        nozHeads = tk.Entry(top)
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
        checkpointX.grid(row=5, column=1)
        checkpointY = tk.Entry(top)
        checkpointY.grid(row=5, column=2)

        tk.Label(top, text='PCB:').grid(row=6, column=0)
        pcbX = tk.Entry(top)
        pcbX.grid(row=6, column=1)
        pcbY = tk.Entry(top)
        pcbY.grid(row=6, column=2)
        """ feedercart 1"""
        row1 = 7
        tk.Label(top, text='Feedercart 1:').grid(row=row1, column=0)
        feedercart_1x = tk.Entry(top)
        feedercart_1x.grid(row=row1, column=1)
        feedercart_1y = tk.Entry(top)
        feedercart_1y.grid(row=row1, column=2)
        """ feedercart 2"""
        row2 = 8
        tk.Label(top, text='Feedercart 2:').grid(row=row2, column=0)
        feedercart_2x = tk.Entry(top)
        feedercart_2x.grid(row=row2, column=1)
        feedercart_2y = tk.Entry(top)
        feedercart_2y.grid(row=row2, column=2)
        """ feedercart 3"""
        row3 = 9
        tk.Label(top, text='Feedercart 3:').grid(row=row3, column=0)
        feedercart_3x = tk.Entry(top)
        feedercart_3x.grid(row=row3, column=1)
        feedercart_3y = tk.Entry(top)
        feedercart_3y.grid(row=row3, column=2)
        """ feedercart 4"""
        row4 = 10
        tk.Label(top, text='Feedercart 4:').grid(row=row4, column=0)
        feedercart_4x = tk.Entry(top)
        feedercart_4x.grid(row=row4, column=1)
        feedercart_4y = tk.Entry(top)
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
                    self.machines[name] = Machine(name, cph, noz)
                    return close()
                args = {
                    "checkpoint": [int(checkpointX.get()), int(checkpointY.get())],
                    "pcb": [int(pcbX.get()), int(pcbY.get())],
                    "feedercarts": [
                        {"feedercart_1": [int(feedercart_1x.get()), int(feedercart_1y.get())]},
                        {"feedercart_2": [int(feedercart_2x.get()), int(feedercart_2y.get())]},
                        {"feedercart_3": [feedercart_3x.get(), feedercart_3y.get()]},
                        {"feedercart_4": [feedercart_4x.get(), feedercart_4y.get()]}
                    ]
                }
                self.machines[name] = Machine(name, cph, noz, offsets=args)
                close()
            except Exception as e:
                tk.Label(top, text='Please only use Numbers for CPH and Nozzle Heads').grid(row=51, column=1)
            
        def load():
            data = self.__openNew()
            if data == None:
                return
            for i in data['machines']:
                self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'], i['offsets'])
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

    def __viewMachines(self):
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
            data = self.__openNew()
            if data == None:
                return
            for i in data['machines']:
                self.machines[i['machine']] = Machine(i['machine'], i['cph'], i['nozHeads'], i['offsets'])
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

    def __setOptions(self):
        top = tk.Toplevel(self.mainframe)
        top.geometry('300x150')
        top.title('Options')
        tk.Label(top, text='Placeholder').pack()

    def __new(self):
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
            data = DataLoader(path)
            manufacturing = Manufacturing(data(), list(self.machines.values())[0] )
            simulationData = manufacturing(plotPCB=True, multithread=self.muiltthread.get())
            print(simulationData['time'])
            avg = simulationData['time'] * int(self.numManu.get())
            #self.__createLabel(2, 1, avg)
            Controller(self.mainframe)(simulationData['plot_x'], simulationData['plot_y'], simulationData['time'], int(self.numManu.get()))
        #except Exception as e:
            #return self.errors.handle(e)
        





if __name__ == '__main__':
    Interface()()