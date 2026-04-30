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
| Machine Learning | **Random Forest Regressor** | Forecast a congestion factor `C` from `(RoadID, TimeOfDay, Capacity, Volume)`. | Training: O(n · log n · trees) |

The first six implementations live in `algorithms.py` and operate on the shared graph defined in `models.py`. The ML forecaster lives in `ML_Model.py` and is trained on `augmented_traffic_data.csv`.

## Project Structure

```text
Algorithm_Project/
├── main.py                       # Entry point — launches the GUI
├── GUI.py                        # Tkinter UI, canvas visualization, and tab logic
├── algorithms.py                 # Kruskal, Dijkstra, A*, DP, and greedy implementations
├── models.py                     # Node, Edge, and TransportationGraph classes
├── data_loader.py                # Loads the Cairo dataset into the graph
├── ML_Model.py                   # Random Forest traffic-congestion forecaster
├── augmented_traffic_data.csv    # Training set (RoadID, TimeOfDay, Capacity, Volume, C)
├── traffic_model.pkl             # Trained model (joblib)
├── road_encoder.pkl              # LabelEncoder for RoadID
├── time_encoder.pkl              # LabelEncoder for TimeOfDay
├── requirements.txt              # ML dependencies (sklearn, joblib, pandas, numpy)
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

The core GUI app (route planning, MST, A*, DP optimizers, metro display, etc.) uses **only the Python standard library**. The optional **ML Traffic Forecast** feature in the Route tab additionally needs `scikit-learn`, `joblib`, `pandas`, and `numpy` — these are listed in `requirements.txt`.

## Installation

```bash
git clone <your-repo-url>
cd Algorithm_Project

# Optional — only needed if you want the ML traffic forecast feature
pip install -r requirements.txt
```

If you skip the `pip install`, the app still runs; the "🔮 Predict Route Congestion" button will simply report that the ML model is unavailable.

### Re‑training the model (optional)

The repo ships pre‑trained `traffic_model.pkl`, `road_encoder.pkl`, and `time_encoder.pkl`. To regenerate them from `augmented_traffic_data.csv`:

```bash
python ML_Model.py
```

This reports MSE / R² on a held‑out 20% test split and overwrites the three `.pkl` files.

## Usage

From the project root run:

```bash
python main.py
```

The main window (`1600x900`) opens with the Cairo network rendered on the right and the algorithm control panel on the left.

## GUI Tabs Overview

- **Route** — Pick a start node, an end node, and a time period; runs Dijkstra (or A*) and highlights the resulting path with travel time and distance. Includes a **🧠 ML Traffic Forecast** subsection that uses the Random Forest in `ML_Model.py` to predict a congestion factor for each segment of the current route that has training data.
- **Network** — Runs Kruskal's MST with toggles for *prioritize critical facilities* and *include new road proposals*; displays the selected MST edges and total cost.
- **Emergency** — Runs A\* between any node and the nearest medical facility (or a chosen destination) with quick‑scenario buttons.
- **Transit** — Runs the bus scheduling DP for a chosen route and number of available buses, reporting maximum population coverage. Also lets you visualize any of the three metro lines (M1/M2/M3) on the canvas, and run greedy traffic‑signal optimization for an intersection.
- **Maintenance** — Runs the 0/1 knapsack DP given a budget and lists the roads selected for repair along with total cost and benefit.

Each tab also shows a textual summary of the result alongside the canvas highlights.

## ML Model Details

`ML_Model.py` trains a `RandomForestRegressor` with 100 estimators on a **merged training set**:

1. **`augmented_traffic_data.csv`** — 32 hand‑labeled rows for 8 central‑Cairo road segments × 4 time periods (real‑world ground truth).
2. **Synthetic rows** auto‑generated from every other graph edge so the model can predict for any route in the network. Volume is reverse‑derived from each edge's stored `traffic_pattern`, and the synthetic congestion target follows a simple linear rule fit on the hand‑labeled data: `C ≈ clamp(0.5 + 4 · (volume / capacity), 0.5, 3.5)`.

When a road appears in both sources, the hand‑labeled row wins (its `C` is real, not derived). Total training set: **184 rows across 46 roads**.

Inputs to the Random Forest are `(RoadID, TimeOfDay, Capacity, Volume)` after label‑encoding the categorical fields; the target `C` is a real‑valued congestion factor in roughly the [0.5, 3.5] range.

At runtime the GUI:

1. Lazily loads the three `.pkl` artifacts the first time a prediction is requested (cached via `lru_cache`).
2. Maps the current graph edge to its RoadID via `_build_edge_road_map()` in `ML_Model.py` — uses the friendly CSV name for the 8 hand‑labeled roads, derives `"<Node A>-<Node B> Road"` for everything else.
3. Approximates `Volume` from the edge's stored `traffic_pattern` ratio so the prediction matches the training distribution.
4. Categorizes the predicted `C` into Light / Moderate / Heavy / Severe for the result text.

Click **🔄 Retrain Model** in the Route tab (or run `python ML_Model.py`) to regenerate the artifacts after editing the graph or the CSV.

## Notes

- Coordinates in the dataset are real Cairo lat/long values, but the GUI uses a manually tuned layout (see `TransportationGUI.calculate_layout`) to keep the central nodes readable.
- The travel‑time model combines distance, a time‑of‑day congestion factor, and a road‑condition factor; emergency routing applies an additional condition bonus so well‑maintained roads are preferred.
- Edges are stored as undirected: the key for `graph.edges` is `tuple(sorted([from_id, to_id]))`.
