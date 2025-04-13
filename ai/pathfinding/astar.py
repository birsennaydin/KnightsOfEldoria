import heapq
from utils.enums import CellType

def heuristic(a, b):
    """Calculate Manhattan distance (suitable for grid-based movement)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal, role="default"):
    """
    Finds the shortest path from start to goal using the A* algorithm on a grid.
    :param grid: Grid object
    :param start: (x, y) tuple
    :param goal: (x, y) tuple
    :return: path as a list of (x, y) tuples: [(x1, y1), (x2, y2), ...]
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruct path by backtracking from goal
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        # Use different neighbor selection based on role
        if role == "knight":
            neighbors = grid.get_knight_neighbors(*current)
        else:
            neighbors = grid.get_neighbors(*current)

        for neighbor in neighbors:
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []
