import tkinter as tk
import random
from search import gbfs, astar

CELL_SIZE = 28

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Module 4 - Final Visuals (Frontier + Dynamic)")
        self.root.minsize(1100, 700)

        self.rows = 15
        self.cols = 20
        self.grid = []
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.mode = "wall"

        # search / animation
        self.visited_set = set()
        self.frontier_set = set()
        self.path_list = []
        self.path_set = set()

        self.full_steps = []
        self.anim_i = 0
        self.anim_running = False

        self.delay_var = tk.IntVar()
        self.delay_var.set(60)

        # dynamic mode
        self.dynamic_on = tk.IntVar()
        self.dynamic_on.set(0)
        self.spawn_var = tk.IntVar()
        self.spawn_var.set(5)
        self.agent = None
        self.move_i = 0
        self.moving = False

        self.last_cost = 0
        self.last_time = 0

        # -------- main layout --------
        self.main = tk.Frame(root, bg="#dddddd")
        self.main.pack(fill="both", expand=True)

        self.left = tk.Frame(self.main, bg="#dddddd")
        self.left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right = tk.Frame(self.main, bg="#eeeeee", width=430)
        self.right.pack(side="right", fill="y", padx=10, pady=10)
        self.right.pack_propagate(False)

        # -------- LEFT: canvas + scrollbars --------
        self.canvas_box = tk.Frame(self.left, bg="#dddddd")
        self.canvas_box.pack(fill="both", expand=True)

        self.ybar = tk.Scrollbar(self.canvas_box, orient="vertical")
        self.ybar.pack(side="right", fill="y")

        self.xbar = tk.Scrollbar(self.canvas_box, orient="horizontal")
        self.xbar.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(
            self.canvas_box,
            bg="white",
            highlightthickness=1,
            highlightbackground="#aaaaaa",
            xscrollcommand=self.xbar.set,
            yscrollcommand=self.ybar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.xbar.config(command=self.canvas.xview)
        self.ybar.config(command=self.canvas.yview)

        self.canvas.bind("<Button-1>", self.click_cell)

        # -------- RIGHT: scrollable sidebar --------
        self.side_canvas = tk.Canvas(self.right, bg="#eeeeee", highlightthickness=0)
        self.side_scroll = tk.Scrollbar(self.right, orient="vertical", command=self.side_canvas.yview)
        self.side_canvas.configure(yscrollcommand=self.side_scroll.set)
        self.side_scroll.pack(side="right", fill="y")
        self.side_canvas.pack(side="left", fill="both", expand=True)

        self.side_frame = tk.Frame(self.side_canvas, bg="#eeeeee")
        self.side_win = self.side_canvas.create_window((0, 0), window=self.side_frame, anchor="nw")
        self.side_frame.bind("<Configure>", self.update_side_scroll)
        self.side_canvas.bind("<Configure>", self.side_fit_width)

        self.build_sidebar()
        self.make_grid()

    def update_side_scroll(self, e=None):
        self.side_canvas.configure(scrollregion=self.side_canvas.bbox("all"))

    def side_fit_width(self, e):
        self.side_canvas.itemconfig(self.side_win, width=e.width)

    def build_sidebar(self):
        f = self.side_frame
        tk.Label(f, text="Controls", bg="#eeeeee", font=("Arial", 15, "bold")).pack(pady=(10, 10))

        box_size = tk.Frame(f, bg="#eeeeee")
        box_size.pack(fill="x", padx=10, pady=6)

        row_line = tk.Frame(box_size, bg="#eeeeee")
        row_line.pack(fill="x", pady=3)
        tk.Label(row_line, text="Rows:", bg="#eeeeee").pack(side="left")
        self.ent_rows = tk.Entry(row_line, width=12)
        self.ent_rows.insert(0, str(self.rows))
        self.ent_rows.pack(side="left", padx=10)

        col_line = tk.Frame(box_size, bg="#eeeeee")
        col_line.pack(fill="x", pady=3)
        tk.Label(col_line, text="Cols:", bg="#eeeeee").pack(side="left")
        self.ent_cols = tk.Entry(col_line, width=12)
        self.ent_cols.insert(0, str(self.cols))
        self.ent_cols.pack(side="left", padx=12)

        tk.Button(f, text="Make Grid", command=self.make_grid).pack(fill="x", padx=10, pady=6)

        box_den = tk.Frame(f, bg="#eeeeee")
        box_den.pack(fill="x", padx=10, pady=6)
        tk.Label(box_den, text="Density (0-1):", bg="#eeeeee").pack(side="left")
        self.ent_den = tk.Entry(box_den, width=12)
        self.ent_den.insert(0, "0.30")
        self.ent_den.pack(side="left", padx=10)

        tk.Button(f, text="Random Walls", command=self.random_walls).pack(fill="x", padx=10, pady=6)

        tk.Label(f, text="Search", bg="#eeeeee", font=("Arial", 12, "bold")).pack(pady=(16, 6))

        self.alg_var = tk.StringVar()
        self.alg_var.set("A*")
        tk.OptionMenu(f, self.alg_var, "A*", "GBFS").pack(fill="x", padx=10, pady=4)

        self.h_var = tk.StringVar()
        self.h_var.set("Manhattan")
        tk.OptionMenu(f, self.h_var, "Manhattan", "Euclidean").pack(fill="x", padx=10, pady=4)

        tk.Label(f, text="Delay (ms/step)", bg="#eeeeee").pack(pady=(10, 0))
        tk.Scale(f, from_=0, to=300, orient="horizontal",
                 variable=self.delay_var, bg="#eeeeee", highlightthickness=0).pack(fill="x", padx=10)

        tk.Label(f, text="Dynamic Mode", bg="#eeeeee", font=("Arial", 12, "bold")).pack(pady=(14, 6))

        tk.Checkbutton(
            f, text="Enable Dynamic Obstacles",
            variable=self.dynamic_on, bg="#eeeeee", anchor="w", wraplength=360
        ).pack(fill="x", padx=10)

        tk.Label(f, text="Spawn Chance (% per move)", bg="#eeeeee").pack(pady=(6, 0))
        tk.Scale(f, from_=0, to=30, orient="horizontal",
                 variable=self.spawn_var, bg="#eeeeee", highlightthickness=0).pack(fill="x", padx=10)

        self.btn_run = tk.Button(f, text="Run Search", command=self.run_search)
        self.btn_run.pack(fill="x", padx=10, pady=10)

        self.btn_move = tk.Button(f, text="Start Moving Agent", command=self.start_agent_move)
        self.btn_move.pack(fill="x", padx=10, pady=6)

        tk.Label(f, text="Edit Mode", bg="#eeeeee", font=("Arial", 12, "bold")).pack(pady=(12, 6))
        tk.Button(f, text="Place Start", command=self.mode_start).pack(fill="x", padx=10, pady=4)
        tk.Button(f, text="Place Goal", command=self.mode_goal).pack(fill="x", padx=10, pady=4)
        tk.Button(f, text="Toggle Wall", command=self.mode_wall).pack(fill="x", padx=10, pady=4)

        tk.Label(f, text="Clear", bg="#eeeeee", font=("Arial", 12, "bold")).pack(pady=(12, 6))
        tk.Button(f, text="Clear Walls", command=self.clear_walls).pack(fill="x", padx=10, pady=4)
        tk.Button(f, text="Clear All", command=self.clear_all).pack(fill="x", padx=10, pady=4)
        tk.Button(f, text="Clear Search Colors", command=self.clear_search).pack(fill="x", padx=10, pady=4)

        self.lbl = tk.Label(f, text="Mode: WALL", bg="#eeeeee", fg="#333333", font=("Arial", 11))
        self.lbl.pack(pady=(10, 6))

        tk.Label(f, text="Metrics", bg="#eeeeee", font=("Arial", 12, "bold")).pack(pady=(10, 6))
        self.lbl_nodes = tk.Label(f, text="Nodes Visited: 0", bg="#eeeeee")
        self.lbl_nodes.pack(anchor="w", padx=10)
        self.lbl_cost = tk.Label(f, text="Path Cost: 0", bg="#eeeeee")
        self.lbl_cost.pack(anchor="w", padx=10)
        self.lbl_time = tk.Label(f, text="Time (ms): 0", bg="#eeeeee")
        self.lbl_time.pack(anchor="w", padx=10)

        self.lbl_status = tk.Label(f, text="Status: Ready", bg="#eeeeee", fg="#444444")
        self.lbl_status.pack(anchor="w", padx=10, pady=(8, 10))

        tip = (
            "Colors:\n"
            "- Frontier: Yellow\n"
            "- Visited: Blue\n"
            "- Path: Green\n"
            "- Agent: Orange\n"
            "- Walls: Black"
        )
        tk.Label(f, text=tip, bg="#eeeeee", justify="left", fg="#444444").pack(padx=10, pady=(0, 10), anchor="w")

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
        if self.anim_running or self.moving:
            return
        try:
            r = int(self.ent_rows.get())
            c = int(self.ent_cols.get())
        except:
            return
        if r < 2: r = 2
        if c < 2: c = 2
        if r > 80: r = 80
        if c > 80: c = 80

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
        self.agent = None

        self.clear_search()
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self.rects = []
        for r in range(self.rows):
            one_row = []
            for c in range(self.cols):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = self.get_cell_color(r, c)
                box = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#bbbbbb")
                one_row.append(box)
            self.rects.append(one_row)

        w = self.cols * CELL_SIZE
        h = self.rows * CELL_SIZE
        self.canvas.configure(scrollregion=(0, 0, w, h))

    def get_cell_color(self, r, c):
        pos = (r, c)
        if self.grid[r][c] == 1:
            return "black"
        if pos == self.start:
            return "#22aa22"
        if pos == self.goal:
            return "#dd3333"
        if self.agent is not None and pos == self.agent:
            return "#ff9900"
        if pos in self.path_set:
            return "#00cc66"
        if pos in self.visited_set:
            return "#66a3ff"
        if pos in self.frontier_set:
            return "#ffdd55"
        return "white"

    def recolor(self, r, c):
        self.canvas.itemconfig(self.rects[r][c], fill=self.get_cell_color(r, c))

    def click_cell(self, e):
        if self.anim_running or self.moving:
            return

        x = int(self.canvas.canvasx(e.x))
        y = int(self.canvas.canvasy(e.y))
        c = x // CELL_SIZE
        r = y // CELL_SIZE
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return

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
            if self.agent is None:
                self.agent = self.start
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
        if self.anim_running or self.moving:
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
        if self.anim_running or self.moving:
            return
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) != self.start and (r, c) != self.goal:
                    self.grid[r][c] = 0
        self.draw_grid()

    def clear_all(self):
        if self.anim_running or self.moving:
            return
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.agent = None
        self.clear_search()
        self.draw_grid()

    # ---------- search ----------
    def clear_search(self):
        if self.anim_running or self.moving:
            return
        self.visited_set = set()
        self.frontier_set = set()
        self.path_list = []
        self.path_set = set()
        self.full_steps = []
        self.anim_i = 0
        self.agent = self.start
        self.move_i = 0

        self.lbl_nodes.config(text="Nodes Visited: 0")
        self.lbl_cost.config(text="Path Cost: 0")
        self.lbl_time.config(text="Time (ms): 0")
        self.lbl_status.config(text="Status: Ready")

    def run_search(self):
        if self.anim_running or self.moving:
            return

        self.visited_set = set()
        self.frontier_set = set()
        self.path_set = set()
        self.full_steps = []
        self.anim_i = 0

        self.lbl_nodes.config(text="Nodes Visited: 0")
        self.lbl_cost.config(text="Path Cost: 0")
        self.lbl_time.config(text="Time (ms): 0")
        self.lbl_status.config(text="Status: Searching...")

        alg = self.alg_var.get()
        hname = self.h_var.get()
        cur_start = self.start if self.agent is None else self.agent

        if alg == "GBFS":
            res = gbfs(self.grid, cur_start, self.goal, hname)
        else:
            res = astar(self.grid, cur_start, self.goal, hname)

        self.full_steps = res.get("steps", [])
        self.path_list = res.get("path", [])
        self.last_cost = res.get("cost", 0)
        self.last_time = res.get("time_ms", 0)

        self.anim_running = True
        self.btn_run.config(state="disabled")
        self.btn_move.config(state="disabled")

        self.animate_search()

    def animate_search(self):
        if not self.anim_running:
            return

        if self.anim_i < len(self.full_steps):
            step = self.full_steps[self.anim_i]
            self.anim_i += 1

            node = step["expanded"]
            new_frontier = set(step["frontier"])

            # recolor old frontier cells (they may turn white/visited)
            old_front = self.frontier_set
            self.frontier_set = new_frontier

            # mark expanded as visited
            self.visited_set.add(node)

            # recolor changed frontier + visited node
            all_change = old_front.union(new_frontier)
            all_change.add(node)

            for p in all_change:
                r, c = p
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.recolor(r, c)

            self.lbl_nodes.config(text="Nodes Visited: " + str(len(self.visited_set)))

            d = self.delay_var.get()
            if d < 0: d = 0
            self.root.after(d, self.animate_search)
            return

        # finish: show final path
        self.frontier_set = set()
        self.path_set = set(self.path_list)

        for p in self.path_list:
            self.recolor(p[0], p[1])

        if self.path_list:
            self.lbl_cost.config(text="Path Cost: " + str(self.last_cost))
            self.lbl_status.config(text="Status: Done (Path Found)")
        else:
            self.lbl_cost.config(text="Path Cost: No Path")
            self.lbl_status.config(text="Status: Done (No Path)")

        self.lbl_time.config(text="Time (ms): " + str(self.last_time))

        self.anim_running = False
        self.btn_run.config(state="normal")
        self.btn_move.config(state="normal")

    # ---------- dynamic move ----------
    def start_agent_move(self):
        if self.anim_running or self.moving:
            return
        if self.agent is None:
            self.agent = self.start

        if not self.path_list:
            self.compute_path_no_anim()

        if not self.path_list:
            self.lbl_status.config(text="Status: No path to move")
            return

        self.moving = True
        self.btn_run.config(state="disabled")
        self.btn_move.config(state="disabled")
        self.move_i = 0
        self.lbl_status.config(text="Status: Moving...")
        self.move_step()

    def compute_path_no_anim(self):
        alg = self.alg_var.get()
        hname = self.h_var.get()
        cur_start = self.agent

        if alg == "GBFS":
            res = gbfs(self.grid, cur_start, self.goal, hname)
        else:
            res = astar(self.grid, cur_start, self.goal, hname)

        self.path_list = res.get("path", [])
        self.path_set = set(self.path_list)
        self.last_cost = res.get("cost", 0)
        self.last_time = res.get("time_ms", 0)

        self.lbl_cost.config(text="Path Cost: " + (str(self.last_cost) if self.path_list else "No Path"))
        self.lbl_time.config(text="Time (ms): " + str(self.last_time))
        self.draw_grid()

    def spawn_obstacle(self):
        p = self.spawn_var.get()
        if p <= 0:
            return None
        if random.randint(1, 100) > p:
            return None

        tries = 0
        while tries < 200:
            tries += 1
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            pos = (r, c)

            if pos == self.start or pos == self.goal or pos == self.agent:
                continue
            if self.grid[r][c] == 1:
                continue

            self.grid[r][c] = 1
            self.recolor(r, c)
            return pos
        return None

    def move_step(self):
        if not self.moving:
            return

        if self.agent == self.goal:
            self.moving = False
            self.btn_run.config(state="normal")
            self.btn_move.config(state="normal")
            self.lbl_status.config(text="Status: Reached Goal")
            return

        new_wall = None
        if self.dynamic_on.get() == 1:
            new_wall = self.spawn_obstacle()

        if new_wall is not None:
            rem = self.path_list[self.move_i+1:] if self.move_i+1 < len(self.path_list) else []
            if new_wall in rem:
                self.lbl_status.config(text="Status: Replanning...")
                self.path_set = set()
                self.draw_grid()
                self.compute_path_no_anim()
                self.move_i = 0
                self.lbl_status.config(text="Status: Moving...")

        if not self.path_list or len(self.path_list) < 2:
            self.moving = False
            self.btn_run.config(state="normal")
            self.btn_move.config(state="normal")
            self.lbl_status.config(text="Status: Stopped (No Path)")
            return

        if self.move_i >= len(self.path_list) or self.path_list[self.move_i] != self.agent:
            if self.agent in self.path_list:
                self.move_i = self.path_list.index(self.agent)
            else:
                self.move_i = 0

        if self.move_i + 1 < len(self.path_list):
            old = self.agent
            self.agent = self.path_list[self.move_i + 1]
            self.move_i += 1
            self.recolor(old[0], old[1])
            self.recolor(self.agent[0], self.agent[1])

        d = self.delay_var.get()
        if d < 0: d = 0
        self.root.after(d, self.move_step)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
