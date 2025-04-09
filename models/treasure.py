class Treasure:
    def __init__(self, treasure_type, x, y):
        self.treasure_type = treasure_type
        self.x = x
        self.y = y
        self.value = self._get_initial_value()
        print("✅ İNİT ", self.value)

    def _get_initial_value(self):
        print("✅ TREASURE TYPEget_initial_value: ", self.treasure_type.name)
        if self.treasure_type.name == "BRONZE":
            print("✅ 00000: ", self.treasure_type.name)
            return 3.0
        elif self.treasure_type.name == "SILVER":
            print("✅ 11111: ", self.treasure_type.name)
            return 7.0
        elif self.treasure_type.name == "GOLD":
            print("✅ 222222: ", self.treasure_type.name)
            return 13.0
        return 1.0

    def decay(self):
        print("✅ TREASURE TYPEdecay00: ", self.value)
        self.value = max(0.0, self.value - 0.1)
        print("✅ TREASURE TYPEdecay11: ", self.value)

    def is_depleted(self):
        print("✅ TREASURE TYPE self value: ", self.value)
        return self.value <= 0

    def __str__(self):
        return f"Treasure(type={self.treasure_type.name}, x={self.x}, y={self.y}, value={self.value})"