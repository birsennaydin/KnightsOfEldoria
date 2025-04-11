import random

from models.knight import Knight
from utils.constants import RECRUIT_PROBABILITY

class Garrison:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.capacity = 5
        self.knights = []  # Garrison'da bulunan knight'lar
        self.knight_patrols = []  # Knightların yakın zamanda yaptığı devriye


    def add_knight(self, knight):
        """Add knight to the garrison for resting."""
        # Eğer knight dinlenmeye ihtiyacı varsa, garrison'a ekleyin
        self.knights.append(knight)
        knight.resting = True
        knight.garrison = self  # Garrison'ı knight'a atıyoruz
        knight.rest()  # Knight dinlenmeye başlar
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
        Tüm bilinen devriye ve garrison bilgilerini paylaşıyoruz.
        """
        all_knight_patrols = set()
        for knight in self.knights:
            all_knight_patrols.update(knight.memory)

        for knight in self.knights:
            knight.memory = list(set(knight.memory) | all_knight_patrols)
            # Diğer knight'lar için paylaşılan bilgi
            knight.known_knight_patrols = self.knight_patrols

    def try_recruit(self):
            new_name = f"Recruit-{self.x}-{self.y}-{random.randint(100, 999)}"
            new_knight = Knight(new_name, self.x, self.y)
            self.add_knight(new_knight)
            new_knight.log(f"has been recruited with skill: {new_knight.name}")


    def rest_knights(self):
        """
        Garrison'da dinlenmek için knight'ların enerji yenilemesi işlemi.
        """
        for knight in self.knights:
            if knight.is_exhausted():
                knight.rest()
                print(f"{knight.name} is resting at the garrison.")
