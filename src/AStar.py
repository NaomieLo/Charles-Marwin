import heapq
import os
import transformations
from PathFinderBase import PathFinderBase

class AStar(PathFinderBase):
    def __init__(self, test_mode, test_map=None):
        super().__init__(test_mode,test_map=test_map)
        
    def find_path(self, start, goal):
        
        start_row,start_col,end_row,end_col = self.GeoCoord2RowCol(start,goal)
        #print(f"Start: ({start_row}, {start_col}) Goal: ({end_row}, {end_col})")

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
            neighbors = self.get_neighbors(cur_y, cur_x)
            #check neighbors
            for neighbor in neighbors:
                neighbor_x, neighbor_y = neighbor
                
                tentative_g_score = g_score[curr] + self.get_cost(cur_y, cur_x, neighbor[1], neighbor[0])
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    path_history[neighbor] = curr
                    g_score[neighbor] = tentative_g_score  
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor_x, neighbor_y, end_row, end_col)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None  # No path found