import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import time
from typing import Dict, Tuple, List 
from data_loader import load_data
from algorithms import dijkstra_shortest_path, kruskal_mst, a_star_emergency_routing, dynamic_programming_bus_scheduling, dp_road_maintenance_allocation, greedy_traffic_signal_optimization
from ML_Model import predict_traffic

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
        self.setup_prediction_tab(notebook)
        
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
    
    def setup_prediction_tab(self, notebook):
        """Setup ML prediction tab."""
        frame = tk.Frame(notebook, bg='#16213e')
        notebook.add(frame, text="🤖 ML Prediction")
        
        tk.Label(frame, text="Traffic Congestion Prediction", font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#9C27B0').pack(pady=5)
        
        tk.Label(frame, text="Predict traffic congestion using\nmachine learning model", 
                bg='#16213e', fg='#ccc', justify=tk.CENTER).pack(pady=2)
        
        # Input fields
        input_frame = tk.Frame(frame, bg='#16213e')
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Road ID
        tk.Label(input_frame, text="Road ID:", bg='#16213e', fg='white').grid(row=0, column=0, sticky='w', pady=2)
        self.pred_road_var = tk.StringVar(value="Maadi-Downtown Road")
        road_combo = ttk.Combobox(input_frame, textvariable=self.pred_road_var, width=20)
        road_combo['values'] = [
            "Maadi-Downtown Road",
            "Maadi-Giza Road", 
            "Nasr City-Downtown Road",
            "Nasr City-Heliopolis Road",
            "Downtown-Heliopolis Road",
            "Downtown-Zamalek Road",
            "Downtown-Mohandessin Road",
            "Downtown-Dokki Road"
        ]
        road_combo.grid(row=0, column=1, pady=2, padx=(5,0))
        
        # Time of Day
        tk.Label(input_frame, text="Time of Day:", bg='#16213e', fg='white').grid(row=1, column=0, sticky='w', pady=2)
        self.pred_time_var = tk.StringVar(value="Morning")
        time_combo = ttk.Combobox(input_frame, textvariable=self.pred_time_var, width=15)
        time_combo['values'] = ["Morning", "Afternoon", "Evening", "Night"]
        time_combo.grid(row=1, column=1, pady=2, padx=(5,0))
        
        # Capacity
        tk.Label(input_frame, text="Capacity:", bg='#16213e', fg='white').grid(row=2, column=0, sticky='w', pady=2)
        self.pred_capacity_var = tk.IntVar(value=3000)
        capacity_entry = tk.Entry(input_frame, textvariable=self.pred_capacity_var, width=17, bg='#0f3460', fg='white')
        capacity_entry.grid(row=2, column=1, pady=2, padx=(5,0))
        
        # Volume
        tk.Label(input_frame, text="Volume:", bg='#16213e', fg='white').grid(row=3, column=0, sticky='w', pady=2)
        self.pred_volume_var = tk.IntVar(value=1500)
        volume_entry = tk.Entry(input_frame, textvariable=self.pred_volume_var, width=17, bg='#0f3460', fg='white')
        volume_entry.grid(row=3, column=1, pady=2, padx=(5,0))
        
        # Buttons
        btn_frame = tk.Frame(frame, bg='#16213e')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔮 Predict Congestion", command=self.predict_congestion,
                 bg='#9C27B0', fg='white', font=('Helvetica', 10, 'bold'),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="🔄 Reset", command=self.reset_prediction_inputs,
                 bg='#FF9800', fg='white', font=('Helvetica', 10),
                 padx=15, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Results
        self.pred_result_text = tk.Text(frame, height=8, bg='#1a1a2e', fg='#9C27B0',
                                        font=('Consolas', 9), wrap=tk.WORD)
        self.pred_result_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Info
        info_text = """ℹ️ Model Info:
• Random Forest Regressor
• Trained on historical traffic data
• Predicts congestion level (0-5 scale)
• Lower values = better traffic flow"""
        tk.Label(frame, text=info_text, bg='#16213e', fg='#aaa', 
                justify=tk.LEFT, font=('Helvetica', 8)).pack(pady=5, anchor='w', padx=10)
    
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
    
    def predict_congestion(self):
        """Predict traffic congestion using ML model."""
        road_id = self.pred_road_var.get()
        time_of_day = self.pred_time_var.get()
        capacity = self.pred_capacity_var.get()
        volume = self.pred_volume_var.get()
        
        self.pred_result_text.delete(1.0, tk.END)
        
        # Validate inputs
        if not road_id or not time_of_day:
            self.pred_result_text.insert(1.0, "⚠️ Please fill in all fields!")
            return
        
        try:
            capacity = int(capacity)
            volume = int(volume)
        except ValueError:
            self.pred_result_text.insert(1.0, "⚠️ Capacity and Volume must be numbers!")
            return
        
        # Make prediction
        try:
            prediction = predict_traffic(road_id, time_of_day, capacity, volume)
            
            if prediction is not None:
                # Interpret prediction level
                if prediction < 1.0:
                    level = "Excellent Flow"
                    color = "🟢"
                    desc = "Very light traffic, smooth flow"
                elif prediction < 2.0:
                    level = "Good Flow"
                    color = "🟡"
                    desc = "Light traffic, minor delays"
                elif prediction < 3.0:
                    level = "Moderate Congestion"
                    color = "🟠"
                    desc = "Moderate traffic, some delays"
                elif prediction < 4.0:
                    level = "Heavy Congestion"
                    color = "🔴"
                    desc = "Heavy traffic, significant delays"
                else:
                    level = "Severe Congestion"
                    color = "🚫"
                    desc = "Very heavy traffic, major delays"
                
                result = f"🔮 PREDICTION RESULT\n\n"
                result += f"📍 Road: {road_id}\n"
                result += f"🕐 Time: {time_of_day}\n"
                result += f"🚗 Capacity: {capacity:,}\n"
                result += f"📊 Volume: {volume:,}\n\n"
                result += f"🎯 Congestion Level: {prediction:.3f}\n"
                result += f"📈 Traffic Status: {color} {level}\n"
                result += f"ℹ️ Description: {desc}\n\n"
                result += f"💡 Recommendation:\n"
                
                if prediction < 2.0:
                    result += "   ✅ Traffic flow is good - no action needed"
                elif prediction < 3.0:
                    result += "   ⚠️ Consider traffic management measures"
                else:
                    result += "   🚨 High congestion - implement traffic controls"
                
                self.pred_result_text.insert(1.0, result)
                self.log_info(f"ML Prediction: {road_id} {time_of_day} → {prediction:.3f} ({level})", 'success')
                self.status_var.set(f"Prediction: {road_id} | Congestion: {prediction:.3f} | Status: {level}")
            else:
                self.pred_result_text.insert(1.0, "❌ Prediction failed!\n\nCheck if model files exist and inputs are valid.")
                self.log_info("ML prediction failed", 'error')
                
        except Exception as e:
            self.pred_result_text.insert(1.0, f"❌ Error during prediction:\n\n{str(e)}")
            self.log_info(f"ML prediction error: {str(e)}", 'error')
    
    def reset_prediction_inputs(self):
        """Reset prediction input fields to defaults."""
        self.pred_road_var.set("Maadi-Downtown Road")
        self.pred_time_var.set("Morning")
        self.pred_capacity_var.set(3000)
        self.pred_volume_var.set(1500)
        self.pred_result_text.delete(1.0, tk.END)
        self.pred_result_text.insert(1.0, "Inputs reset to defaults")
        self.log_info("Prediction inputs reset", 'info')
    
    def run(self):
        """Start the application."""
        self.root.mainloop()