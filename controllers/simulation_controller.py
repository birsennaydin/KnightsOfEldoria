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
from utils.logger import log  # Loglama fonksiyonu


class SimulationController:
    def __init__(self, grid_size=GRID_MIN_SIZE):
        self.grid = Grid(grid_size)
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []
        self.step_count = 0
        self.treasures_delivered = 0  # Optional: track delivered treasures

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

        # Decay all treasures
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                cell = self.grid.get_cell(x, y)
                if cell.cell_type == CellType.TREASURE and cell.content:
                    cell.content.decay()
                    if cell.content.is_depleted():
                        log(f"[Treasure] {cell.content.type.name.title()} at ({x}, {y}) depleted and removed.")
                        cell.clear()

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
                    log("⚠️ No space to place recruited hunter.")

        # Step summary log
        alive_hunters = len([h for h in self.hunters if h.alive])
        active_knights = len([k for k in self.knights if not k.resting])
        treasures_on_grid = self.count_remaining_treasures()

        log(f"[Step {self.step_count}] Hunters alive: {alive_hunters} | Knights active: {active_knights} | Treasures remaining: {treasures_on_grid}")

    def run(self, steps=100):
        for _ in range(steps):
            if self.count_remaining_treasures() == 0 or not any(h.alive for h in self.hunters):
                log("🛑 Simulation ended: No more treasures or hunters left.")
                break
            self.step()
            self.print_grid()

    def print_grid(self):
        """Print the current state of the grid to the terminal."""
        print(f"\n--- Grid at Step {self.step_count} ---")
        for y in range(self.grid.size):
            row = ""
            for x in range(self.grid.size):
                cell = self.grid.get_cell(x, y)
                if cell.cell_type == CellType.HUNTER:
                    row += " H "
                elif cell.cell_type == CellType.KNIGHT:
                    row += " K "
                elif cell.cell_type == CellType.TREASURE:
                    row += " T "
                elif cell.cell_type == CellType.HIDEOUT:
                    row += " D "
                else:
                    row += " . "
            print(row)
        print("-" * (self.grid.size * 3))

    def count_remaining_treasures(self):
        """Count number of treasures currently on the grid."""
        count = 0
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                cell = self.grid.get_cell(x, y)
                if cell.cell_type == CellType.TREASURE:
                    count += 1
        return count
