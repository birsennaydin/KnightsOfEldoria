import random

from models.knight import Knight
from utils.constants import RECRUIT_PROBABILITY

class Garrison:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.capacity = 5
        self.knights = []  # Knights currently in the garrison
        self.knight_patrols = []  # Patrols recently performed by knights

    def add_knight(self, knight):
        """Add knight to the garrison for resting."""
        # If the knight needs rest, add to the garrison
        self.knights.append(knight)
        knight.resting = True
        knight.garrison = self  # Assign this garrison to the knight
        knight.rest()  # Start resting process
        print(f"{knight.name} is resting at the garrison. Function: add_knight")

    def remove_knight(self, knight):
        """Remove knight from the garrison when fully rested."""
        if knight in self.knights:
            self.knights.remove(knight)
            knight.resting = False
            knight.garrison = None
            print(f"{knight.name} has left the garrison.")

    def share_knowledge(self):
        """
        Share all known patrol and garrison-related information among all knights.
        """
        all_knight_patrols = set()
        for knight in self.knights:
            all_knight_patrols.update(knight.memory)

        for knight in self.knights:
            knight.memory = list(set(knight.memory) | all_knight_patrols)
            # Shared patrol information for other knights
            knight.known_knight_patrols = self.knight_patrols

    def try_recruit(self):
        """
        Attempt to recruit a new knight to the garrison.
        """
        new_name = f"Recruit-{self.x}-{self.y}-{random.randint(100, 999)}"
        new_knight = Knight(new_name, self.x, self.y)
        self.add_knight(new_knight)
        new_knight.log(f"has been recruited with skill: {new_knight.name}")

    def rest_knights(self):
        """
        Restore energy of knights resting in the garrison.
        """
        for knight in self.knights:
            if knight.is_exhausted():
                knight.rest()
                print(f"{knight.name} is resting at the garrison.")
