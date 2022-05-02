import math
import random
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
from pathlib import Path
from modules.cartsetup import CartSetup
from modules.dataloader import DataLoader
global XMOD 
XMOD = 1
RANDOM_PROBLEMS = (0,0)#(30, 300)
OFFSET_X = 0
OFFSET_Y = 0
DROPOFF = 0.1
PICKUP = 0.1
CHECKPOINT = (30.0, -4.0)


class Manufacturing():
  """ 
  Simulates the manufacturing process in SMD machines M10 and M20 
  - `machine`: either M10 (default) or M20
  
  """
  def __init__(self, data: tuple, machine: str = 'M10') -> object:
    # assign machine property
    self.machine = machine
    self.components = data[1]
    self.data = data[0]
    self.offsets = data[2]

  def calcVector(self, vectorA: tuple, vectorB: tuple, velocity: float):
    """
    Calculates the pathlength between two given vectors
    - vectorA: where you are
    - vectorB: where you want to go 
    """
    #print('Type: ', type(vectorA[0]), type(vectorA[1]), type(vectorB[0]), type(vectorB[1]))
    #print('Vector teile: ',(vectorB[0]), (vectorA[0]), (vectorB[1]), (vectorA[1]))
    #print()
    #print((float(vectorB[0]) - float(vectorA[0])), (float(vectorB[1]) - float(vectorA[1])))
    #print('===')
    vector_AB = ((float(vectorB[0]) - float(vectorA[0])), (float(vectorB[1]) - float(vectorA[1])))
    path_length = math.sqrt(vector_AB[0]**2 + vector_AB[1]**2)
    #print('path length:', path_length)
    return path_length / velocity

  def __call__(self, multiPickOption: bool = True, plotPCB: bool = False, *args: any, **kwds: any) -> int:
    """ Start the assembly simulation """

    def isNan(string):
      return string != string

    # the estimated velocity of the machine arm
    # M20 = 1345.87 mm/s | M10 = 1621.4 mm/s
    machine = self.machine
    
    #print(self.components)
    TIME = 0
    plotting_x = []
    plotting_y = []
    multiPick = deque()
    print('Calculating assembly time')
    for offset_index, offset_row in self.offsets.iterrows():
      for index, row in self.data.iterrows():
        # check for NaN values and continue if found
        if isNan(row.Code):
          print(row.Code)
          continue

        # calculating the path, adding offset for coordinate transformation
        lookupTable = self.components[self.components['index'].str.match(row.Code)]
        #print(lookupTable)
        location_vector_A = (lookupTable.Pickup_X, lookupTable.Pickup_Y)
        location_vector_B = ((row.X + OFFSET_X + offset_row.X), (row.Y + OFFSET_Y + offset_row.Y))
        #print(lookupTable)
        velocity = 1345.87 if str(machine) == "M20" else 1621.4
        velocity = velocity * ( lookupTable.mean_acceleration.max() / 1000)
        #velocity = velocity.max()
        
        if multiPickOption == True:
          # picking components with multiple heads at once
          # path changes from "Pickup -> Component" to "Pickup1 -> Pickup2 -> Pickup3 -> Component3 -> Component2 -> Component1" 
          if row.Task == 'Multiple Pickup':
            # append component vector to queue
            multiPick.append(location_vector_B)

            # calculate path/time to next pickup
            next_index = index +1
            while next_index not in self.data.index:
              if next_index >= self.data.index.max():
                next_index = next_index - 1
                break
              next_index = next_index +1
            nextLookUpTable = self.components[self.components['index'].str.match( self.data.loc[ next_index , 'Code'])]
            next_pickup = (nextLookUpTable.Pickup_X, nextLookUpTable.Pickup_Y)
            TIME = self.calcVector(location_vector_A, next_pickup, velocity) + TIME + PICKUP

          elif row.Task == 'End Multiple Pickup':
            # calculate the path to the current component
            loc_vector_A = (lookupTable.Pickup_X, lookupTable.Pickup_Y)
            loc_vector_B = ((row.X + OFFSET_X + offset_row.X), (row.Y + OFFSET_Y + offset_row.Y))
            checkpoint = self.calcVector(loc_vector_A, CHECKPOINT, velocity)
            path = self.calcVector(CHECKPOINT, loc_vector_B, velocity)
            TIME = path + TIME + DROPOFF + checkpoint

            # set the current component vector as the current postition
            current_pos = location_vector_B

            # rotate the queue
            multiPick.rotate()

            # loop over queue
            for i in multiPick:
              # calculate path and time between components
              multiPath = self.calcVector(current_pos, i, velocity)
              TIME = (multiPath) + TIME + DROPOFF
              current_pos = i
            multiPick.clear()

            # calculate the path/time to return to the next pickup point
            next_index = index +1
            while next_index not in self.data.index:
              if next_index >= self.data.index.max():
                next_index = next_index - 1
                break
              next_index = next_index +1
            nextLookUpTable = self.components[self.components['index'].str.match( self.data.loc[ next_index , 'Code']  )]
            next_pickup_vector = (nextLookUpTable.Pickup_X, nextLookUpTable.Pickup_Y)
            TIME = (self.calcVector(next_pickup_vector, current_pos, velocity)) + TIME + DROPOFF

          elif row.Task == 'Fiducial':
            path_length = self.calcVector((0, 0), location_vector_B, velocity)
            TIME = (path_length) + TIME 

          else:
            #print('==  single pick, multipick opt  ==')
            # calculate the path/time for a single pickup
            path_length = self.calcVector(location_vector_A, CHECKPOINT, velocity)
            checkpoint = self.calcVector(CHECKPOINT, location_vector_B, velocity)
            TIME = (path_length) + TIME + DROPOFF + checkpoint

            # calculate the path/time to return to the next pickup point
            next_index = index +1
            while next_index not in self.data.index:
              if next_index > self.data.index.max():
                next_index = next_index - 1
                break
              next_index = next_index +1
            nextLookUpTable = self.components[self.components['index'].str.match( self.data.loc[ next_index , 'Code']  )]
            next_pickup_vector = (nextLookUpTable.Pickup_X, nextLookUpTable.Pickup_Y)
            #print('it breaks here')
            #print(self.data.loc[ next_index , 'Code'])
            #print(self.components[self.components['index'].str.match( self.data.loc[ next_index , 'Code']  )])

            TIME = (self.calcVector(next_pickup_vector, location_vector_B, velocity) ) + TIME + DROPOFF + PICKUP

        elif row.Task == 'Fiducial':
            path_length = self.calcVector((0, 0), location_vector_B, velocity)
            TIME = (path_length) + TIME

        else:
          # all components get treated with single pick
          path_length = self.calcVector(location_vector_A, CHECKPOINT, velocity)
          checkpoint = self.calcVector(CHECKPOINT, location_vector_B, velocity)
          TIME = (path_length) + TIME + DROPOFF + checkpoint
          next_index = index + 1
          while next_index not in self.data.index:
            #next_index = next_index +1
            if next_index > self.data.index.max():
              next_index = next_index - 1
              break
            next_index = next_index +1
          nextLookUpTable = self.components[self.components['index'].str.match( self.data.loc[ next_index , 'Code']  )]
          next_pickup_vector = (nextLookUpTable.Pickup_X, nextLookUpTable.Pickup_Y)
          TIME = (self.calcVector(location_vector_B, next_pickup_vector, velocity)) + TIME + DROPOFF + PICKUP
        
        # saving coordinates for visual plotting
        plotting_x.append(location_vector_B[0])
        plotting_y.append(location_vector_B[1])
        #break
      #break

    # return the calculated time + a random time caused by problems
    # modify the result with XMOD to provide scaleability
    if plotPCB == True:
      fig1 = plt.figure()
      ax1 = fig1.add_subplot(111)
      #ax2 = fig2.add_subplot(111)
      #ax1.scatter(self.data['Y'], self.data['X'])
      ax1.scatter(plotting_x, plotting_y)
      plt.show()
    return (TIME + random.randint(0,30)) 
  
  def coating(self):
    """ simulates the time for coating a PCB """
    velocity = 20 # mm/s

    # highest coordinate on PCB
    high = self.data['Y'].max() + self.offsets['Y'].max()
    print(high)
    return (math.sqrt(0**2 + high**2) / velocity)


if __name__ == '__main__':
  path = Path('/data/26AAWAB')
  dataloader = DataLoader(path)