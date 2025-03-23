from utils.enums import CellType


class KnightController:
    def __init__(self, grid):
        self.grid = grid  # Grid is needed for accessing nearby cells

    def process(self, knight):
        # If resting, try to recover stamina
        if knight.resting:
            knight.rest()
            if not knight.resting:
                knight.log("recovered and is now active.")
            return

        # Detect nearby hunters
        nearby_cells = self.grid.get_cells_in_radius(knight.x, knight.y, 3)
        visible_hunters = knight.detect_hunters(nearby_cells)

        if visible_hunters:
            knight.log(f"detected {len(visible_hunters)} hunters nearby.")
            knight.choose_target(visible_hunters)
            if knight.target:
                knight.log(f"targeting hunter: {knight.target.name}")
                knight.chase()
                knight.log(f"chasing hunter: {knight.target.name}")

                if (knight.target.x, knight.target.y) == (knight.x, knight.y):
                    knight.interact_with_hunter(knight.target, method="detain")
                    knight.log(f"detained hunter: {knight.target.name}")
        else:
            knight.log("no hunters detected nearby.")

        # If stamina is low, begin resting
        if knight.should_rest():
            knight.resting = True
            knight.log("is now resting.")
