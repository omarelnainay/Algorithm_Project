import heapq
import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set
import time
class Node:
    """Represents a neighborhood or facility in the network."""
    def __init__(self, id_str: str, name: str, population: int, node_type: str, x: float, y: float):
        self.id = id_str
        self.name = name
        self.population = population
        self.type = node_type
        self.x = x
        self.y = y
        
    def __repr__(self):
        return f"Node({self.id}, {self.name})"

class Edge:
    """Represents a road in the network."""
    def __init__(self, from_id: str, to_id: str, distance: float, capacity: int, condition: int = 7, 
                 is_new: bool = False, construction_cost: float = 0):
        self.from_id = from_id
        self.to_id = to_id
        self.distance = distance
        self.capacity = capacity
        self.condition = condition
        self.is_new = is_new
        self.construction_cost = construction_cost
        self.traffic_pattern = [1.0, 0.7, 0.9, 0.5]
        
    def get_travel_time(self, time_period: int = 0) -> float:
        """Calculate travel time based on distance and traffic conditions.
        time_period: 0=morning, 1=afternoon, 2=evening, 3=night"""
        base_time = self.distance * 1.5
        congestion_factor = self.traffic_pattern[time_period]
        condition_factor = 1 + (10 - self.condition) * 0.03
        return base_time * congestion_factor * condition_factor

class TransportationGraph:
    """Weighted graph representation of Cairo's transportation network."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[Tuple[str, str], Edge] = {}
        self.adjacency: Dict[str, List[Tuple[str, Edge]]] = defaultdict(list)
        self.metro_lines = {}
        self.bus_routes = {}
        
    def add_node(self, node: Node):
        self.nodes[node.id] = node
        
    def add_edge(self, edge: Edge):
        key = tuple(sorted([edge.from_id, edge.to_id]))
        self.edges[key] = edge
        self.adjacency[edge.from_id].append((edge.to_id, edge))
        self.adjacency[edge.to_id].append((edge.from_id, edge))
        
    def get_edge(self, from_id: str, to_id: str) -> Optional[Edge]:
        key = tuple(sorted([from_id, to_id]))
        return self.edges.get(key)
    
    def get_neighbors(self, node_id: str) -> List[Tuple[str, Edge]]:
        return self.adjacency.get(node_id, [])
    
    def node_exists(self, node_id: str) -> bool:
        return node_id in self.nodes

# ============================================================================
# DATA INITIALIZATION
# ============================================================================

def load_data() -> TransportationGraph:
    """Load all provided data into the graph structure."""
    graph = TransportationGraph()
    
    # Neighborhoods data
    neighborhoods = [
        ("1", "Maadi", 250000, "Residential", 31.25, 29.96),
        ("2", "Nasr City", 500000, "Mixed", 31.34, 30.06),
        ("3", "Downtown Cairo", 100000, "Business", 31.24, 30.04),
        ("4", "New Cairo", 300000, "Residential", 31.47, 30.03),
        ("5", "Heliopolis", 200000, "Mixed", 31.32, 30.09),
        ("6", "Zamalek", 50000, "Residential", 31.22, 30.06),
        ("7", "6th October City", 400000, "Mixed", 30.98, 29.93),
        ("8", "Giza", 550000, "Mixed", 31.21, 29.99),
        ("9", "Mohandessin", 180000, "Business", 31.20, 30.05),
        ("10", "Dokki", 220000, "Mixed", 31.21, 30.03),
        ("11", "Shubra", 450000, "Residential", 31.24, 30.11),
        ("12", "Helwan", 350000, "Industrial", 31.33, 29.85),
        ("13", "New Admin Capital", 50000, "Government", 31.80, 30.02),
        ("14", "Al Rehab", 120000, "Residential", 31.49, 30.06),
        ("15", "Sheikh Zayed", 150000, "Residential", 30.94, 30.01),
    ]
    
    for n in neighborhoods:
        graph.add_node(Node(*n))
    
    # Facilities
    facilities = [
        ("F1", "Cairo Intl Airport", "Airport", 31.41, 30.11),
        ("F2", "Ramses Railway Stn", "Transit Hub", 31.25, 30.06),
        ("F3", "Cairo University", "Education", 31.21, 30.03),
        ("F4", "Al-Azhar University", "Education", 31.26, 30.05),
        ("F5", "Egyptian Museum", "Tourism", 31.23, 30.05),
        ("F6", "Cairo Intl Stadium", "Sports", 31.30, 30.07),
        ("F7", "Smart Village", "Business", 30.97, 30.07),
        ("F8", "Cairo Festival City", "Commercial", 31.40, 30.03),
        ("F9", "Qasr El Aini Hospital", "Medical", 31.23, 30.03),
        ("F10", "Maadi Military Hosp", "Medical", 31.25, 29.95),
    ]
    
    for f in facilities:
        graph.add_node(Node(f[0], f[1], 0, f[2], f[3], f[4]))
    
    # Existing roads - using the exact data from the PDF
    existing_roads = [
        ("1", "3", 8.5, 3000, 7), ("1", "8", 6.2, 2500, 6),
        ("2", "3", 5.9, 2800, 8), ("2", "5", 4.0, 3200, 9),
        ("3", "5", 6.1, 3500, 7), ("3", "6", 3.2, 2000, 8),
        ("3", "9", 4.5, 2600, 6), ("3", "10", 3.8, 2400, 7),
        ("4", "2", 15.2, 3800, 9), ("4", "14", 5.3, 3000, 10),
        ("5", "11", 7.9, 3100, 7), ("6", "9", 2.2, 1800, 8),
        ("7", "8", 24.5, 3500, 8), ("7", "15", 9.8, 3000, 9),
        ("8", "10", 3.3, 2200, 7), ("8", "12", 14.8, 2600, 5),
        ("9", "10", 2.1, 1900, 7), ("10", "11", 8.7, 2400, 6),
        ("11", "F2", 3.6, 2200, 7), ("12", "1", 12.7, 2800, 6),
        ("13", "4", 45.0, 4000, 10), ("14", "13", 35.5, 3800, 9),
        ("15", "7", 9.8, 3000, 9), ("F1", "5", 7.5, 3500, 9),
        ("F1", "2", 9.2, 3200, 8), ("F2", "3", 2.5, 2000, 7),
        ("F7", "15", 8.3, 2800, 8), ("F8", "4", 6.1, 3000, 9),
    ]
    
    for road in existing_roads:
        graph.add_edge(Edge(road[0], road[1], road[2], road[3], road[4]))
    
    # Potential new roads - from PDF
    new_roads = [
        ("1", "4", 22.8, 4000, 450), ("1", "14", 25.3, 3800, 500),
        ("2", "13", 48.2, 4500, 950), ("3", "13", 56.7, 4500, 1100),
        ("5", "4", 16.8, 3500, 320), ("6", "8", 7.5, 2500, 150),
        ("7", "13", 82.3, 4000, 1600), ("9", "11", 6.9, 2800, 140),
        ("10", "F7", 27.4, 3200, 550), ("11", "13", 62.1, 4200, 1250),
        ("12", "14", 30.5, 3600, 610), ("14", "5", 18.2, 3300, 360),
        ("15", "9", 22.7, 3000, 450), ("F1", "13", 40.2, 4000, 800),
        ("F7", "9", 26.8, 3200, 540),
    ]
    
    for road in new_roads:
        # Check if both nodes exist
        if graph.node_exists(road[0]) and graph.node_exists(road[1]):
            graph.add_edge(Edge(road[0], road[1], road[2], road[3], 7, True, road[4]))
    
    # Traffic flow patterns - from PDF
    traffic_data = {
        ("1", "3"): [2800, 1500, 2600, 800], ("1", "8"): [2200, 1200, 2100, 600],
        ("2", "3"): [2700, 1400, 2500, 700], ("2", "5"): [3000, 1600, 2800, 650],
        ("3", "5"): [3200, 1700, 3100, 800], ("3", "6"): [1800, 1400, 1900, 500],
        ("3", "9"): [2400, 1300, 2200, 550], ("3", "10"): [2300, 1200, 2100, 500],
        ("4", "2"): [3600, 1800, 3300, 750], ("4", "14"): [2800, 1600, 2600, 600],
        ("5", "11"): [2900, 1500, 2700, 650], ("6", "9"): [1700, 1300, 1800, 450],
        ("7", "8"): [3200, 1700, 3000, 700], ("7", "15"): [2800, 1500, 2600, 600],
        ("8", "10"): [2000, 1100, 1900, 450], ("8", "12"): [2400, 1300, 2200, 500],
        ("9", "10"): [1800, 1200, 1700, 400], ("10", "11"): [2200, 1300, 2100, 500],
        ("11", "F2"): [2100, 1200, 2000, 450], ("12", "1"): [2600, 1400, 2400, 550],
        ("13", "4"): [3800, 2000, 3500, 800], ("14", "13"): [3600, 1900, 3300, 750],
        ("15", "7"): [2800, 1500, 2600, 600], ("F1", "5"): [3300, 2200, 3100, 1200],
        ("F1", "2"): [3000, 2000, 2800, 1100], ("F2", "3"): [1900, 1600, 1800, 900],
        ("F7", "15"): [2600, 1500, 2400, 550], ("F8", "4"): [2800, 1600, 2600, 600],
    }
    
    for (from_id, to_id), patterns in traffic_data.items():
        edge = graph.get_edge(from_id, to_id)
        if edge:
            max_cap = edge.capacity
            if max_cap > 0:
                edge.traffic_pattern = [
                    max(0.3, min(2.5, (p / max_cap) * 1.5)) for p in patterns
                ]
    
    # Metro lines - from PDF
    graph.metro_lines = {
        "M1": {"name": "Line 1 (Helwan-New Marg)", "stations": ["12", "1", "3", "F2", "11"], "daily_passengers": 1500000},
        "M2": {"name": "Line 2 (Shubra-Giza)", "stations": ["11", "F2", "3", "10", "8"], "daily_passengers": 1200000},
        "M3": {"name": "Line 3 (Airport-Imbaba)", "stations": ["F1", "5", "2", "3", "9"], "daily_passengers": 800000},
    }
    
    # Bus routes - from PDF
    graph.bus_routes = {
        "B1": {"stops": ["1", "3", "6", "9"], "buses": 25, "daily_passengers": 35000},
        "B2": {"stops": ["7", "15", "8", "10", "3"], "buses": 30, "daily_passengers": 42000},
        "B3": {"stops": ["2", "5", "F1"], "buses": 20, "daily_passengers": 28000},
        "B4": {"stops": ["4", "14", "2", "3"], "buses": 22, "daily_passengers": 31000},
        "B5": {"stops": ["8", "12", "1"], "buses": 18, "daily_passengers": 25000},
        "B6": {"stops": ["11", "5", "2"], "buses": 24, "daily_passengers": 33000},
        "B7": {"stops": ["13", "4", "14"], "buses": 15, "daily_passengers": 21000},
        "B8": {"stops": ["F7", "15", "7"], "buses": 12, "daily_passengers": 17000},
    }
    
    return graph

# ============================================================================
# ALGORITHM IMPLEMENTATIONS
# ============================================================================

class DisjointSet:
    """Disjoint Set Union for Kruskal's algorithm."""
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            self.parent[px] = py
        elif self.rank[px] > self.rank[py]:
            self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        return True

