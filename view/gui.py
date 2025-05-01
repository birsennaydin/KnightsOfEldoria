import tkinter as tk
from tkinter import messagebox
from models.cell import Cell
from utils.enums import CellType


class Gui(tk.Tk):
    def __init__(self, grid, sim_controller):
        super().__init__()
        self.grid_data = grid
        self.sim_controller = sim_controller
        self.title("Knights of Eldoria")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.__closed = False

        self.cell_size = 25
        self.color_map = {
            CellType.EMPTY: "white",
            CellType.HUNTER: "blue",
            CellType.TREASURE: "gold",
            CellType.KNIGHT: "red",
            CellType.HIDEOUT: "green",
            CellType.GARRISON: "purple"  # Added color for garrison
        }

        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack()

        self.legend_panel = tk.Frame(self)
        self.legend_panel.pack(pady=10)

        self._draw_legend()
        self._draw_grid()

    def _draw_legend(self):
        for widget in self.legend_panel.winfo_children():
            widget.destroy()

        counts = self._count_entities()

        for cell_type, color in self.color_map.items():
            color_box = tk.Label(self.legend_panel, bg=color, width=2, height=1, relief="solid")
            label = tk.Label(
                self.legend_panel,
                text=f"{cell_type.name.title()} ({counts.get(cell_type, 0)})"
            )
            color_box.pack(side=tk.LEFT, padx=5)
            label.pack(side=tk.LEFT, padx=5)

    def _draw_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        for y in range(self.grid_data.size):
            for x in range(self.grid_data.size):
                cell = self.grid_data.get_cell(x, y)
                color = self.color_map.get(cell.cell_type, "gray")
                canvas = tk.Canvas(self.grid_frame, width=self.cell_size, height=self.cell_size,
                                   bg=color, bd=1, relief="solid")
                canvas.grid(row=y, column=x)

    def render(self):
        self._draw_legend()
        self._draw_grid()
        self.update()
        self.update_idletasks()

    def on_closing(self):
        """Handle the window close event with confirmation dialog."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.__closed = True
            self.destroy()

    def is_closed(self) -> bool:
        """Check if the window has been closed."""
        return self.__closed

    def _count_entities(self):
        """Count entities based on simulation controller lists."""
        hunters = len(self.sim_controller.hunters)
        knights = len(self.sim_controller.knights)
        hideouts = len(self.sim_controller.hideouts)
        garrisons = len(self.sim_controller.garrisons)
        treasures_on_grid = len(self.sim_controller.treasures)
        treasures = treasures_on_grid

        # Calculate empty cells
        total_cells = self.grid_data.size * self.grid_data.size
        non_empty_cells = hunters + knights + hideouts + garrisons + treasures
        empty = total_cells - non_empty_cells

        counts = {
            CellType.EMPTY: empty,
            CellType.HUNTER: hunters,
            CellType.KNIGHT: knights,
            CellType.HIDEOUT: hideouts,
            CellType.GARRISON: garrisons,
            CellType.TREASURE: treasures,
        }
        return counts
