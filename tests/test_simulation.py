# tests/test_simulation_controller.py

import pytest
from controllers.simulation_controller import SimulationController
from utils.enums import TreasureType, HunterSkill, CellType
from models.treasure import Treasure
from models.hunter import Hunter
from models.knight import Knight
from models.hideout import Hideout

# Fixture for a clean controller
@pytest.fixture
def sim():
    controller = SimulationController()
    controller.hunters.clear()
    controller.knights.clear()
    controller.hideouts.clear()
    controller.treasures.clear()
    controller.garrisons.clear()
    return controller

def test_add_treasure_to_list(sim):
    treasure = Treasure(TreasureType.GOLD, 3, 3)
    assert treasure not in sim.treasures
    sim.add_treasure_to_list(treasure)
    assert treasure in sim.treasures

def test_remove_treasure_from_list(sim):
    treasure = Treasure(TreasureType.SILVER, 1, 1)
    sim.treasures.append(treasure)
    sim.remove_treasure_from_list(treasure)
    assert treasure not in sim.treasures

def test_remove_hunter_from_list(sim):
    hunter = Hunter("TestHunter", HunterSkill.STEALTH, 0, 0)
    sim.hunters.append(hunter)
    sim.grid.place_hunter(hunter)
    sim.remove_hunter_from_list(hunter)
    assert hunter not in sim.hunters
    assert sim.grid.get_cell(0, 0).is_empty()

def test_grid_initialization_size():
    sim = SimulationController()
    assert sim.grid.size == 20
    assert len(sim.grid.cells) == 20
    assert len(sim.grid.cells[0]) == 20

def test_populate_random_grid_sets_some_entities():
    sim = SimulationController()
    assert len(sim.treasures) > 0
    assert len(sim.hunters) > 0
    assert len(sim.knights) > 0
    assert len(sim.hideouts) > 0
    assert len(sim.garrisons) > 0