def kruskal_mst(graph: TransportationGraph, prioritize_critical: bool = True) -> Tuple[List[Edge], float]:
    """
    Kruskal's Minimum Spanning Tree algorithm.
    Time Complexity: O(E log E), Space Complexity: O(V + E)
    """
    all_edges = list(graph.edges.values())
    
    critical_types = {'Medical', 'Government', 'Airport', 'Transit Hub'}
    critical_nodes = {n.id for n in graph.nodes.values() if n.type in critical_types}
    
    def edge_cost(edge: Edge) -> float:
        if edge.is_new:
            base = edge.construction_cost
        else:
            base = edge.distance * 10
        
        if prioritize_critical:
            if edge.from_id in critical_nodes or edge.to_id in critical_nodes:
                base *= 0.5
        
        pop_from = graph.nodes[edge.from_id].population if edge.from_id in graph.nodes else 0
        pop_to = graph.nodes[edge.to_id].population if edge.to_id in graph.nodes else 0
        avg_pop = (pop_from + pop_to) / 2
        if avg_pop > 300000:
            base *= 0.7
        
        return base
    
    sorted_edges = sorted(all_edges, key=edge_cost)
    
    all_nodes = list(graph.nodes.keys())
    dsu = DisjointSet(all_nodes)
    
    mst_edges = []
    total_cost = 0.0
    
    for edge in sorted_edges:
        if dsu.union(edge.from_id, edge.to_id):
            mst_edges.append(edge)
            if edge.is_new:
                total_cost += edge.construction_cost
            else:
                total_cost += edge.distance * 5
            
            if len(mst_edges) == len(all_nodes) - 1:
                break
    
    return mst_edges, total_cost

def dijkstra_shortest_path(graph: TransportationGraph, start: str, end: str, 
                          time_period: int = 0) -> Tuple[List[str], float, float]:
    """
    Dijkstra's algorithm for shortest path with time-dependent traffic.
    Returns: (path, travel_time_minutes, total_distance_km)
    """
    if start not in graph.nodes or end not in graph.nodes:
        return [], float('inf'), 0
    
    # Priority queue: (cost_so_far, node, path, distance_so_far)
    pq = [(0, start, [start], 0)]
    # Track best known distance to each node
    best_cost = {start: 0}
    
    while pq:
        current_cost, current_node, path, current_dist = heapq.heappop(pq)
        
        # If we found a better path to this node already, skip
        if current_cost > best_cost.get(current_node, float('inf')):
            continue
        
        if current_node == end:
            return path, current_cost, current_dist
        
        for neighbor, edge in graph.get_neighbors(current_node):
            travel_time = edge.get_travel_time(time_period)
            new_cost = current_cost + travel_time
            new_dist = current_dist + edge.distance
            
            if new_cost < best_cost.get(neighbor, float('inf')):
                best_cost[neighbor] = new_cost
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_cost, neighbor, new_path, new_dist))
    
    return [], float('inf'), 0

