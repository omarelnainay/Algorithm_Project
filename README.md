# Cairo Smart City Transportation Optimization System

An interactive desktop application that models Cairo's transportation network as a weighted graph and applies classic algorithm‑design techniques (greedy, dynamic programming, shortest‑path, and informed search) to solve real‑world urban‑mobility problems.

The system ships with a Tkinter GUI that visualizes the network on a custom canvas and lets the user run each algorithm interactively, inspecting results both numerically and graphically.

---

## Table of Contents

- [Features](#features)
- [Algorithms Implemented](#algorithms-implemented)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [GUI Tabs Overview](#gui-tabs-overview)
- [Notes](#notes)

---

## Features

- Weighted graph model of Cairo with 15 neighborhoods, 10 critical facilities, existing roads, candidate new roads, traffic patterns, metro lines, and bus routes.
- Time‑of‑day aware travel times (morning, afternoon, evening, night) driven by per‑edge traffic patterns and road condition.
- Interactive Tkinter GUI with a custom map canvas, color‑coded node types, and highlighted result paths/edges.
- Five algorithm modules covering shortest path, network design, emergency routing, transit planning, and maintenance allocation.

## Algorithms Implemented

| Category | Algorithm | Purpose | Complexity |
|---|---|---|---|
| Greedy | **Kruskal's MST** (with Union–Find) | Design a minimum‑cost road network that prioritizes critical facilities and high‑population areas. | O(E log E) |
| Shortest Path | **Dijkstra** | Time‑dependent shortest travel‑time route between any two nodes. | O((V + E) log V) |
| Informed Search | **A\*** | Emergency vehicle routing using straight‑line distance heuristic and condition bonus. | O((V + E) log V) |
| Dynamic Programming | **Bus Scheduling DP** | Allocate a limited fleet across a route to maximize population coverage. | O(n · k) |
| Dynamic Programming | **Road Maintenance (0/1 Knapsack)** | Pick repairs that maximize benefit under a fixed budget. | O(n · budget) |
| Greedy | **Traffic Signal Optimization** | Distribute green‑time at an intersection proportional to flow × population. | O(d log d) |

All implementations live in `algorithms.py` and operate on the shared graph defined in `models.py`.

## Project Structure

```text
Algorithm_Project/
├── main.py           # Entry point — launches the GUI
├── GUI.py            # Tkinter UI, canvas visualization, and tab logic
├── algorithms.py     # Kruskal, Dijkstra, A*, DP, and greedy implementations
├── models.py         # Node, Edge, and TransportationGraph classes
├── data_loader.py    # Loads the Cairo dataset into the graph
└── README.md
```

## Dataset

The dataset is hard‑coded in `data_loader.py` and includes:

- **15 neighborhoods** — id, name, population, type (Residential / Mixed / Business / Industrial / Government), and geographic coordinates.
- **10 facilities** — airport, transit hub, universities, hospitals, museum, stadium, etc.
- **Existing roads** — distance (km), capacity (vehicles/hour), condition (1–10).
- **Candidate new roads** — same fields plus construction cost (millions EGP).
- **Traffic flow patterns** — morning / afternoon / evening / night demand per edge.
- **3 metro lines** and **8 bus routes** with stops and daily passenger counts.

## Requirements

- Python **3.8+**
- Tkinter (bundled with the standard CPython installer on Windows/macOS; on Debian/Ubuntu install with `sudo apt install python3-tk`)

The project uses **only the Python standard library** (`tkinter`, `heapq`, `math`, `collections`, `typing`, `time`) — no third‑party packages are required.

## Installation

```bash
git clone <your-repo-url>
cd Algorithm_Project
```

No `pip install` step is needed.

## Usage

From the project root run:

```bash
python main.py
```

The main window (`1600x900`) opens with the Cairo network rendered on the right and the algorithm control panel on the left.

## GUI Tabs Overview

- **Route Planning** — Pick a start node, an end node, and a time period; runs Dijkstra and highlights the resulting path with travel time and distance.
- **Network Design** — Runs Kruskal's MST with toggles for *prioritize critical facilities* and *include new road proposals*; displays the selected MST edges and total cost.
- **Emergency** — Runs A\* between any node and the nearest medical facility (or a chosen destination) with quick‑scenario buttons.
- **Transit** — Runs the bus scheduling DP for a chosen route and number of available buses, reporting maximum population coverage.
- **Maintenance** — Runs the 0/1 knapsack DP given a budget and lists the roads selected for repair along with total cost and benefit.

Each tab also shows a textual summary of the result alongside the canvas highlights.

## Notes

- Coordinates in the dataset are real Cairo lat/long values, but the GUI uses a manually tuned layout (see `TransportationGUI.calculate_layout`) to keep the central nodes readable.
- The travel‑time model combines distance, a time‑of‑day congestion factor, and a road‑condition factor; emergency routing applies an additional condition bonus so well‑maintained roads are preferred.
- Edges are stored as undirected: the key for `graph.edges` is `tuple(sorted([from_id, to_id]))`.
