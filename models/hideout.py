import random

from models.hunter import Hunter
from utils.constants import HIDEOUT_CAPACITY, RECRUIT_PROBABILITY


class Hideout:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.hunters = []
        self.stored_treasures = []

    def enter(self, hunter):
        """Add hunter to the hideout if there's space."""
        if len(self.hunters) < HIDEOUT_CAPACITY:
            self.hunters.append(hunter)
            hunter.hideout = self
            self.receive_treasure(hunter)
            return True
        return False

    def receive_treasure(self, hunter):
        """Store treasure carried by hunter."""
        if hunter.carrying:
            self.stored_treasures.append(hunter.carrying)
            hunter.carrying = None

    def rest_all(self):
        """Restore stamina of all hunters resting here."""
        for hunter in self.hunters:
            if hunter.alive and not hunter.collapsing:
                hunter.rest()

    def share_knowledge(self):
        """Hunters in the hideout share known treasures, hideouts, and knight patrols."""
        all_treasures = set()
        all_hideouts = set()
        all_knights = set()

        for hunter in self.hunters:
            all_treasures.update(hunter.known_treasures)
            all_hideouts.update(hunter.known_hideouts)
            if hasattr(hunter, "known_knight_locations"):
                all_knights.update(hunter.known_knight_locations)

        for hunter in self.hunters:
            for loc in all_treasures:
                if loc not in hunter.known_treasures:
                    hunter.known_treasures.append(loc)
            for loc in all_hideouts:
                if loc not in hunter.known_hideouts:
                    hunter.known_hideouts.append(loc)
            if hasattr(hunter, "known_knight_locations"):
                for loc in all_knights:
                    if loc not in hunter.known_knight_locations:
                        hunter.known_knight_locations.append(loc)

    def attempt_recruit(self):
        """Recruit a new hunter if skill diversity and space conditions are met."""
        if len(self.hunters) >= 2 and len(self.hunters) < HIDEOUT_CAPACITY:
            skills = {hunter.skill for hunter in self.hunters}
            if len(skills) >= 2 and random.random() < RECRUIT_PROBABILITY:
                new_skill = random.choice(list(skills))
                return Hunter(name="Recruited", skill=new_skill)  # should be handled in controller
        return None

    def __repr__(self):
        return f"Hideout({self.x}, {self.y}) with {len(self.hunters)} hunters and {len(self.stored_treasures)} treasures"
