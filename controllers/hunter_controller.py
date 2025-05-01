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
            hunter.log(f"💀 Hunter is dead and removed from grid at ({hunter.x}, {hunter.y})")
            return

        # If the hunter is inside a hideout
        if hunter.is_resting_in_hideout():
            hunter.log(f"1111 hunter.is_at_hideout ({hunter.carrying}, {hunter})")
            if hunter.carrying:
                hunter.log(f"reached hideout at ({hunter.x}, {hunter.y})")
                hunter.deliver_treasure(self.simulation_controller)
                hunter.log("delivered treasure to hideout.")

            hunter.rest(self.grid)
            return

        # If stamina is exactly 0, set collapsing state if not already set
        if hunter.stamina == 0 and not hunter.collapsing:
            hunter.collapsing = True
            hunter.log("has reached 0 stamina and is collapsing.")

        # If the hunter is collapsing, perform collapse check
        if hunter.collapsing:
            hunter.collapse_check()
            return

        # If the hunter is carrying the treasure
        if hunter.carrying:
            hunter.log(f"✅ HUNTER CARRYİNG THE TR ({hunter.carrying})")
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
                    hunter.log(f"✅ HIDEOUT HUNTERS COUNT({len(hideout.hunters)},{hideout.hunters})")
                    if hideout and len(hideout.hunters) < hideout.capacity:

                        hideout.stored_treasures.append(hunter.carrying)
                        hunter.log(f"✅ Stored treasure in hideout at ({new_x}, {new_y}), HUNTER CARRYING: {hunter.carrying}")

                        self.simulation_controller.remove_treasure_from_list(hunter.carrying)
                        hunter.carrying = None

                        # Add hunter to the hideout
                        hideout.add_hunter(hunter, self.grid)
                        return  # Step ends here
                    else:
                        hunter.log(f"🚫 Hideout at ({new_x}, {new_y}) is full. Can't enter.")
                        hunter.move()  # still reduce stamina
                        return

                # If there is another hunter in the target cell, do not move
                if new_cell.cell_type == CellType.HUNTER:
                    hunter.log("🚫 Can't move, another hunter is in the target cell.")
                    hunter.move()  # Stamina -0.02

                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return

                # If the cell is TREASURE
                if new_cell.cell_type == CellType.TREASURE:
                    new_treasure = new_cell.content
                    if new_treasure.value > hunter.carrying.value:
                        hunter.log(f"🔄 Swapping carried treasure with better treasure at ({new_x}, {new_y})")

                        # Leave the old treasure at the current (old) position
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
                        hunter.log(
                            f"📦 Found lesser treasure at ({new_x}, {new_y}), keeping current treasure and moving over it.")

                        # Keeps the current treasure but moves over the lesser one
                        old_cell = self.grid.get_cell(hunter.x, hunter.y)
                        old_cell.clear()

                        # Drop the lesser treasure at the old position
                        old_cell.set_transit_content(new_treasure, CellType.TREASURE)

                        self.grid.clear_cell(new_x, new_y)
                        hunter.x, hunter.y = new_x, new_y
                        self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)

                    # Move and scan surroundings
                    hunter.move()
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)

                    return

                # Otherwise move one step forward
                hunter.log(f"🚶 Moving to empty cell at ({new_x}, {new_y})")

                old_cell = self.grid.get_cell(hunter.x, hunter.y)
                old_cell.clear()

                hunter.x, hunter.y = new_x, new_y
                self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)

                hunter.move()  # Stamina -0.02
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)

                return
            else:
                hunter.log("⚠️ Carrying treasure but no safe path to hideout found. Waiting...")

                # Even if not moving, stamina should decrease
                hunter.move()

                # Scan surroundings to possibly discover new hideouts
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)

                return

        if hunter.stamina <= 0.06:
            hunter.log("⚠️ Low stamina detected, attempting to reach nearest hideout...")

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
                        hunter.log(f"💤 Entering hideout at ({new_x}, {new_y}) to rest.")
                        hideout.add_hunter(hunter, self.grid)
                        return
                    else:
                        hunter.log(f"🚫 Hideout at ({new_x}, {new_y}) is full.")
                        hunter.move()
                        return

                elif new_cell.cell_type == CellType.HUNTER:
                    hunter.log("🚫 Another hunter blocks the path.")
                    hunter.move()
                    return

                elif new_cell.cell_type == CellType.TREASURE:
                    treasure = new_cell.content
                    hunter.carrying = treasure
                    hunter.log(f"📦 Picked up treasure at ({new_x}, {new_y}) with value {treasure.value}")

                    # Update the grid
                    self.grid.clear_cell(new_x, new_y)
                    old_cell.clear()

                    hunter.x, hunter.y = new_x, new_y
                    self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)

                    # Move and scan
                    hunter.move()
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return

                else:
                    # Normal step forward (like to empty cell)
                    old_cell.clear()

                    hunter.x, hunter.y = new_x, new_y
                    self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)

                    hunter.move()
                    nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                    hunter.scan_and_remember(nearby)
                    return
            else:
                hunter.log("⚠️ No hideout reachable, standing still to rest.")
                hunter.move()  # Reduce stamina
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                return
        else:
            hunter.log(f"🧭 Hunter Stamina is normal Searching for treasure... {hunter}")

            path = self.get_safe_path_to_treasure(hunter)
            hunter.log(f"🧭 Hunter Path... {path}, Hunter old location: {hunter.x}, {hunter.y}")
            if path:
                next_pos = path[0]
                hunter.log(f"🧭 Hunter Path Details... next_pos: {next_pos}, details nextposxy: {next_pos[0]}, {next_pos[1]}")
                dx = next_pos[0] - hunter.x
                dy = next_pos[1] - hunter.y
                hunter.log(f"🧭 Hunter differences xy: {dx}, {dy}")
                new_x, new_y = self.grid.wrap(hunter.x + dx, hunter.y + dy)
                hunter.log(f"🧭 Hunter new location xy: {new_x}, {new_y}")
                new_cell = self.grid.get_cell(new_x, new_y)
                hunter.log(f"🧭 Hunter new location CELL: {new_cell}")
                old_cell = self.grid.get_cell(hunter.x, hunter.y)
                hunter.log(f"🧭 Hunter OLD location CELL: {old_cell}")

                hunter.log(f"🧭 Hunter new location CELLTYPE: {new_cell.cell_type}, content: {new_cell.content}")
                if new_cell.cell_type == CellType.TREASURE:
                    treasure = new_cell.content
                    hunter.carrying = treasure
                    hunter.log(f"📦 Collected treasure at ({new_x}, {new_y}) worth {treasure.value}")
                    self.grid.clear_cell(new_x, new_y)

                old_cell.clear()
                hunter.x, hunter.y = new_x, new_y
                self.grid.get_cell(new_x, new_y).set_transit_content(hunter, CellType.HUNTER)

                hunter.move()
                hunter.log(f"📦 HUNTER AFTER MOVE ({hunter})")
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                hunter.log(f"❓ HEREEEEHUNTER:{hunter}")
                return
            else:
                hunter.log("❓ No path to treasure — waiting and scanning.")
                hunter.move()
                nearby = self.grid.get_cells_in_radius(hunter.x, hunter.y, 1)
                hunter.scan_and_remember(nearby)
                hunter.log(f"❓ HEREEEEHUNTER:{hunter}")
                return

    def get_safe_path_to_treasure(self, hunter):
        """
        Returns a safe path to the best known treasure,
        or scans nearby cells for treasure or empty fallback.
        """

        hunter.log("🔎 [DEBUG] get_safe_path_to_treasure called.")
        # === 1. If there are known treasures ===
        hunter.log(f"🔎 Known treasures: {hunter.known_treasures}")
        for pos in hunter.known_treasures:
            cell = self.grid.get_cell(*pos)
            hunter.log(f"🧪 Checking cell at {pos} → type: {cell.cell_type.name}, content: {repr(cell.content)}")

        valid_known_treasures = [
            pos for pos in hunter.known_treasures
            if self.grid.get_cell(*pos).cell_type == CellType.TREASURE and
               isinstance(self.grid.get_cell(*pos).content, Treasure)
        ]

        hunter.log(f"✅ Valid known treasures: {valid_known_treasures}")

        if valid_known_treasures:
            sorted_treasures = sorted(
                valid_known_treasures,
                key=lambda pos: (
                    abs(hunter.x - pos[0]) + abs(hunter.y - pos[1]),
                    -self.grid.get_cell(*pos).content.value
                )
            )
            hunter.log(f"📍 Sorted valid treasures by distance & value: {sorted_treasures}")

            for treasure_pos in sorted_treasures:
                hunter.log(f"🛣️ Attempting A* path to treasure at {treasure_pos}")
                path = astar(self.grid, (hunter.x, hunter.y), treasure_pos)
                if path:
                    hunter.log(f"✅ Path found: {path}")
                    is_safe = all(
                        self.grid.get_cell(*pos).cell_type not in [
                            CellType.KNIGHT, CellType.GARRISON, CellType.HIDEOUT
                        ]
                        for pos in path
                    )
                    hunter.log(f"🔐 Path safety: {'SAFE' if is_safe else 'UNSAFE'}")
                    if is_safe:
                        return path
                else:
                    hunter.log(f"❌ No path found to {treasure_pos}")

        # === 2. Check nearby (1-cell radius) for treasure ===
        neighbors = self.grid.get_neighbors(hunter.x, hunter.y)
        hunter.log(f"👁️ Nearby cells to scan: {neighbors}")

        best_treasure = None
        best_value = -1

        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            if cell.cell_type == CellType.TREASURE and isinstance(cell.content, Treasure):
                hunter.log(f"💎 Nearby treasure found at ({nx}, {ny}) with value {cell.content.value}")
                if cell.content.value > best_value:
                    best_value = cell.content.value
                    best_treasure = (nx, ny)

        if best_treasure:
            hunter.log(f"🔍 No known treasure, but found nearby treasure at {best_treasure}")
            return [best_treasure]  # If there's a nearby treasure

        # === 3. Fallback to empty cell ===
        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            if cell.is_empty():
                hunter.log(f"🔄 No treasure found — fallback to empty cell at ({nx}, {ny})")
                return [(nx, ny)]

        hunter.log("🚫 No valid path to treasure or movement fallback found.")
        return None  # No valid move

    def get_safe_path_to_hideout(self, hunter):
        """
        Returns a safe path to the nearest known hideout or a valid adjacent cell to move into.
        Priority:
        1. First safe known hideout (path has no knight/garrison and hideout has space)
        2. Nearby hideout (adjacent cell)
        3. Any valid adjacent cell (not knight, garrison, or another hunter)
        """

        hunter.log("🏠 [DEBUG] get_safe_path_to_hideout() called.")
        hunter.log(f"🔍 Known hideouts: {hunter.known_hideouts}, hunter: {hunter}")

        # === 1. If known hideouts exist, try them one by one ===
        if hunter.known_hideouts:
            sorted_hideouts = sorted(
                hunter.known_hideouts,
                key=lambda pos: abs(hunter.x - pos[0]) + abs(hunter.y - pos[1])
            )

            for hideout_pos in sorted_hideouts:
                hunter.log(f"🧭 Trying path to known hideout at {hideout_pos}, Sorted POST: {sorted_hideouts}")
                path = astar(self.grid, (hunter.x, hunter.y), hideout_pos)

                hunter.log(f"🧭 Known Hideout path: {path}")
                if path:
                    hunter.log(f"✅ A* path found to {hideout_pos}: {path}")
                    dangerous = any(self.grid.get_cell(*pos).cell_type.name in ["GARRISON", "KNIGHT"] for pos in path)
                    if dangerous:
                        hunter.log(f"⚠️ Path to {hideout_pos} is unsafe (includes Garrison/Knight), skipping. {dangerous}")
                        continue

                    target_cell = self.grid.get_cell(*path[-1])
                    if target_cell.cell_type == CellType.HIDEOUT:
                        hideout = target_cell.content
                        if hideout:
                            hunter.log(
                                f"🏠 Checking hideout at ({target_cell.x}, {target_cell.y}) → current count: {len(hideout.hunters)} / {hideout.capacity}")
                            if len(hideout.hunters) < hideout.capacity:
                                hunter.log(f"✅ Safe path confirmed to hideout at {hideout_pos}")
                                return path
                        else:
                            hunter.log(f"🚫 Target cell has no hideout content despite being of type HIDEOUT")
                else:
                    hunter.log(f"❌ No path found to {hideout_pos}")

        # === 2. Check nearby hideouts (adjacent cells) ===
        hunter.log("🔎 Checking adjacent neighbors for direct hideout entry...")
        neighbors = self.grid.get_neighbors(hunter.x, hunter.y)
        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            hunter.log(f"🟦 Neighbor at ({nx}, {ny}) → type: {cell.cell_type}")
            if cell.cell_type == CellType.HIDEOUT:
                hideout = cell.content
                if hideout:
                    hunter.log(
                        f"🏠 Found adjacent hideout at ({nx}, {ny}) → {len(hideout.hunters)} / {hideout.capacity}")
                    if len(hideout.hunters) < hideout.capacity:
                        hunter.log(f"✅ Entering nearby hideout at ({nx}, {ny})")
                        return [(nx, ny)]
                else:
                    hunter.log(f"🚫 Adjacent hideout cell at ({nx}, {ny}) has no content.")

        # === 3. If there's a valid traversable cell, move there ===
        hunter.log("🔄 No hideout available, searching fallback neighbor...")
        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            hunter.log(f"🧱 Checking fallback neighbor ({nx}, {ny}) → type: {cell.cell_type}")
            if cell.cell_type not in [CellType.GARRISON, CellType.KNIGHT, CellType.HUNTER]:
                hunter.log(f"✅ Fallback move to ({nx}, {ny}) allowed.")
                return [(nx, ny)]

        hunter.log("🚫 No safe move found — hunter must wait.")
        return None

