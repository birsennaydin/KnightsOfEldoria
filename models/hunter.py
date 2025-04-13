import random

from utils.enums import CellType
from utils.logger import log

class Hunter:
    def __init__(self, name, skill, x, y):
        self.name = name
        self.skill = skill
        self.x = x
        self.y = y
        self.stamina = 1.0
        self.carrying = None
        self.hideout = None
        self.known_treasures = []
        self.known_hideouts = []
        self.alive = True
        self.collapsing = False
        self.collapse_counter = 0

    def move(self):
        self.stamina -= 0.02
        if self.stamina <= 0:
            self.stamina = 0
            self.collapsing = True

    def rest(self):
        self.stamina = min(1.0, self.stamina + 0.01)

    def is_at_hideout(self):
        return self.hideout and self.x == self.hideout.x and self.y == self.hideout.y

    def wants_to_return(self):
        return self.carrying is not None

    def deliver_treasure(self):
        # Deliver the carried treasure to the hideout
        if self.carrying:
            self.hideout.stored_treasures.append(self.carrying)
            self.log(
                f"delivered treasure: {self.carrying.treasure_type.name} → Hideout @ ({self.hideout.x}, {self.hideout.y})"
            )
            self.carrying = None

    def collect_treasure(self, treasure):
        # Pick up the treasure
        self.carrying = treasure

    def scan_and_remember(self, nearby_cells):
        # Scan nearby cells to remember treasure and hideout positions
        for cell in nearby_cells:
            self.log(f"SCAN AND REMEMBER. {cell}")
            if cell.cell_type.name == "TREASURE" and cell.content:
                pos = (cell.x, cell.y)
                if pos not in self.known_treasures:
                    self.known_treasures.append(pos)
            elif cell.cell_type.name == "HIDEOUT" and cell.content:
                pos = (cell.x, cell.y)
                if pos not in self.known_hideouts:
                    self.known_hideouts.append(pos)

    def collapse_check(self):
        # Increment collapse counter and check if hunter has fully collapsed
        self.collapse_counter += 1
        self.log(f"is collapsing... ({self.collapse_counter}/3)")
        if self.collapse_counter >= 3:
            self.alive = False
            self.log("has collapsed and is eliminated.")

    def log(self, message):
        log(f"[Hunter] {self.name}: {message}")

    def drop_treasure(self, grid, simulation_controller=None):
        """
        Drops the treasure at the current location, then moves hunter to a random nearby empty cell.
        Also remembers the drop location for future retrieval.
        """
        self.log(f"DROP TREASURE - SIMULATION CONTROLLER: {simulation_controller}")
        self.log(f"DROP TREASURE - IS CARRYING: {self.carrying}")
        if not self.carrying:
            return

        old_x, old_y = self.x, self.y
        treasure = self.carrying

        self.log(f"DROP TREASURE - TREASURE {treasure}")
        self.log(f"DROP TREASURE - Hunter location: {self.x} {self.y}")

        # Find valid escape cells
        neighbors = grid.get_neighbors(self.x, self.y)
        self.log(f"DROP TREASURE - NEIGHBORS: {neighbors}")
        random.shuffle(neighbors)
        for new_x, new_y in neighbors:
            self.log(f"DROP TREASURE - FOR EACH: {new_x}-{new_y}")
            cell = grid.get_cell(new_x, new_y)
            self.log(f"DROP TREASURE - CELL: {cell}")
            if cell.is_empty():
                self.log(f"DROP TREASURE - CELL IS EMPTY?")
                # Move hunter to new location
                grid.clear_cell(self.x, self.y)
                self.log(f"DROP TREASURE - HUNTER OLD LOCATION? {self.x}, {self.y} and {old_x}, {old_y}")
                self.x, self.y = new_x, new_y
                self.log(f"DROP TREASURE - HUNTER NEW LOCATION? {self.x}, {self.y}")
                grid.get_cell(self.x, self.y).set_content(self, CellType.HUNTER)

                # Drop treasure in old cell
                treasure.x, treasure.y = old_x, old_y
                self.log(f"DROP TREASURE - TREASURE NEW LOCATION? {treasure.x}, {treasure.y}")
                self.log(f"DROP TREASURE - TREASURE {treasure}")
                grid.get_cell(old_x, old_y).set_content(treasure, CellType.TREASURE)

                # Add treasure back to simulation list
                if simulation_controller:
                    self.log(f"DROP TREASURE - ADD SIMULATION LIST")
                    simulation_controller.add_treasure_to_list(treasure)

                # Add drop location to known treasures
                if (old_x, old_y) not in self.known_treasures:
                    self.log(f"DROP TREASURE - KNOWN TREASURE LIST {self.known_treasures}")
                    self.log(f"DROP TREASURE - TREASURE there is not in KNOWN TREASURE LIST")
                    self.known_treasures.append((old_x, old_y))
                    self.log(f"DROP TREASURE - KNOWN TREASURE LIST {self.known_treasures}")

                # Clear carried treasure
                self.carrying = None
                self.log(f"DROP TREASURE - CARRYING {self.carrying}")
                self.log(f"dropped treasure at ({old_x}, {old_y}) and fled to ({new_x}, {new_y})")
                return
