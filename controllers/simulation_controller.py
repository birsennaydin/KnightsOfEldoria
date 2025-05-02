import random
import sys
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
        sys.stdout = open("simulation_log.txt", "w", buffering=1)

        self.grid = Grid(size=20, simulation_controller=self)
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []
        self.garrisons = []

        self.hunter_controller = HunterController(self.grid, self)
        self.knight_controller = KnightController(self.grid)

        print(f"SIMULATION CONTROLLER IS STARTING: {self}", flush=True)

        self._populate_random_grid()
        self.gui = Gui(self.grid, self)

    def remove_treasure_from_list(self, treasure):
        """Remove the treasure from the simulation."""
        print(f"TREASURE REMOVED: {treasure}")
        if treasure in self.treasures:
            self.treasures.remove(treasure)
        print(f"CURRENT TREASURES: {len(self.treasures)}, {self.treasures}")

    def add_treasure_to_list(self, treasure):
        """Add the treasure back to the simulation list if it's not already present."""
        if treasure not in self.treasures:
            self.treasures.append(treasure)
            print(f"TREASURE ADDED BACK: {treasure}")

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

        num_empty = int(total_cells * 0.60)
        num_treasure = int(total_cells * 0.04)
        num_knight = int(total_cells * 0.04)
        num_hunter = int(total_cells * 0.20)
        num_hideout = int(total_cells * 0.10)
        num_garrison = int(total_cells * 0.02)

        print(f"Grid Initialization: empty={num_empty}, treasure={num_treasure}, knight={num_knight}, "
              f"hunter={num_hunter}, hideout={num_hideout}, garrison={num_garrison}")

        # Place garrisons on the grid
        for _ in range(num_garrison):
            x, y = all_positions.pop()
            garrison = Garrison(x, y)
            self.grid.place_garrison(garrison)
            self.garrisons.append(garrison)
        # Place treasures on the grid
        for _ in range(num_treasure):
            x, y = all_positions.pop()
            t_type = random.choice(list(TreasureType))
            treasure = Treasure(t_type, x, y)
            self.grid.place_treasure(treasure)
            self.treasures.append(treasure)
        # Place knights on the grid
        for _ in range(num_knight):
            x, y = all_positions.pop()
            knight = Knight(f"Knight-{x}-{y}", x, y, self.grid)
            self.grid.place_knight(knight)
            self.knights.append(knight)

        # Place hunters on the grid
        for _ in range(num_hunter):
            x, y = all_positions.pop()
            skill = random.choice(list(HunterSkill))
            hunter = Hunter(f"Hunter-{x}-{y}", skill, x, y)
            self.grid.place_hunter(hunter)
            self.hunters.append(hunter)

        # Place hideouts on the grid
        for _ in range(num_hideout):
            x, y = all_positions.pop()
            hideout = Hideout(x, y)
            self.grid.place_hideout(hideout)
            self.hideouts.append(hideout)

        # Ensure remaining cells are empty
        for _ in range(num_empty):
            x, y = all_positions.pop()
            self.grid.get_cell(x, y).clear()

    def run(self, steps=300):
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
                    print("Treasure depleted:", treasure)
                    self.grid.clear_cell(treasure.x, treasure.y)
                    self.treasures.remove(treasure)
            # Let hideouts share knowledge and attempt to recruit
            for hideout in self.hideouts:
                hideout.share_knowledge()
                hideout.try_recruit(self.grid)

            print(f"Step {step + 1} Summary: treasures={len(self.treasures)}, "
                  f"all_carrying_none={all(hunter.carrying is None for hunter in self.hunters)}, "
                  f"stored_empty={all(len(h.stored_treasures) == 0 for h in self.hideouts)}, "
                  f"hunters_alive={any(h.alive for h in self.hunters)}")

            no_active_treasure = (
                len(self.treasures) == 0 and
                all(hunter.carrying is None for hunter in self.hunters)
            )
            all_hunters_dead = all(not h.alive for h in self.hunters)

            if no_active_treasure or all_hunters_dead:
                print("Simulation ended: No more treasures or all hunters are inactive.")
                break

            self.gui.render()
            time.sleep(0.2)

    def __str__(self):
        return (
            f"\n--- SimulationController ---\n"
            f"Grid Size: {self.grid.size} x {self.grid.size}\n\n"
            f"Hunters ({len(self.hunters)}):\n" +
            "\n".join(f"  - {hunter}" for hunter in self.hunters) + "\n\n" +
            f"Knights ({len(self.knights)}):\n" +
            "\n".join(f"  - {knight}" for knight in self.knights) + "\n\n" +
            f"Hideouts ({len(self.hideouts)}):\n" +
            "\n".join(f"  - {hideout}" for hideout in self.hideouts) + "\n\n" +
            f"Treasures ({len(self.treasures)}):\n" +
            "\n".join(f"  - {treasure}" for treasure in self.treasures) + "\n\n" +
            f"Garrisons ({len(self.garrisons)}):\n" +
            "\n".join(f"  - {garrison}" for garrison in self.garrisons) + "\n"
        )
