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
        if len(self.knights) < self.capacity:
            self.knights.append(knight)
            knight.garrison = self  # Knight, garrison'a atandı

    def remove_knight(self, knight):
        if knight in self.knights:
            self.knights.remove(knight)
            knight.garrison = None  # Knight, garrison'dan çıkarıldı

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

    def rest_knights(self):
        """
        Garrison'da dinlenmek için knight'ların enerji yenilemesi işlemi.
        """
        for knight in self.knights:
            if knight.is_exhausted():
                knight.rest()
                print(f"{knight.name} is resting at the garrison.")
