from models.hunter import Hunter
from utils.enums import HunterSkill

def test_hunter_is_weak():
    hunter = Hunter("Test", HunterSkill.STEALTH)
    hunter.stamina = 0.05
    assert hunter.is_weak()
