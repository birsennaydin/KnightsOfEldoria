class Treasure:
    def __init__(self, treasure_type, x, y):
        self.treasure_type = treasure_type
        self.x = x
        self.y = y
        self.value = self._get_initial_value()

    def _get_initial_value(self):
        if self.treasure_type.name == "BRONZE":
            return 3.0
        elif self.treasure_type.name == "SILVER":
            return 7.0
        elif self.treasure_type.name == "GOLD":
            return 13.0
        return 1.0

    def decay(self):
        self.value = max(0.0, self.value - 0.1)

    def is_depleted(self):
        return self.value <= 0