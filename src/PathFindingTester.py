import AStar
import BidirectionalAStar as BidirectionalAStar
import numpy as np
import time
import matplotlib.pyplot as plt

class PathFindingTester:
    def __init__(self, visualization):
        self.visualization = visualization
        
        self.mock_elevation_map = np.array([
            [9999, 9999, 9999, 9999, 9999],
            [10, 2, -3, 100, 1],
            [-1, 22000, -1, 3, 20],
            [400, -300, 0.0, -8001, 50],
            [300, -200, 3, -1, 55],
            [10, -10, 1, 1, 1]
        ])
        
        self.start = (1, 0)  # (row, col)
        self.goal = (5, 2)   # (row, col)
        self.expected = [(1, 0), (1, 1), (2, 2), (2, 3), (3, 4), (4, 3), (5, 2)]

    def print_map_with_path(self, elevation_map, path):
        rows, cols = elevation_map.shape
        vis_map = [[f"{int(elevation_map[r, c])}" if elevation_map[r, c].is_integer() 
                    else f"{elevation_map[r, c]:.1f}" for c in range(cols)] for r in range(rows)]
        
        for i in range(len(path) - 1):
            curr_row, curr_col = path[i]
            next_row, next_col = path[i + 1]
            
            dx = next_col - curr_col
            dy = next_row - curr_row
            
            symbol = ""
            if dx == 0:
                symbol = "↑" if dy < 0 else "↓"
            elif dy == 0:
                symbol = "←" if dx < 0 else "→"
            else:
                symbol = "↘" if dx > 0 and dy > 0 else "↗" if dx > 0 else "↙" if dy > 0 else "↖"
            
            vis_map[curr_row][curr_col] = f"[{vis_map[curr_row][curr_col]}{symbol}]"
        
        last_row, last_col = path[-1]
        if not (0 <= last_row < rows and 0 <= last_col < cols):
            raise ValueError(f"Invalid path coordinates: ({last_col}, {last_row}) out of bounds")
        
        vis_map[last_row][last_col] = f"[{vis_map[last_row][last_col]}X]"
        
        return "\n".join(" ".join(row) for row in vis_map)



    def run_Astar_test(self):
        astar = AStar.AStar(True, self.mock_elevation_map)
        path = astar.find_path(self.start, self.goal)
        
        print("\n=========== A* Pathfinding Test ===========")
        if path is None:
            print("No path found")
        else:
            print("\nMap with returned path (arrows show movement direction, X marks end):")
            print(self.print_map_with_path(self.mock_elevation_map, path))
            

    def run_BidirectionalAstar_test(self):
        bi_astar = BidirectionalAStar.BidirectionalAStar(True, self.mock_elevation_map)
        path = bi_astar.find_path(self.start, self.goal)
        
        print("\n=========== Bidirectional A* Test ===========")
        if path is None:
            print("No path found")
        else:
            print("\nMap with returned path (arrows show movement direction, X marks end):")
            print(self.print_map_with_path(self.mock_elevation_map, path))


print("=========== Running A* Test ===========")      
p = PathFindingTester(True)
p.run_Astar_test()

print("\n=========== Running Bidirectional A* Test ===========")
p.run_BidirectionalAstar_test()
