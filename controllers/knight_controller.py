from utils.enums import CellType


class KnightController:
    def __init__(self, grid):
        self.grid = grid  # Grid is needed for accessing nearby cells

    def process(self, knight):
        """Handle behavior of a single knight for one simulation step."""

        if knight.resting:
            knight.rest()
            return

        # Detect hunters within a 3-cell radius
        nearby_cells = self.grid.get_cells_in_radius(knight.x, knight.y, 3)
        visible_hunters = knight.detect_hunters(nearby_cells)

        if visible_hunters:
            knight.choose_target(visible_hunters)
            knight.chase()

            # If knight reached the hunter (same cell), interact
            if knight.target and (knight.target.x, knight.target.y) == (knight.x, knight.y):
                knight.interact_with_hunter(knight.target, method="detain")

        # If energy is too low, start resting
        if knight.should_rest():
            knight.resting = True
