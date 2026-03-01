Dynamic Pathfinding Agent - Report (Template)

1) Environment Specifications
- Dynamic grid sizing (rows x cols)
- Fixed start and goal
- Random map generation with density
- Interactive map editor (click walls)

2) Algorithms Implemented
- Greedy Best First Search (GBFS): f(n)=h(n)
- A* Search: f(n)=g(n)+h(n)

3) Heuristics
- Manhattan Distance
- Euclidean Distance

4) Dynamic Mode (Obstacles + Replanning)
- Obstacles spawn with probability each move
- If obstacle blocks remaining path -> replan from current agent location
- If obstacle not on path -> keep moving (efficiency)

5) Visualization & Metrics
- Frontier: Yellow
- Visited/Expanded: Blue
- Final Path: Green
- Agent: Orange
Metrics:
- Nodes visited
- Path cost
- Execution time (ms)

6) Test Cases (Screenshots)
- Best case for GBFS
- Worst case for GBFS
- Best case for A*
- Worst case for A*

(Add screenshots in screenshots/ folder and reference them here)
