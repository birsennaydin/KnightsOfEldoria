from enum import Enum

class CellType(Enum):
    EMPTY = 0
    TREASURE = 1
    HUNTER = 2
    KNIGHT = 3
    HIDEOUT = 4

class TreasureType(Enum):
    BRONZE = 3     # +3% wealth
    SILVER = 7     # +7% wealth
    GOLD = 13      # +13% wealth

class HunterSkill(Enum):
    NAVIGATION = 1
    ENDURANCE = 2
    STEALTH = 3

class KnightAction(Enum):
    NONE = 0
    DETAIN = 1        # -5% stamina + drop treasure
    CHALLENGE = 2     # -20% stamina + drop treasure

class EntityStatus(Enum):
    ACTIVE = 1
    RESTING = 2
    COLLAPSING = 3
    ELIMINATED = 4
