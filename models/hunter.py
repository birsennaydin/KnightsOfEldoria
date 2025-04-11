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
        if self.carrying:
            self.hideout.stored_treasures.append(self.carrying)
            self.log(
                f"delivered treasure: {self.carrying.treasure_type.name} → Hideout @ ({self.hideout.x}, {self.hideout.y})"
            )
            self.carrying = None

    def collect_treasure(self, treasure):
        self.carrying = treasure

    def scan_and_remember(self, nearby_cells):
        self.log(f"NEARBY CELL. {nearby_cells}")
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
        self.collapse_counter += 1
        self.log(f"is collapsing... ({self.collapse_counter}/3)")
        if self.collapse_counter >= 3:
            self.alive = False
            self.log("has collapsed and is eliminated.")

    def log(self, message):
        log(f"[Hunter] {self.name}: {message}")

    def drop_treasure(self):
        """
        Drops the treasure the hunter is carrying (if any).
        """
        if self.carrying:
            self.carrying = None  # Drops the treasure
            self.log(f"{self.name} dropped their treasure.")
