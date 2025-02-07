import AStar
import BidirectionalAStar as BidirectionalAStar
import numpy as np
import time
class PathFindingTester:
    def __init__(self,visualization):
        self.visualization = visualization
        
        self.mock_elevation_map = np.array([
            [10, 2, -3, 100, 1],
            [-1, 22000, -1, 3, 20],
            [400, -300, 0.0, -8001, 50],
            [300, -200, 3, -1, 55],
            [10, -10, 1, 1, 1]
        ]) 
        
        self.start = (0, 1)#(col,row)
        self.goal = (2, 4)
        self.expected = [(0, 1), (1,0), (2, 1), (3,1), (4, 2),(3,3),(2,4)]
        
    def print_map_with_path(self, elevation_map, path):
        # Create a visualization map with arrows showing movement direction
        rows, cols = elevation_map.shape
        vis_map = [
            [
                f"{int(elevation_map[i, j])}" if elevation_map[i, j].is_integer() 
                else f"{elevation_map[i, j]:.1f}"
                for j in range(cols)
            ]
            for i in range(rows)
        ]
        
        for i in range(len(path)-1):
            curr_x, curr_y = path[i]
            next_x, next_y = path[i+1]
            
            # Determine direction
            dx = next_x - curr_x
            dy = next_y - curr_y
            
            # Create direction symbol
            symbol = ""
            if dx == 0:
                if dy < 0: symbol = "↑"
                else: symbol = "↓"
            elif dy == 0:
                if dx < 0: symbol = "←"
                else: symbol = "→"
            else:
                if dx > 0 and dy > 0: symbol = "↘"
                elif dx > 0 and dy < 0: symbol = "↗"
                elif dx < 0 and dy > 0: symbol = "↙"
                else: symbol = "↖"
                
            val = vis_map[curr_y][curr_x].strip()
            vis_map[curr_y][curr_x] = f"[{val}{symbol}]"
        
        # Mark final position
        last_x, last_y = path[-1]
        val = vis_map[last_y][last_x].strip()
        vis_map[last_y][last_x] = f"[{val}X]"
    
        return "\n".join(" ".join(row) for row in vis_map)

    def calculate_path_cost(self,elevation_map, path):
        total_cost = 0
        steps = []
        
        for i in range(len(path)-1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            
            # Calculate if movement is diagonal
            diagonal = x1 != x2 and y1 != y2
            base_cost = 1.4142 if diagonal else 1.0
            
            elevation_diff = abs(elevation_map[y2,x2] - elevation_map[y1,x1])
            step_cost = base_cost + elevation_diff
            
            steps.append({
                'from': (x1,y1),
                'to': (x2,y2),
                'diagonal': diagonal,
                'elevation_diff': elevation_diff,
                'step_cost': step_cost
            })
            total_cost += step_cost
        
        return steps, total_cost
    
    def run_Astar_test(self):
        astar = AStar.AStar(True,self.mock_elevation_map)
        path = astar.find_path(self.start,self.goal)
        
        if self.visualization:
            if self.expected == None:
                print("Expected: There should be no path found")
                print("Test result:")
            else:
                print("Map with likely path (arrows show movement direction, X marks end):")
                print(self.print_map_with_path(self.mock_elevation_map, self.expected))
            if path == None:
                print("No path found")
            else:
                print("\nMap with returned path (arrows show movement direction, X marks end):")
                print(self.print_map_with_path(self.mock_elevation_map, path))

        steps, total_cost = self.calculate_path_cost(self.mock_elevation_map, path)

        print("\nStep-by-step analysis:")
        for i, step in enumerate(steps, 1):
            print(f"\nStep {i}:")
            print(f"  Move: {step['from']} → {step['to']}")
            print(f"  Movement type: {'Diagonal' if step['diagonal'] else 'Orthogonal'}")
            print(f"  Elevation change: {step['elevation_diff']}")
            print(f"  Step cost: {step['step_cost']:.2f}")

        print(f"\nTotal path cost: {total_cost:.2f}")
    
    def run_BidirectionAstar_test(self):
        biAstar = BidirectionalAStar.BidirectionalAStar(True,self.mock_elevation_map)
        path = biAstar.find_path(self.start,self.goal)
        print("Path",path)
        if self.visualization:
            if self.expected == None:
                print("Expected: There should be no path found")
                print("Test result:")
            else:
                print("Map with likely path (arrows show movement direction, X marks end):")
                print(self.print_map_with_path(self.mock_elevation_map, self.expected))
            if path == None:
                print("No path found")
            else:
                print("\nMap with returned path (arrows show movement direction, X marks end):")
                print(self.print_map_with_path(self.mock_elevation_map, path))

        steps, total_cost = self.calculate_path_cost(self.mock_elevation_map, path)

        print("\nStep-by-step analysis:")
        for i, step in enumerate(steps, 1):
            print(f"\nStep {i}:")
            print(f"  Move: {step['from']} → {step['to']}")
            print(f"  Movement type: {'Diagonal' if step['diagonal'] else 'Orthogonal'}")
            print(f"  Elevation change: {step['elevation_diff']}")
            print(f"  Step cost: {step['step_cost']:.2f}")

        print(f"\nTotal path cost: {total_cost:.2f}")
    
print("===========AStar===========")      
p = PathFindingTester(True)
start=time.time()
p.run_Astar_test()
end=time.time()
total = end-start
print("Running time:",total,"sec")
print("===========================")
print()
print("============BiDirection AStar================")
p = PathFindingTester(True) 
start=time.time()
p.run_BidirectionAstar_test()
end=time.time()
print("Running time:",total,"sec")