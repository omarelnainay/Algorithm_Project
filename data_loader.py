from models import Node, Edge, TransportationGraph
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
        # Medical facility connections (F9, F10 were isolated - no roads)
        ("F10", "1", 1.2, 2000, 8),   # Maadi Military Hospital ↔ Maadi
        ("F10", "12", 12.0, 2500, 6), # Maadi Military Hospital ↔ Helwan
        ("F9", "3", 1.5, 2000, 8),    # Qasr El Aini Hospital ↔ Downtown Cairo
        ("F9", "10", 2.0, 1800, 7),   # Qasr El Aini Hospital ↔ Dokki
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