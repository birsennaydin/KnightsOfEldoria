import pytest
from controllers.simulation_controller import SimulationController
from utils.enums import TreasureType, HunterSkill, CellType
from models.treasure import Treasure
from models.hunter import Hunter
from models.knight import Knight
from models.hideout import Hideout


def test_add_treasure():
    sim = SimulationController(grid_size=10)
    sim.add_treasure(2, 2, TreasureType.SILVER)
    cell = sim.grid.get_cell(2, 2)
    assert cell.cell_type == CellType.TREASURE
    assert isinstance(cell.content, Treasure)


def test_add_hunter():
    sim = SimulationController(grid_size=10)
    sim.add_hideout(0, 0)  # Ensure at least one hideout exists
    sim.add_hunter("Birsen", HunterSkill.NAVIGATION, 1, 1)
    cell = sim.grid.get_cell(1, 1)
    assert cell.cell_type == CellType.HUNTER
    assert isinstance(cell.content, Hunter)


def test_add_knight():
    sim = SimulationController(grid_size=10)
    sim.add_knight("Melisa", 5, 5)
    cell = sim.grid.get_cell(5, 5)
    assert cell.cell_type == CellType.KNIGHT
    assert isinstance(cell.content, Knight)


def test_add_hideout():
    sim = SimulationController(grid_size=10)
    sim.add_hideout(0, 0)
    cell = sim.grid.get_cell(0, 0)
    assert cell.cell_type == CellType.HIDEOUT
    assert isinstance(cell.content, Hideout)


def test_count_remaining_treasures():
    sim = SimulationController(grid_size=10)
    sim.add_treasure(1, 1, TreasureType.GOLD)
    sim.add_treasure(2, 2, TreasureType.SILVER)
    assert sim.count_remaining_treasures() == 2
