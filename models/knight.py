import random

from ai.pathfinding.astar import astar
from utils.enums import CellType


# Knight class with interaction methods and movement
class Knight:
    def __init__(self, name: str, x: int, y: int, grid):
        self.name = name
        self.x = x
        self.y = y
        self.grid = grid
        self.energy = 1.0
        self.resting = False
        self.target = None
        self.memory = []
        self.alive = True
        self.garrison = None

    def log(self, message: str):
        from utils.logger import log
        log(f"[Knight] {self.name}: {message}")

    def rest_at_garrison(self):
        """
        Resting function inside the garrison:
        If the knight's energy falls below 20%, they go to the nearest garrison and rest.
        """
        if self.is_exhausted() and self.garrison:  # If knight is exhausted and has a garrison
            self.resting = True
            self.garrison.add_knight(self)  # Add the knight to the garrison
            self.rest()  # Start the resting process
            print(f"{self.name} is resting at the garrison.")

    def move(self):

        # If energy is low do not allow movement
        if self.is_exhausted():
            self.log(f"{self.name} cannot move because they should rest.")
            return

        self.energy -= 0.02
        if self.is_exhausted():
            if self.energy <= 0:
                self.energy = 0
            self.resting = True
            return

    def is_exhausted(self):
        return self.energy <= 0.2

    def rest(self):
        """Resting at the garrison."""
        print(f"{self} - KNIGHT REST.")
        self.energy += 0.1
        if self.energy >= 1.0:
            self.energy = 1.0  # Energy should not exceed 100%
            self.resting = False
            print(f"{self} - KNIGHT ENERGY IS READY.")
            # When rest is complete, remove the knight from the garrison
            if self.garrison:
                print(f"{self.name} THERE IS GARRISON. {self.garrison}")
                self.garrison.remove_knight(self)
            print(f"{self.name} REMOVE FROM GARRISON. {self.garrison}")

    def remember(self, location):
        self.memory.append(location)

    def detect_hunters(self, nearby_cells):
        """Return a list of hunters within nearby cells (used for knight detection)."""
        hunters = []
        for cell in nearby_cells:
            if cell:
                self.log(f"Scanning cell ({cell.x}, {cell.y}) → {cell.cell_type.name} | content: {cell.content}")
            if cell and cell.cell_type == CellType.HUNTER and cell.content:
                self.log(f"⚔️ FOUND HUNTER at ({cell.x}, {cell.y})")
                hunters.append(cell.content)
        return hunters

    def should_rest(self) -> bool:
        """
        Determine if the knight should rest based on energy level.
        Returns True if energy is 20% or below.
        """
        return self.energy <= 0.2

    def choose_target(self, hunters):
        """
        Choose the closest hunter as the target.
        This is a simple heuristic; you can modify this based on other factors.
        """
        if not hunters:
            return None

        best_target = None
        best_cost = float('inf')

        for h in hunters:
            path = astar(self.grid, (self.x, self.y), (h.x, h.y), role="knight")
            if path and len(path) < best_cost:
                best_target = h
                best_cost = len(path)

        self.target = best_target
        if best_target:
            self.log(
                f"Target selected: {best_target.name} at ({best_target.x}, {best_target.y}) with path length {best_cost}")
        else:
            self.log("No reachable target found with A*")

    def move_to(self, x, y):
        """
        Move the knight to the specified coordinates and update their position.
        """
        old_cell = self.grid.get_cell(self.x, self.y)
        if old_cell:
            old_cell.clear()

        self.x = x
        self.y = y

        new_cell = self.grid.get_cell(x, y)
        if new_cell:
            new_cell.set_content(self, CellType.KNIGHT)

        self.log(f"{self.name} moved to ({self.x}, {self.y})")

    def interact_with_hunter(self, hunter, method: str):
        """
        Interacts with a hunter, either detaining or challenging them.
        :param hunter: The hunter the knight is interacting with.
        :param method: The action method (either 'detain' or 'challenge').
        """
        if method == "detain":
            hunter.stamina -= 0.05
            hunter.drop_treasure(self.grid, self.grid.simulation_controller)
            self.log(f"Detained {hunter.name}, reduced stamina and forced to drop treasure.")
        elif method == "challenge":
            hunter.stamina -= 0.20
            hunter.drop_treasure(self.grid, self.grid.simulation_controller)
            self.log(f"Challenged {hunter.name}, reduced stamina significantly and forced to drop treasure.")
        else:
            self.log(f"Unknown interaction method: {method}")
