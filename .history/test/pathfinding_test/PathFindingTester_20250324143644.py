import AStar
import BidirectionalAStar
import MultiResolutionPathFinder
import numpy as np
import time
import matplotlib.pyplot as plt


class PathFindingTester:
    def __init__(self, visualization):
        self.visualization = visualization

        self.mock_elevation_map = np.array(
            [
                [9999, 9999, 9999, 9999, 9999],
                [10, 2, -3, 100, 1],
                [-1, 22000, -1, 3, 20],
                [400, -300, 0.0, -8001, 50],
                [300, -200, 3, -1, 55],
                [10, -10, 1, 1, 1],
            ]
        )

        self.start = (1, 0)  # (row, col)
        self.goal = (5, 2)  # (row, col)
        self.expected = [(1, 0), (1, 1), (2, 2), (2, 3), (3, 4), (4, 3), (5, 2)]

    def print_map_with_path(self, elevation_map, path):
        rows, cols = elevation_map.shape
        vis_map = [
            [
                (
                    f"{int(elevation_map[r, c])}"
                    if elevation_map[r, c].is_integer()
                    else f"{elevation_map[r, c]:.1f}"
                )
                for c in range(cols)
            ]
            for r in range(rows)
        ]

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
                symbol = (
                    "↘"
                    if dx > 0 and dy > 0
                    else "↗" if dx > 0 else "↙" if dy > 0 else "↖"
                )

            vis_map[curr_row][curr_col] = f"[{vis_map[curr_row][curr_col]}{symbol}]"

        last_row, last_col = path[-1]
        if not (0 <= last_row < rows and 0 <= last_col < cols):
            raise ValueError(
                f"Invalid path coordinates: ({last_col}, {last_row}) out of bounds"
            )

        vis_map[last_row][last_col] = f"[{vis_map[last_row][last_col]}X]"

        return "\n".join(" ".join(row) for row in vis_map)

    def run_resolution_test(self):
        a = MultiResolutionPathFinder.MultiResolutionPathFinder(
            True, self.mock_elevation_map
        )
        path = a.find_path(self.start, self.goal)

        print("\n=========== Gaussian Test ===========")
        if path is None:
            print("No path found")
        else:
            print(
                "\nMap with returned path (arrows show movement direction, X marks end):"
            )
            if self.visualization:
                print(self.print_map_with_path(self.mock_elevation_map, path))

    def run_Astar_test(self):
        astar = AStar.AStar(True, self.mock_elevation_map)
        path = astar.find_path(self.start, self.goal)

        print("\n=========== A* Pathfinding Test ===========")
        if path is None:
            print("No path found")
        else:
            print(
                "\nMap with returned path (arrows show movement direction, X marks end):"
            )
            if self.visualization:
                print(self.print_map_with_path(self.mock_elevation_map, path))

    def run_BidirectionalAstar_test(self):
        bi_astar = BidirectionalAStar.BidirectionalAStar(True, self.mock_elevation_map)
        path = bi_astar.find_path(self.start, self.goal)

        print("\n=========== Bidirectional A* Test ===========")
        if path is None:
            print("No path found")
        else:
            print(
                "\nMap with returned path (arrows show movement direction, X marks end):"
            )
            if self.visualization:
                print(self.print_map_with_path(self.mock_elevation_map, path))

    def debug_abstract_graph(self, hpa):
        print("\nAbstract Graph Connections:")
        for node in hpa.abstract_graph:
            print(f"Node {node} connects to:")
            for neighbor, cost in hpa.abstract_graph[node].items():
                print(f"  -> {neighbor} (cost: {cost})")

    def visualize_real_map(self, path, obj, margin=10):
        """Visualizes a section of the elevation map with the path, start, and goal points."""
        # print(f"Path: {path}")
        print_path_validation_results(path, obj.elevation_map)
        if path is None or len(path) == 0:
            print("❌ No path found! Showing only the map section.")
            path_points = []
        else:
            path_points = path
            # Use first and last points from path as start/goal
            start = path[0]
            goal = path[-1]

        # Include start and goal in bounding box calculation
        all_points = path_points
        all_rows = [p[0] for p in all_points]
        all_cols = [p[1] for p in all_points]

        # Determine bounding box with margin
        min_row = max(0, min(all_rows) - margin)
        max_row = min(obj.elevation_map.shape[0] - 1, max(all_rows) + margin)
        min_col = max(0, min(all_cols) - margin)
        max_col = min(obj.elevation_map.shape[1] - 1, max(all_cols) + margin)

        # Extract the relevant section of the elevation map
        section = obj.elevation_map[min_row : max_row + 1, min_col : max_col + 1]

        # Create figure and plot elevation map
        plt.figure(figsize=(12, 8))
        plt.imshow(section, cmap="terrain", origin="upper")
        plt.colorbar(label="Elevation")

        # Plot path if it exists
        if path_points:
            # Adjust coordinates relative to the extracted section
            adj_path_rows = [p[0] - min_row for p in path_points]
            adj_path_cols = [p[1] - min_col for p in path_points]
            plt.plot(adj_path_cols, adj_path_rows, "r-", linewidth=2, label="Path")

            # Adjust start and goal coordinates relative to the extracted section
            start_adj = (start[0] - min_row, start[1] - min_col)
            goal_adj = (goal[0] - min_row, goal[1] - min_col)

            # Plot adjusted start and goal points
            plt.scatter(
                start_adj[1],
                start_adj[0],
                color="green",
                s=100,
                label="Start (S)",
                zorder=5,
            )
            plt.scatter(
                goal_adj[1],
                goal_adj[0],
                color="blue",
                s=100,
                label="Goal (G)",
                zorder=5,
            )

        # Set proper axis labels and title
        plt.xlabel("Column Index")
        plt.ylabel("Row Index")
        plt.title("Elevation Map Section with Path")
        plt.legend()

        # Add original coordinates as text
        plt.text(
            0.02,
            0.98,
            f"Original Start (row,col): {start}\nOriginal Goal (row,col): {goal}",
            transform=plt.gca().transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=dict(facecolor="white", alpha=0.7),
        )

        # Set proper axis limits
        plt.xlim(-0.5, section.shape[1] - 0.5)
        plt.ylim(section.shape[0] - 0.5, -0.5)

        plt.show()

    def run_Astar_real_map(self):
        start = (80, 70)
        goal = (79, 69)
        astar = AStar.AStar(False)
        path = astar.find_path(start, goal)

        print("\n=========== A* Pathfinding Test ===========")
        if path is None:
            print("No path found")
        else:
            print(
                "\nMap with returned path (arrows show movement direction, X marks end):"
            )
            if self.visualization:
                self.visualize_real_map(path, astar)

    def run_biAstar_real_map(self):
        start = (80, 70)
        goal = (79, 69)
        biastar = BidirectionalAStar.BidirectionalAStar(False)
        path = biastar.find_path(start, goal)

        print("\n=========== Bidirectional A* Pathfinding Test ===========")
        if path is None:
            print("No path found")
        else:
            print(
                "\nMap with returned path (arrows show movement direction, X marks end):"
            )
            if self.visualization:
                self.visualize_real_map(path, biastar)

    def run_resloution_real_map(self):
        start = (80, 70)
        goal = (60, 40)
        m = MultiResolutionPathFinder.MultiResolutionPathFinder(False)
        path = m.find_path(start, goal)

        print("\n=========== MultiResolutionPathFinder Pathfinding Test ===========")
        if path is None:
            print("No path found")
        else:
            print(
                "\nMap with returned path (arrows show movement direction, X marks end):"
            )
            if self.visualization:
                self.visualize_real_map(path, m)


