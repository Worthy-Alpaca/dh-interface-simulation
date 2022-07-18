import sys
import os
import math
PACKAGE_PARENT = '../..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from pathlib import Path




class Machine:
    """ Class that represents a machine """
    def __init__(self, name: str, cph: int, nozHeads: int, machineType: str, offsets: dict = None) -> None:
        self.machineName = name
        self.cph = cph
        self.nozHeads = nozHeads
        self.SMD = machineType
        cps = 3600 / cph
        self.velocity = math.sqrt(180**2 + 180**2) / cps
        #if offsets is not None:
        self.offsets = offsets

    def getData(self) -> dict:
        return {
            'machine': self.machineName,
            'cph': self.cph,
            'nozHeads': self.nozHeads,
            'SMD': self.SMD,
            'offsets': self.offsets
        }


if __name__ == '__main__':
    from modules.simulation.dataloader import DataLoader
    path = Path(os.getcwd() + os.path.normpath('/data/3011330'))
    dataloader = DataLoader(path)
    data = dataloader()
    for i in data[1]['Nozzle_No'].unique():
        print(i)