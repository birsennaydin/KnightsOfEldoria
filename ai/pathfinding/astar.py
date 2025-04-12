import heapq

from utils.enums import CellType


def heuristic(a, b):
    """Manhattan mesafesi hesaplayıcı (dik hareket için uygun)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal, role="default"):
    """
    A* algoritması ile grid üzerinde start → goal arası en kısa yolu bulur.
    :param grid: Grid nesnesi
    :param start: (x, y) tuple
    :param goal: (x, y) tuple
    :return: [(x1, y1), (x2, y2), ...] yol dizisi
    """
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:

            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

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
