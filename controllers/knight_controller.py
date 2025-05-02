from models.hunter import Hunter
from utils.enums import CellType
from ai.pathfinding.astar import astar
import random

class KnightController:
    def __init__(self, grid):
        self.grid = grid

    def process(self, knight):
        knight.log(f"KnightController started for {knight}, {knight.name}")

        # If the knight is already resting, continue resting
        if knight.resting:
            knight.log(f"{knight.name} is resting.")
            knight.rest()
            if not knight.resting:
                knight.log(f"{knight.name} has recovered and is active again.")
            return

        # If the knight is too tired, initiate resting
        if knight.should_rest():
            knight.resting = True
            knight.log(f"{knight.name} is too tired and starts resting.")
            if knight.garrison:
                knight.garrison.add_knight(knight)
            else:
                knight.rest()
            return

        nearby_cells = self.grid.get_cells_in_radius(knight.x, knight.y, 3)
        visible_hunters = knight.detect_hunters(nearby_cells)
        knight.log(f"Detected {len(visible_hunters)} hunter(s).")

        if visible_hunters:
            path = self.get_safe_path_to_hunter(knight, [(h.x, h.y) for h in visible_hunters])
            if path:
                next_pos = path[0]
                dx = next_pos[0] - knight.x
                dy = next_pos[1] - knight.y
                new_x, new_y = self.grid.wrap(knight.x + dx, knight.y + dy)
                new_cell = self.grid.get_cell(new_x, new_y)
                old_cell = self.grid.get_cell(knight.x, knight.y)

                if new_cell.cell_type == CellType.EMPTY:
                    knight.move_to(new_x, new_y)
                    knight.energy = max(0, round(knight.energy - 0.2, 2))
                elif new_cell.cell_type == CellType.HUNTER and isinstance(new_cell.content, Hunter):
                    knight.interact_with_hunter(new_cell.content, method="detain")
                    knight.log(f"Detained hunter: {new_cell.content}")
                    knight.energy = max(0, round(knight.energy - 0.2, 2))
                else:
                    knight.log("Target cell not reachable. Switching to patrol.")
                    knight.target = None
                    self.random_patrol(knight)
            else:
                knight.log("No path to target. Switching to patrol.")
                knight.target = None
                self.random_patrol(knight)
        else:
            knight.log("No visible hunters. Switching to patrol.")
            knight.target = None
            self.random_patrol(knight)

    def random_patrol(self, knight):
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        new_x, new_y = self.grid.wrap(knight.x + dx, knight.y + dy)
        cell = self.grid.get_cell(new_x, new_y)

        if cell and cell.cell_type == CellType.EMPTY:
            knight.move_to(new_x, new_y)
            knight.log(f"{knight.name} patrolled to empty cell at ({new_x}, {new_y})")
        elif cell and cell.cell_type == CellType.HUNTER and cell.content:
            knight.interact_with_hunter(cell.content, method="detain")
            knight.log(f"{knight.name} patrolled into hunter cell and detained: {cell.content.name}")
        else:
            knight.log(f"{knight.name} attempted patrol to non-empty cell. Staying in place.")

        knight.energy = max(0, round(knight.energy - 0.2, 2))
        knight.log(f"{knight.name} lost 0.2 energy during patrol. Current energy: {knight.energy:.2f}")

    def get_safe_path_to_hunter(self, knight, visible_hunters):
        knight.log(f"get_safe_path_to_hunter called. Knight: {knight}")
        valid_visible_hunters = [
            pos for pos in visible_hunters
            if self.grid.get_cell(*pos).cell_type == CellType.HUNTER and
               isinstance(self.grid.get_cell(*pos).content, Hunter)
        ]

        if valid_visible_hunters:
            sorted_hunters = sorted(
                valid_visible_hunters,
                key=lambda pos: abs(knight.x - pos[0]) + abs(knight.y - pos[1])
            )

            for hunter_pos in sorted_hunters:
                path = astar(self.grid, (knight.x, knight.y), hunter_pos, role="knight")
                if path:
                    is_safe = all(
                        self.grid.get_cell(*pos).cell_type not in [
                            CellType.KNIGHT, CellType.GARRISON, CellType.HIDEOUT, CellType.TREASURE
                        ]
                        for pos in path[1:]
                    )
                    if is_safe:
                        return path
        neighbors = self.grid.get_knight_neighbors(knight.x, knight.y)
        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            if cell and cell.cell_type in {CellType.EMPTY, CellType.HUNTER}:
                return [(nx, ny)]
        return None