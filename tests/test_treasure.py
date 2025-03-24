from models.treasure import Treasure
from utils.enums import TreasureType
from utils.constants import TREASURE_MIN_VALUE, TREASURE_DECAY_PERCENT


def test_treasure_decay():
    treasure = Treasure(TreasureType.GOLD)
    initial_value = treasure.value
    treasure.decay()
    assert treasure.value == max(TREASURE_MIN_VALUE, initial_value - TREASURE_DECAY_PERCENT)


def test_treasure_depletion():
    treasure = Treasure(TreasureType.BRONZE)
    treasure.value = 0.00001
    treasure.decay()
    assert treasure.is_depleted()
