import random

from models.hunter import Hunter
from utils.constants import RECRUIT_PROBABILITY
from utils.enums import CellType


class Hideout:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.capacity = 5
        self.hunters = []
        self.knight_patrols = []  # Track recent knight patrols
        self.stored_treasures = []  # Store delivered treasures

    def add_hunter(self, hunter, grid):
        hunter.log(f"entered hideout at ({self.x}, {self.y})")
        # Add hunter to the hideout if there is available capacity
        if len(self.hunters) < self.capacity:
            self.hunters.append(hunter)
            hunter.in_hideout = self
            grid.clear_cell(hunter.x, hunter.y)
            hunter.log(f"entered hideout at There is capacity({self.capacity}, {len(self.hunters)})")

    def remove_hunter(self, hunter, grid):
        # Remove hunter from the hideout
        hunter.in_hideout = None
        if hunter in self.hunters:
            self.hunters.remove(hunter)

            neighbors = grid.get_neighbors(self.x, self.y)
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if grid.get_cell(nx, ny).is_empty():
                    hunter.x, hunter.y = nx, ny
                    grid.get_cell(nx, ny).set_transit_content(hunter, CellType.HUNTER)
                    hunter.log(f"left hideout and moved to ({nx}, {ny})")
                    break

    def share_knowledge(self):
        """
        Share all known treasures and hideouts among hunters in this hideout.
        """
        all_treasures = set()
        all_hideouts = set()

        for h in self.hunters:
            all_treasures.update(h.known_treasures)
            all_hideouts.update(h.known_hideouts)

        for h in self.hunters:
            h.known_treasures = list(set(h.known_treasures) | all_treasures)
            h.known_hideouts = list(set(h.known_hideouts) | all_hideouts)
            # Also share knight patrol information
            h.known_knight_patrols = self.knight_patrols

    def try_recruit(self, grid):
        """
        Attempt to recruit a new hunter with 20% probability
        if hideout is not full and has a variety of skills.
        """
        # Do not recruit if hideout is already full
        if len(self.hunters) >= self.capacity:
            return

        # Check for diversity in hunter skills
        existing_skills = list({h.skill for h in self.hunters})
        if len(existing_skills) < 2:
            return  # Not enough diversity

        # 20% chance to recruit a new hunter
        if random.random() <= RECRUIT_PROBABILITY:
            new_skill = random.choice(existing_skills)
            new_name = f"Recruit-{self.x}-{self.y}-{random.randint(100, 999)}"
            new_hunter = Hunter(new_name, new_skill, self.x, self.y)
            self.add_hunter(new_hunter, grid)  # Create new hunter with one of the existing diverse skills
            new_hunter.log(f"has been recruited with skill: {new_skill.name}")

    def __str__(self):
        """String representation of the hunter."""
        return f"Hideout(capacity={self.capacity}, x={self.x}, y={self.y}, hunters={self.hunters}, knıghts_patrols={self.knight_patrols}, stored_treasure={self.stored_treasures})"

    def __repr__(self):
        return self.__str__()