def emergency_heuristic(graph: TransportationGraph, node_id: str, goal_id: str) -> float:
    """
    Heuristic for A* emergency routing.
    Uses straight-line distance scaled for emergency vehicle speed.
    """
    node = graph.nodes.get(node_id)
    goal = graph.nodes.get(goal_id)
    if not node or not goal:
        return 0
    
    # Coordinate difference in degrees
    dx = abs(node.x - goal.x) 
    dy = abs(node.y - goal.y)
    
    # Approximate conversion to km (1 degree ≈ 111 km at this latitude)
    distance_km = math.sqrt((dx * 111.32)**2 + (dy * 110.57)**2)
    
    # Emergency vehicles can go faster, so heuristic is distance / speed
    # Assuming 80 km/h for emergency vehicles = 0.75 min/km
    return distance_km * 0.75

def a_star_emergency_routing(graph: TransportationGraph, start: str, end: str,
                            time_period: int = 0) -> Tuple[List[str], float, float]:
    """
    A* search algorithm for emergency vehicle routing.
    Uses heuristic to guide search toward medical facilities.
    
    Returns: (path, travel_time_minutes, total_distance_km)
    """
    # Validate inputs
    if start not in graph.nodes:
        print(f"DEBUG: Start node '{start}' not in graph")
        return [], float('inf'), 0
    if end not in graph.nodes:
        print(f"DEBUG: End node '{end}' not in graph")
        return [], float('inf'), 0
    
    if start == end:
        return [start], 0, 0
    
    # Priority queue: (f_score, counter, g_score, node, path, distance)
    # f_score = g_score + heuristic
    counter = 0
    start_h = emergency_heuristic(graph, start, end)
    pq = [(start_h, counter, 0, start, [start], 0)]
    
    # Track best g_score for each node
    best_g = {start: 0}
    visited = set()
    
    while pq:
        f_score, _, current_g, current_node, path, current_dist = heapq.heappop(pq)
        
        # Skip if we already found a better path to this node
        if current_g > best_g.get(current_node, float('inf')):
            continue
        
        # Found the goal!
        if current_node == end:
            return path, current_g, current_dist
        
        # Mark as visited
        visited.add(current_node)
        
        # Explore neighbors
        for neighbor, edge in graph.get_neighbors(current_node):
            if neighbor in visited:
                continue
            
            # Calculate travel time for emergency vehicle
            base_time = edge.get_travel_time(time_period)
            # Emergency vehicles get priority: better roads = faster, poor roads don't slow them as much
            condition_bonus = 0.6 + (edge.condition / 10) * 0.4  # Range: 0.6 to 1.0
            travel_time = base_time * condition_bonus
            
            new_g = current_g + travel_time
            new_dist = current_dist + edge.distance
            
            # Only consider if this is a better path
            if new_g < best_g.get(neighbor, float('inf')):
                best_g[neighbor] = new_g
                h = emergency_heuristic(graph, neighbor, end)
                f = new_g + h
                new_path = path + [neighbor]
                counter += 1
                heapq.heappush(pq, (f, counter, new_g, neighbor, new_path, new_dist))
    
    # No path found
    return [], float('inf'), 0

