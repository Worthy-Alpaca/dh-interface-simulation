from modules.cartsetup import CartSetup
from modules.dataloader import DataLoader
from modules.manufacturing import Manufacturing
from pathlib import Path
import sys 
import os
import pandas as pd



if __name__ == '__main__':
    path = Path(os.getcwd() + os.path.normpath('/data/26AAWAB'))
    dataloader = DataLoader(path)
    manufacturing = Manufacturing(dataloader(), machine='M20')

    time = 0
    amount = 10
    for i in range(amount):
        runtime = manufacturing(multiPickOption=True, plotPCB=True) 
        time = (runtime) + time
        print(f"run: {i}    | time: {runtime}")
    
    print("average: ", time / amount, "sec")
    print("total time:", time, "sec")