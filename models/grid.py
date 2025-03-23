from models.cell import Cell
from utils.constants import GRID_MIN_SIZE


class Grid:
    def __init__(self, size: int = GRID_MIN_SIZE):
        self.size = max(size, GRID_MIN_SIZE)
        self.grid = [[Cell(x, y) for y in range(self.size)] for x in range(self.size)]

    def wrap(self, x: int, y: int) -> tuple:
        """Wrap coordinates around the grid edges."""
        return x % self.size, y % self.size

    def get_cell(self, x: int, y: int) -> Cell:
        x, y = self.wrap(x, y)
        return self.grid[x][y]

    def get_neighbors(self, x: int, y: int) -> list:
        """Return list of adjacent neighbor cells (up, down, left, right)."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = self.wrap(x + dx, y + dy)
            neighbors.append(self.get_cell(nx, ny))
        return neighbors

    def get_cells_in_radius(self, x: int, y: int, radius: int) -> list:
        """Return all cells within a square radius (wrap-around aware)."""
        cells = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue  # Skip the center cell
                nx, ny = self.wrap(x + dx, y + dy)
                cells.append(self.get_cell(nx, ny))
        return cells

    def __repr__(self):
        return f"Grid({self.size}x{self.size})"