def validate_path(path, elevation_map):
    """
    Validates if a path is valid based on elevation constraints and
    simulates battery consumption along the path.

    Args:
        path: List of tuples [(row1, col1), (row2, col2), ...] representing the path.
        elevation_map: 2D numpy array containing elevation data.

    Returns:
        (bool, list, float, int): A tuple containing:
            - Boolean indicating if the path is valid.
            - List of validation errors (if any).
            - Total battery consumption used (sum of battery cost for each move).
            - Number of charging events needed.
    """
    if not path or len(path) < 2:
        return False, ["Path is empty or contains only one point"], None, None

    MIN_ELEVATION = -8200
    MAX_ELEVATION = 22000
    MAX_ELEVATION_DIFF = 100
    validation_errors = []

    # Validate each point for in-bound and proper elevation range.
    for idx, (row, col) in enumerate(path):
        errors = []
        if (
            row < 0
            or row >= elevation_map.shape[0]
            or col < 0
            or col >= elevation_map.shape[1]
        ):
            errors.append(f"Point {idx+1}: ({row}, {col}) is out of map bounds")
        else:
            elevation = elevation_map[row, col]
            if elevation < MIN_ELEVATION:
                errors.append(
                    f"Point {idx+1}: ({row}, {col}) has elevation {elevation} below minimum {MIN_ELEVATION}"
                )
            elif elevation > MAX_ELEVATION:
                errors.append(
                    f"Point {idx+1}: ({row}, {col}) has elevation {elevation} above maximum {MAX_ELEVATION}"
                )
        if errors:
            validation_errors.extend(errors)

    # Optionally, check if elevation differences between consecutive points exceed MAX_ELEVATION_DIFF.
    for i in range(len(path) - 1):
        row1, col1 = path[i]
        row2, col2 = path[i + 1]
        if (
            0 <= row1 < elevation_map.shape[0]
            and 0 <= col1 < elevation_map.shape[1]
            and 0 <= row2 < elevation_map.shape[0]
            and 0 <= col2 < elevation_map.shape[1]
        ):
            elev1 = elevation_map[row1, col1]
            elev2 = elevation_map[row2, col2]
            if abs(elev2 - elev1) > MAX_ELEVATION_DIFF:
                validation_errors.append(
                    f"Elevation difference between point {i+1} and {i+2} exceeds allowed maximum "
                    f"({abs(elev2 - elev1)} > {MAX_ELEVATION_DIFF})"
                )

    is_valid = len(validation_errors) == 0

    # Simulate battery consumption along the path.
    battery = 100.0
    charging_count = 0
    total_battery_consumption = 0.0

    def estimate_battery_cost(elev1, elev2):
        diff = elev2 - elev1
        if diff < 0:
            return 0.5  # Downhill: lower battery cost
        elif diff <= 10:
            return 1.0  # Flat ground
        elif diff <= 50:
            return 2.5  # Mild uphill
        elif diff <= 100:
            return 3.0  # Steep uphill
        else:
            # Should not happen if the path is valid
            return float("inf")

    for i in range(len(path) - 1):
        row1, col1 = path[i]
        row2, col2 = path[i + 1]
        if (
            0 <= row1 < elevation_map.shape[0]
            and 0 <= col1 < elevation_map.shape[1]
            and 0 <= row2 < elevation_map.shape[0]
            and 0 <= col2 < elevation_map.shape[1]
        ):
            elev1 = elevation_map[row1, col1]
            elev2 = elevation_map[row2, col2]
            cost = estimate_battery_cost(elev1, elev2)
            # If the cost is infinite, we skip simulation (or handle as error)
            if cost == float("inf"):
                continue
            # If battery is insufficient for the move, simulate a charging event.
            if battery < cost:
                charging_count += 1
                battery = 100.0  # recharge battery to full
            battery -= cost
            total_battery_consumption += cost

    return is_valid, validation_errors, total_battery_consumption, charging_count


