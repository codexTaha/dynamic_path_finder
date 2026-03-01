import tkinter as tk
import random
from search import gbfs, astar

CELL_SIZE = 28

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Module 2 - GBFS / A* (Animated)")
        self.root.minsize(950, 620)

        self.rows = 15
        self.cols = 20
        self.grid = []
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.mode = "wall"

        # animation / results
        self.visited_set = set()
        self.path_set = set()
        self.full_visited = []
        self.full_path = []
        self.anim_i = 0
        self.anim_running = False

        self.last_cost = 0
        self.last_time = 0

        self.main = tk.Frame(root, bg="#dddddd")
        self.main.pack(fill="both", expand=True)

        self.left = tk.Frame(self.main, bg="#dddddd")
        self.left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right = tk.Frame(self.main, bg="#eeeeee", width=320)
        self.right.pack(side="right", fill="y", padx=10, pady=10)
        self.right.pack_propagate(False)

        tk.Label(self.right, text="Controls", bg="#eeeeee",
                 font=("Arial", 15, "bold")).pack(pady=(10, 10))

        # rows/cols
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

        # density
        box_den = tk.Frame(self.right, bg="#eeeeee")
        box_den.pack(fill="x", padx=10, pady=6)
        tk.Label(box_den, text="Density (0-1):", bg="#eeeeee").pack(side="left")
        self.ent_den = tk.Entry(box_den, width=10)
        self.ent_den.insert(0, "0.30")
        self.ent_den.pack(side="left", padx=10)

        tk.Button(self.right, text="Random Walls", command=self.random_walls).pack(fill="x", padx=10, pady=6)

        # search
        tk.Label(self.right, text="Search", bg="#eeeeee",
                 font=("Arial", 12, "bold")).pack(pady=(16, 6))

        self.alg_var = tk.StringVar()
        self.alg_var.set("A*")
        tk.OptionMenu(self.right, self.alg_var, "A*", "GBFS").pack(fill="x", padx=10, pady=4)

        self.h_var = tk.StringVar()
        self.h_var.set("Manhattan")
        tk.OptionMenu(self.right, self.h_var, "Manhattan", "Euclidean").pack(fill="x", padx=10, pady=4)

        # delay slider (ms per step)
        tk.Label(self.right, text="Delay (ms/step)", bg="#eeeeee").pack(pady=(10, 0))
        self.delay_var = tk.IntVar()
        self.delay_var.set(60)  # default slow
        tk.Scale(self.right, from_=0, to=300, orient="horizontal",
                 variable=self.delay_var, bg="#eeeeee", highlightthickness=0).pack(fill="x", padx=10)

        self.btn_run = tk.Button(self.right, text="Run Search (Animated)", command=self.run_search)
        self.btn_run.pack(fill="x", padx=10, pady=8)

        # edit mode
        tk.Label(self.right, text="Edit Mode", bg="#eeeeee",
                 font=("Arial", 12, "bold")).pack(pady=(10, 6))
        tk.Button(self.right, text="Place Start", command=self.mode_start).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Place Goal", command=self.mode_goal).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Toggle Wall", command=self.mode_wall).pack(fill="x", padx=10, pady=4)

        # clear
        tk.Label(self.right, text="Clear", bg="#eeeeee",
                 font=("Arial", 12, "bold")).pack(pady=(10, 6))
        tk.Button(self.right, text="Clear Walls", command=self.clear_walls).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Clear All", command=self.clear_all).pack(fill="x", padx=10, pady=4)
        tk.Button(self.right, text="Clear Search Colors", command=self.clear_search).pack(fill="x", padx=10, pady=4)

        self.lbl = tk.Label(self.right, text="Mode: WALL", bg="#eeeeee",
                            fg="#333333", font=("Arial", 11))
        self.lbl.pack(pady=(12, 6))

        # metrics
        tk.Label(self.right, text="Metrics", bg="#eeeeee",
                 font=("Arial", 12, "bold")).pack(pady=(10, 6))

        self.lbl_nodes = tk.Label(self.right, text="Nodes Visited: 0", bg="#eeeeee")
        self.lbl_nodes.pack(anchor="w", padx=10)
        self.lbl_cost = tk.Label(self.right, text="Path Cost: 0", bg="#eeeeee")
        self.lbl_cost.pack(anchor="w", padx=10)
        self.lbl_time = tk.Label(self.right, text="Time (ms): 0", bg="#eeeeee")
        self.lbl_time.pack(anchor="w", padx=10)

        tip = (
            "Colors:\n"
            "- Visited: Blue\n"
            "- Final Path: Green\n"
            "- Start: Green\n"
            "- Goal: Red"
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

    # ---------- modes ----------
    def mode_wall(self):
        self.mode = "wall"
        self.lbl.config(text="Mode: WALL")

    def mode_start(self):
        self.mode = "start"
        self.lbl.config(text="Mode: START")

    def mode_goal(self):
        self.mode = "goal"
        self.lbl.config(text="Mode: GOAL")

    # ---------- grid ----------
    def make_grid(self):
        if self.anim_running:
            return

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

        self.clear_search()
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
                color = self.get_cell_color(r, c)
                box = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                   fill=color, outline="#bbbbbb")
                one_row.append(box)
            self.rects.append(one_row)

    def get_cell_color(self, r, c):
        pos = (r, c)

        if self.grid[r][c] == 1:
            return "black"
        if pos == self.start:
            return "#22aa22"
        if pos == self.goal:
            return "#dd3333"
        if pos in self.path_set:
            return "#00cc66"
        if pos in self.visited_set:
            return "#66a3ff"
        return "white"

    def recolor(self, r, c):
        self.canvas.itemconfig(self.rects[r][c], fill=self.get_cell_color(r, c))

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
        if self.anim_running:
            return

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
        if self.anim_running:
            return

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

        self.clear_search()
        self.draw_grid()

    def clear_walls(self):
        if self.anim_running:
            return
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) != self.start and (r, c) != self.goal:
                    self.grid[r][c] = 0
        self.draw_grid()

    def clear_all(self):
        if self.anim_running:
            return
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.clear_search()
        self.draw_grid()

    # ---------- search / animation ----------
    def clear_search(self):
        if self.anim_running:
            return
        self.visited_set = set()
        self.path_set = set()
        self.full_visited = []
        self.full_path = []
        self.anim_i = 0
        self.last_cost = 0
        self.last_time = 0

        self.lbl_nodes.config(text="Nodes Visited: 0")
        self.lbl_cost.config(text="Path Cost: 0")
        self.lbl_time.config(text="Time (ms): 0")

    def run_search(self):
        if self.anim_running:
            return

        # reset colors
        self.visited_set = set()
        self.path_set = set()
        self.anim_i = 0

        self.lbl_nodes.config(text="Nodes Visited: 0")
        self.lbl_cost.config(text="Path Cost: 0")
        self.lbl_time.config(text="Time (ms): 0")

        if self.start == self.goal:
            return

        alg = self.alg_var.get()
        hname = self.h_var.get()

        # compute fast, then animate slow
        if alg == "GBFS":
            res = gbfs(self.grid, self.start, self.goal, hname)
        else:
            res = astar(self.grid, self.start, self.goal, hname)

        self.full_visited = res["visited"]
        self.full_path = res["path"]
        self.last_cost = res["cost"]
        self.last_time = res["time_ms"]

        self.anim_running = True
        self.btn_run.config(state="disabled")

        self.draw_grid()
        self.animate_step()

    def animate_step(self):
        if not self.anim_running:
            return

        # show visited nodes slowly
        if self.anim_i < len(self.full_visited):
            node = self.full_visited[self.anim_i]
            self.anim_i += 1

            # add to visited set
            self.visited_set.add(node)

            # recolor only that cell (if it is inside grid)
            r, c = node
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.recolor(r, c)

            self.lbl_nodes.config(text="Nodes Visited: " + str(len(self.visited_set)))

            d = self.delay_var.get()
            if d < 0:
                d = 0
            self.root.after(d, self.animate_step)
            return

        # after visited animation, show final path
        self.path_set = set(self.full_path)
        for p in self.full_path:
            r, c = p
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.recolor(r, c)

        # update final metrics
        if self.full_path:
            self.lbl_cost.config(text="Path Cost: " + str(self.last_cost))
        else:
            self.lbl_cost.config(text="Path Cost: No Path")

        self.lbl_time.config(text="Time (ms): " + str(self.last_time))

        self.anim_running = False
        self.btn_run.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
