from utils.enums import HunterSkill, CellType
from utils.constants import (
    HUNTER_STAMINA_LOSS_PER_MOVE,
    HUNTER_CRITICAL_STAMINA,
    HUNTER_REST_GAIN,
    HUNTER_COLLAPSE_STEPS
)


class Hunter:
    def __init__(self, name: str, skill: HunterSkill):
        self.name = name
        self.skill = skill
        self.stamina = 1.0  # 100%
        self.carrying = None  # Can carry one Treasure
        self.hideout = None  # Link to assigned hideout
        self.known_treasures = []  # Memory of seen treasures (optional AI)
        self.known_hideouts = []
        self.steps_since_collapse = 0
        self.collapsing = False
        self.alive = True

    def move(self):
        """Simulate moving to another cell. Reduce stamina."""
        if self.alive and not self.collapsing:
            self.stamina -= HUNTER_STAMINA_LOSS_PER_MOVE
            if self.stamina <= 0:
                self.stamina = 0
                self.collapsing = True
                self.steps_since_collapse = 0

    def rest(self):
        """Regain stamina while in hideout."""
        if self.alive and not self.collapsing:
            self.stamina = min(1.0, self.stamina + HUNTER_REST_GAIN)

    def collapse_check(self):
        """Called each step while collapsing. After 3 steps, hunter dies."""
        if self.collapsing:
            self.steps_since_collapse += 1
            if self.steps_since_collapse >= HUNTER_COLLAPSE_STEPS:
                self.alive = False

    def is_weak(self):
        """Should the hunter go rest?"""
        return self.stamina <= HUNTER_CRITICAL_STAMINA

    def collect_treasure(self, treasure):
        """Pick up treasure if not already carrying one or if it is more valuable."""
        if self.carrying is None or treasure.value > self.carrying.value:
            self.carrying = treasure

    def remember_treasure(self, x, y):
        if (x, y) not in self.known_treasures:
            self.known_treasures.append((x, y))

    def remember_hideout(self, x, y):
        if (x, y) not in self.known_hideouts:
            self.known_hideouts.append((x, y))

    def scan_and_remember(self, nearby_cells):
        for cell in nearby_cells:
            if cell.cell_type == CellType.TREASURE:
                self.remember_treasure(cell.x, cell.y)
            elif cell.cell_type == CellType.HIDEOUT:
                self.remember_hideout(cell.x, cell.y)

    def can_collect(self, treasure):
        return self.carrying is None or treasure.value > self.carrying.value

    def __repr__(self):
        skill = self.skill.name.title()
        status = "Dead" if not self.alive else "Collapsing" if self.collapsing else "Active"
        return f"Hunter({self.name}, {skill}, {status}, {self.stamina:.2f})"
