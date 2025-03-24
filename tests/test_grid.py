from models.grid import Grid
from models.cell import Cell
from utils.constants import GRID_MIN_SIZE

def test_wrap_coordinates():
    grid = Grid(size=GRID_MIN_SIZE)
    expected = (GRID_MIN_SIZE - 1, GRID_MIN_SIZE - 1)
    assert grid.wrap(-1, -1) == expected

def test_get_cell():
    grid = Grid(size=5)
    cell = grid.get_cell(1, 1)
    assert isinstance(cell, Cell)
    assert cell.x == 1 and cell.y == 1
