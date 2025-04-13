from models.treasure import Treasure
from utils.enums import TreasureType
from utils.constants import TREASURE_MIN_VALUE, TREASURE_DECAY_PERCENT


def test_treasure_decay():
    # Create a treasure with a given type and position
    treasure = Treasure(TreasureType.GOLD, x=5, y=5)
    initial_value = treasure.value
    treasure.decay()
    # Check if the value decays correctly but does not go below the minimum
    assert treasure.value == max(TREASURE_MIN_VALUE, initial_value - TREASURE_DECAY_PERCENT)


def test_treasure_depletion():
    # Create a treasure with a low value close to depletion
    treasure = Treasure(TreasureType.BRONZE, x=2, y=3)
    treasure.value = 0.00001
    treasure.decay()
    # After decay, the treasure should be considered depleted
    assert treasure.is_depleted()
