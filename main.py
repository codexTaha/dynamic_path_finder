import tkinter as tk
import random

CELL_SIZE = 28

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Module 1 - Grid Editor")
        self.root.minsize(950, 620)

        self.rows = 15
        self.cols = 20
        self.grid = []
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.mode = "wall"

        self.main = tk.Frame(root, bg="#dddddd")
        self.main.pack(fill="both", expand=True)

        self.left = tk.Frame(self.main, bg="#dddddd")
        self.left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # make sidebar a bit wider so nothing gets cut
        self.right = tk.Frame(self.main, bg="#eeeeee", width=320)
        self.right.pack(side="right", fill="y", padx=10, pady=10)
        self.right.pack_propagate(False)

        tk.Label(self.right, text="Controls", bg="#eeeeee",
                 font=("Arial", 15, "bold")).pack(pady=(10, 10))

        # ===== Rows / Cols (separate lines, no cutting) =====
        box_size = tk.Frame(self.right, bg="#eeeeee")
        box_size.pack(fill="x", padx=10, pady=6)

        row_line = tk.Frame(box_size, bg="#eeeeee")
        row_line.pack(fill="x", pady=3)
        tk.Label(row_line, text="Rows:", bg="#eeeeee").pack(side="left")
        self.ent_rows = tk.Entry(row_line, width=10)
        self.ent_rows.insert(0, str(self.rows))
        self.ent_rows.pack(side="left", padx=10)

        col_line = tk.Frame(box_size, bg="#eeeeee")
        col_line.pack(fill="x", pady=3)
        tk.Label(col_line, text="Cols:", bg="#eeeeee").pack(side="left")
        self.ent_cols = tk.Entry(col_line, width=10)
        self.ent_cols.insert(0, str(self.cols))
        self.ent_cols.pack(side="left", padx=12)

        tk.Button(self.right, text="Make Grid", command=self.make_grid).pack(fill="x", padx=10, pady=6)

        # density + random
        box_den = tk.Frame(self.right, bg="#eeeeee")
        box_den.pack(fill="x", padx=10, pady=6)

        tk.Label(box_den, text="Density (0-1):", bg="#eeeeee").pack(side="left")
        self.ent_den = tk.Entry(box_den, width=10)
        self.ent_den.insert(0, "0.30")
        self.ent_den.pack(side="left", padx=10)

        tk.Button(self.right, text="Random Walls", command=self.random_walls).pack(fill="x", padx=10, pady=6)

        # mode buttons
        tk.Label(self.right, text="Edit Mode", bg="#eeeeee",
                 font=("Arial", 12, "bold")).pack(pady=(16, 6))

        tk.Button(self.right, text="Place Start", command=self.mode_start).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Place Goal", command=self.mode_goal).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Toggle Wall", command=self.mode_wall).pack(fill="x", padx=10, pady=4)

        # clear buttons
        tk.Label(self.right, text="Clear", bg="#eeeeee",
                 font=("Arial", 12, "bold")).pack(pady=(16, 6))
        tk.Button(self.right, text="Clear Walls", command=self.clear_walls).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Clear All", command=self.clear_all).pack(fill="x", padx=10, pady=4)

        self.lbl = tk.Label(self.right, text="Mode: WALL", bg="#eeeeee",
                            fg="#333333", font=("Arial", 11))
        self.lbl.pack(pady=(18, 6))

        tip = (
            "Tips:\n"
            "- Click cells to edit\n"
            "- Start = Green\n"
            "- Goal = Red\n"
            "- Walls = Black"
        )
        tk.Label(self.right, text=tip, bg="#eeeeee", justify="left",
                 fg="#444444").pack(padx=10, pady=(10, 10), anchor="w")

        # canvas
        self.canvas = tk.Canvas(self.left, bg="white",
                                highlightthickness=1, highlightbackground="#aaaaaa")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.click_cell)
        self.canvas.bind("<Configure>", self.on_resize)

        self.rects = []
        self.make_grid()

    def mode_wall(self):
        self.mode = "wall"
        self.lbl.config(text="Mode: WALL")

    def mode_start(self):
        self.mode = "start"
        self.lbl.config(text="Mode: START")

    def mode_goal(self):
        self.mode = "goal"
        self.lbl.config(text="Mode: GOAL")

    def make_grid(self):
        try:
            r = int(self.ent_rows.get())
            c = int(self.ent_cols.get())
        except:
            return

        if r < 2: r = 2
        if c < 2: c = 2
        if r > 60: r = 60
        if c > 60: c = 60

        self.rows = r
        self.cols = c

        self.grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(0)
            self.grid.append(row)

        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)

        self.draw_grid()

    def on_resize(self, e):
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self.rects = []

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        grid_w = self.cols * CELL_SIZE
        grid_h = self.rows * CELL_SIZE

        off_x = (cw - grid_w) // 2
        off_y = (ch - grid_h) // 2
        if off_x < 10: off_x = 10
        if off_y < 10: off_y = 10

        self.off_x = off_x
        self.off_y = off_y

        for r in range(self.rows):
            one_row = []
            for c in range(self.cols):
                x1 = off_x + c * CELL_SIZE
                y1 = off_y + r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = "white"
                if self.grid[r][c] == 1:
                    color = "black"
                if (r, c) == self.start:
                    color = "#22aa22"
                if (r, c) == self.goal:
                    color = "#dd3333"

                box = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                   fill=color, outline="#bbbbbb")
                one_row.append(box)
            self.rects.append(one_row)

    def recolor(self, r, c):
        color = "white"
        if self.grid[r][c] == 1:
            color = "black"
        if (r, c) == self.start:
            color = "#22aa22"
        if (r, c) == self.goal:
            color = "#dd3333"
        self.canvas.itemconfig(self.rects[r][c], fill=color)

    def get_cell_from_mouse(self, x, y):
        x = x - self.off_x
        y = y - self.off_y
        if x < 0 or y < 0:
            return None
        c = x // CELL_SIZE
        r = y // CELL_SIZE
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return None
        return (r, c)

    def click_cell(self, e):
        pos = self.get_cell_from_mouse(e.x, e.y)
        if pos is None:
            return
        r, c = pos

        if self.mode == "wall":
            if (r, c) == self.start or (r, c) == self.goal:
                return
            self.grid[r][c] = 0 if self.grid[r][c] == 1 else 1
            self.recolor(r, c)

        elif self.mode == "start":
            if (r, c) == self.goal: return
            if self.grid[r][c] == 1: return
            old = self.start
            self.start = (r, c)
            self.recolor(old[0], old[1])
            self.recolor(r, c)

        elif self.mode == "goal":
            if (r, c) == self.start: return
            if self.grid[r][c] == 1: return
            old = self.goal
            self.goal = (r, c)
            self.recolor(old[0], old[1])
            self.recolor(r, c)

    def random_walls(self):
        try:
            den = float(self.ent_den.get())
        except:
            den = 0.30
        if den < 0: den = 0
        if den > 1: den = 1

        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) == self.start or (r, c) == self.goal:
                    self.grid[r][c] = 0
                else:
                    self.grid[r][c] = 1 if random.random() < den else 0
        self.draw_grid()

    def clear_walls(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) != self.start and (r, c) != self.goal:
                    self.grid[r][c] = 0
        self.draw_grid()

    def clear_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.draw_grid()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
