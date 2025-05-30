import random

from utils.enums import CellType
from utils.logger import log
from nlp.sentiment_analyzer import analyze_sentiment

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
        self.log(f"Stamina before move: {self.stamina:.2f}")
        self.stamina = round(self.stamina - 0.02, 2)
        self.log(f"Stamina after move: {self.stamina:.2f}")
        if self.stamina <= 0:
            self.stamina = 0
            self.collapsing = True

    def rest(self, grid):
        self.stamina = round(min(1.0, self.stamina + 0.01), 2)
        if self.stamina >= 1.0:
            self.stamina = 1.0
            self.collapsing = False
            self.collapse_counter = 0
            if self.in_hideout is not None:
                self.in_hideout.remove_hunter(self, grid)
                self.log(f"Fully rested and left the hideout at ({self.x}, {self.y})")

    def is_resting_in_hideout(self):
        return self.in_hideout is not None

    def wants_to_return(self):
        return self.carrying is not None

    def deliver_treasure(self, simulation_controller):
        # Deliver the carried treasure to the hideout
        if self.carrying:
            if self.in_hideout is not None:
                self.in_hideout.stored_treasures.append(self.carrying)
                self.log(
                    f"Delivered treasure: {self.carrying.treasure_type.name} → Hideout @ ({self.in_hideout.x}, {self.in_hideout.y})"
                )
                simulation_controller.remove_treasure_from_list(self.carrying)
                self.carrying = None

    def collect_treasure(self, treasure):
        self.carrying = treasure

    def scan_and_remember(self, nearby_cells):
        for cell in nearby_cells:
            if cell.cell_type.name == "TREASURE" and cell.content:
                pos = (cell.x, cell.y)
                if pos not in self.known_treasures:
                    self.known_treasures.append(pos)
                    self.log(f"New treasure remembered at {pos}")
            elif cell.cell_type.name == "HIDEOUT" and cell.content:
                pos = (cell.x, cell.y)
                if pos not in self.known_hideouts:
                    self.known_hideouts.append(pos)
                    self.log(f"New hideout remembered at {pos}")
            elif cell.cell_type.name == "KNIGHT" and cell.content:
                pos = (cell.x, cell.y)
                if pos not in self.known_knights:
                    self.known_knights.append(pos)
                    self.log(f"New knight remembered at {pos}")

    def collapse_check(self):
        self.collapse_counter += 1
        self.log(f"Collapse check: ({self.collapse_counter}/3)")
        if self.collapse_counter >= 3:
            self.alive = False
            self.log("Hunter has collapsed and is eliminated.")

    def log(self, message):
        log(f"[Hunter] {self.name}: {message}")

    def drop_treasure(self, grid, simulation_controller=None):
        if not self.carrying:
            return

        old_x, old_y = self.x, self.y
        treasure = self.carrying

        neighbors = grid.get_neighbors(self.x, self.y)
        random.shuffle(neighbors)
        for new_x, new_y in neighbors:
            cell = grid.get_cell(new_x, new_y)
            if cell.is_empty():
                # Move hunter to new location
                grid.clear_cell(self.x, self.y)
                self.x, self.y = new_x, new_y
                grid.get_cell(self.x, self.y).set_transit_content(self, CellType.HUNTER)

                # Drop treasure in old cell
                treasure.x, treasure.y = old_x, old_y
                grid.get_cell(old_x, old_y).set_transit_content(treasure, CellType.TREASURE)

                # Add treasure back to simulation list
                if simulation_controller:
                    simulation_controller.add_treasure_to_list(treasure)

                # Add drop location to known treasures
                if (old_x, old_y) not in self.known_treasures:
                    self.known_treasures.append((old_x, old_y))

                # Clear carried treasure
                self.carrying = None
                self.log(f"Dropped treasure at ({old_x}, {old_y}) and fled to ({new_x}, {new_y})")
                self.analyze_emotion_and_log("Dropped treasure due to knight interaction.")
                return

    def analyze_emotion_and_log(self, message: str):
        sentiment_score = analyze_sentiment(message)
        self.log(f"Sentiment analysis of '{message}' → polarity: {sentiment_score:.2f}")
        return sentiment_score

    def __str__(self):
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
