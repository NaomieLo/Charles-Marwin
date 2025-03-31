import PathFinder
from AStar import AStar
from BidirectionalAStar import BidirectionalAStar
from MultiResolutionPathFinder import MultiResolutionPathFinder
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
    - initPosition (tuple): Initial spawn coordinates
    - endPosition (tuple): Destination in the path traversal
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

        self.Path = []
        self.initPosition = (0,0)
        self.endPosition = (0,0)


        
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
    

    def set_positions(self, start, end):
        """Validate selected positions in spawn screen before setting them"""
        if not isinstance(start, tuple) or not isinstance(end, tuple):
            raise ValueError("Position must be tuple")
        if len(start) != 2 or len(end) != 2:
            raise ValueError("Postitions must be (x, y)")

        self.initPosition = start
        self.endPosition = end

        if self.Brain: # if algorithm is already set
            self.Path = self.Brain.find_path(start, end)
    
    


        
    

