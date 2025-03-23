from utils.enums import CellType
import random


class HunterController:
    def __init__(self, grid):
        self.grid = grid  # Reference to the grid, needed for movement and neighbor checks

    def process(self, hunter):
        """Handle behavior of a single hunter for one simulation step."""

        if not hunter.alive:
            return

        if hunter.collapsing:
            hunter.collapse_check()
            return

        # If the hunter is in a hideout, rest to regain stamina
        if hunter.hideout and (hunter.x, hunter.y) == (hunter.hideout.x, hunter.hideout.y):
            hunter.rest()
            return

        # Move in a random direction (can be replaced with smarter decision-making later)
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
        new_cell = self.grid.get_cell(new_x, new_y)

        if new_cell.is_empty():
            # Move hunter to new cell
            old_cell = self.grid.get_cell(hunter.x, hunter.y)
            old_cell.clear()
            new_cell.set_content(hunter, cell_type=CellType.HUNTER)
            hunter.x, hunter.y = new_x, new_y
            hunter.move()

            # Scan nearby cells and remember treasures, hideouts, knights
            nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
            hunter.scan_and_remember(nearby)
