import PathFinder
from AStar import AStar
from BidirectionalAStar import BidirectionalAStar
from MultiResolutionPathFinder import MultiResolutionPathFinder
#from PathFinderBase import get_cost


class Robot:
    
    
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
    
if __name__ == "__main__":
    r = Robot("Crash", "A*")
    r.Path = [(80,80),(81,80),(82,80),(82,81)]
    print(r.Name)
    print(r.Brain)
    print(r.compute_path_cost())

        
    

