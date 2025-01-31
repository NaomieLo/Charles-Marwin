import heapq
import os
import rasterio
import transformations
from PathFinderBase import PathFinderBase

class AStar(PathFinderBase):
    def __init__(self, test_mode, test_map=None):
        super().__init__(test_mode,test_map=test_map)
        
    def find_path(self, start, goal):
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
        
        #heuristic function for A* cost calculation
        def heuristic(x1, y1, x2, y2):
            #fundamentally a distance cost
            return ((x1-x2)**2 + (y1-y2)**2)**0.5

        open_set = []
        heapq.heappush(open_set, (0, (start_row, start_col)))
        
        g_score = {(start_row, start_col): 0}#elevation cost
        f_score = {(start_row, start_col): heuristic(start_row, start_col, end_row, end_col)}#heuristic cost
        
        path_history = {}
        #A* finding a path
        while open_set:
            _, curr = heapq.heappop(open_set)
            
            if curr == (end_row, end_col):
                return self._reconstruct_path(path_history, curr)
            
            cur_x, cur_y = curr
            neighbors = self.get_neighbors(cur_x, cur_y)
            #check neighbors
            for neighbor in neighbors:
                neighbor_x, neighbor_y = neighbor
                
                tentative_g_score = g_score[curr] + self.get_cost(cur_x, cur_y, neighbor_x, neighbor_y)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    path_history[neighbor] = curr
                    g_score[neighbor] = tentative_g_score  
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor_x, neighbor_y, end_row, end_col)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None  # No path found


