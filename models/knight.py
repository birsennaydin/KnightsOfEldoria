from utils.constants import (
    KNIGHT_ENERGY_LOSS_PER_CHASE,
    KNIGHT_REST_GAIN,
    KNIGHT_REST_THRESHOLD
)


class Knight:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.energy = 1.0  # 100%
        self.resting = False
        self.target = None  # Hunter object (if any)

    def detect_hunters(self, nearby_cells):
        """Return a list of hunters detected in nearby cells."""
        hunters = []
        for cell in nearby_cells:
            if cell.cell_type.name == "HUNTER":
                hunters.append(cell.content)
        return hunters

    def choose_target(self, hunters):
        """Choose one hunter to pursue (basic strategy: first one)."""
        if hunters:
            self.target = hunters[0]
            return self.target
        return None

    def chase(self):
        """Chase the target, losing energy per pursuit."""
        if self.energy > KNIGHT_REST_THRESHOLD and self.target:
            self.energy -= KNIGHT_ENERGY_LOSS_PER_CHASE
            if self.energy <= 0:
                self.energy = 0
                self.resting = True

    def rest(self):
        """Recover energy while resting."""
        self.energy = min(1.0, self.energy + KNIGHT_REST_GAIN)
        if self.energy > KNIGHT_REST_THRESHOLD:
            self.resting = False

    def should_rest(self):
        """Determine if knight should go into resting mode."""
        return self.energy <= KNIGHT_REST_THRESHOLD

    def interact_with_hunter(self, hunter, method="detain"):
        """Detain or challenge a hunter, forcing them to drop their treasure."""
        if not hunter.alive:
            return

        if method == "detain":
            hunter.stamina = max(0.0, hunter.stamina - 0.05)
        elif method == "challenge":
            hunter.stamina = max(0.0, hunter.stamina - 0.20)

        # Drop treasure and remember the location
        if hunter.carrying:
            lost_treasure_location = (hunter.x, hunter.y)
            hunter.remember_treasure(*lost_treasure_location)
            hunter.carrying = None

    def log(self, message):
        print(f"[Knight:{self.name}] {message}")

    def __repr__(self):
        status = "Resting" if self.resting else "Active"
        return f"Knight({self.name}, {status}, Energy: {self.energy:.2f})"
