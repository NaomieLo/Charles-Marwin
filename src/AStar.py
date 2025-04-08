import heapq
import os
import transformations
import time
from PathFinderBase import PathFinderBase

class AStar(PathFinderBase):
    def __init__(self, test_mode, test_map=None):
        super().__init__(test_mode,test_map=test_map)
        
    def find_path(self, start, goal, max_iterations=None):
        """
        Find a path between start and goal with optional iteration limit
        
        Args:
        start (tuple): Starting coordinates (row, col)
        goal (tuple): Goal coordinates (row, col)
        max_iterations (int, optional): Maximum number of iterations to prevent infinite loops
        
        Returns:
        list: Path from start to goal, or None if no path found
        """
        start_row, start_col, end_row, end_col = start, goal
        #print("start row,col= ",(start_row,start_col))
        def heuristic(x1, y1, x2, y2):
            return ((x1-x2)**2 + (y1-y2)**2)**0.5

        open_set = []
        heapq.heappush(open_set, (0, (start_row, start_col)))
        
        g_score = {(start_row, start_col): 0}
        f_score = {(start_row, start_col): heuristic(start_row, start_col, end_row, end_col)}
        
        path_history = {}
        
        # Track iterations
        iterations = 0
        start_time=time.time()
        while open_set:
            # Check iteration limit if specified
            if max_iterations is not None:
                iterations += 1
                if iterations > max_iterations:
                    return None
            
            _, curr = heapq.heappop(open_set)
            
            if curr == (end_row, end_col):
                return self._reconstruct_path(path_history, curr)
            
            cur_x, cur_y = curr
            neighbors = self.get_neighbors(cur_y, cur_x)
            
            for neighbor in neighbors:
                neighbor_x, neighbor_y = neighbor
                
                tentative_g_score = g_score[curr] + self.get_cost(cur_y, cur_x, neighbor[1], neighbor[0])
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    path_history[neighbor] = curr
                    g_score[neighbor] = tentative_g_score  
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor_x, neighbor_y, end_row, end_col)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
            
            end_time=time.time()
            time_elapsed=end_time-start_time
            if time_elapsed >= 50.0:
                return self._reconstruct_path(path_history, curr)#partial path
        
        return None  # No path found
    
    def __str__(self):
        return "AStar Brain"