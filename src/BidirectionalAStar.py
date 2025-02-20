import heapq
from PathFinderBase import PathFinderBase

class BidirectionalAStar(PathFinderBase):
    def __init__(self, test_mode, test_map=None):
        super().__init__(test_mode, test_map=test_map)

    def _init_search(self):
        # Initialize data structures for both forward and backward searches
        return {
            'open_set': [],
            'g_score': {},
            'f_score': {},
            'path_history': {}
        }

    def heuristic(self, x1, y1, x2, y2):
        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def find_path(self, start, goal,max_iterations=None):
        start_row, start_col, end_row, end_col = self.GeoCoord2RowCol(start, goal)
        
        # Initialize forward and backward searches
        forward = self._init_search()
        backward = self._init_search()
        
        # Initialize start node (forward search)
        heapq.heappush(forward['open_set'], (0, (start_row, start_col)))
        forward['g_score'][(start_row, start_col)] = 0
        forward['f_score'][(start_row, start_col)] = self.heuristic(start_row, start_col, end_row, end_col)
        
        # Initialize goal node (backward search)
        heapq.heappush(backward['open_set'], (0, (end_row, end_col)))
        backward['g_score'][(end_row, end_col)] = 0
        backward['f_score'][(end_row, end_col)] = self.heuristic(end_row, end_col, start_row, start_col)
        
        # Best path cost found so far
        best_path_cost = float('inf')
        meeting_point = None
        
        while forward['open_set'] and backward['open_set']:
            # Process forward search
            if forward['open_set']:
                meeting_node = self._process_node(
                    forward, backward,
                    (end_row, end_col),
                    'forward',
                    best_path_cost
                )
                if meeting_node:
                    new_path_cost = forward['g_score'][meeting_node] + backward['g_score'][meeting_node]
                    if new_path_cost < best_path_cost:
                        best_path_cost = new_path_cost
                        meeting_point = meeting_node
            
            # Process backward search
            if backward['open_set']:
                meeting_node = self._process_node(
                    backward, forward,
                    (start_row, start_col),
                    'backward',
                    best_path_cost
                )
                if meeting_node:
                    new_path_cost = forward['g_score'][meeting_node] + backward['g_score'][meeting_node]
                    if new_path_cost < best_path_cost:
                        best_path_cost = new_path_cost
                        meeting_point = meeting_node
            
            # If we've found a valid path and all remaining paths would be longer
            min_forward = forward['open_set'][0][0] if forward['open_set'] else float('inf')
            min_backward = backward['open_set'][0][0] if backward['open_set'] else float('inf')
            if min_forward + min_backward >= best_path_cost:
                break
        
        if meeting_point is not None:
            # Reconstruct the complete path
            forward_path = self._reconstruct_path(forward['path_history'], meeting_point)
            backward_path = self._reconstruct_path(backward['path_history'], meeting_point)
            backward_path.pop()  # Remove duplicate meeting point
            complete_path = forward_path + backward_path[::-1]
            return complete_path
            
        return None

    def _process_node(self, primary_search, opposite_search, target, direction, best_path_cost):
        if not primary_search['open_set']:
            return None
            
        _, current = heapq.heappop(primary_search['open_set'])
        
        # Check if we've found a meeting point
        if current in opposite_search['g_score']:
            return current
            
        cur_x, cur_y = current
        neighbors = self.get_neighbors(cur_y, cur_x)
        
        for neighbor in neighbors:
            neighbor_x, neighbor_y = neighbor
            
            tentative_g_score = primary_search['g_score'][current] + \
                                self.get_cost(cur_y, cur_x, neighbor[1], neighbor[0])
            
            if neighbor not in primary_search['g_score'] or \
                tentative_g_score < primary_search['g_score'][neighbor]:
                
                # Update the path
                primary_search['path_history'][neighbor] = current
                primary_search['g_score'][neighbor] = tentative_g_score
                
                # Calculate f_score based on direction
                if direction == 'forward':
                    h_score = self.heuristic(neighbor_x, neighbor_y, target[0], target[1])
                else:
                    h_score = self.heuristic(neighbor_x, neighbor_y, target[0], target[1])
                
                f_score = tentative_g_score + h_score
                primary_search['f_score'][neighbor] = f_score
                
                # Only add to open set if the path could potentially be better than best found
                if f_score < best_path_cost:
                    heapq.heappush(primary_search['open_set'], (f_score, neighbor))
        
        return None