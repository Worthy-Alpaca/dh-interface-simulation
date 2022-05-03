from modules.simulation.cartsetup import CartSetup
from modules.simulation.dataloader import DataLoader
from modules.simulation.manufacturing import Manufacturing
from pathlib import Path
import matplotlib.pyplot as plt
import sys 
import os
import pandas as pd



if __name__ == '__main__':
    path = Path(os.getcwd() + os.path.normpath('/data/26AAWAB'))
    dataloader = DataLoader(path)
    manufacturing = Manufacturing(dataloader(), machine='M20')

    time = 0
    amount = 1
    for i in range(amount):
        runtime = manufacturing(multiPickOption=True, plotPCB=True) 
        if type(runtime) == int:
            time = (runtime) + time
            print(f"run: {i}    | time: {runtime}")
        else:
            time = (runtime['time']) + time
            print(f"run: {i}    | time: {runtime['time']}")
    
    print("average: ", time / amount, "sec")
    print("total time:", time, "sec")
    if type(runtime) == dict:
        plt.scatter(runtime['plot_x'], runtime['plot_y'])
        plt.show()