from utils.enums import TreasureType
from utils.constants import TREASURE_DECAY_PERCENT, TREASURE_MIN_VALUE


class Treasure:
    def __init__(self, treasure_type: TreasureType):
        self.type = treasure_type
        self.value = float(treasure_type.value)  # starting value: 3 / 7 / 13

    def decay(self):
        """Decrease the value of the treasure slightly each simulation step."""
        self.value = max(TREASURE_MIN_VALUE, self.value - TREASURE_DECAY_PERCENT)
        print("Self Value:", self.value)

    def is_depleted(self) -> bool:
        """Check if treasure has lost all its value."""
        return self.value <= TREASURE_MIN_VALUE

    def __repr__(self):
        return f"{self.type.name.title()} Treasure ({self.value:.2f}%)"
