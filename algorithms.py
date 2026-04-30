import heapq
import math
from typing import Dict, List, Tuple
from models import TransportationGraph, Edge
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
                total_cost += edge.distance * 10
            
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
        return [], float('inf'), 0
    if end not in graph.nodes:
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
