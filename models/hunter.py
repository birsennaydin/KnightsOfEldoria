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
        self.name = name
        self.skill = skill
        self.stamina = 1.0
        self.carrying = None
        self.hideout = None
        self.known_treasures = []
        self.known_hideouts = []
        self.known_knight_locations = []
        self.steps_since_collapse = 0
        self.collapsing = False
        self.alive = True
        self.x = None
        self.y = None

    def move(self):
        if self.alive and not self.collapsing:
            self.stamina -= HUNTER_STAMINA_LOSS_PER_MOVE
            if self.stamina <= 0:
                self.stamina = 0
                self.collapsing = True
                self.steps_since_collapse = 0

    def rest(self):
        if self.alive and not self.collapsing:
            self.stamina = min(1.0, self.stamina + HUNTER_REST_GAIN)

    def collapse_check(self):
        if self.collapsing:
            self.steps_since_collapse += 1
            if self.steps_since_collapse >= HUNTER_COLLAPSE_STEPS:
                self.alive = False

    def is_weak(self):
        return self.stamina <= HUNTER_CRITICAL_STAMINA

    def collect_treasure(self, treasure):
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
        for cell in nearby_cells:
            if cell.cell_type == CellType.TREASURE:
                self.remember_treasure(cell.x, cell.y)
            elif cell.cell_type == CellType.HIDEOUT:
                self.remember_hideout(cell.x, cell.y)
            elif cell.cell_type == CellType.KNIGHT:
                self.remember_knight(cell.x, cell.y)

    def deliver_treasure(self):
        if self.hideout and self.carrying:
            self.hideout.receive_treasure(self)
            self.carrying = None

    def wants_to_return(self):
        return self.carrying is not None or self.is_weak()

    def is_at_hideout(self):
        return self.hideout and self.x == self.hideout.x and self.y == self.hideout.y

    def express_opinion(self, text: str):
        """
        Express a sentence and get sentiment analysis result.
        """
        score = analyze_sentiment(text)
        mood = "🙂 Positive" if score > 0 else "😐 Neutral" if score == 0 else "🙁 Negative"
        print(f"[{self.name} says] \"{text}\" → Sentiment: {mood} ({score:.2f})")

    def log(self, message):
        print(f"[Hunter {self.name}] {message}")

    def __repr__(self):
        skill = self.skill.name.title()
        status = "Dead" if not self.alive else "Collapsing" if self.collapsing else "Active"
        return f"Hunter({self.name}, {skill}, {status}, {self.stamina:.2f})"
