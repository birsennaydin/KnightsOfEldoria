from utils.enums import HunterSkill, CellType
from utils.constants import (
    HUNTER_STAMINA_LOSS_PER_MOVE,
    HUNTER_CRITICAL_STAMINA,
    HUNTER_REST_GAIN,
    HUNTER_COLLAPSE_STEPS
)
from nlp.sentiment_analyzer import analyze_sentiment


class Hunter:
    def __init__(self, name: str, skill: HunterSkill):
        # Identity
        self.name = name
        self.skill = skill

        # Position
        self.x = 0
        self.y = 0

        # State
        self.stamina = 1.0  # 100%
        self.carrying = None  # Can carry one Treasure
        self.alive = True
        self.collapsing = False
        self.steps_since_collapse = 0

        # Memory
        self.known_treasures = []
        self.known_hideouts = []
        self.known_knight_locations = []  # NEW: Memory of knight patrols

        # Links
        self.hideout = None

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

    def remember_knight(self, x, y):
        if (x, y) not in self.known_knight_locations:
            self.known_knight_locations.append((x, y))

    def scan_and_remember(self, nearby_cells):
        """Scan surrounding cells and remember what is seen."""
        for cell in nearby_cells:
            if cell.cell_type == CellType.TREASURE:
                self.remember_treasure(cell.x, cell.y)
            elif cell.cell_type == CellType.HIDEOUT:
                self.remember_hideout(cell.x, cell.y)
            elif cell.cell_type == CellType.KNIGHT:
                self.remember_knight(cell.x, cell.y)

    def can_collect(self, treasure):
        return self.carrying is None or treasure.value > self.carrying.value

    def wants_to_return(self):
        """Hunter wants to return if carrying treasure."""
        return self.carrying is not None

    def is_at_hideout(self):
        """Check if hunter is in their assigned hideout."""
        return self.hideout and (self.x, self.y) == (self.hideout.x, self.hideout.y)

    def deliver_treasure(self):
        """Deliver treasure to the hideout."""
        if self.carrying and self.is_at_hideout():
            self.hideout.receive_treasure(self)

    def log(self, message):
        print(f"[Hunter:{self.name}] {message}")

    def express_opinion(self, text):
        score = analyze_sentiment(text)
        mood = "🙂 Positive" if score > 0 else "😐 Neutral" if score == 0 else "🙁 Negative"
        print(f"[{self.name} says] \"{text}\" → Sentiment: {mood} ({score:.2f})")

    def __repr__(self):
        skill = self.skill.name.title()
        status = "Dead" if not self.alive else "Collapsing" if self.collapsing else "Active"
        return f"Hunter({self.name}, {skill}, {status}, {self.stamina:.2f})"
