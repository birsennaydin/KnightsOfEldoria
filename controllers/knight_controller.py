from models.hunter import Hunter
from utils.enums import CellType
from ai.pathfinding.astar import astar
import random

class KnightController:
    def __init__(self, grid):
        self.grid = grid

    def process(self, knight):
        knight.log(f"KNIGHT CONTROLLER IS STARTING {knight}, {knight.name}")

        # Rule 1: If the knight is already resting, continue resting
        if knight.resting:
            knight.log(f"{knight.name} is resting. RULE1")
            knight.rest()
            if not knight.resting:
                knight.log(f"{knight.name} has recovered and is active again.")
            return

        # Rule 2: If the knight is too tired, initiate resting
        if knight.should_rest():
            knight.resting = True
            knight.log(f"{knight.name} is too tired and starts resting.")
            # Send knight to garrison to rest if available
            if knight.garrison:
                knight.garrison.add_knight(knight)  # Add knight to garrison for resting
            else:
                knight.rest()  # If no garrison, rest in place
            return

        # Rule 3: Scan for hunters within radius
        nearby_cells = self.grid.get_cells_in_radius(knight.x, knight.y, 3)
        knight.log(f"GET NEARBY CELLS {nearby_cells}")
        visible_hunters = knight.detect_hunters(nearby_cells)
        knight.log(f"VISIBLE HUNTERS {len(visible_hunters)} {visible_hunters}")

        if visible_hunters:
            knight.log(f"spotted {len(visible_hunters)} hunters nearby.")
            path = self.get_safe_path_to_hunter(knight, [(h.x, h.y) for h in visible_hunters])
            knight.log(f"🧭 Knight Path... {path}, Knight old location: {knight.x}, {knight.y}")

            if path:
                next_pos = path[0]
                knight.log(
                    f"🧭 Knight Path Details... next_pos: {next_pos}, details nextposxy: {next_pos[0]}, {next_pos[1]}")
                dx = next_pos[0] - knight.x
                dy = next_pos[1] - knight.y

                knight.log(f"🧭 Knight differences xy: {dx}, {dy}")
                new_x, new_y = self.grid.wrap(knight.x + dx, knight.y + dy)
                knight.log(f"🧭 Knight new location xy: {new_x}, {new_y}")
                new_cell = self.grid.get_cell(new_x, new_y)
                knight.log(f"🧭 Knight new location CELL: {new_cell}")
                old_cell = self.grid.get_cell(knight.x, knight.y)
                knight.log(f"🧭 Knight OLD location CELL: {old_cell}")

                knight.log(f"🧭 Knight new location CELLTYPE: {new_cell.cell_type}, content: {new_cell.content}")

                knight.log(
                    f"KNIGHT Current Position: ({knight.x}, {knight.y}), "
                    f"KNIGHT Energy: {knight.energy}, "
                    f"KNIGHT Resting: {knight.resting}"
                )

                if new_cell.cell_type == CellType.EMPTY:
                    knight.move_to(new_x, new_y)
                    knight.energy = max(0, round(knight.energy - 0.2, 2))
                elif new_cell.cell_type == CellType.HUNTER and isinstance(new_cell.content, Hunter):
                    knight.interact_with_hunter(new_cell.content, method="detain")
                    knight.log(f"⚔️ Detained hunter: {new_cell.content}")
                    knight.energy = max(0, round(knight.energy - 0.2, 2))
                else:
                    knight.log("cannot reach target – switching to patrol.")
                    knight.target = None
                    self.random_patrol(knight)  # If path is blocked, patrol randomly

            else:
                knight.log("cannot reach target – switching to patrol.")
                knight.target = None
                self.random_patrol(knight)  # If path is blocked, patrol randomly

            knight.log(
                f"KNIGHT Current Position: ({knight.x}, {knight.y}), "
                f"KNIGHT Energy: {knight.energy}, "
                f"KNIGHT Resting: {knight.resting}"
            )
        else:
            knight.log("cannot reach any visible hunter – switching to patrol.")
            knight.target = None
            self.random_patrol(knight)  # If path is blocked, patrol randomly
            knight.log(
                f"KNIGHT Current Position: ({knight.x}, {knight.y}), "
                f"KNIGHT Energy: {knight.energy}, "
                f"KNIGHT Resting: {knight.resting}")

    def random_patrol(self, knight):
        # Rule 7: Patrol in a random direction
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])  # Random movement choices
        new_x, new_y = self.grid.wrap(knight.x + dx, knight.y + dy)  # Wrap around grid bounds
        cell = self.grid.get_cell(new_x, new_y)

        knight.log(f"🎲 Patrol attempt → ({new_x}, {new_y}) | Cell type: {cell.cell_type if cell else 'None'}")

        if cell and cell.cell_type == CellType.EMPTY:
            knight.move_to(new_x, new_y)
            knight.log(f"✅ {knight.name} patrolled to empty cell at ({new_x}, {new_y})")

        elif cell and cell.cell_type == CellType.HUNTER and cell.content:
            knight.interact_with_hunter(cell.content, method="detain")
            knight.log(f"⚔️ {knight.name} patrolled into hunter cell and detained: {cell.content.name}")

        else:
            knight.log(f"⛔ {knight.name} attempted patrol to non-empty cell. Staying in place.")

        # Deduct energy regardless of outcome
        knight.energy = max(0, round(knight.energy - 0.2, 2))

        knight.log(f"🔋 {knight.name} lost 0.2 energy during patrol. Current energy: {knight.energy:.2f}")

    def get_safe_path_to_hunter(self, knight, visible_hunters):

        knight.log(f"🔎 [DEBUG] get_safe_path_to_hunter called.Knight: {knight}")
        # === 1. If there are visible hunters ===
        knight.log(f"🔎 Visible Hunters: {visible_hunters}")
        for pos in visible_hunters:
            cell = self.grid.get_cell(*pos)
            knight.log(f"🧪 Checking cell at {pos} → type: {cell.cell_type.name}, content: {repr(cell.content)}")

        valid_visible_hunters = [
            pos for pos in visible_hunters
            if self.grid.get_cell(*pos).cell_type == CellType.HUNTER and
               isinstance(self.grid.get_cell(*pos).content, Hunter)
        ]

        knight.log(f"✅ Valid known hunters: {valid_visible_hunters}")

        if valid_visible_hunters:
            sorted_hunters = sorted(
                valid_visible_hunters,
                key=lambda pos: abs(knight.x - pos[0]) + abs(knight.y - pos[1])
            )
            knight.log(f"📍 Sorted valid hunters by distance & value: {sorted_hunters}")

            for hunter_pos in sorted_hunters:
                knight.log(f"🛣️ Attempting A* path to hunter at {hunter_pos}")
                path = astar(self.grid, (knight.x, knight.y), hunter_pos, role="knight")
                if path:
                    knight.log(f"✅ Path found: {path}")
                    is_safe = all(
                        self.grid.get_cell(*pos).cell_type not in [
                            CellType.KNIGHT, CellType.GARRISON, CellType.HIDEOUT, CellType.TREASURE
                        ]
                        for pos in path[1:]  # Exclude knight's own cell
                    )
                    knight.log(f"🔐 Path safety: {'SAFE' if is_safe else 'UNSAFE'}")
                    if is_safe:
                        return path
                else:
                    knight.log(f"❌ No path found to {knight}.")

        # === 2. Check nearby (1-cell radius) for hunter ===
        neighbors = self.grid.get_knight_neighbors(knight.x, knight.y)
        knight.log(f"👁️ Nearby movable cells: {neighbors}")

        for nx, ny in neighbors:
            cell = self.grid.get_cell(nx, ny)
            if cell and cell.cell_type in {CellType.EMPTY, CellType.HUNTER}:
                knight.log(f"🔄 No reachable hunter — fallback move to ({nx}, {ny})")
                return [(nx, ny)]

        knight.log("🚫 No valid path to hunter or fallback empty cell found.")
        return None