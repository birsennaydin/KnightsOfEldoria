import random

from models.hunter import Hunter
from utils.constants import RECRUIT_PROBABILITY


class Hideout:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.capacity = 5
        self.hunters = []
        self.treasures = []
        self.knight_patrols = []  # Track recent knight patrols

    def store_treasure(self, treasure):
        self.treasures.append(treasure)

    def add_hunter(self, hunter):
        if len(self.hunters) < self.capacity:
            self.hunters.append(hunter)
            hunter.hideout = self

    def remove_hunter(self, hunter):
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            hunter.hideout = None

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
            # Share knight patrol information as well
            h.known_knight_patrols = self.knight_patrols

    def try_recruit(self):
        """
        Attempt to recruit a new hunter with 20% probability
        if hideout is not full and has a variety of skills.
        """
        if len(self.hunters) >= self.capacity:
            return

        if random.random() <= RECRUIT_PROBABILITY:
            existing_skills = list({h.skill for h in self.hunters})
            if not existing_skills:
                return

            new_skill = random.choice(existing_skills)
            new_name = f"Recruit-{self.x}-{self.y}-{random.randint(100, 999)}"
            new_hunter = Hunter(new_name, new_skill, self.x, self.y)
            self.add_hunter(new_hunter)
            new_hunter.log(f"has been recruited with skill: {new_skill.name}")