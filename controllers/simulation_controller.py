import random
from models.grid import Grid
from models.treasure import Treasure
from models.hunter import Hunter
from models.knight import Knight
from models.hideout import Hideout
from controllers.hunter_controller import HunterController
from controllers.knight_controller import KnightController
from utils.enums import TreasureType, HunterSkill, CellType
from utils.constants import GRID_MIN_SIZE


class SimulationController:
    def __init__(self, grid_size=GRID_MIN_SIZE):
        self.grid = Grid(grid_size)
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []
        self.step_count = 0

        # Initialize controllers
        self.hunter_controller = HunterController(self.grid)
        self.knight_controller = KnightController(self.grid)

    def add_treasure(self, x, y, treasure_type=TreasureType.GOLD):
        treasure = Treasure(treasure_type)
        cell = self.grid.get_cell(x, y)
        cell.set_content(treasure, cell_type=CellType.TREASURE)
        self.treasures.append(treasure)

    def add_hunter(self, name, skill, x, y):
        hunter = Hunter(name, skill)
        hunter.x = x
        hunter.y = y
        cell = self.grid.get_cell(x, y)
        cell.set_content(hunter, cell_type=CellType.HUNTER)
        self.hunters.append(hunter)

    def add_knight(self, name, x, y):
        knight = Knight(name, x, y)
        cell = self.grid.get_cell(x, y)
        cell.set_content(knight, cell_type=CellType.KNIGHT)
        self.knights.append(knight)

    def add_hideout(self, x, y):
        hideout = Hideout(x, y)
        cell = self.grid.get_cell(x, y)
        cell.set_content(hideout, cell_type=CellType.HIDEOUT)
        self.hideouts.append(hideout)

    def step(self):
        """Perform a single simulation step."""
        self.step_count += 1

        # Process all hunters
        for hunter in self.hunters:
            self.hunter_controller.process(hunter)

        # Process all knights
        for knight in self.knights:
            self.knight_controller.process(knight)

        # Process hideouts (rest, share knowledge, recruit)
        for hideout in self.hideouts:
            hideout.rest_all()
            hideout.share_knowledge()
            new_hunter = hideout.attempt_recruit()

            if new_hunter:
                # Try placing the new hunter in a random empty cell
                placed = False
                for _ in range(20):
                    x = random.randint(0, self.grid.size - 1)
                    y = random.randint(0, self.grid.size - 1)
                    cell = self.grid.get_cell(x, y)
                    if cell.is_empty():
                        new_hunter.x = x
                        new_hunter.y = y
                        cell.set_content(new_hunter, CellType.HUNTER)
                        self.hunters.append(new_hunter)
                        placed = True
                        break

                if not placed:
                    print("No space to place recruited hunter.")

    def run(self, steps=100):
        """Run the simulation for the given number of steps."""
        for _ in range(steps):
            self.step()
