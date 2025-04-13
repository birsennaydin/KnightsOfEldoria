import tkinter as tk
from tkinter import messagebox
from models.cell import Cell
from utils.enums import CellType


class Gui(tk.Tk):
    def __init__(self, grid):
        super().__init__()
        self.grid_data = grid
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
        """Draw legend showing color representation for each cell type."""
        for cell_type, color in self.color_map.items():
            color_box = tk.Label(self.legend_panel, bg=color, width=2, height=1, relief="solid")
            label = tk.Label(self.legend_panel, text=cell_type.name.title())
            color_box.pack(side=tk.LEFT, padx=5)
            label.pack(side=tk.LEFT, padx=5)

    def _draw_grid(self):
        """Render the grid by drawing each cell with the corresponding color."""
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
        """Redraw the grid and update the window."""
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
