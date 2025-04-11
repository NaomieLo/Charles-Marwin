import cv2
import numpy as np
import copy
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
        start_row, start_col = start
        goal_row, goal_col = goal
        #print("Before shrink",goal)
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
            #print("In loop",scaled_path[-1])
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

        # If the refined path's final node doesn't match the specified goal,
        # refine the last segment using full-resolution A*
        if coarse_path[-1] != goal:
            if len(coarse_path) >= 1:
                # Compute a final segment from the second to last point to the actual goal
                final_segment = self.bidirectional_astar.find_path(coarse_path[-1], goal,call_from_gaussian=True)
                if final_segment is not None:
                    # Append the final segment, skipping the duplicate node
                    coarse_path = coarse_path[:-1] + final_segment
                else:
                    # Can't reach goal
                    coarse_path=None
            else:
                coarse_path=None

        if coarse_path[0] != start:
            final_segment = self.bidirectional_astar.find_path(start, coarse_path[0], call_from_gaussian=True)
            if final_segment is not None:
                # Avoid duplicating the first node of coarse_path if it's already the last node of final_segment.
                if final_segment[-1] == coarse_path[0]:
                    coarse_path = final_segment[:-1] + coarse_path
                else:
                    coarse_path = final_segment + coarse_path
            else:
                coarse_path = None

        return coarse_path