class Treasure:
    def __init__(self, treasure_type, x, y):
        self.treasure_type = treasure_type
        self.x = x
        self.y = y
        self.value = self._get_initial_value()  # Set initial value based on treasure type

    def _get_initial_value(self):
        """Assign initial value based on the treasure type."""
        if self.treasure_type.name == "BRONZE":
            return 3.0
        elif self.treasure_type.name == "SILVER":
            return 7.0
        elif self.treasure_type.name == "GOLD":
            return 13.0
        return 1.0  # Default value if treasure type is unknown

    def decay(self):
        """Reduce the value of the treasure over time."""
        print("✅ TREASURE TYPEdecay00: ", self.value)
        self.value = max(0.0, self.value * (1 - 0.001))
        print("✅ TREASURE TYPEdecay11: ", self.value)

    def is_depleted(self):
        """Check if the treasure has no remaining value."""
        print("✅ TREASURE TYPE self value: ", self.value)
        return self.value <= 0

    def __str__(self):
        """String representation of the treasure."""
        return f"Treasure(type={self.treasure_type.name}, x={self.x}, y={self.y}, value={self.value})"

    def __repr__(self):
        return self.__str__()