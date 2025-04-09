from utils.enums import CellType


# Knight class with interaction methods and movement
class Knight:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.energy = 1.0
        self.resting = False
        self.target = None
        self.memory = []
        self.alive = True
        self.garrison = None

    def log(self, message: str):
        from utils.logger import log
        log(f"[Knight] {self.name}: {message}")

    def move(self):
        if not self.alive:  # If the knight is dead, do not allow movement
            self.log(f"{self.name} cannot move because they are dead.")
            return

        if self.energy <= 0:
            self.die()
            return

        self.energy -= 0.02
        if self.energy < 0:
            self.energy = 0
            self.die()  # If energy reaches 0, the knight dies

    def is_exhausted(self):
        return self.energy <= 0.2

    def rest(self):
        """Garrison'da dinlenme."""
        self.energy += 0.1
        if self.energy > 1.0:
            self.energy = 1.0  # Enerji 100% geçmemeli

    def remember(self, location):
        self.memory.append(location)

    def detect_hunters(self, nearby_cells):
        """Return a list of hunters within nearby cells (used for knight detection)."""
        hunters = []
        for cell in nearby_cells:
            if cell and cell.cell_type == CellType.HUNTER:
                hunters.append(cell.content)
        return hunters

    def should_rest(self) -> bool:
        """
        Determine if the knight should rest based on energy level.
        Returns True if energy is 20% or below.
        """
        if not self.alive:  # If the knight is dead, they cannot decide to rest
            return False
        return self.energy <= 0.2

    def die(self):
        """Mark the knight as dead."""
        self.alive = False
        self.log(f"{self.name} has fallen. They are no longer alive.")

    def choose_target(self, hunters):
        """
        Choose the closest hunter as the target.
        This is a simple heuristic; you can modify this based on other factors.
        """
        if not hunters:
            return None

        # Choose the hunter closest to the knight (using Manhattan distance)
        target = min(hunters, key=lambda hunter: abs(hunter.x - self.x) + abs(hunter.y - self.y))
        self.target = target

    def move_to(self, x, y):
        """
        Move the knight to the specified coordinates and update their position.
        """
        self.x = x
        self.y = y
        self.log(f"{self.name} moved to ({self.x}, {self.y})")

    def interact_with_hunter(self, hunter, method: str):
        """
        Interacts with a hunter, either detaining or challenging them.
        :param hunter: The hunter the knight is interacting with.
        :param method: The action method (either 'detain' or 'challenge').
        """
        if method == "detain":
            # If detaining, reduce hunter's stamina and force them to drop their treasure
            hunter.stamina -= 0.05  # Decrease hunter's stamina by 5%
            hunter.drop_treasure()  # Assuming a drop_treasure method exists in the Hunter class
            self.log(f"Detained {hunter.name}, reduced stamina and forced to drop treasure.")
        elif method == "challenge":
            # If challenging, reduce hunter's stamina more severely and force them to drop their treasure
            hunter.stamina -= 0.20  # Decrease hunter's stamina by 20%
            hunter.drop_treasure()  # Assuming a drop_treasure method exists in the Hunter class
            self.log(f"Challenged {hunter.name}, reduced stamina significantly and forced to drop treasure.")
        else:
            self.log(f"Unknown interaction method: {method}")