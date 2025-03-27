from utils.enums import CellType
from ai.pathfinding.astar import astar
import random


class HunterController:
    def __init__(self, grid):
        self.grid = grid  # Reference to the grid, needed for movement and neighbor checks

    def process(self, hunter):
        if not hunter.alive:
            hunter.log(f"is dead at ({hunter.x}, {hunter.y})")
            return

        if hunter.collapsing:
            hunter.collapse_check()
            return

        # If in hideout, rest and possibly deliver treasure
        if hunter.is_at_hideout():
            if hunter.carrying:
                hunter.log(f"reached hideout at ({hunter.x}, {hunter.y})")
                hunter.deliver_treasure()
                hunter.log("delivered treasure to hideout.")
            hunter.rest()
            return

        # === Critical stamina check ===
        if hunter.stamina <= 0.06 and hunter.hideout:
            hunter.log("is exhausted and trying to return to a hideout to rest.")
            start = (hunter.x, hunter.y)
            goal = (hunter.hideout.x, hunter.hideout.y)
            path = astar(self.grid, start, goal)

            if path:
                next_pos = path[0]
                dx = next_pos[0] - hunter.x
                dy = next_pos[1] - hunter.y
                hunter.log(f"critical stamina → heading to hideout using A* → next step: {next_pos}")
            else:
                dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                hunter.log("no path to hideout found – moving randomly")

        # If carrying treasure, move toward hideout
        elif hunter.wants_to_return() and hunter.hideout:
            dx = hunter.hideout.x - hunter.x
            dy = hunter.hideout.y - hunter.y
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0
            dx, dy = random.choice([(move_x, 0), (0, move_y)])

        else:
            # Random exploration
            dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])

        # Move the hunter
        new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
        new_cell = self.grid.get_cell(new_x, new_y)

        if new_cell.is_empty() or new_cell.cell_type == CellType.TREASURE:
            old_cell = self.grid.get_cell(hunter.x, hunter.y)
            old_cell.clear()
            new_cell.set_content(hunter, cell_type=CellType.HUNTER)
            hunter.x, hunter.y = new_x, new_y
            hunter.move()

            # Scan surroundings and remember
            nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
            hunter.scan_and_remember(nearby)

            # Check if current cell has treasure
            if new_cell.cell_type == CellType.TREASURE and new_cell.content:
                hunter.collect_treasure(new_cell.content)
                hunter.log(
                    f"collected treasure: {new_cell.content.treasure_type.name} (value={new_cell.content.value})"
                )
                new_cell.clear()  # Remove treasure from map

    def select_best_treasure(self, hunter, grid):
        best_score = float("-inf")
        best_target = None

        for (tx, ty) in hunter.known_treasures:
            treasure_cell = grid.get_cell(tx, ty)

            # Skip if it's not really a treasure
            if not treasure_cell.content or treasure_cell.cell_type.name != "TREASURE":
                continue

            value = treasure_cell.content.value
            distance = abs(tx - hunter.x) + abs(ty - hunter.y)
            stamina = hunter.stamina

            value_score = value * 10
            distance_score = distance * 2
            stamina_penalty = (1 - stamina) * 5

            utility = value_score - distance_score - stamina_penalty

            if utility > best_score:
                best_score = utility
                best_target = (tx, ty)

        return best_target



