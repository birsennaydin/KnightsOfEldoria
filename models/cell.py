from utils.enums import CellType


class Cell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.content = None          # The object in the cell (Treasure, Hunter, etc.)
        self.cell_type = CellType.EMPTY  # Type of the cell content

    def is_empty(self) -> bool:
        return self.cell_type == CellType.EMPTY

    def set_content(self, content, cell_type: CellType):
        self.content = content
        self.cell_type = cell_type

    def clear(self):
        """Remove content from the cell."""
        self.content = None
        self.cell_type = CellType.EMPTY

    def __repr__(self):
        return f"Cell({self.x}, {self.y}): {self.cell_type.name}"
