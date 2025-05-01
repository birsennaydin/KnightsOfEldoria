from utils.enums import CellType


class Cell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.content = None          # The entity currently in this cell (e.g., Treasure, Hunter, etc.)
        self.cell_type = CellType.EMPTY  # The type of the content occupying this cell

    def is_empty(self) -> bool:
        return self.cell_type == CellType.EMPTY

    def set_content(self, content, cell_type: CellType):
        self.content = content
        self.cell_type = cell_type

    def set_transit_content(self, content, cell_type: CellType):
        if self.cell_type in [CellType.HIDEOUT, CellType.GARRISON]:
            print(
                f"⚠️ Cannot overwrite static cell at ({self.x}, {self.y}) - current type={self.cell_type}. Ignoring set_transit_content.")
            return
        self.content = content
        self.cell_type = cell_type

    def clear(self):
        """Clear the cell content unless it is a permanent structure like a Hideout or Garrison."""
        print(f"🧹 CLEARING CELL ({self.x}, {self.y}) - TYPE: {self.cell_type.name} - TYPE: {self.cell_type}")
        if self.cell_type not in [CellType.HIDEOUT, CellType.GARRISON]:
            self.cell_type = CellType.EMPTY
            self.content = None
            print(f"🧹 CLEARING CELL01 ({self.x}, {self.y}) - TYPE: {self.cell_type.name} - TYPE: {self.cell_type}")
        else:
            print(f"⛔ Cell NOT cleared (protected type): ({self.x}, {self.y}) → {self.cell_type.name}")

    def __repr__(self):
        return f"Cell({self.x}, {self.y}): {self.cell_type.name}"
