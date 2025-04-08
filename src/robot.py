import PathFinder
import Exceptions
import os
import rasterio
import transformations
from AStar import AStar
from BidirectionalAStar import BidirectionalAStar
from MultiResolutionPathFinder import MultiResolutionPathFinder
from motors import Motors
from sensors import Sensor

#from PathFinderBase import get_cost


class Robot:
    '''
    Represents the back end of the robot, storing 
    the necessary information for the correct functioning
    of the application and the processing of new entries for
    the database.

    Fields:
    - Name (str): Name of the robot
    - Brain (PathFinder): Aggregation of a Pathfinding Algorithm
    - Path (list): Computed path
    - Motor (Motot): Aggreagation of Motors
    - Sensor (sensors): Aggregation of sensors
    - initPosition (tuple): Initial spawn coordinates
    - endPosition (tuple): Destination in the path traversal
    - curr_dix (int): store the index of the current position in Path
    '''
    
    
    def __init__(self, name:str, brain:str):
        self.Name = name
        self.Mesh = ""
        if (name == "Perseverance"):
            self.Mesh = "src/models/perseverance/ImageToStl.com_25042_perseverance.obj" 
        elif (name == "Curiosity"):
            self.Mesh = "src/models/curiosity/24584_Curiosity_static.obj"
        elif (name == "Spirit"):
            self.Mesh = "src/models/spirit/24883_MER_static.obj"

        self.Brain = None
        if (brain == "A*"):
            self.Brain = AStar(None)
        elif (brain == "Bidirectional A*"):
            self.Brain = BidirectionalAStar(None)
        elif (brain == "Multiresolution Pathfinder"):
            self.Brain = MultiResolutionPathFinder(None)

        self.Sensor = None
        self.Path = []
        self.Motor = Motors(None, None)
        self.initPosition = (0,0)
        self.endPosition = (0,0)
        self.curr_idx=0

        
    def compute_path_cost(self) -> int:
        i = 0
        j = 1
        cost = 0
        path = self.Path

        while (j < len(path)):
            cost += self.Brain.get_cost(path[i][0], path[i][1], path[j][0], path[j][1])
            i += 1
            j += 1

        return cost
    
    
    

    
    def get_next_pos_in_path(self):
        if not self.Path and self.curr_idx+1<len(self.path):
            next_pos = self.Path[self.curr_idx+1]
            return next_pos
        raise Exceptions.NoNextNode("There is no next node")


        
    

