import cv2
import numpy as np
import matplotlib.pyplot as plt
from PathFinderBase import PathFinderBase
from BidirectionalAStar import BidirectionalAStar

class MultiResolutionPathFinder(PathFinderBase):
    
    def __init__(self, test_mode, test_map=None):
        super().__init__(test_mode, test_map=test_map)
        
        # Check if we should use the Gaussian Pyramid
        self.use_pyramid = self.elevation_map.shape[0] > 100 or self.elevation_map.shape[1] > 100
        self.bidirectional_astar = BidirectionalAStar(test_mode, test_map=test_map)

        if self.use_pyramid:
            self.elevation_pyramid = self.gaussian_pyramid()
            
    def gaussian_pyramid(self, levels=4):
        """Create a Gaussian Pyramid if the map is large."""
        elevation_map = self.elevation_map.astype(np.float32)  # Convert to float32
        pyramid = [elevation_map]

        for _ in range(levels):
            elevation_map = cv2.pyrDown(elevation_map)  # Downsample
            pyramid.append(elevation_map)

        return pyramid  # Store all levels


    def find_path(self, start, goal):
        """Select pathfinding method based on map size."""
        if not self.use_pyramid:
            # Directly use Bidirectional A* for small maps
            return self.bidirectional_astar.find_path(start, goal)

        # Convert coordinates to row/col in full-resolution map
        start_row, start_col, goal_row, goal_col = self.GeoCoord2RowCol(start, goal)

        # Start at the lowest resolution (coarsest level)
        level = len(self.elevation_pyramid) - 1
        scaled_start = (start_row // (2 ** level), start_col // (2 ** level))
        scaled_goal = (goal_row // (2 ** level), goal_col // (2 ** level))
        if not self.test_mode:
            geo_start,geo_goal=self.RowCol2GeoCoord(scaled_start,scaled_goal)
        else:
            geo_start=scaled_start
            geo_goal=scaled_goal
        # Run Bidirectional A* at the coarse level
        path = self.bidirectional_astar.find_path(geo_start, geo_goal)

        # If no path is found at the lowest resolution, try at higher resolutions
        while path is None and level > 0:
            level -= 1  # Move to a finer resolution
            scaled_start = (start_row // (2 ** level), start_col // (2 ** level))
            scaled_goal = (goal_row // (2 ** level), goal_col // (2 ** level))
            if not self.test_mode:
                geo_start,geo_goal=self.RowCol2GeoCoord(scaled_start,scaled_goal)
            else:
                geo_start=scaled_start
                geo_goal=scaled_goal
            path = self.bidirectional_astar.find_path(scaled_start, scaled_goal)

        if path is None:
            print("Warning: No path found at any resolution!")
            return None  # Return None instead of causing an error

        # Refine the path at higher resolutions
        for level in range(level, len(self.elevation_pyramid) - 1):
            refined_path = [(r * 2, c * 2) for (r, c) in path]  # Scale back up
            if not self.test_mode:
                geo_start,geo_goal=self.RowCol2GeoCoord(refined_path[0],refined_path[-1])
            else:
                geo_start=refined_path[0]
                geo_goal=refined_path[-1]
            path = self.bidirectional_astar.find_path(refined_path[0], refined_path[-1])

            if path is None:  # Ensure we don't break on None again
                print("Warning: Refinement failed at resolution level", level)
                return refined_path  # Return the last valid path

        return path
