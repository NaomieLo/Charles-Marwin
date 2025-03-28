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
        self.Brain = None
        if (brain == "A*"):
            self.Brain = AStar(None)
        elif (brain == "Bidirectional A*"):
            self.Brain = BidirectionalAStar(None)
        elif (brain == "Multiresolution Pathfinder"):
            self.Brain = MultiResolutionPathFinder(None)

        elevation_map, affine_transform = self._load_map()
        self.Sensor = Sensor(elevation_map,affine_transform)
        self.Path = []
        self.Motor = Motors(None, None)
        self.initPosition = (0,0)
        self.endPosition = (0,0)
        self.curr_idx=0

    def _load_map(self):
        """Load the elevation map from a predefined file path."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(base_dir)
        dem_path = os.path.join(parent_dir, 'data/MarsMGSMOLA_MAP2_EQUI.tif')
        
        with rasterio.open(dem_path) as data:
            elevation_map = data.read(1)
            crs = data.crs
            affine_transform = data.transform
            self.affine_transform = affine_transform
            self.transform=transformations.setup_transformer(crs)
        return elevation_map, affine_transform
        
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
        if not self.path and self.curr_idx+1<len(self.path):
            next_pos = self.path[self.curr_idx+1]
            return next_pos
        raise Exceptions.NoNextNode("There is no next node")


        
    

