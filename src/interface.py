from pathlib import Path
import tkinter as tk
from types import FunctionType
import configparser
from os.path import exists
import time as tm
import requests
import threading
from tkinter import *
import sys
import os
import json

PACKAGE_PARENT = "../"
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
try:
    from src.modules.gui.parent.canvas import MyCanvas
    from src.modules.gui.controller.controller import Controller
    from src.modules.gui.backend.machine import Machine
    from src.modules.gui.backend.network import NetworkRequests
except:
    from modules.gui.parent.canvas import MyCanvas
    from modules.gui.controller.controller import Controller
    from modules.gui.backend.machine import Machine
    from modules.gui.backend.network import NetworkRequests
from tkinter import Grid, filedialog, PhotoImage, ttk, messagebox
from tkcalendar import Calendar


class Interface:
    def __init__(self) -> None:
        """Creates the interface and it's child modules."""
        self.mainframe = tk.Tk()
        self.mainframe.protocol("WM_DELETE_WINDOW", self.__onClose)

        self.mainframe.title("SMD Produktion")
        # self.mainframe.geometry("1200x750")
        self.mainframe.minsize(width=900, height=570)

        # bind keyboard controlls
        self.mainframe.bind("<Control-x>", self.__onClose)
        # self.mainframe.bind("<Control-F1>", self.__getAPIData)
        self.mainframe.bind("<F1>", self.__startSimulation)
        self.mainframe.bind("<F2>", self.__startCompare)

        # configuring rows
        Grid.rowconfigure(self.mainframe, 0, weight=1)
        Grid.rowconfigure(self.mainframe, 1, weight=1)
        Grid.rowconfigure(self.mainframe, 2, weight=1)

        # configuring columns
        Grid.columnconfigure(self.mainframe, 0, weight=1)
        Grid.columnconfigure(self.mainframe, 1, weight=1)
        Grid.columnconfigure(self.mainframe, 2, weight=1)
        Grid.columnconfigure(self.mainframe, 3, weight=1)
        Grid.columnconfigure(self.mainframe, 4, weight=1)
        Grid.columnconfigure(self.mainframe, 5, weight=1)
        Grid.columnconfigure(self.mainframe, 6, weight=1)
        Grid.columnconfigure(self.mainframe, 7, weight=1)

        photo = PhotoImage(file=os.getcwd() + os.path.normpath("/src/assets/logo.png"))
        self.mainframe.iconphoto(True, photo)
        self.calDate = {}
        self.machines = {}
        self.OptionList = []
        self.dateLabel1 = tk.Label(self.mainframe).grid(row=1, column=3, sticky="nsew")
        self.dateLabel2 = tk.Label(self.mainframe).grid(row=1, column=5, sticky="nsew")
        self.config = configparser.ConfigParser()
        self.__configInit()

        # Create interface elements
        menubar = tk.Menu(self.mainframe)
        fileMenu = {
            "New": self.__new,
            "Load": self.__openNew,
            "Save": self.__saveAs,
            "seperator": "",
            "Exit Strg+x": self.__onClose,
        }
        setupMenu = {
            "Add Machine": self.__setupMachines,
            "View Machines": self.__viewMachines,
            "Dummy": self.__dummy,
        }
        self.__createMenu(menubar, "File", fileMenu)
        self.__createMenu(menubar, "Setup", setupMenu)
        self.__createOptionsMenu(menubar)
        self.mainframe.config(menu=menubar)
        # Canvas(self.mainframe)
        frame = tk.Frame(self.mainframe)
        frame.grid(row=3, column=0, sticky="nsew")
        MyCanvas(self.mainframe)
        self.__createButton(8, 0, text="Compare F2", function=self.__dummy, margin=50)
        self.__createButton(2, 0, text="Simulate F1", function=self.__simulate)

        self.requests = NetworkRequests(
            networkAddress=self.config.get("network", "api_address"),
            basePath=self.config.get("network", "base_path"),
        )
        self.__createForms()
        self.__loadConfig()

    def __configInit(self) -> configparser.ConfigParser:
        """Initiate the config variables.

        Returns:
            ConfigParser: Module that contains config settings.
        """
        path = os.getcwd() + os.path.normpath("/data/settings/settings.ini")
        if exists(path):
            return self.config.read(path)

        self.config.add_section("default")
        self.config.set("default", "randomInterruptMax", "0")
        self.config.set("default", "randomInterruptMin", "0")
        self.config.set("default", "useIdealState", "false")
        self.config.set("default", "randomInterrupt", "false")
        self.config.set("default", "useAISim", "false")
        self.config.add_section("network")
        self.config.set("network", "api_address", "http://127.0.0.1:5000")
        self.config.set("network", "base_path", "/api/v1/")

    def __call__(self, *args: any, **kwds: any) -> None:
        """Call this to initate the window."""
        self.mainframe.mainloop()

    def run(self) -> None:
        """Call this to initate the window."""
        self.mainframe.mainloop()

    def __onClose(self, *args: any, **kwargs: any) -> None:
        """Closing Operation. Saves config variables to file."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if not exists(os.getcwd() + os.path.normpath("/data/settings")):
                os.mkdir(os.getcwd() + os.path.normpath("/data/settings"))
            with open(
                os.getcwd() + os.path.normpath("/data/settings/settings.ini"), "w"
            ) as configfile:
                self.config.write(configfile)
            self.mainframe.destroy()
            exit()

    def __startThread(self, function: FunctionType, *args):
        """Start a new thread with a given function.

        Args:
            function (FunctionType): The current function.
        """
        threading.Thread(target=function).start()

    def __dummy(self, text="") -> None:
        """Dummy function. Used for testing.

        Args:
            text (str, optional): Optional Textstring. Defaults to "".
        """
        top = tk.Toplevel(self.mainframe)
        top.geometry("500x500")
        Grid.rowconfigure(top, 0, weight=1)

        Grid.columnconfigure(top, 0, weight=1)

        Grid.rowconfigure(top, 1, weight=1)
        button_1 = Button(top, text="Button 1")
        button_2 = Button(top, text="Button 2")
        button_1.grid(row=0, column=0, sticky="nsew")
        button_2.grid(row=1, column=0, sticky="nsew")

    def __loadConfig(self) -> None:
        """Load a machine config from `.json` file."""
        data = self.__openNew()
        if data == None:
            return
        for i in data["machines"]:
            self.machines[i["machine"]] = Machine(
                i["machine"], i["cph"], i["nozHeads"], i["SMD"], i["offsets"]
            )
        self.__viewMachines()

    def __createMenu(self, menubar: tk.Menu, label: str, data: dict) -> None:
        """Create a menu in the menubar.

        Args:
            menubar (tk.Menu): The current MenuBar instance.
            label (str): The Label of the menu.
            data (dict): Options in the menu.
        """
        filemenu = tk.Menu(menubar, tearoff=0)
        for key in data:
            if key == "seperator":
                filemenu.add_separator()
            else:
                filemenu.add_command(label=key, command=data[key])
        menubar.add_cascade(label=label, menu=filemenu)

    def __createOptionsMenu(self, menubar: tk.Menu) -> tk.Menu:
        """Creates the Options Menu.

        Args:
            menubar (tk.Menu): The current MenuBar instance.

        Returns:
            tk.Menu: The created menu.
        """
        filemenu = tk.Menu(menubar, tearoff=0)
        self.useIdealState = tk.BooleanVar()
        self.useIdealState.set(self.config.getboolean("default", "useIdealState"))
        filemenu.add_checkbutton(
            label="Use ideal Simulation Time",
            var=self.useIdealState,
            command=lambda: self.config.set(
                "default", "useIdealState", str(self.useIdealState.get())
            ),
        )
        self.randomInterupt = tk.BooleanVar()
        self.randomInterupt.set(self.config.getboolean("default", "randomInterrupt"))
        filemenu.add_checkbutton(
            label="Use Random Interuptions",
            var=self.randomInterupt,
            command=lambda: self.config.set(
                "default", "randomInterrupt", str(self.randomInterupt.get())
            ),
        )
        self.useAISim = tk.BooleanVar()
        self.useAISim.set(self.config.getboolean("default", "useAISim"))
        filemenu.add_checkbutton(
            label="Use AI Simulation",
            var=self.useAISim,
            command=lambda: self.config.set(
                "default", "useAISim", str(self.randomInterupt.get())
            ),
        )
        filemenu.add_separator()
        filemenu.add_command(label="Options", command=self.__setOptions)
        menubar.add_cascade(label="Options", menu=filemenu)

    def __createButton(
        self,
        posX: int,
        posY: int,
        text: str,
        function: FunctionType,
        margin: int = None,
    ) -> tk.Button:
        """Creates a Button at the given position.

        Args:
            posX (int): The X Grid Position.
            posY (int): The Y Grid Position.
            text (str): The display text.
            function (FunctionType): The function to be called on button press.
            margin (int, optional): Margin to next element in Grid. Defaults to None.

        Returns:
            tk.Button: The created Button.
        """
        if margin == None:
            margin = 30
        button = tk.Button(
            master=self.mainframe,
            height=1,
            width=10,
            text=text,
            command=lambda: self.__startThread(function),
        )
        button.grid(column=posX, row=posY, padx=(margin, 0), sticky="nsew")

    def __createLabel(self, posX: int, posY: int, text: str) -> tk.Label:
        """Creates a Label at the given position.

        Args:
            posX (int): The X Grid Position.
            posY (int): The Y Grid Position.
            text (str): The display text.

        Returns:
            tk.Label: The created Label.
        """
        label = tk.Label(master=self.mainframe, text=text)
        label.grid(column=posX, row=posY, sticky="nsew")

    def __runAPICheck(self, *args):
        """Get Data all Program options from API."""
        request = self.requests.get("/data/options/")
        if type(request) == tuple:
            controller = Controller(self.mainframe)
            controller.error("Connection to the API could not be established!")
            self.OptionList = ["API", "CONNECTION", "FAILED"]
        else:
            self.OptionList = request["programms"]

        menu = self.option["menu"]
        menu.delete(0, "end")
        for string in self.OptionList:
            menu.add_command(
                label=string, command=lambda value=string: self.product.set(value)
            )

    def __createForms(self) -> None:
        """Creates the Inputs."""
        tk.Label(self.mainframe, text="Program:").grid(row=0, column=0, sticky="nsew")
        tk.Label(self.mainframe, text="Parts to manufacture:").grid(
            row=1, column=0, sticky="nsew"
        )
        tk.Label(self.mainframe, text="Start Date:").grid(
            row=0, column=4, sticky="nsew"
        )
        tk.Label(self.mainframe, text="End Date:").grid(row=0, column=6, sticky="nsew")
        self.numManu = tk.Entry(self.mainframe)
        self.numManu.insert("end", 1)
        self.numManu.grid(row=1, column=1, sticky="nsew")
        self.product = tk.StringVar(self.mainframe)
        self.product.set("")
        self.option = tk.OptionMenu(self.mainframe, self.product, "", *self.OptionList)
        self.option.grid(row=0, column=1, sticky="nsew")
        self.option.bind("<Enter>", self.__runAPICheck)

        self.date1 = self.__createButton(
            5, 0, "Select", function=lambda: self.__showCal("start", 5, 1)
        )
        self.date2 = self.__createButton(
            7, 0, "Select", function=lambda: self.__showCal("end", 7, 1)
        )

    def __showCal(self, i: str, posX: int, posY: int) -> tk.Toplevel:
        """Creates the popup Calendar.

        Args:
            i (str): Current time point.
            posX (int): The X Grid Position
            posY (int): The Y Grid Position

        Returns:
            tk.Toplevel: The created Calendar Toplevel
        """
        top = tk.Toplevel(self.mainframe)
        cal = Calendar(top, font="Arial 14", selectmode="day")

        def getDate(cal: Calendar):
            top.withdraw()
            self.calDate[i] = cal.selection_get()
            self.__createLabel(posX, posY, self.calDate[i])

        cal.pack(fill="both", expand=True)
        ttk.Button(top, text="ok", command=lambda: getDate(cal)).pack()

    def __setupMachines(self) -> tk.Toplevel:
        """Creates the form for Machine setup.

        Returns:
            tk.Toplevel: The created Form.
        """
        top = tk.Toplevel(self.mainframe)
        top.title("Add Machine")
        menubar = tk.Menu(top)
        tk.Label(top, text="Machine Name:").grid(row=0, column=0)
        nameEntry = tk.Entry(top)
        nameEntry.grid(row=0, column=1)

        tk.Label(top, text="CPH:").grid(row=1, column=0)
        cphEntry = tk.Entry(top)
        cphEntry.insert("end", "1")
        cphEntry.grid(row=1, column=1)

        tk.Label(top, text="Nozzle Heads:").grid(row=2, column=0)
        nozHeads = tk.Entry(top)
        nozHeads.insert("end", "1")
        nozHeads.grid(row=2, column=1)

        self.button_pressed = tk.StringVar()
        smdMachine = tk.BooleanVar()
        smdMachine.set(False)
        tk.Label(top, text="SMD Machine:").grid(row=3, column=0)

        # Offset entries
        tk.Label(top, text="Offsets").grid(row=4, column=0)
        tk.Label(top, text="X").grid(row=4, column=1)
        tk.Label(top, text="Y").grid(row=4, column=2)
        tk.Label(top, text="Checkpoint:").grid(row=5, column=0)
        checkpointX = tk.Entry(top)
        checkpointX.insert("end", "0")
        checkpointX.grid(row=5, column=1)
        checkpointY = tk.Entry(top)
        checkpointY.insert("end", "0")
        checkpointY.grid(row=5, column=2)

        tk.Label(top, text="PCB:").grid(row=6, column=0)
        pcbX = tk.Entry(top)
        pcbX.insert("end", "0")
        pcbX.grid(row=6, column=1)
        pcbY = tk.Entry(top)
        pcbY.insert("end", "0")
        pcbY.grid(row=6, column=2)

        tk.Label(top, text="Tool Pickup:").grid(row=7, column=0)
        toolX = tk.Entry(top)
        toolX.insert("end", "0")
        toolX.grid(row=7, column=1)
        toolY = tk.Entry(top)
        toolY.insert("end", "0")
        toolY.grid(row=7, column=2)

        # feedercart 1
        row1 = 8
        tk.Label(top, text="Feedercart Front Left:").grid(row=row1, column=0)
        feedercart_1x = tk.Entry(top)
        feedercart_1x.insert("end", "0")
        feedercart_1x.grid(row=row1, column=1)
        feedercart_1y = tk.Entry(top)
        feedercart_1y.insert("end", "0")
        feedercart_1y.grid(row=row1, column=2)
        # feedercart 2
        row2 = 9
        tk.Label(top, text="Feedercart Back Left:").grid(row=row2, column=0)
        feedercart_2x = tk.Entry(top)
        feedercart_2x.insert("end", "0")
        feedercart_2x.grid(row=row2, column=1)
        feedercart_2y = tk.Entry(top)
        feedercart_2y.insert("end", "0")
        feedercart_2y.grid(row=row2, column=2)
        # feedercart 3
        row3 = 10
        tk.Label(top, text="Feedercart Front Right:").grid(row=row3, column=0)
        feedercart_3x = tk.Entry(top)
        feedercart_3x.insert("end", "0")
        feedercart_3x.grid(row=row3, column=1)
        feedercart_3y = tk.Entry(top)
        feedercart_3y.insert("end", "0")
        feedercart_3y.grid(row=row3, column=2)
        # feedercart 4
        row4 = 11
        tk.Label(top, text="Feedercart Back Right:").grid(row=row4, column=0)
        feedercart_4x = tk.Entry(top)
        feedercart_4x.insert("end", "0")
        feedercart_4x.grid(row=row4, column=1)
        feedercart_4y = tk.Entry(top)
        feedercart_4y.insert("end", "0")
        feedercart_4y.grid(row=row4, column=2)

        machineType = tk.Checkbutton(top, var=smdMachine)
        machineType.grid(row=3, column=1)

        def clearMachine():
            nameEntry.delete(0, "end")
            cphEntry.delete(0, "end")
            nozHeads.delete(0, "end")

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
                    "tools": [int(toolX.get()), int(toolY.get())],
                    "feedercarts": [
                        {"ST-FL": [int(feedercart_1x.get()), int(feedercart_1y.get())]},
                        {"ST-RL": [int(feedercart_2x.get()), int(feedercart_2y.get())]},
                        {"ST-FR": [feedercart_3x.get(), feedercart_3y.get()]},
                        {"ST-RR": [feedercart_4x.get(), feedercart_4y.get()]},
                    ],
                }
                self.machines[name] = Machine(
                    name, cph, noz, smdMachine.get(), offsets=args
                )
                close()
            except Exception as e:
                tk.Label(
                    top, text="Please only use Numbers for CPH and Nozzle Heads"
                ).grid(row=51, column=1)

        def load():
            self.machines.clear()
            data = self.__openNew()
            if data == None:
                return
            for i in data["machines"]:
                self.machines[i["machine"]] = Machine(
                    i["machine"], i["cph"], i["nozHeads"], i["SMD"], i["offsets"]
                )
            close()

        def nextMachine():
            confirm()
            self.__setupMachines()

        fileMenu = {"New": clearMachine, "Load": load, "Exit": close}
        self.conButton = ttk.Button(top, text="OK", command=confirm)
        self.conButton.grid(row=50, column=0)
        nextButton = ttk.Button(top, text="Add another", command=nextMachine)
        nextButton.grid(row=50, column=1)
        self.__createMenu(menubar, "File", fileMenu)
        top.config(menu=menubar)

    def __viewMachines(self) -> tk.Toplevel:
        """Creates the window to view the loaded machines.

        Returns:
            tk.Toplevel: The created Window.
        """
        top = tk.Toplevel(self.mainframe)
        top.geometry("300x200")
        top.title("Machines")
        menubar = tk.Menu(top)
        scrollbar = tk.Scrollbar(top)
        scrollbar.pack(side="right", fill="y")
        mylist = tk.Listbox(top, yscrollcommand=scrollbar.set)

        def createEntry(machine: Machine):
            mylist.insert("end", f"Machine: {machine.machineName} ")
            mylist.insert("end", f"CPH: {machine.cph} ")
            mylist.insert("end", f"Velocity: {machine.velocity} ")
            mylist.insert("end", f"Nozzle Heads: {machine.nozHeads} ")
            mylist.insert("end", f"Offsets: {machine.offsets} ")
            mylist.insert("end", f"-------------")

        for key in self.machines:
            createEntry(self.machines[key])
        mylist.pack(side="top", fill="both")
        scrollbar.config(command=mylist.yview)

        def close():
            top.withdraw()

        def clearMachines():
            close()
            self.machines.clear()

        def save():
            machines = []
            for key in self.machines:
                machines.append(self.machines[key].getData())

            data = {"machines": machines}
            self.__saveAs(data)

        def load():
            self.machines.clear()
            data = self.__openNew()
            if data == None:
                return
            for i in data["machines"]:
                self.machines[i["machine"]] = Machine(
                    i["machine"], i["cph"], i["nozHeads"], i["SMD"], i["offsets"]
                )
            close()
            self.__viewMachines()

        fileMenu = {"Clear": clearMachines, "Save": save, "Load": load, "Exit": close}
        self.__createMenu(menubar, "File", fileMenu)
        top.config(menu=menubar)
        ttk.Button(top, text="ok", command=close).pack()

    def __setOptions(self) -> tk.Toplevel:
        """Creates window for option management.

        Returns:
            tk.Toplevel: The created window.
        """
        top = tk.Toplevel(self.mainframe)
        top.geometry("300x150")
        top.title("Options")

        def callback():
            max = randominterruptmax.get()
            min = randominterruptmin.get()
            address = networkAddress.get()
            if min > max:
                return tk.Label(
                    top,
                    text="The maximum interrupt value needs to be higher then the minimum!",
                    foreground="red",
                    wraplengt=200,
                ).pack()
            self.config.set("default", "randominterruptmax", str(max))
            self.config.set("default", "randominterruptmin", str(min))
            self.config.set("network", "api_address", str(address))
            top.withdraw()
            return True

        tk.Label(top, text="Random Interruptions Max").pack()
        randominterruptmax = tk.IntVar()
        randominterruptmax.set(self.config.getint("default", "randominterruptmax"))
        tk.Entry(top, textvariable=randominterruptmax).pack()
        tk.Label(top, text="Random Interruptions Min").pack()
        randominterruptmin = tk.IntVar()
        randominterruptmin.set(self.config.getint("default", "randominterruptmin"))
        tk.Entry(top, textvariable=randominterruptmin).pack()
        tk.Label(top, text="API Network Address").pack()
        networkAddress = tk.StringVar()
        networkAddress.set(self.config.get("network", "api_address"))
        tk.Entry(top, textvariable=networkAddress).pack()

        ttk.Button(top, text="OK", command=callback).pack()

    def __new(self) -> None:
        """Clears all entries."""
        self.numManu.delete(0, "end")

    def __saveAs(self, data: dict) -> None:
        """Save the privided Data to `.json`.

        Args:
            data (dict): The data to save.
        """
        file_opt = options = {}
        options["filetypes"] = [("JSON files", ".json"), ("all files", ".*")]
        options["initialdir"] = os.getcwd() + os.path.normpath("/data/presets")

        filename = filedialog.asksaveasfile(defaultextension=".json", **file_opt)
        if filename is None:
            return

        json.dump(data, filename)

    def __openNew(self) -> (None | dict):
        """Opens an interface for file loading.

        Returns:
            Dict: The loaded `.json` file.
            None: If no file is selected.
        """
        file_opt = options = {}
        options["filetypes"] = [("JSON files", ".json"), ("all files", ".*")]
        options["initialdir"] = os.getcwd() + os.path.normpath("/data/presets")
        filename = filedialog.askopenfilename(**file_opt)
        if filename == None or filename == "":
            return
        with open(filename) as file:
            data = json.load(file)

        return data

    def __compare(self) -> None:
        """Dummy operation for now."""
        # startDate = str(self.calDate["start"])
        # endDate = str(self.calDate["end"])

        request = requests.get(
            f"{self.config.get('network', 'api_address')}/data/options"
        )
        controller = Controller(self.mainframe)
        controller.error(request.status_code)
        print(request.json())

    def __startSimulation(self, *args: any, **kwargs: any):
        """Starts simulation in a new Thread."""
        threading.Thread(target=self.__simulate).start()

    def __startCompare(self, *args: any, **kwargs: any):
        """Starts Compare function in a new Thread."""
        threading.Thread(target=self.__compare).start()

    def __simulate(self) -> None:
        """Simulate the manufacturing environment."""
        machineTime = {}
        setupTime = {}
        coords = {}
        product_id = self.product.get()
        controller = Controller(self.mainframe)
        controller.wait()
        randomInterrupt = (
            (0, 0)
            if self.randomInterupt.get() == False
            else (
                self.config.getint("default", "randominterruptmin"),
                self.config.getint("default", "randominterruptmax"),
            )
        )
        # return
        if len(self.machines) == 0:
            return controller.error(
                "Please load or create a machine configuration first!"
            )
        for i in self.machines:
            machine: Machine = self.machines[i]
            data = machine.getData()
            manufacturingType = "manufacturing"

            params = {
                "productId": product_id,
                "machine": machine.machineName,
                "randomInterMin": randomInterrupt[0],
                "randomInterMax": randomInterrupt[1],
                "useIdealState": self.useIdealState.get(),
            }
            requestData = self.requests.get("/simulate/setup/", params)

            if type(requestData) == tuple:
                return controller.error(requestData[1])

            setupTime[machine.machineName] = requestData["time"]

            if self.useAISim.get():
                manufacturingType = "AI"

            if self.machines[i].SMD == False:
                manufacturingType = "coating"

            request = self.requests.put(f"/simulate/{manufacturingType}/", params, data)

            if type(request) == tuple:
                return controller.error(request[1])

            if request.status_code != 200:
                error = f"{request.status_code} - {request.reason} "
                return controller.error(error)
            requestData = request.json()
            machineTime[self.machines[i].machineName] = requestData["time"]
            if "plot_x" in requestData:
                coords[self.machines[i].machineName] = {
                    "X": requestData["plot_x"],
                    "Y": requestData["plot_y"],
                }

        controller(
            coords=coords,
            mTime=machineTime,
            sTime=setupTime,
            numParts=int(self.numManu.get()),
            randomInterupt=randomInterrupt,
            prodName=product_id,
        )


if __name__ == "__main__":
    Interface()()
