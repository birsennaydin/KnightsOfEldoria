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
        self.known_treasures = []
        self.known_hideouts = []
        self.known_knights = []
        self.alive = True
        self.collapsing = False
        self.collapse_counter = 0
        self.resting = False
        self.assigned_hideout = None
        self.in_hideout = None

    def move(self):
        self.log(f"Before movement Stamina: {self.stamina}")
        self.stamina -= 0.02
        self.log(f"After movement Stamina: {self.stamina}")
        if self.stamina <= 0:
            self.stamina = 0
            self.collapsing = True

    def rest(self, grid):
        self.stamina = min(1.0, self.stamina + 0.01)

        if self.stamina >= 1.0:
            self.stamina = 1.0
            self.collapsing = False
            self.collapse_counter = 0

            if self.in_hideout is not None:
                # Remove from the hideout
                self.in_hideout.remove_hunter(self, grid)
                self.log(f"fully rested and left the hideout at ({self.x}, {self.y})")

    def is_resting_in_hideout(self):
        self.log(f"is_resting_in_hideout ({self.in_hideout} , Stamina:{self.stamina})")
        return self.in_hideout is not None

    def wants_to_return(self):
        return self.carrying is not None

    def deliver_treasure(self, simulation_controller):
        # Deliver the carried treasure to the hideout
        if self.carrying:
            self.log(
                f"delivered treasure: {self.carrying} → In Hıdeout {self.in_hideout})"
            )
            if self.in_hideout is not None:
                self.in_hideout.stored_treasures.append(self.carrying)
                self.log(
                    f"delivered treasure: {self.carrying.treasure_type.name} → Hideout @ ({self.in_hideout.x}, {self.in_hideout.y})"
                )
                simulation_controller.remove_treasure_from_list(self.carrying)
                self.carrying = None

    def collect_treasure(self, treasure):
        # Pick up the treasure
        self.carrying = treasure

    def scan_and_remember(self, nearby_cells):
        # Scan nearby cells to remember treasure and hideout positions
        for cell in nearby_cells:
            self.log(f"SCAN AND REMEMBER. {cell}, CELL NAME: {cell.cell_type.name}, CONTENT: {cell.content}")
            if cell.cell_type.name == "TREASURE" and cell.content:
                self.log(f"SCAN TREASURE. {cell.x},{cell.y}, knownTREASURE: {self.known_treasures}")
                pos = (cell.x, cell.y)
                if pos not in self.known_treasures:
                    self.known_treasures.append(pos)
                    self.log(f"APPEND TREASURE {self.known_treasures}")
            elif cell.cell_type.name == "HIDEOUT" and cell.content:
                self.log(f"SCAN HIDEOUT. {cell.x},{cell.y}, knownHIDEOUT: {self.known_hideouts}")
                pos = (cell.x, cell.y)
                if pos not in self.known_hideouts:
                    self.known_hideouts.append(pos)
                    self.log(f"APPEND HIDEOUT {self.known_hideouts}")
            elif cell.cell_type.name == "KNIGHT" and cell.content:
                self.log(f"SCAN KNIGHT. {cell.x},{cell.y}, known KNIGHT: {self.known_knights}")
                pos = (cell.x, cell.y)
                if pos not in self.known_knights:
                    self.known_knights.append(pos)
                    self.log(f"APPEND KNIGHT {self.known_knights}")

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
        if not self.carrying:
            return

        old_x, old_y = self.x, self.y
        treasure = self.carrying

        # Find valid escape cells
        neighbors = grid.get_neighbors(self.x, self.y)
        random.shuffle(neighbors)
        for new_x, new_y in neighbors:
            cell = grid.get_cell(new_x, new_y)
            if cell.is_empty():
                # Move hunter to new location
                grid.clear_cell(self.x, self.y)
                self.x, self.y = new_x, new_y
                grid.get_cell(self.x, self.y).set_content(self, CellType.HUNTER)

                # Drop treasure in old cell
                treasure.x, treasure.y = old_x, old_y
                grid.get_cell(old_x, old_y).set_content(treasure, CellType.TREASURE)

                # Add treasure back to simulation list
                if simulation_controller:
                    simulation_controller.add_treasure_to_list(treasure)

                # Add drop location to known treasures
                if (old_x, old_y) not in self.known_treasures:
                    self.known_treasures.append((old_x, old_y))

                # Clear carried treasure
                self.carrying = None
                self.log(f"dropped treasure at ({old_x}, {old_y}) and fled to ({new_x}, {new_y})")
                return

    def __str__(self):
        """Multiline string representation of the hunter."""
        return (
            f"Hunter:\n"
            f"  Name: {self.name}\n"
            f"  Position: ({self.x}, {self.y})\n"
            f"  Stamina: {self.stamina}\n"
            f"  Carrying: {self.carrying}\n"
            f"  Skill: {self.skill}\n"
            f"  Alive: {self.alive}\n"
            f"  Collapsed Counter: {self.collapse_counter}\n"
            f"  Resting: {self.resting}\n"
            f"  Collapsing: {self.collapsing}\n"
            f"  Known Treasures: {self.known_treasures}\n"
            f"  Known Hideouts: {self.known_hideouts}\n"
            f"  Known Knights: {self.known_knights}\n"
        )

    def __repr__(self):
        return self.__str__()