class KnightController:
    def __init__(self, grid):
        self.grid = grid

    def process(self, knight):
        # === Decision Tree begins ===

        if knight.resting:
            knight.rest()
            if not knight.resting:
                knight.log("has recovered and is active again.")
            return

        if knight.should_rest():
            knight.resting = True
            knight.log("is too tired and starts resting.")
            return

        nearby_cells = self.grid.get_cells_in_radius(knight.x, knight.y, 3)
        visible_hunters = knight.detect_hunters(nearby_cells)

        if visible_hunters:
            knight.log(f"spotted {len(visible_hunters)} hunters nearby.")
            knight.choose_target(visible_hunters)

            if knight.target:
                if knight.energy > 0.6:
                    knight.log("is energized and charges the target.")
                    knight.chase()
                elif 0.3 < knight.energy <= 0.6:
                    knight.log("is cautious but still chasing.")
                    knight.chase()
                else:
                    knight.log("is too weak to engage in pursuit.")
                    knight.resting = True
                    return

                # Interaction if caught
                if (knight.target.x, knight.target.y) == (knight.x, knight.y):
                    knight.interact_with_hunter(knight.target, method="detain")
                    knight.log(f"detained hunter: {knight.target.name}")
        else:
            knight.log("patrolling area, no hunters in sight.")
