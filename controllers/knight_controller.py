from utils.enums import CellType
from ai.pathfinding.astar import astar
import random

class KnightController:
    def __init__(self, grid):
        self.grid = grid

    def process(self, knight):

        # Rule 1: Knight is already resting if this flag is set
        if knight.resting:
            knight.log(f"{knight.name} is resting. RULE1")
            knight.rest()
            if not knight.resting:
                knight.log(f"{knight.name} has recovered and is active again.")
            return

        #Rule 2: If knight is too tired, check if it should rest.
        if knight.should_rest():
            knight.resting = True
            knight.log(f"{knight.name} is too tired and starts resting.")
            # Send knight to garrison to rest if it has a garrison
            if knight.garrison:
                knight.garrison.add_knight(knight)  # Add knight to garrison for resting
            else:
                knight.rest() # there is not garrison, starting to rest in the same cell
            return


        # Rule 3: Scan for hunters in the knight's radius
        nearby_cells = self.grid.get_cells_in_radius(knight.x, knight.y, 3)
        knight.log(f"GET NEARBY CELLS {nearby_cells}")
        visible_hunters = knight.detect_hunters(nearby_cells)
        knight.log(f"VISIBLE HUNTERS {len(visible_hunters)} {visible_hunters}")

        if visible_hunters:
            knight.log(f"spotted {len(visible_hunters)} hunters nearby.")
            knight.choose_target(visible_hunters)

            # Rule 4: If knight has a target, move towards them
            if knight.target:
                # Use A* pathfinding to determine the path to the target
                path = astar(self.grid, (knight.x, knight.y), (knight.target.x, knight.target.y), role="knight")
                if path:
                    next_x, next_y = path[0]
                    knight.move_to(next_x, next_y)

                    knight.log(
                        f"KNIGHT Current Position: ({knight.x}, {knight.y}), "
                        f"KNIGHT Energy: {knight.energy}, "
                        f"KNIGHT Resting: {knight.resting}"
                    )

                    knight.energy -= 0.2  # Energy decreases with movement
                    knight.log(f"moving toward target at ({knight.target.x}, {knight.target.y})")
                else:
                    knight.log("cannot reach target – switching to patrol.")
                    knight.target = None
                    self.random_patrol(knight)  # If path is blocked, patrol randomly

                # Rule 5: If knight reaches target, interact with hunter (detain or challenge)
                if (knight.target.x, knight.target.y) == (knight.x, knight.y):
                    knight.interact_with_hunter(knight.target, method="detain")
                    knight.log(f"detained hunter: {knight.target.name}")
        else:
            # Rule 6: No hunters in sight, knight continues to patrol
            knight.log("no hunters nearby. Patrolling...")
            self.random_patrol(knight)  # Patrol randomly if no target

    def random_patrol(self, knight):
        # Rule 7: Randomly patrol the area if no target is found
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])  # Random movement choices
        new_x, new_y = self.grid.wrap(knight.x + dx, knight.y + dy)  # Ensure knight stays within grid bounds
        knight.move_to(new_x, new_y)  # Move the knight to the new position
        knight.energy -= 0.2  # Patrolling consumes some energy
        knight.log(f"{knight.name} is patrolling to ({new_x}, {new_y})")

        # Check if a hunter is at the new location
        cell = self.grid.get_cell(new_x, new_y)
        if cell and cell.cell_type == CellType.HUNTER and cell.content:
            knight.interact_with_hunter(cell.content, method="detain")
            knight.log(f"{knight.name} randomly encountered and detained hunter: {cell.content.name}")