def dynamic_programming_bus_scheduling(graph: TransportationGraph, route_id: str, 
                                       available_buses: int) -> Dict:
    """
    Dynamic Programming for optimal bus scheduling.
    Time Complexity: O(n * k), Space Complexity: O(n * k)
    """
    if route_id not in graph.bus_routes:
        return {}
    
    route = graph.bus_routes[route_id]
    stops = route['stops']
    n = len(stops)
    
    populations = []
    for stop_id in stops:
        node = graph.nodes.get(stop_id)
        populations.append(node.population if node else 0)
    
    dp = [[0] * (available_buses + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for j in range(1, available_buses + 1):
            dp[i][j] = dp[i-1][j]
            
            for prev in range(i):
                segment_length = i - prev
                buses_needed = max(1, segment_length // 3)
                
                if buses_needed <= j:
                    coverage = sum(populations[prev:i])
                    if dp[prev][j - buses_needed] + coverage > dp[i][j]:
                        dp[i][j] = dp[prev][j - buses_needed] + coverage
    
    return {
        'route_id': route_id,
        'stops': stops,
        'max_coverage': dp[n][available_buses],
        'population_per_stop': dict(zip(stops, populations)),
        'total_population': sum(populations)
    }

def dp_road_maintenance_allocation(graph: TransportationGraph, budget: float) -> Dict:
    """
    DP for road maintenance allocation (0/1 knapsack).
    Time Complexity: O(n * budget), Space Complexity: O(n * budget)
    """
    existing_roads = [e for e in graph.edges.values() if not e.is_new]
    
    road_data = []
    for edge in existing_roads:
        cost_to_repair = int((10 - edge.condition) * 15)
        if cost_to_repair <= 0:
            continue
            
        pop_from = graph.nodes[edge.from_id].population if edge.from_id in graph.nodes else 0
        pop_to = graph.nodes[edge.to_id].population if edge.to_id in graph.nodes else 0
        benefit = int((edge.capacity / 1000) * (pop_from + pop_to) / 100000)
        
        road_data.append({
            'edge': edge,
            'cost': cost_to_repair,
            'benefit': benefit,
            'condition': edge.condition,
            'road': f"{edge.from_id}-{edge.to_id}"
        })
    
    budget_int = int(budget)
    dp = [0] * (budget_int + 1)
    selected = [[] for _ in range(budget_int + 1)]
    
    for road in road_data:
        cost = road['cost']
        benefit = road['benefit']
        
        for b in range(budget_int, cost - 1, -1):
            if dp[b - cost] + benefit > dp[b]:
                dp[b] = dp[b - cost] + benefit
                selected[b] = selected[b - cost] + [road]
    
    best_b = budget_int
    while best_b > 0 and not selected[best_b]:
        best_b -= 1
    
    return {
        'budget': budget,
        'total_cost': sum(r['cost'] for r in selected[best_b]) if best_b > 0 else 0,
        'total_benefit': dp[best_b] if best_b > 0 else 0,
        'roads_to_repair': selected[best_b] if best_b > 0 else [],
        'num_roads_repaired': len(selected[best_b]) if best_b > 0 else 0
    }

def greedy_traffic_signal_optimization(graph: TransportationGraph, 
                                      intersection_id: str) -> Dict:
    """
    Greedy traffic signal optimization.
    Time Complexity: O(d log d) where d = number of connected roads
    """
    if intersection_id not in graph.nodes:
        return {}
    
    connected = []
    for neighbor, edge in graph.get_neighbors(intersection_id):
        pop = graph.nodes[neighbor].population if neighbor in graph.nodes else 0
        connected.append({
            'neighbor': neighbor,
            'name': graph.nodes[neighbor].name if neighbor in graph.nodes else neighbor,
            'flow': edge.capacity,
            'population': pop,
            'edge': edge
        })
    
    connected.sort(key=lambda x: x['flow'] * x['population'], reverse=True)
    
    total_flow = sum(c['flow'] for c in connected) or 1
    cycle_time = 120
    
    signal_plan = []
    for i, conn in enumerate(connected):
        proportion = conn['flow'] / total_flow
        green_time = max(15, min(45, int(cycle_time * proportion * 0.7)))
        
        signal_plan.append({
            'direction': f"{intersection_id} → {conn['neighbor']} ({conn['name']})",
            'green_time_seconds': green_time,
            'priority': 'HIGH' if i < len(connected)//3 else 'MEDIUM' if i < 2*len(connected)//3 else 'LOW'
        })
    
    return {
        'intersection': intersection_id,
        'intersection_name': graph.nodes[intersection_id].name,
        'signal_plan': signal_plan,
        'total_cycle_time': sum(s['green_time_seconds'] for s in signal_plan)
    }

# ============================================================================
# ENHANCED VISUALIZATION - Manual Node Layout for Better Spacing
# ============================================================================

class TransportationGUI:
    """Enhanced GUI with manual layout for clearer visualization."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cairo Smart City Transportation Optimization System")
        self.root.geometry("1600x900")
        self.root.configure(bg='#1a1a2e')
        
        # Load data
        self.graph = load_data()
        
        # Manual node positions for better spacing (spread out central nodes)
        # These override the geographic coordinates for display purposes
        self.node_positions = self.calculate_layout()
        
        # Node type colors
        self.type_colors = {
            'Residential': '#4CAF50',
            'Mixed': '#FF9800',
            'Business': '#2196F3',
            'Industrial': '#9E9E9E',
            'Government': '#F44336',
            'Airport': '#9C27B0',
            'Transit Hub': '#00BCD4',
            'Education': '#795548',
            'Tourism': '#FF5722',
            'Sports': '#8BC34A',
            'Commercial': '#E91E63',
            'Medical': '#FF1744',
        }
        
        # Visualization state
        self.selected_path = []
        self.mst_edges = []
        self.emergency_path = []
        
        self.setup_ui()
    
    def calculate_layout(self) -> Dict[str, Tuple[float, float]]:
        """
        Calculate better spaced positions for nodes.
        Spreads out the central Cairo nodes while maintaining relative positions.
        """
        positions = {}
        
        # Manually place nodes with better spacing
        # Format: node_id: (x_percent, y_percent) where percents are 0-100 of canvas
        
        # Far East (New Admin Capital area)
        positions["13"] = (90, 48)
        positions["14"] = (82, 42)
        positions["4"] = (78, 38)
        positions["F8"] = (76, 35)
        
        # East/Northeast (Airport, Heliopolis, Nasr City)
        positions["F1"] = (72, 18)
        positions["5"] = (62, 28)
        positions["2"] = (60, 35)
        positions["F6"] = (58, 32)
        positions["11"] = (52, 22)
        positions["F2"] = (50, 30)
        
        # Central Cairo - SPREAD OUT MORE
        positions["3"] = (45, 38)      # Downtown - moved from center
        positions["F5"] = (43, 35)     # Museum
        positions["F4"] = (44, 40)     # Al-Azhar
        positions["6"] = (38, 37)      # Zamalek
        positions["9"] = (35, 35)      # Mohandessin
        positions["F9"] = (40, 42)     # Qasr El Aini Hospital
        positions["10"] = (32, 41)     # Dokki
        positions["F3"] = (30, 43)     # Cairo University
        
        # North
        positions["F7"] = (18, 20)     # Smart Village
        
        # West (Giza, Sheikh Zayed, 6th October)
        positions["15"] = (15, 30)     # Sheikh Zayed
        positions["7"] = (10, 38)      # 6th October City
        positions["8"] = (28, 50)      # Giza
        
        # South (Maadi, Helwan)
        positions["1"] = (42, 58)      # Maadi
        positions["F10"] = (40, 60)    # Maadi Hospital
        positions["12"] = (48, 65)     # Helwan
        
        return positions
    
    def get_canvas_pos(self, node_id: str) -> Tuple[float, float]:
        """Get canvas position with margin offset."""
        canvas_w = max(self.canvas.winfo_width(), 1000)
        canvas_h = max(self.canvas.winfo_height(), 700)
        
        margin_x = 60
        margin_y = 50
        
        if node_id not in self.node_positions:
            return (canvas_w // 2, canvas_h // 2)
        
        x_pct, y_pct = self.node_positions[node_id]
        
        # Convert percentages to canvas coordinates
        avail_w = canvas_w - 2 * margin_x
        avail_h = canvas_h - 2 * margin_y
        
        x = margin_x + (x_pct / 100.0) * avail_w
        y = margin_y + (y_pct / 100.0) * avail_h
        
        return (x, y)
    
    def setup_ui(self):
        """Setup the user interface."""
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left control panel
        control_panel = tk.Frame(main_frame, bg='#16213e', width=380)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_panel.pack_propagate(False)
        
        # Title
        title_label = tk.Label(control_panel, text="🚦 Cairo Transportation\nOptimization System", 
                               font=('Helvetica', 14, 'bold'), bg='#16213e', fg='#e94560')
        title_label.pack(pady=8)
        
        # Notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#16213e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#0f3460', foreground='white', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#e94560')])
        
        notebook = ttk.Notebook(control_panel)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Setup all tabs
        self.setup_path_tab(notebook)
        self.setup_network_tab(notebook)
        self.setup_emergency_tab(notebook)
        self.setup_transit_tab(notebook)
        self.setup_maintenance_tab(notebook)
        
        # Right panel - Canvas
        canvas_frame = tk.Frame(main_frame, bg='#0f3460')
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#0a0a1a', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bottom info panel
        info_frame = tk.Frame(self.root, bg='#16213e', height=100)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(5, 5))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=5, bg='#1a1a2e', fg='#e0e0e0',
                                                   font=('Consolas', 10), insertbackground='white')
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags
        self.info_text.tag_configure('success', foreground='#4CAF50')
        self.info_text.tag_configure('error', foreground='#f44336')
        self.info_text.tag_configure('info', foreground='#2196F3')
        self.info_text.tag_configure('warning', foreground='#FF9800')
        self.info_text.tag_configure('highlight', foreground='#e94560', font=('Consolas', 10, 'bold'))
        
        # Status bar
        self.status_var = tk.StringVar(value=f"Ready | Nodes: {len(self.graph.nodes)} | Roads: {len(self.graph.edges)}")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bg='#0f3460', fg='#aaa',
                             font=('Helvetica', 9), anchor=tk.W, padx=10)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind canvas events
        self.canvas.bind("<Configure>", lambda e: self.draw_network())
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Initial draw
        self.draw_network()
        self.log_info("System initialized successfully", 'success')
        self.log_info("Select start and end nodes to find routes", 'info')
    
    def setup_path_tab(self, notebook):
        """Setup route planning tab."""
        frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(frame, text="🛣️ Route Planning")
        
        tk.Label(frame, text="Find Shortest Path", font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#4CAF50').pack(pady=5)
        
        node_frame = tk.Frame(frame, bg='#16213e')
        node_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(node_frame, text="From:", bg='#16213e', fg='white', width=6).grid(row=0, column=0, sticky='w')
        self.path_start_var = tk.StringVar()
        start_combo = ttk.Combobox(node_frame, textvariable=self.path_start_var, width=25)
        start_combo['values'] = sorted(self.graph.nodes.keys())
        start_combo.grid(row=0, column=1, pady=2)
        
        tk.Label(node_frame, text="To:", bg='#16213e', fg='white', width=6).grid(row=1, column=0, sticky='w')
        self.path_end_var = tk.StringVar()
        end_combo = ttk.Combobox(node_frame, textvariable=self.path_end_var, width=25)
        end_combo['values'] = sorted(self.graph.nodes.keys())
        end_combo.grid(row=1, column=1, pady=2)
        
        options_frame = tk.Frame(frame, bg='#16213e')
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(options_frame, text="Time:", bg='#16213e', fg='white').grid(row=0, column=0, sticky='w')
        self.path_time_var = tk.StringVar(value="Morning")
        time_combo = ttk.Combobox(options_frame, textvariable=self.path_time_var, width=12)
        time_combo['values'] = ["Morning", "Afternoon", "Evening", "Night"]
        time_combo.grid(row=0, column=1, pady=2)
        
        tk.Label(options_frame, text="Algorithm:", bg='#16213e', fg='white').grid(row=1, column=0, sticky='w')
        self.path_algo_var = tk.StringVar(value="Dijkstra")
        algo_combo = ttk.Combobox(options_frame, textvariable=self.path_algo_var, width=12)
        algo_combo['values'] = ["Dijkstra", "A* Search"]
        algo_combo.grid(row=1, column=1, pady=2)
        
        btn_frame = tk.Frame(frame, bg='#16213e')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔍 Find Route", command=self.find_route,
                 bg='#4CAF50', fg='white', font=('Helvetica', 10, 'bold'),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="🗺️ Show All", command=self.show_all_roads,
                 bg='#2196F3', fg='white', font=('Helvetica', 10),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="🧹 Clear", command=self.clear_paths,
                 bg='#FF9800', fg='white', font=('Helvetica', 10),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=2)
        
        self.path_result_text = tk.Text(frame, height=10, bg='#1a1a2e', fg='#4CAF50',
                                        font=('Consolas', 9), wrap=tk.WORD)
        self.path_result_text.pack(fill=tk.X, padx=10, pady=5)
    
    def setup_network_tab(self, notebook):
        """Setup network design tab."""
        frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(frame, text="🌐 Network Design")
        
        tk.Label(frame, text="MST Network Optimization", font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#FF9800').pack(pady=5)
        
        info_text = """Design optimal road network using 
Kruskal's Minimum Spanning Tree.
Prioritizes critical facilities 
and high-population areas."""
        tk.Label(frame, text=info_text, bg='#16213e', fg='#ccc', 
                justify=tk.LEFT, font=('Helvetica', 9)).pack(pady=5)
        
        self.mst_prioritize_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="✓ Prioritize critical facilities", 
                      variable=self.mst_prioritize_var, bg='#16213e', fg='white',
                      selectcolor='#0f3460', activebackground='#16213e',
                      activeforeground='white').pack(pady=5, anchor='w', padx=10)
        
        tk.Checkbutton(frame, text="✓ Include new road proposals", 
                      variable=tk.BooleanVar(value=True), bg='#16213e', fg='white',
                      selectcolor='#0f3460', activebackground='#16213e',
                      activeforeground='white').pack(pady=5, anchor='w', padx=10)
        
        tk.Button(frame, text="🏗️ Generate MST", command=self.generate_mst,
                 bg='#FF9800', fg='white', font=('Helvetica', 10, 'bold'),
                 padx=20, pady=5).pack(pady=15)
        
        self.mst_result_text = tk.Text(frame, height=8, bg='#1a1a2e', fg='#FF9800',
                                       font=('Consolas', 9), wrap=tk.WORD)
        self.mst_result_text.pack(fill=tk.X, padx=10, pady=5)
    
    def setup_emergency_tab(self, notebook):
        """Setup emergency routing tab."""
        frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(frame, text="🚑 Emergency")
        
        tk.Label(frame, text="Emergency Vehicle Routing", font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#f44336').pack(pady=5)
        
        tk.Label(frame, text="A* Search optimized for\nemergency response to medical facilities", 
                bg='#16213e', fg='#ccc', justify=tk.CENTER).pack(pady=2)
        
        tk.Label(frame, text="Emergency From:", bg='#16213e', fg='white').pack(anchor='w', padx=10)
        self.em_from_var = tk.StringVar()
        em_from = ttk.Combobox(frame, textvariable=self.em_from_var, width=25)
        em_from['values'] = sorted(self.graph.nodes.keys())
        em_from.pack(pady=2)
        
        tk.Label(frame, text="To Medical Facility:", bg='#16213e', fg='white').pack(anchor='w', padx=10)
        self.em_to_var = tk.StringVar()
        em_to = ttk.Combobox(frame, textvariable=self.em_to_var, width=25)
        medical_ids = [n.id for n in self.graph.nodes.values() if n.type == 'Medical']
        em_to['values'] = medical_ids
        em_to.pack(pady=2)
        
        # Quick scenario buttons
        tk.Label(frame, text="Quick Scenarios:", bg='#16213e', fg='white').pack(anchor='w', padx=10, pady=(10,0))
        scenario_frame = tk.Frame(frame, bg='#16213e')
        scenario_frame.pack(fill=tk.X, padx=10)
        
        scenarios = [
            ("Maadi → Maadi Hospital", "1", "F10"),
            ("Downtown → Qasr El Aini", "3", "F9"),
            ("Nasr City → Maadi Hospital", "2", "F10"),
            ("Heliopolis → Qasr El Aini", "5", "F9"),
        ]
        
        for label, frm, to in scenarios:
            tk.Button(scenario_frame, text=label, 
                     command=lambda f=frm, t=to: self.run_emergency_scenario(f, t),
                     bg='#f44336', fg='white', font=('Helvetica', 7),
                     padx=5, pady=2).pack(side=tk.LEFT, padx=2)
        
        tk.Button(frame, text="🚨 Find Emergency Route", command=self.find_emergency_route,
                 bg='#f44336', fg='white', font=('Helvetica', 10, 'bold'),
                 padx=20, pady=5).pack(pady=15)
        
        self.em_result_text = tk.Text(frame, height=10, bg='#1a1a2e', fg='#f44336',
                                      font=('Consolas', 9), wrap=tk.WORD)
        self.em_result_text.pack(fill=tk.X, padx=10, pady=5)
    
    def setup_transit_tab(self, notebook):
        """Setup public transit tab."""
        frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(frame, text="🚌 Transit")
        
        tk.Label(frame, text="Public Transit Optimization", font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#00BCD4').pack(pady=5)
        
        tk.Label(frame, text="Bus Schedule (DP):", bg='#16213e', fg='white',
                font=('Helvetica', 10)).pack(anchor='w', padx=10)
        
        sel_frame = tk.Frame(frame, bg='#16213e')
        sel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(sel_frame, text="Route:", bg='#16213e', fg='#aaa').grid(row=0, column=0)
        self.bus_route_var = tk.StringVar(value="B1")
        route_combo = ttk.Combobox(sel_frame, textvariable=self.bus_route_var, width=8)
        route_combo['values'] = list(self.graph.bus_routes.keys())
        route_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(sel_frame, text="Buses:", bg='#16213e', fg='#aaa').grid(row=0, column=2)
        self.bus_count_var = tk.IntVar(value=10)
        tk.Spinbox(sel_frame, from_=5, to=50, textvariable=self.bus_count_var, 
                  width=5, bg='#0f3460', fg='white').grid(row=0, column=3, padx=5)
        
        tk.Button(frame, text="📊 Optimize Schedule", command=self.optimize_bus_schedule,
                 bg='#00BCD4', fg='white', font=('Helvetica', 9, 'bold'),
                 padx=15, pady=3).pack(pady=5)
        
        self.transit_result_text = tk.Text(frame, height=6, bg='#1a1a2e', fg='#00BCD4',
                                           font=('Consolas', 9), wrap=tk.WORD)
        self.transit_result_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Traffic signal optimization
        tk.Label(frame, text="Traffic Signal (Greedy):", bg='#16213e', fg='white',
                font=('Helvetica', 10)).pack(anchor='w', padx=10, pady=(10,0))
        
        sig_frame = tk.Frame(frame, bg='#16213e')
        sig_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(sig_frame, text="Intersection:", bg='#16213e', fg='#aaa').grid(row=0, column=0)
        self.intersection_var = tk.StringVar(value="3")
        int_combo = ttk.Combobox(sig_frame, textvariable=self.intersection_var, width=8)
        int_combo['values'] = sorted(self.graph.nodes.keys())
        int_combo.grid(row=0, column=1, padx=5)
        
        tk.Button(frame, text="🚦 Optimize Signals", command=self.optimize_intersection,
                 bg='#FFEB3B', fg='#333', font=('Helvetica', 9, 'bold'),
                 padx=15, pady=3).pack(pady=5)
        
        self.signal_result_text = tk.Text(frame, height=6, bg='#1a1a2e', fg='#FFEB3B',
                                          font=('Consolas', 9), wrap=tk.WORD)
        self.signal_result_text.pack(fill=tk.X, padx=10, pady=5)
    
    def setup_maintenance_tab(self, notebook):
        """Setup maintenance tab."""
        frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(frame, text="🔧 Maintenance")
        
        tk.Label(frame, text="Road Maintenance Allocation", font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#FF9800').pack(pady=5)
        
        tk.Label(frame, text="DP-based resource allocation\nfor road repairs", 
                bg='#16213e', fg='#ccc', justify=tk.CENTER).pack(pady=2)
        
        tk.Label(frame, text="Budget (Million EGP):", bg='#16213e', fg='white').pack()
        self.budget_var = tk.DoubleVar(value=500)
        budget_scale = tk.Scale(frame, from_=100, to=2000, variable=self.budget_var, 
                               orient=tk.HORIZONTAL, bg='#16213e', fg='white',
                               highlightbackground='#16213e', length=200)
        budget_scale.pack(pady=5)
        
        tk.Button(frame, text="🔧 Optimize Allocation", command=self.optimize_maintenance,
                 bg='#FF9800', fg='white', font=('Helvetica', 9, 'bold'),
                 padx=15, pady=3).pack(pady=5)
        
        self.maint_result_text = tk.Text(frame, height=8, bg='#1a1a2e', fg='#FF9800',
                                         font=('Consolas', 9), wrap=tk.WORD)
        self.maint_result_text.pack(fill=tk.X, padx=10, pady=5)
    
    def run_emergency_scenario(self, from_id, to_id):
        """Run a predefined emergency scenario."""
        self.em_from_var.set(from_id)
        self.em_to_var.set(to_id)
        self.find_emergency_route()
    
    def find_route(self):
        """Execute route finding."""
        start = self.path_start_var.get()
        end = self.path_end_var.get()
        time_str = self.path_time_var.get()
        algo = self.path_algo_var.get()
        
        if not start or not end:
            self.path_result_text.delete(1.0, tk.END)
            self.path_result_text.insert(1.0, "⚠️ Please select both start and end nodes!")
            return
        
        time_map = {"Morning": 0, "Afternoon": 1, "Evening": 2, "Night": 3}
        time_period = time_map.get(time_str, 0)
        
        if algo == "Dijkstra":
            path, travel_time, distance = dijkstra_shortest_path(self.graph, start, end, time_period)
        else:
            path, travel_time, distance = a_star_emergency_routing(self.graph, start, end, time_period)
        
        self.path_result_text.delete(1.0, tk.END)
        
        if path:
            self.selected_path = path
            self.emergency_path = []
            self.mst_edges = []
            
            path_names = []
            for node_id in path:
                node = self.graph.nodes.get(node_id)
                if node:
                    path_names.append(f"{node.name} ({node_id})")
            
            cost = distance * 2.5
            
            result = f"✅ Route Found!\n\n"
            result += f"📍 Path ({len(path)-1} segments):\n"
            result += f"   {' → '.join(path)}\n\n"
            result += f"📍 Via:\n"
            for i, name in enumerate(path_names):
                prefix = '🟢' if i == 0 else '🔴' if i == len(path_names)-1 else '🔵'
                result += f"   {prefix} {name}\n"
            
            result += f"\n📊 Statistics:\n"
            result += f"   Distance: {distance:.1f} km\n"
            result += f"   Travel Time: {travel_time:.1f} min\n"
            result += f"   Est. Fuel Cost: {cost:.1f} EGP\n"
            result += f"   Algorithm: {algo}\n"
            result += f"   Traffic: {time_str}"
            
            self.path_result_text.insert(1.0, result)
            self.log_info(f"Route found: {start} → {end} ({distance:.1f} km, {travel_time:.1f} min)", 'success')
            self.status_var.set(f"Route: {start} → {end} | Distance: {distance:.1f} km | Time: {travel_time:.1f} min")
        else:
            self.path_result_text.insert(1.0, f"❌ No route found between {start} and {end}!\nCheck if nodes are connected.")
            self.log_info(f"No route between {start} and {end}", 'error')
        
        self.draw_network()
    
    def generate_mst(self):
        """Generate MST network."""
        prioritize = self.mst_prioritize_var.get()
        mst_edges, total_cost = kruskal_mst(self.graph, prioritize)
        
        self.mst_edges = mst_edges
        self.selected_path = []
        self.emergency_path = []
        
        self.mst_result_text.delete(1.0, tk.END)
        
        result = f"🏗️ Optimal MST Network\n\n"
        result += f"📊 Summary:\n"
        result += f"   Total Edges: {len(mst_edges)}\n"
        result += f"   Total Cost: {total_cost:.1f} M EGP\n\n"
        result += f"🛣️ Selected Roads:\n"
        
        for i, edge in enumerate(mst_edges[:10]):
            from_name = self.graph.nodes[edge.from_id].name if edge.from_id in self.graph.nodes else edge.from_id
            to_name = self.graph.nodes[edge.to_id].name if edge.to_id in self.graph.nodes else edge.to_id
            cost = edge.construction_cost if edge.is_new else edge.distance * 5
            result += f"   {i+1}. {from_name} ↔ {to_name}: {cost:.0f}M\n"
        
        if len(mst_edges) > 10:
            result += f"   ... and {len(mst_edges)-10} more"
        
        self.mst_result_text.insert(1.0, result)
        self.log_info(f"MST generated: {len(mst_edges)} edges, {total_cost:.1f}M EGP", 'success')
        self.status_var.set(f"MST: {len(mst_edges)} edges | Cost: {total_cost:.1f}M EGP")
        self.draw_network()
    
    def find_emergency_route(self):
        """Find emergency route using A*."""
        start = self.em_from_var.get()
        end = self.em_to_var.get()
        
        self.em_result_text.delete(1.0, tk.END)
        
        if not start or not end:
            self.em_result_text.insert(1.0, "⚠️ Please select both start and destination!")
            return
        
        # Validate nodes exist
        if start not in self.graph.nodes:
            self.em_result_text.insert(1.0, f"❌ Start node '{start}' not found!")
            return
        if end not in self.graph.nodes:
            self.em_result_text.insert(1.0, f"❌ Destination node '{end}' not found!")
            return
        
        # Run A* emergency routing
        path, travel_time, distance = a_star_emergency_routing(self.graph, start, end)
        
        if path and len(path) > 0:
            self.emergency_path = path
            self.selected_path = []
            self.mst_edges = []
            
            start_name = self.graph.nodes[start].name
            end_name = self.graph.nodes[end].name
            
            result = f"🚨 EMERGENCY ROUTE FOUND!\n\n"
            result += f"📍 From: {start_name} ({start})\n"
            result += f"📍 To: {end_name} ({end})\n\n"
            result += f"🛣️ Optimal Route:\n"
            result += f"   {' → '.join(path)}\n\n"
            result += f"📍 Via Locations:\n"
            for node_id in path:
                node = self.graph.nodes.get(node_id)
                if node:
                    result += f"   • {node.name} ({node_id})\n"
            
            result += f"\n⏱️ Response Time: {travel_time:.1f} minutes\n"
            result += f"📏 Distance: {distance:.1f} km\n"
            result += f"🚑 Priority: EMERGENCY - A* optimized route"
            
            self.em_result_text.insert(1.0, result)
            self.log_info(f"🚨 Emergency route: {start} → {end} | Response: {travel_time:.1f} min", 'warning')
            self.status_var.set(f"🚨 Emergency: {start} → {end} | Response: {travel_time:.1f} min")
        else:
            result = f"❌ No emergency route found!\n\n"
            result += f"Could not find path from:\n"
            result += f"  {self.graph.nodes[start].name} ({start})\n"
            result += f"to:\n"
            result += f"  {self.graph.nodes[end].name} ({end})\n\n"
            result += f"Check network connectivity between these locations."
            
            self.em_result_text.insert(1.0, result)
            self.log_info(f"Emergency route failed: {start} → {end}", 'error')
        
        self.draw_network()
    
    def show_all_roads(self):
        """Show all roads."""
        self.selected_path = []
        self.emergency_path = []
        self.mst_edges = []
        self.path_result_text.delete(1.0, tk.END)
        self.path_result_text.insert(1.0, "🗺️ Showing all roads in network")
        self.log_info("Displaying all roads", 'info')
        self.status_var.set(f"All roads | Nodes: {len(self.graph.nodes)} | Roads: {len(self.graph.edges)}")
        self.draw_network()
    
    def clear_paths(self):
        """Clear all highlights."""
        self.selected_path = []
        self.emergency_path = []
        self.mst_edges = []
        self.path_result_text.delete(1.0, tk.END)
        self.path_result_text.insert(1.0, "Paths cleared")
        self.log_info("Paths cleared", 'info')
        self.draw_network()
    
    def optimize_bus_schedule(self):
        """Optimize bus schedule using DP."""
        route_id = self.bus_route_var.get()
        buses = self.bus_count_var.get()
        
        result = dynamic_programming_bus_scheduling(self.graph, route_id, buses)
        
        self.transit_result_text.delete(1.0, tk.END)
        
        if result:
            text = f"🚌 Route {route_id} Optimization\n\n"
            text += f"📍 Stops:\n"
            for stop_id in result['stops']:
                node = self.graph.nodes.get(stop_id)
                pop = result['population_per_stop'].get(stop_id, 0)
                if node:
                    text += f"   • {node.name} ({stop_id}): {pop:,} pop.\n"
            
            text += f"\n📊 Results:\n"
            text += f"   Available Buses: {buses}\n"
            text += f"   Max Coverage: {result['max_coverage']:,}\n"
            text += f"   Total Population: {result['total_population']:,}\n"
            if result['total_population'] > 0:
                text += f"   Coverage Rate: {result['max_coverage']/result['total_population']*100:.1f}%\n"
            
            self.transit_result_text.insert(1.0, text)
            self.log_info(f"Bus {route_id}: Coverage {result['max_coverage']:,} with {buses} buses", 'success')
    
    def optimize_maintenance(self):
        """Optimize maintenance using DP."""
        budget = self.budget_var.get()
        result = dp_road_maintenance_allocation(self.graph, budget)
        
        self.maint_result_text.delete(1.0, tk.END)
        
        text = f"🔧 Maintenance Plan\n\n"
        text += f"💰 Budget: {result['budget']:.0f} M EGP\n"
        text += f"💵 Used: {result['total_cost']:.0f} M EGP\n"
        text += f"📈 Total Benefit: {result['total_benefit']}\n"
        text += f"🛣️ Roads Repaired: {result['num_roads_repaired']}\n\n"
        
        if result['roads_to_repair']:
            text += f"🔨 Repair Priority List:\n"
            for i, road in enumerate(result['roads_to_repair'][:8]):
                text += f"   {i+1}. {road['road']}: Cost={road['cost']}M, Benefit={road['benefit']}, Cond={road['condition']}/10\n"
        
        self.maint_result_text.insert(1.0, text)
        self.log_info(f"Maintenance: {result['num_roads_repaired']} roads for {result['total_cost']}M EGP", 'success')
    
    def optimize_intersection(self):
        """Optimize traffic signals."""
        int_id = self.intersection_var.get()
        result = greedy_traffic_signal_optimization(self.graph, int_id)
        
        self.signal_result_text.delete(1.0, tk.END)
        
        if result:
            text = f"🚦 Signal Plan: {result['intersection_name']} ({int_id})\n\n"
            text += f"⏱️ Total Cycle: {result['total_cycle_time']}s\n\n"
            
            for i, plan in enumerate(result['signal_plan']):
                p = '🔴' if plan['priority'] == 'HIGH' else '🟡' if plan['priority'] == 'MEDIUM' else '🟢'
                text += f"{p} {plan['direction']}\n"
                text += f"   Green: {plan['green_time_seconds']}s | Priority: {plan['priority']}\n\n"
            
            self.signal_result_text.insert(1.0, text)
            self.log_info(f"Signal optimization for {result['intersection_name']}", 'info')
    
    def log_info(self, text, tag='info'):
        """Add colored log entry."""
        timestamp = time.strftime("%H:%M:%S")
        self.info_text.insert(tk.END, f"[{timestamp}] ", 'info')
        self.info_text.insert(tk.END, f"{text}\n", tag)
        self.info_text.see(tk.END)
    
    def on_canvas_click(self, event):
        """Handle canvas clicks for node selection."""
        min_dist = float('inf')
        closest_node = None
        
        for node_id in self.graph.nodes:
            x, y = self.get_canvas_pos(node_id)
            dist = math.sqrt((event.x - x)**2 + (event.y - y)**2)
            if dist < min_dist and dist < 35:
                min_dist = dist
                closest_node = node_id
        
        if closest_node:
            node = self.graph.nodes[closest_node]
            self.log_info(f"Clicked: {closest_node} ({node.name})", 'info')
            
            if not self.path_start_var.get():
                self.path_start_var.set(closest_node)
            elif not self.path_end_var.get() and closest_node != self.path_start_var.get():
                self.path_end_var.set(closest_node)
    
    def draw_network(self):
        """Draw the network with manual layout for clarity."""
        self.canvas.delete("all")
        
        canvas_w = max(self.canvas.winfo_width(), 1000)
        canvas_h = max(self.canvas.winfo_height(), 700)
        
        # Background
        self.canvas.create_rectangle(0, 0, canvas_w, canvas_h, fill='#0a0a1a')
        
        # Title
        self.canvas.create_text(canvas_w//2, 18, text="Greater Cairo Transportation Network", 
                               fill='white', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(canvas_w//2, 35, text="Smart City Optimization System", 
                               fill='#e94560', font=('Helvetica', 10))
        
        # Draw grid
        for i in range(0, canvas_w, 60):
            self.canvas.create_line(i, 55, i, canvas_h, fill='#111133', width=1)
        for i in range(55, canvas_h, 60):
            self.canvas.create_line(0, i, canvas_w, i, fill='#111133', width=1)
        
        # Determine highlighted edges
        highlight_edges = set()
        if self.selected_path:
            for i in range(len(self.selected_path) - 1):
                highlight_edges.add(tuple(sorted([self.selected_path[i], self.selected_path[i+1]])))
        elif self.emergency_path:
            for i in range(len(self.emergency_path) - 1):
                highlight_edges.add(tuple(sorted([self.emergency_path[i], self.emergency_path[i+1]])))
        elif self.mst_edges:
            for edge in self.mst_edges:
                highlight_edges.add(tuple(sorted([edge.from_id, edge.to_id])))
        
        # Draw edges
        drawn_edges = set()
        for edge_key, edge in self.graph.edges.items():
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)
            
            from_pos = self.get_canvas_pos(edge.from_id)
            to_pos = self.get_canvas_pos(edge.to_id)
            
            is_highlighted = edge_key in highlight_edges
            
            if is_highlighted and self.selected_path:
                color = '#4CAF50'
                width = 5
                dash = None
            elif is_highlighted and self.emergency_path:
                color = '#FF1744'
                width = 5
                dash = (10, 5)
            elif is_highlighted and self.mst_edges:
                color = '#FF9800'
                width = 4
                dash = None
            elif edge.is_new:
                color = '#444466'
                width = 1
                dash = (5, 5)
            else:
                color = '#2a2a4a'
                width = 2
                dash = None
            
            self.canvas.create_line(from_pos[0], from_pos[1], to_pos[0], to_pos[1],
                                   fill=color, width=width, dash=dash, tags="edge")
            
            # Edge labels for highlighted or main roads
            if is_highlighted or edge.condition >= 8:
                mid_x = (from_pos[0] + to_pos[0]) / 2
                mid_y = (from_pos[1] + to_pos[1]) / 2
                
                label = f"{edge.distance:.1f}km"
                if edge.is_new and is_highlighted:
                    label += f" [{edge.construction_cost}M]"
                
                self.canvas.create_text(mid_x, mid_y, text=label,
                                       fill='#aaa' if not is_highlighted else 'white',
                                       font=('Arial', 7, 'bold' if is_highlighted else 'normal'))
        
        # Draw nodes
        for node_id, node in self.graph.nodes.items():
            x, y = self.get_canvas_pos(node_id)
            color = self.type_colors.get(node.type, '#607D8B')
            
            # Node size
            base_radius = 12
            if node.type in ['Medical', 'Government', 'Airport']:
                base_radius = 16
            elif node.population > 400000:
                base_radius = 15
            elif node.population > 200000:
                base_radius = 13
            
            is_in_path = node_id in (self.selected_path or self.emergency_path or [])
            is_start = ((self.selected_path and node_id == self.selected_path[0]) or 
                       (self.emergency_path and node_id == self.emergency_path[0]))
            is_end = ((self.selected_path and node_id == self.selected_path[-1]) or 
                     (self.emergency_path and node_id == self.emergency_path[-1]))
            
            # Glow for path nodes
            if is_in_path:
                self.canvas.create_oval(x - base_radius - 5, y - base_radius - 5,
                                       x + base_radius + 5, y + base_radius + 5,
                                       fill='', outline='white', width=2)
            
            # Main node
            outline_color = 'white' if is_in_path else '#333'
            outline_width = 3 if is_in_path else 1
            
            self.canvas.create_oval(x - base_radius, y - base_radius,
                                   x + base_radius, y + base_radius,
                                   fill=color, outline=outline_color, width=outline_width)
            
            # Start/End indicators
            if is_start:
                self.canvas.create_text(x, y - base_radius - 18, text="▼ START",
                                       fill='#4CAF50', font=('Arial', 9, 'bold'))
            if is_end:
                self.canvas.create_text(x, y + base_radius + 18, text="▲ END",
                                       fill='#f44336', font=('Arial', 9, 'bold'))
            
            # Node name
            name = node.name[:18] + ".." if len(node.name) > 18 else node.name
            self.canvas.create_text(x, y - base_radius - 20, text=name, fill='white',
                                   font=('Arial', 8, 'bold'))
            
            # Node ID
            self.canvas.create_text(x, y + base_radius + 14, text=f"({node_id})",
                                   fill='#888', font=('Arial', 7))
            
            # Population for large nodes
            if node.population > 200000:
                pop_text = f"{node.population//1000}K"
                self.canvas.create_text(x + base_radius + 20, y, text=pop_text,
                                       fill='#FFD700', font=('Arial', 7))
        
        # Draw legend
        self.draw_legend(canvas_w, canvas_h)
    
    def draw_legend(self, canvas_w, canvas_h):
        """Draw legend in corner."""
        legend_x = 15
        legend_y = canvas_h - 230
        
        # Background
        self.canvas.create_rectangle(legend_x - 5, legend_y - 25, legend_x + 155, legend_y + 225,
                                    fill='#16213e', outline='#333')
        
        self.canvas.create_text(legend_x + 70, legend_y - 12, text="📋 Legend",
                               fill='white', font=('Arial', 10, 'bold'))
        
        y_offset = 10
        for type_name, color in sorted(self.type_colors.items()):
            if y_offset > 190:
                break
            self.canvas.create_oval(legend_x + 5, legend_y + y_offset,
                                   legend_x + 18, legend_y + y_offset + 12,
                                   fill=color, outline='white', width=1)
            self.canvas.create_text(legend_x + 25, legend_y + y_offset + 6,
                                   text=type_name, fill='white',
                                   font=('Arial', 7), anchor=tk.W)
            y_offset += 20
        
        # Line styles
        y_offset += 10
        lines = [
            ('#4CAF50', 3, None, 'Shortest Path'),
            ('#FF1744', 3, (6, 4), 'Emergency Route'),
            ('#FF9800', 3, None, 'MST Network'),
            ('#444466', 1, (4, 4), 'Proposed Road'),
        ]
        
        for color, width, dash, label in lines:
            self.canvas.create_line(legend_x + 2, legend_y + y_offset + 6,
                                   legend_x + 18, legend_y + y_offset + 6,
                                   fill=color, width=width, dash=dash)
            self.canvas.create_text(legend_x + 25, legend_y + y_offset + 6,
                                   text=label, fill='white',
                                   font=('Arial', 7), anchor=tk.W)
            y_offset += 20
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = TransportationGUI()
    app.run()