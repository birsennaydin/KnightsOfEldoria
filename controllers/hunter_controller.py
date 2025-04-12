from utils.enums import CellType
from ai.pathfinding.astar import astar
import random


class HunterController:
    def __init__(self, grid, simulation_controller):
        self.grid = grid  # Reference to the grid, needed for movement and neighbor checks
        self.simulation_controller = simulation_controller  # Reference to SimulationController

    def process(self, hunter):
        # If hunter is not alive, remove them from the simulation
        if not hunter.alive:
            self.simulation_controller.remove_hunter_from_list(hunter)
            hunter.log(f"is dead at ({hunter.x}, {hunter.y})")
            return

        # If hunter is inside a hideout
        if hunter.is_at_hideout():
            if hunter.carrying:
                hunter.log(f"reached hideout at ({hunter.x}, {hunter.y})")
                hunter.deliver_treasure()
                hunter.log("delivered treasure to hideout.")
            hunter.rest()
            return

        # If stamina is exactly 0, set collapsing state if not already collapsing
        if hunter.stamina == 0 and not hunter.collapsing:
            hunter.collapsing = True
            hunter.log("has reached 0 stamina and is collapsing.")

        # If hunter is collapsing, perform collapse check
        if hunter.collapsing:
            hunter.collapse_check()
            return

        # === Handle critical stamina scenario ===
        if hunter.stamina <= 0.06:
            if hunter.hideout:
                # Move towards assigned hideout
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

            elif hunter.known_hideouts:
                # Assign a remembered hideout and attempt to pathfind to it
                hx, hy = hunter.known_hideouts[0]
                hideout_cell = self.grid.get_cell(hx, hy)
                if hideout_cell and hideout_cell.content:
                    hunter.hideout = hideout_cell.content
                    hunter.log(f"assigned to new hideout at ({hx}, {hy})")
                    start = (hunter.x, hunter.y)
                    goal = (hx, hy)
                    path = astar(self.grid, start, goal)

                    if path:
                        next_pos = path[0]
                        dx = next_pos[0] - hunter.x
                        dy = next_pos[1] - hunter.y
                        hunter.log(f"heading to assigned hideout using A* → next step: {next_pos}")
                    else:
                        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                        hunter.log("no path to remembered hideout found – moving randomly")
                else:
                    dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                    hunter.log("known hideout is invalid – moving randomly")

            else:
                dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                hunter.log("exhausted and lost — no hideout known.")

        # === Treasure hunting and general movement ===
        else:
            best_treasure_pos = self.select_best_treasure(hunter)

            if best_treasure_pos:
                hunter.log(f"heading towards treasure at {best_treasure_pos}")
                path = astar(self.grid, (hunter.x, hunter.y), best_treasure_pos)

                if path:
                    next_pos = path[0]
                    dx = next_pos[0] - hunter.x
                    dy = next_pos[1] - hunter.y
                    hunter.log(f"moving towards treasure using A* → next step: {next_pos}")
                else:
                    dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                    hunter.log("no path to treasure found – moving randomly")
            else:
                dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                hunter.log("no known treasures – exploring randomly")

        # === Move the hunter on the grid ===
        new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
        new_cell = self.grid.get_cell(new_x, new_y)

        if new_cell.is_empty() or new_cell.cell_type == CellType.TREASURE:
            old_cell = self.grid.get_cell(hunter.x, hunter.y)
            old_cell.clear()

            hunter.x, hunter.y = new_x, new_y
            hunter.move()

            # Scan surroundings and remember
            nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
            hunter.scan_and_remember(nearby)

            print(f"✅ COLLECT TREASURE01010: {new_cell.cell_type}")
            # Check if current cell has treasure
            if new_cell.cell_type == CellType.TREASURE and new_cell.content:
                print(f"✅ COLLECT TREASURE02020: {new_cell.cell_type} {new_cell.content}")
                treasure = new_cell.content  # Access the treasure object
                hunter.collect_treasure(treasure)
                hunter.log(f"collected treasure: {treasure.treasure_type.name} (value={treasure.value})")
                new_cell.clear()
                self.simulation_controller.remove_treasure_from_list(treasure)

                # Additionally clear the treasure from the grid and cell
                self.grid.clear_cell(treasure.x, treasure.y)  # Ensure treasure is cleared from grid too
                print(f"✅ Treasure {treasure.treasure_type.name} collected and removed from grid.")

            new_cell.set_content(hunter, cell_type=CellType.HUNTER)

    def select_best_treasure(self, hunter):
        best_score = float("-inf")
        best_target = None

        for (tx, ty) in hunter.known_treasures:
            treasure_cell = self.grid.get_cell(tx, ty)

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
