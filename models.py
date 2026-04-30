from collections import defaultdict
from typing import Dict, List, Tuple, Optional
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