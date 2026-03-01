import math
import heapq
import time

def h_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def h_euclidean(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x*x + y*y)

def get_neighbors(pos, rows, cols):
    r, c = pos
    nbrs = []
    if r > 0: nbrs.append((r-1, c))
    if r < rows-1: nbrs.append((r+1, c))
    if c > 0: nbrs.append((r, c-1))
    if c < cols-1: nbrs.append((r, c+1))
    return nbrs

def build_path(parent, start, goal):
    if goal not in parent and goal != start:
        return []
    cur = goal
    path = [cur]
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path

def gbfs(grid, start, goal, h_name):
    rows = len(grid)
    cols = len(grid[0])

    h_fun = h_euclidean if h_name == "Euclidean" else h_manhattan
    t0 = time.time()

    open_heap = []
    parent = {}
    visited = set()

    visited_order = []
    steps = []  # each step has expanded node + frontier nodes

    frontier_set = set()

    heapq.heappush(open_heap, (h_fun(start, goal), start))
    visited.add(start)
    frontier_set.add(start)

    while open_heap:
        hval, node = heapq.heappop(open_heap)
        frontier_set.discard(node)

        visited_order.append(node)

        if node == goal:
            t1 = time.time()
            path = build_path(parent, start, goal)
            cost = len(path) - 1 if path else 0
            return {
                "path": path,
                "cost": cost,
                "visited": visited_order,
                "time_ms": int((t1 - t0) * 1000),
                "steps": steps
            }

        for nb in get_neighbors(node, rows, cols):
            r, c = nb
            if grid[r][c] == 1:
                continue
            if nb in visited:
                continue
            visited.add(nb)
            parent[nb] = node
            heapq.heappush(open_heap, (h_fun(nb, goal), nb))
            frontier_set.add(nb)

        steps.append({"expanded": node, "frontier": list(frontier_set)})

    t1 = time.time()
    return {"path": [], "cost": 0, "visited": visited_order, "time_ms": int((t1 - t0) * 1000), "steps": steps}

def astar(grid, start, goal, h_name):
    rows = len(grid)
    cols = len(grid[0])

    h_fun = h_euclidean if h_name == "Euclidean" else h_manhattan
    t0 = time.time()

    open_heap = []
    parent = {}
    best_g = {}
    closed = set()

    visited_order = []
    steps = []

    best_g[start] = 0
    heapq.heappush(open_heap, (h_fun(start, goal), 0, start))  # (f,g,node)

    while open_heap:
        f, g, node = heapq.heappop(open_heap)

        if node in closed:
            continue
        closed.add(node)

        visited_order.append(node)

        if node == goal:
            t1 = time.time()
            path = build_path(parent, start, goal)
            cost = best_g[goal]
            return {
                "path": path,
                "cost": cost,
                "visited": visited_order,
                "time_ms": int((t1 - t0) * 1000),
                "steps": steps
            }

        for nb in get_neighbors(node, rows, cols):
            r, c = nb
            if grid[r][c] == 1:
                continue

            new_g = best_g[node] + 1
            if nb not in best_g or new_g < best_g[nb]:
                best_g[nb] = new_g
                parent[nb] = node
                new_f = new_g + h_fun(nb, goal)
                heapq.heappush(open_heap, (new_f, new_g, nb))

        # build frontier snapshot from heap (unique nodes not in closed)
        frontier = set()
        for ff, gg, nn in open_heap:
            if nn not in closed:
                frontier.add(nn)

        steps.append({"expanded": node, "frontier": list(frontier)})

    t1 = time.time()
    return {"path": [], "cost": 0, "visited": visited_order, "time_ms": int((t1 - t0) * 1000), "steps": steps}
