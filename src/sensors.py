import numpy as np 
import transformations

class Sensor:
    
    MIN_ELEVATION = -8200
    MAX_ELEVATION = 22000
    PASSABLE_ELEVATION = 100
    

    def __init__(self, elevation_map, affine_transform):
        self.elevation_map = elevation_map
        self.affine_transform = affine_transform


    def get_neighbors(self, r, c):
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (1,1), (-1,1), (-1,-1), (1,-1)]:
            nx, ny = r + dx, c + dy
            if 1 <= ny < self.elevation_map.shape[0] and 0 <= nx < self.elevation_map.shape[1]:
                neighbors.append((ny, nx))
        return neighbors
    

    # Make sure that elevation is within bounds
    def validate_elevation(self, elevation):
        if elevation < Sensor.MIN_ELEVATION:
            return Sensor.MIN_ELEVATION
        elif elevation > Sensor.MAX_ELEVATION:
            return Sensor.MAX_ELEVATION
        return elevation

    
    # Retrieves terrain height at the given coordinates
    def get_elevation_at_position(self, x, y):
        if 1 <= y < self.elevation_map.shape[0] and 0 <= x < self.elevation_map.shape[1]: # row ranges should start with 1
            elevation = self.elevation_map[y, x]

            if elevation == 0.0: # if invalid, handle error
                return self.estimate_missing_elevation(y, x)
            
            return self.validate_elevation(elevation)
        
        return None
            

    # Estimate invalid data (0.0) by taking mean of neighbors
    def estimate_missing_elevation(self, row, col):
        neighbors = self.get_neighbors(row, col)
        valid_elevations = [self.validate_elevation(self.elevation_map[nr, nc])
                            for nr, nc in neighbors
                            if self.elevation_map[nr, nc] != 0.0
                            ]
        if valid_elevations:
            return np.mean(valid_elevations)
    
        return 2100 # default elevation


    # check if movement between two neighbors is possible based on elevation
    def is_passable(self, x1, y1, x2, y2):
        elevation1 = self.get_elevation_at_position(x1, y1) # this was 
        elevation2 = self.get_elevation_at_position(x2, y2)

        if elevation1 is None or elevation2 is None:
            return False # out of bounds 

        return abs(elevation2-elevation1) <= Sensor.PASSABLE_ELEVATION
    

    # Uses logic that Yijun used to calculate movement cost between two neighboring coordinates
    def get_cost(self, x1, y1, x2, y2):
        curr = self.get_elevation_at_position(x1, y1)
        next = self.get_elevation_at_position(x2, y2)

        if self.is_passable(x1, y1, x2, y2):
            elevation_diff = abs(next - curr)
        else:
            return float('inf') # return infinite cost if any of the elevation are out of bounds
    
        diagonal = x1 != x2 and y1 != y2
        base_cost = 1.4142 if diagonal else 1.0 # √2 for diagonal movement
        
        battery_cost=0.0
        battery_weight = 1.0 #adjust this if you want to prioritize the battery cost
        if elevation_diff < 0:
            # Downhill: lower battery consumption (e.g., 0.5% cost)
            battery_cost= 0.5
        elif 0 <= elevation_diff <= 10:
            # Flat ground: moderate cost (e.g., 1% battery cost)
            battery_cost= 1.0
        elif 10 < elevation_diff <= 50:
            # Mild uphill: higher cost (e.g., 2.5% battery cost)
            battery_cost= 2.5
        elif 50 < elevation_diff <= 100:
            # Steep uphill: highest cost (e.g., 3% battery cost)
            battery_cost= 3.0
        else:
            # If the elevation change is extreme, make the cost prohibitive.
            battery_cost= float('inf')
        
        return base_cost + elevation_diff + battery_cost*battery_weight