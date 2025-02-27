from zope.interface import Interface

class PathFinder(Interface):
    def _load_map(self):
        """Load elevation map and retrieve all required objects"""
        pass
    
    def find_path(self, start, goal):
        """Find a valid path from start to goal in long/lat"""
        pass
    
    def get_neighbors(x,y):
        """Get neighboring cells in a grid"""
        pass
    
    def get_cost(x1,y1,x2,y2):
        """Calculate movement cost between two points"""
        pass