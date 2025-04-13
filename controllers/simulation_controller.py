import random
import time

from models.garrison import Garrison
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
        self.grid = Grid(size=20, simulation_controller=self)
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []
        self.garrisons = []

        self.hunter_controller = HunterController(self.grid, self)
        self.knight_controller = KnightController(self.grid)

        self._populate_random_grid()
        self.gui = Gui(self.grid)

    def remove_treasure_from_list(self, treasure):
        """Remove the treasure from the Simulation."""
        print(f"✅ TREASURE REMOVED000: {treasure}")
        if treasure in self.treasures:
            self.treasures.remove(treasure)
            print(f"✅ TREASURE REMOVED001: {treasure}")

    def add_treasure_to_list(self, treasure):
        """Add treasure back to simulation list if it's not already included."""
        print(f"✅ SHOULD TREASURE RE-ADDED TO SIMULATION?: {treasure}")
        if treasure not in self.treasures:
            self.treasures.append(treasure)
            print(f"✅ TREASURE RE-ADDED TO SIMULATION: {treasure}")

    def remove_hunter_from_list(self, hunter):
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            cell = self.grid.get_cell(hunter.x, hunter.y)
            cell.clear()

    def _populate_random_grid(self):
        size = self.grid.size
        total_cells = size * size
        all_positions = [(x, y) for x in range(size) for y in range(size)]
        random.shuffle(all_positions)

        num_empty = int(total_cells * 0.5)
        num_treasure = int(total_cells * 0.2)
        num_knight = int(total_cells * 0.12)
        num_hunter = int(total_cells * 0.1)
        num_hideout = int(total_cells * 0.05)
        num_garrison = int(total_cells * 0.03)

        # Add Garrisons to grid
        for _ in range(num_garrison):  # Place Garrisons
            x, y = all_positions.pop()
            garrison = Garrison(x, y)  # Garrison class
            self.grid.place_garrison(garrison)
            self.garrisons.append(garrison)

        for _ in range(num_treasure):
            x, y = all_positions.pop()
            t_type = random.choice(list(TreasureType))
            print(f"✅ SIMULATIONTR: {t_type}")
            treasure = Treasure(t_type, x, y)
            print(f"✅ SIMULATIONTR00:  {treasure}")

            self.grid.place_treasure(treasure)
            self.treasures.append(treasure)
            print("✅ SIMULATIONTR111: ", self.treasures)

        for _ in range(num_knight):
            x, y = all_positions.pop()
            knight = Knight(f"Knight-{x}-{y}", x, y, self.grid)
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

        # The remaining cells will be empty
        for _ in range(num_empty):
            x, y = all_positions.pop()
            self.grid.get_cell(x, y).clear()  # Ensures the cell is empty

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
                    print("✅ TREASURE REMOVE: ", self.treasures, treasure)

            # for just hunters which in the hideout
            for hideout in self.hideouts:
                hideout.share_knowledge()
                hideout.try_recruit()



            # === Termination Condition ===
            all_hunters_dead = all(not h.alive for h in self.hunters)
            if not self.treasures or all_hunters_dead:
                print("✅ Simulation stopped: No treasure or all hunters are dead.")
                break

            self.gui.render()
            time.sleep(0.2)
