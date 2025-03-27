import random
import time
from models.grid import Grid
from models.hunter import Hunter
from models.knight import Knight
from models.treasure import Treasure
from models.hideout import Hideout
from utils.enums import HunterSkill, TreasureType
from controllers.hunter_controller import HunterController
from controllers.knight_controller import KnightController
from view.gui import Gui


class SimulationController:
    def __init__(self):
        self.grid = Grid(size=20)
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []

        self.hunter_controller = HunterController(self.grid)
        self.knight_controller = KnightController(self.grid)

        self._populate_random_grid()
        self.gui = Gui(self.grid)

    def _populate_random_grid(self):
        size = self.grid.size
        total_cells = size * size
        all_positions = [(x, y) for x in range(size) for y in range(size)]
        random.shuffle(all_positions)

        num_empty = int(total_cells * 0.5)
        num_treasure = int(total_cells * 0.2)
        num_knight = int(total_cells * 0.15)
        num_hunter = int(total_cells * 0.1)
        num_hideout = int(total_cells * 0.05)

        for _ in range(num_treasure):
            x, y = all_positions.pop()
            t_type = random.choice(list(TreasureType))
            treasure = Treasure(t_type, x, y)
            self.grid.place_treasure(treasure)
            self.treasures.append(treasure)

        for _ in range(num_knight):
            x, y = all_positions.pop()
            knight = Knight(f"Knight-{x}-{y}", x, y)
            self.grid.place_knight(knight)
            self.knights.append(knight)

        for _ in range(num_hunter):
            x, y = all_positions.pop()
            skill = random.choice(list(HunterSkill))
            hunter = Hunter(f"Hunter-{x}-{y}", skill, x, y)
            self.grid.place_hunter(hunter)
            self.hunters.append(hunter)

        for _ in range(num_hideout):
            x, y = all_positions.pop()
            hideout = Hideout(x, y)
            self.grid.place_hideout(hideout)
            self.hideouts.append(hideout)

    def run(self, steps=100):
        for step in range(steps):
            if self.gui.is_closed():
                break

            for hunter in self.hunters:
                self.hunter_controller.process(hunter)

            for knight in self.knights:
                self.knight_controller.process(knight)

            for treasure in list(self.treasures):
                treasure.decay()
                if treasure.is_depleted():
                    self.grid.clear_cell(treasure.x, treasure.y)
                    self.treasures.remove(treasure)

            for hideout in self.hideouts:
                hideout.share_knowledge()
                hideout.try_recruit()

            # === Termination Condition ===
            active_hunters = any(h.alive for h in self.hunters)
            if not self.treasures or not active_hunters:
                print("✅ Simulation stopped: No treasure or no active hunters left.")
                break

            self.gui.render()
            time.sleep(0.2)
