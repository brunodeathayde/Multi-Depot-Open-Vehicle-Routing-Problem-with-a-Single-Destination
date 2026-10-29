# Optimization Heuristics 

This repository contains Python implementations of constructive heuristics and local search techniques for the variant under study.

---

## Code Base & Included Algorithms

The repository consists of the following Python modules:

### 1. `nearest_neighboor.py`
* **Algorithm:** Nearest Neighbor Heuristic
* **Description:** A greedy constructive heuristic commonly applied to routing problems (e.g., TSP/VRP). It builds a tour by iteratively visiting the nearest unvisited node until all nodes are served.

### 2. `gillet_miller.py`
* **Algorithm:** Gillett & Miller Sweep Algorithm
* **Description:** A classic two-phase heuristic for the Vehicle Routing Problem (VRP). It uses polar coordinates to cluster nodes geographically before routing them.

### 3. `cheapest_insertion.py`
* **Algorithm:** Cheapest Insertion Heuristic
* **Description:** A constructive route-building heuristic that iteratively inserts unassigned nodes into the position within the partial tour that minimizes incremental distance or cost.

### 4. `NEH.py`
* **Algorithm:** Nawaz-Enscore-Ham (NEH) Heuristic
* **Description:** One of the most effective constructive heuristics for the Permutation Flowshop Scheduling Problem (PFSP). It orders jobs by total processing time and places them sequentially into the best position to minimize makespan ($C_{max}$).

### 5. `NEH_local_search.py`
* **Algorithm:** NEH with Local Search Enhancement
* **Description:** An extension of the standard NEH heuristic integrated with local search procedures (e.g., insertion or swap neighborhoods) to refine candidate solutions and achieve superior solutions.

### 6. `beam_search.py`
* **Algorithm:** Beam Search
* **Description:** A heuristic search algorithm that explores a graph/search tree by expanding the most promising nodes in a limited set (beam width), balancing solution quality and computational efficiency.

---

## Usage

Ensure you have Python 3.8+ installed. You can run any individual script directly from the command line:

```bash
python nearest_neighboor.py
python gillet_miller.py
python cheapest_insertion.py
python NEH.py
python NEH_local_search.py
python beam_search.py
