import math

from models.treasure import Treasure
from utils.enums import TreasureType
from utils.constants import TREASURE_MIN_VALUE, TREASURE_DECAY_PERCENT


def test_treasure_decay():
    # Create a treasure with a given type and position
    treasure = Treasure(TreasureType.GOLD, x=5, y=5)
    initial_value = treasure.value
    treasure.decay()
    # Check if the value decays correctly but does not go below the minimum
    expected_value = max(TREASURE_MIN_VALUE, initial_value * (1 - TREASURE_DECAY_PERCENT))
    assert math.isclose(treasure.value, expected_value, rel_tol=1e-6)

def test_treasure_depletion():
    treasure = Treasure(TreasureType.BRONZE, x=2, y=3)
    treasure.value = 0.00001
    treasure.decay()
    assert math.isclose(treasure.value, 0.0, abs_tol=1e-5)
