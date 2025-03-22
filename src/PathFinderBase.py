import zope.interface
import os
import rasterio
import transformations
from PathFinder import PathFinder
from sensors import Sensor
from motors import Motors

@zope.interface.implementer(PathFinder)
class PathFinderBase:
    """A base class providing default implementations for pathfinding algorithms"""
    def __init__(self, test_mode, test_map=None):
        # Load the map once during initialization
        
        if not test_mode:
            self.test_mode = test_mode
            elevation_map, transformer, affine_transform = self._load_map()
            self.elevation_map = elevation_map
            self.reverse_transformer = transformer
            self.sensor = Sensor(elevation_map, affine_transform)
            
        else:
            self.test_mode = test_mode
            self.elevation_map = test_map
            self.reverse_transformer = None
            self.sensor = Sensor(test_map, None)
            self.affine_transform = None
            
            
    
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
        reverse_transformer = transformations.setup_reverse_transformer(crs)
        return elevation_map, reverse_transformer, affine_transform
    
    def _reconstruct_path(self, hist, curr):
        path = [curr]
        while curr in hist:
            curr = hist[curr]
            path.append(curr)
        return path[::-1]  # More efficient than reverse()
    
    def get_neighbors(self,r,c):
        return self.sensor.get_neighbors(r,c)
    
    def get_cost(self,x1,y1,x2,y2):
        return self.sensor.get_cost(x1,y1,x2,y2)
    
    def RowCol2GeoCoord(self,start,goal):
        start_row,start_col=start
        end_row,end_col=goal
        
        start_x,start_y=transformations.rowcol_to_xy(start_row,start_col,self.affine_transform)
        end_x,end_y=transformations.rowcol_to_xy(end_row,end_col,self.affine_transform)
        start_lat,start_long=transformations.xy_to_latlong(start_x,start_y,self.transform)
        end_lat,end_long=transformations.xy_to_latlong(end_x,end_y,self.transform)
        return (start_lat,start_long),(end_lat,end_long)
    
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
    
    
    
    def find_path(self, start, goal,max_iterations=None):
        """Provide a fallback implementation that can be overridden"""
        raise NotImplementedError("Subclasses must implement find_path method")
        return None