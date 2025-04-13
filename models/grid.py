from models.cell import Cell
from utils.enums import CellType


class Grid:
    def __init__(self, size, simulation_controller=None):
        self.size = size
        self.simulation_controller = simulation_controller
        self.cells = [[Cell(x, y) for x in range(size)] for y in range(size)]

    def get_cell(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.cells[y][x]
        return None

    def clear_cell(self, x, y):
        cell = self.get_cell(x, y)
        if cell:
            cell.clear()

    def wrap(self, x, y):
        # Ensure coordinates wrap around the grid boundaries
        return x % self.size, y % self.size

    def get_cells_in_radius(self, x, y, radius):
        # Return all cells within a given radius of (x, y)
        cells = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = self.wrap(x + dx, y + dy)
                cells.append(self.get_cell(nx, ny))
        return cells

    def place_treasure(self, treasure):
        # Place a treasure in its designated cell
        cell = self.get_cell(treasure.x, treasure.y)
        if cell:
            cell.set_content(treasure, cell_type=CellType.TREASURE)

    def place_hunter(self, hunter):
        # Place a hunter in its designated cell
        cell = self.get_cell(hunter.x, hunter.y)
        if cell:
            cell.set_content(hunter, cell_type=CellType.HUNTER)

    def place_knight(self, knight):
        # Place a knight in its designated cell
        cell = self.get_cell(knight.x, knight.y)
        if cell:
            cell.set_content(knight, cell_type=CellType.KNIGHT)

    def remove_knight(self, x, y):
        # Remove knight from the specified cell
        cell = self.get_cell(x, y)
        if cell:
            cell.clear()

    def place_hideout(self, hideout):
        # Place a hideout in its designated cell
        cell = self.get_cell(hideout.x, hideout.y)
        if cell:
            cell.set_content(hideout, cell_type=CellType.HIDEOUT)

    def place_garrison(self, garrison):
        # Place a garrison in its designated cell
        cell = self.get_cell(garrison.x, garrison.y)
        if cell:
            cell.set_content(garrison, cell_type=CellType.GARRISON)

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Return valid neighbors for a given (x, y) position.
        Only includes cells that are empty, treasure, or hideout,
        and excludes cells occupied by a knight.
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []

        for dx, dy in directions:
            nx, ny = self.wrap(x + dx, y + dy)
            cell = self.get_cell(nx, ny)

            # Accept cell if it's empty, contains treasure or hideout, and is not a knight
            if (cell.is_empty() or cell.cell_type == CellType.TREASURE or cell.cell_type == CellType.HIDEOUT) and cell.cell_type != CellType.KNIGHT:
                neighbors.append((nx, ny))

        return neighbors

    def get_knight_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Return valid neighboring positions for a Knight.

        Knights are allowed to move into cells that are:
        - EMPTY (free space)
        - TREASURE (to potentially recover or pass over)
        - HUNTER (to detain or challenge them)
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Possible movement directions
        neighbors = []

        for dx, dy in directions:
            nx, ny = self.wrap(x + dx, y + dy)  # Ensure coordinates stay within grid bounds
            cell = self.get_cell(nx, ny)

            if cell and cell.cell_type in {CellType.EMPTY, CellType.TREASURE, CellType.HUNTER}:
                neighbors.append((nx, ny))

        return neighbors
