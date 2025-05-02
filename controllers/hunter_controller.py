from models.treasure import Treasure
from utils.enums import CellType
from ai.pathfinding.astar import astar
import random


class HunterController:
    def __init__(self, grid, simulation_controller):
        self.grid = grid
        self.simulation_controller = simulation_controller

    def process(self, hunter):
        hunter.log(f"HUNTER CONTROLLER STARTING ({hunter.carrying}, {hunter}),"
                   f"ALIVE {hunter.alive},"
                   f"IS_RESTING_IN_HIDEOUT {hunter.is_resting_in_hideout},"
                   f"STAMINA {hunter.stamina},"
                   f"COLLAPSING {hunter.collapsing},"
                   f"COLLAPSE COUNT {hunter.collapse_counter}")

        # If the hunter is not alive, remove them from the simulation
        if not hunter.alive:
            self.simulation_controller.remove_hunter_from_list(hunter)
            self.grid.clear_cell(hunter.x, hunter.y)
            hunter.log(f"Hunter is dead and removed from grid at ({hunter.x}, {hunter.y})")
            return

        # If the hunter is inside a hideout
        if hunter.is_resting_in_hideout():
            hunter.log(f"Hunter is at hideout ({hunter.carrying}, {hunter})")
            if hunter.carrying:
                hunter.log(f"Reached hideout at ({hunter.x}, {hunter.y})")
                hunter.deliver_treasure(self.simulation_controller)
                hunter.log("Delivered treasure to hideout.")

            hunter.rest(self.grid)
            return

        # If stamina is exactly 0, set collapsing state if not already set
        if hunter.stamina == 0 and not hunter.collapsing:
            hunter.collapsing = True
            hunter.log("Hunter has reached 0 stamina and is collapsing.")
            hunter.analyze_emotion_and_log("I'm collapsing from exhaustion.")

        # If the hunter is collapsing, perform collapse check
        if hunter.collapsing:
            hunter.collapse_check()
            return

        # If the hunter is carrying the treasure
        if hunter.carrying:
            hunter.log(f"Hunter carrying treasure: {hunter.carrying}")
            path = self.get_safe_path_to_hideout(hunter)
            if path:
                next_pos = path[0]
                dx = next_pos[0] - hunter.x
                dy = next_pos[1] - hunter.y
                new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
                new_cell = self.grid.get_cell(new_x, new_y)

                # If the target cell is a hideout and has space, drop the treasure
                if new_cell.cell_type == CellType.HIDEOUT:
                    hideout = new_cell.content
                    hunter.log(f"Hideout hunter count: {len(hideout.hunters)}")
                    if hideout and len(hideout.hunters) < hideout.capacity:
                        hideout.stored_treasures.append(hunter.carrying)
                        hunter.log(f"Stored treasure in hideout at ({new_x}, {new_y})")
                        hunter.analyze_emotion_and_log("Resting in hideout to recover stamina.")
                        self.simulation_controller.remove_treasure_from_list(hunter.carrying)
                        hunter.carrying = None
                        hideout.add_hunter(hunter, self.grid)
                        return
                    else:
                        hunter.log(f"Hideout at ({new_x}, {new_y}) is full.")
                        hunter.move() # still reduce stamina
                        return

                # If there is another hunter in the target cell, do not move
                if new_cell.cell_type == CellType.HUNTER:
                    hunter.log("Target cell occupied by another hunter.")
                    hunter.move() # Stamina -0.02
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return

                if new_cell.cell_type == CellType.TREASURE:
                    new_treasure = new_cell.content
                    if new_treasure.value > hunter.carrying.value:
                        hunter.log(f"Swapping with more valuable treasure at ({new_x}, {new_y})")
                        old_cell = self.grid.get_cell(hunter.x, hunter.y)
                        if old_cell.cell_type != CellType.HIDEOUT and old_cell.cell_type != CellType.GARRISON:
                            old_cell.clear()
                            old_cell.set_transit_content(hunter.carrying, CellType.TREASURE)

                        # Assign the new treasure to the hunter
                        hunter.carrying = new_treasure

                        # Clear the new treasure's cell
                        self.grid.clear_cell(new_x, new_y)

                        # Move the hunter to the new position
                        hunter.x, hunter.y = new_x, new_y
                        self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)
                    else:
                        hunter.log(f"Found lesser treasure at ({new_x}, {new_y}), ignoring.")
                        old_cell = self.grid.get_cell(hunter.x, hunter.y)
                        old_cell.clear()

                        # Drop the lesser treasure at the old position
                        old_cell.set_transit_content(new_treasure, CellType.TREASURE)
                        self.grid.clear_cell(new_x, new_y)
                        hunter.x, hunter.y = new_x, new_y
                        self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)

                    hunter.move()
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return

                hunter.log(f"Moving to empty cell at ({new_x}, {new_y})")
                old_cell = self.grid.get_cell(hunter.x, hunter.y)
                old_cell.clear()
                hunter.x, hunter.y = new_x, new_y
                self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)
                hunter.move()
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                return
            else:
                hunter.log("Carrying treasure but no safe path to hideout found.")
                hunter.move()
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                return

        if hunter.stamina <= 0.06:
            hunter.log("Low stamina, trying to reach nearest hideout.")
            path = self.get_safe_path_to_hideout(hunter)
            if path:
                next_pos = path[0]
                dx = next_pos[0] - hunter.x
                dy = next_pos[1] - hunter.y
                new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
                new_cell = self.grid.get_cell(new_x, new_y)
                old_cell = self.grid.get_cell(hunter.x, hunter.y)

                if new_cell.cell_type == CellType.HIDEOUT:
                    hideout = new_cell.content
                    if hideout and len(hideout.hunters) < hideout.capacity:
                        hunter.log(f"Entering hideout at ({new_x}, {new_y}) to rest.")
                        hideout.add_hunter(hunter, self.grid)
                        return
                    else:
                        hunter.log(f"Hideout at ({new_x}, {new_y}) is full.")
                        hunter.move()
                        return

                elif new_cell.cell_type == CellType.HUNTER:
                    hunter.log("Another hunter is blocking the path.")
                    hunter.move()
                    return

                elif new_cell.cell_type == CellType.TREASURE:
                    treasure = new_cell.content
                    hunter.carrying = treasure
                    hunter.log(f"Picked up treasure at ({new_x}, {new_y}) worth {treasure.value}")
                    self.grid.clear_cell(new_x, new_y)
                    old_cell.clear()
                    hunter.x, hunter.y = new_x, new_y
                    self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)
                    hunter.move()
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return

                else:
                    old_cell.clear()
                    hunter.x, hunter.y = new_x, new_y
                    self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)
                    hunter.move()
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return
            else:
                hunter.log("No reachable hideout, standing still.")
                hunter.move()
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                return
        else:
            hunter.log(f"Hunter has enough stamina. Searching for treasure... {hunter}")
            path = self.get_safe_path_to_treasure(hunter)
            if path:
                next_pos = path[0]
                dx = next_pos[0] - hunter.x
                dy = next_pos[1] - hunter.y
                new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
                new_cell = self.grid.get_cell(new_x, new_y)
                old_cell = self.grid.get_cell(hunter.x, hunter.y)

                if new_cell.cell_type == CellType.TREASURE:
                    treasure = new_cell.content
                    hunter.carrying = treasure
                    hunter.log(f"Collected treasure at ({new_x}, {new_y}) worth {treasure.value}")
                    hunter.analyze_emotion_and_log(f"Found treasure worth {new_cell.content.value}")
                    self.grid.clear_cell(new_x, new_y)

                old_cell.clear()
                hunter.x, hunter.y = new_x, new_y
                self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)
                hunter.move()
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                return
            else:
                hunter.log("No path to treasure — waiting and scanning.")
                hunter.move()
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                return

    def get_safe_path_to_treasure(self, hunter):
        """
        Returns a safe path to the best known treasure,
        or scans nearby cells for treasure or empty fallback.
        """

        hunter.log("Searching for safe path to known treasures.")
        hunter.log(f"Known treasures: {hunter.known_treasures}")

        for pos in hunter.known_treasures:
            cell = self.grid.get_cell(*pos)
            hunter.log(f"Checking cell at {pos} → type: {cell.cell_type.name}, content: {repr(cell.content)}")

        valid_known_treasures = [
            pos for pos in hunter.known_treasures
            if self.grid.get_cell(*pos).cell_type == CellType.TREASURE and
               isinstance(self.grid.get_cell(*pos).content, Treasure)
        ]

        hunter.log(f"Valid known treasures: {valid_known_treasures}")

        if valid_known_treasures:
            sorted_treasures = sorted(
                valid_known_treasures,
                key=lambda pos: (
                    abs(hunter.x - pos[0]) + abs(hunter.y - pos[1]),
                    -self.grid.get_cell(*pos).content.value
                )
            )
            hunter.log(f"Sorted treasures by distance & value: {sorted_treasures}")

            for treasure_pos in sorted_treasures:
                hunter.log(f"Trying path to treasure at {treasure_pos}")
                path = astar(self.grid, (hunter.x, hunter.y), treasure_pos)
                if path:
                    hunter.log(f"Path found: {path}")
                    is_safe = all(
                        self.grid.get_cell(*pos).cell_type not in [
                            CellType.KNIGHT, CellType.GARRISON, CellType.HIDEOUT
                        ]
                        for pos in path
                    )
                    hunter.log(f"Path safety: {'SAFE' if is_safe else 'UNSAFE'}")
                    if is_safe:
                        return path
                else:
                    hunter.log(f"No path found to {treasure_pos}")

        neighbors = self.grid.get_neighbors(hunter.x, hunter.y)
        hunter.log(f"Scanning nearby cells: {neighbors}")

        best_treasure = None
        best_value = -1

        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            if cell.cell_type == CellType.TREASURE and isinstance(cell.content, Treasure):
                hunter.log(f"Nearby treasure at ({nx}, {ny}) with value {cell.content.value}")
                if cell.content.value > best_value:
                    best_value = cell.content.value
                    best_treasure = (nx, ny)

        if best_treasure:
            hunter.log(f"Found nearby treasure at {best_treasure}")
            return [best_treasure]

        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            if cell.is_empty():
                hunter.log(f"No treasure found — fallback to empty cell at ({nx}, {ny})")
                return [(nx, ny)]

        hunter.log("No valid path or fallback cell found.")
        return None

    def get_safe_path_to_hideout(self, hunter):
        """
        Returns a safe path to the nearest known hideout or a valid adjacent cell to move into.
        Priority:
        1. First safe known hideout (path has no knight/garrison and hideout has space)
        2. Nearby hideout (adjacent cell)
        3. Any valid adjacent cell (not knight, garrison, or another hunter)
        """

        hunter.log("Searching for safe path to hideout.")
        hunter.log(f"Known hideouts: {hunter.known_hideouts}")

        if hunter.known_hideouts:
            sorted_hideouts = sorted(
                hunter.known_hideouts,
                key=lambda pos: abs(hunter.x - pos[0]) + abs(hunter.y - pos[1])
            )

            for hideout_pos in sorted_hideouts:
                hunter.log(f"Trying path to hideout at {hideout_pos}")
                path = astar(self.grid, (hunter.x, hunter.y), hideout_pos)
                hunter.log(f"Path to hideout: {path}")
                if path:
                    hunter.log(f"A* path found to {hideout_pos}: {path}")
                    dangerous = any(self.grid.get_cell(*pos).cell_type.name in ["GARRISON", "KNIGHT"] for pos in path)
                    if dangerous:
                        hunter.log(f"Path includes danger (Garrison/Knight), skipping.")
                        continue

                    target_cell = self.grid.get_cell(*path[-1])
                    if target_cell.cell_type == CellType.HIDEOUT:
                        hideout = target_cell.content
                        if hideout:
                            hunter.log(
                                f"Hideout at ({target_cell.x}, {target_cell.y}) has {len(hideout.hunters)} / {hideout.capacity}")
                            if len(hideout.hunters) < hideout.capacity:
                                hunter.log(f"Safe path confirmed to hideout at {hideout_pos}")
                                return path
                        else:
                            hunter.log(f"Target cell marked as HIDEOUT has no content.")

                else:
                    hunter.log(f"No path found to {hideout_pos}")

        hunter.log("Checking adjacent neighbors for direct hideout entry...")
        neighbors = self.grid.get_neighbors(hunter.x, hunter.y)
        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            hunter.log(f"Neighbor at ({nx}, {ny}) → type: {cell.cell_type}")
            if cell.cell_type == CellType.HIDEOUT:
                hideout = cell.content
                if hideout:
                    hunter.log(f"Adjacent hideout at ({nx}, {ny}) → {len(hideout.hunters)} / {hideout.capacity}")
                    if len(hideout.hunters) < hideout.capacity:
                        hunter.log(f"Entering adjacent hideout at ({nx}, {ny})")
                        return [(nx, ny)]
                else:
                    hunter.log(f"Adjacent hideout at ({nx}, {ny}) has no content.")

        hunter.log("Looking for valid fallback cell...")
        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            hunter.log(f"Checking neighbor ({nx}, {ny}) → type: {cell.cell_type}")
            if cell.cell_type not in [CellType.GARRISON, CellType.KNIGHT, CellType.HUNTER]:
                hunter.log(f"Valid fallback move to ({nx}, {ny})")
                return [(nx, ny)]

        hunter.log("No safe move available — waiting.")
        return None