def print_path_validation_results(path, elevation_map):
    """
    Prints formatted validation results for a path.
    """
    print("\n=== Path Validation Results ===")
    is_valid, errors, total_battery_consumption, charging_count = validate_path(
        path, elevation_map
    )

    if is_valid:
        print("✅ Path is valid! All constraints are satisfied.")
        print(
            "There are ",
            total_battery_consumption,
            " consumed and the battery gets charged ",
            charging_count,
            " times",
        )
    else:
        print("❌ Path is invalid! Found the following issues:")
        for i, error in enumerate(errors, 1):
            print(f"\nError {i}:")
            print(error)
    print("\n" + "=" * 30)


# Run all tests
if __name__ == "__main__":

    print("=========== Running A* Test ===========")
    p = PathFindingTester(True)
    p.run_Astar_test()

    print("\n=========== Running Bidirectional A* Test ===========")
    p.run_BidirectionalAstar_test()

    print("\n=========== Running Gaussian Test ===========")
    p.run_resolution_test()

    print("\n=========== Running Gaussian Test ===========")
    start_time = time.time()
    p = PathFindingTester(True)
    p.run_resloution_real_map()
    end_time = time.time()
    print("Running time: ", end_time - start_time)

    print("\n=========== Running Bidirectional A* Test ===========")
    start_time = time.time()
    p = PathFindingTester(True)
    p.run_biAstar_real_map()
    end_time = time.time()
    print("Running time: ", end_time - start_time)

    print("\n=========== Running A* Test ===========")
    start_time = time.time()
    p = PathFindingTester(True)
    p.run_Astar_real_map()
    end_time = time.time()
    print("Running time: ", end_time - start_time)
