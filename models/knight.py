from utils.constants import (
    KNIGHT_ENERGY_LOSS_PER_CHASE,
    KNIGHT_REST_THRESHOLD,
    KNIGHT_REST_GAIN
)
from utils.logger import log
from textblob import TextBlob


class Knight:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.energy = 1.0  # 100%
        self.resting = False
        self.target = None  # Currently pursued Hunter

    def detect_hunters(self, nearby_cells):
        return [cell.content for cell in nearby_cells if cell.cell_type.name == "HUNTER" and cell.content and cell.content.alive]

    def choose_target(self, hunters):
        if hunters:
            self.target = hunters[0]

    def chase(self):
        if self.target and self.energy >= KNIGHT_ENERGY_LOSS_PER_CHASE:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
            self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
            self.energy -= KNIGHT_ENERGY_LOSS_PER_CHASE

    def should_rest(self):
        return self.energy <= KNIGHT_REST_THRESHOLD

    def rest(self):
        self.energy = min(1.0, self.energy + KNIGHT_REST_GAIN)
        if self.energy > KNIGHT_REST_THRESHOLD:
            self.resting = False

    def interact_with_hunter(self, hunter, method="detain"):
        if method == "detain":
            hunter.alive = False

    def log(self, message):
        log(f"[Knight - {self.name} @ ({self.x}, {self.y})]: {message}")

    def express_opinion(self, message):
        sentiment = TextBlob(message).sentiment.polarity
        mood = "positive 😊" if sentiment > 0.2 else "negative 😠" if sentiment < -0.2 else "neutral 😐"
        log(f"[Knight - {self.name}]: '{message}' → Sentiment: {mood}")
