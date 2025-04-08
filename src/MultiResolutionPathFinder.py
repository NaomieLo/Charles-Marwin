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
            
    def gaussian_pyramid(self, levels=5):
        """Create a Gaussian Pyramid if the map is large."""
        elevation_map = self.elevation_map.astype(np.float32)  # Convert to float32
        pyramid = [elevation_map]

        for _ in range(levels):
            elevation_map = cv2.pyrDown(elevation_map)  # Downsample
            pyramid.append(elevation_map)

        return pyramid

    def connect_points_at_level(self, start_point, end_point, call_from_gaussian=True):
        """Find a path between two points at the current resolution level."""
        return self.bidirectional_astar.find_path(start_point, end_point, call_from_gaussian=True)

    def find_path(self, start, goal):
        """Select pathfinding method based on map size."""
        # For small maps, directly use Bidirectional A*
        if not self.use_pyramid:
            return self.bidirectional_astar.find_path(start, goal)

        # Convert coordinates to row/col in full-resolution map
        start_row, start_col, goal_row, goal_col = start, goal
        #print("start row,col= ", (start_row, start_col))
        #print("end row,col= ", (goal_row, goal_col))
        # Start at the lowest resolution (coarsest level)
        level = len(self.elevation_pyramid) - 1
        
        # Find initial path at coarsest level
        scaled_start = (start_row // (2 ** level), start_col // (2 ** level))
        scaled_goal = (goal_row // (2 ** level), goal_col // (2 ** level))
        coarse_path = self.bidirectional_astar.find_path(scaled_start, scaled_goal, call_from_gaussian=True)

        if coarse_path is None:
            print("Warning: Could not find path at coarsest level!")
            return None

        # Refine path through each level
        while level > 0:
            # Scale up the coarse path points to next finer level
            scaled_path = [(r * 2, c * 2) for r, c in coarse_path]
            
            # Move to next finer level
            level -= 1
            
            # Connect segments at current level
            fine_path = []
            for i in range(len(scaled_path) - 1):
                start_point = scaled_path[i]
                end_point = scaled_path[i + 1]
                
                # Find path between consecutive points
                segment = self.connect_points_at_level(start_point, end_point)
                
                if segment is None:
                    print(f"Warning: Failed to connect points at level {level}")
                    # If connection fails, use direct line between points
                    segment = [start_point, end_point]
                
                # Add segment to fine path (avoid duplicating points)
                if i == 0:
                    fine_path.extend(segment)
                else:
                    fine_path.extend(segment[1:])  # Skip first point as it's same as last point of previous segment
            
            coarse_path = fine_path

        return coarse_path