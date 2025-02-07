import zope.interface
import os
import rasterio
import transformations
from PathFinder import PathFinder

@zope.interface.implementer(PathFinder)
class PathFinderBase:
    """A base class providing default implementations for pathfinding algorithms"""
    def __init__(self, test_mode, test_map=None):
        # Load the map once during initialization
        if not test_mode:
            self.test_mode = test_mode
            elevation_map, transformer = self._load_map()
            self.elevation_map = elevation_map
            self.reverse_transformer = transformer
        else:
            self.test_mode = test_mode
            self.elevation_map = test_map
            self.reverse_transformer = None
            self.affine_transform = None
    
    def _load_map(self):
        """Default Implementation"""
        """Load the elevation map from a predefined file path."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(base_dir)
        dem_path = os.path.join(parent_dir, 'data/MarsMGSMOLA_MAP2_EQUI.tif')
        
        with rasterio.open(dem_path) as data:
            elevation_map = data.read(1)
            crs = data.crs
            affine_transform = data.transform
            self.affine_transform = affine_transform 
        reverse_transformer = transformations.setup_reverse_transformer(crs)
        return elevation_map, reverse_transformer
    
    def _reconstruct_path(self, hist, curr):
        path = [curr]
        while curr in hist:
            curr = hist[curr]
            path.append(curr)
        return path[::-1]  # More efficient than reverse()
    
    def get_neighbors(self,r,c):
        """Default implementation"""
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (1,1), (-1,1), (-1,-1), (1,-1)]:
            nx, ny = r + dx, c + dy
            if 0 <= ny < self.elevation_map.shape[0] and 0 <= nx < self.elevation_map.shape[1]:
                if self.elevation_map[ny,nx]<=21000 and self.elevation_map[ny,nx]>=-8000:#range validation
                    neighbors.append((ny, nx))
        #print(f"Current Node: ({r}, {c})")
        #print(f"Neighbors: {neighbors}")

        return neighbors
    
    def get_cost(self,x1,y1,x2,y2):
        """Default Implementation"""
        curr = self.elevation_map[x1,y1]
        next = self.elevation_map[x2,y2]
        
        #valid elevation check (no 0.0)
        if curr == 0 and isinstance(curr,float):
            #invalid number
            neighbors = self.get_neighbors(y1,x1)
            #calculate mean values of neighbors and put it back into curr
            valid_elevations = [self.elevation_map[ny,nx] for nx,ny in neighbors]
            curr = int(sum(valid_elevations)/len(valid_elevations))
        if next == 0 and isinstance(curr,float):
            #invalid number
            neighbors = self.get_neighbors(y2,x2)
            #calculate mean values of neighbors and put it back into curr
            valid_elevations = [self.elevation_map[ny,nx] for nx,ny in neighbors]
            next = int(sum(valid_elevations)/len(valid_elevations))
            
        elevation_diff = abs(next - curr)
        # Add base movement cost (distance)
        diagonal = x1 != x2 and y1 != y2
        base_cost = 1.4142 if diagonal else 1.0  # √2 for diagonal movement
        return base_cost + elevation_diff
    
    def GeoCoord2RowCol(self,start,goal):
        #convert lat/long to row/col
        if self.test_mode:
            start_row, start_col = start
            end_row, end_col = goal
        else:
            start_lat, start_long = start
            goal_lat, goal_long = goal
            
            start_x, start_y = transformations.latlong_to_xy(start_lat, start_long, self.reverse_transformer)
            end_x, end_y = transformations.latlong_to_xy(goal_lat, goal_long, self.reverse_transformer)

            start_row, start_col = transformations.xy_to_rowcol(start_x, start_y, ~self.affine_transform)
            end_row, end_col = transformations.xy_to_rowcol(end_x, end_y, ~self.affine_transform)
        return start_row,start_col,end_row,end_col
    
    def find_path(self, start, goal):
        """No default Implementation"""
        raise Exception("This class is not intended to find any path")
        return None