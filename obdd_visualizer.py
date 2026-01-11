#!/usr/bin/env python3
"""
OBDD Visualizer - A Tkinter application for creating and visualizing Ordered Binary Decision Diagrams.

Features:
- Visual canvas for creating OBDDs
- Draggable nodes (decision nodes as circles, terminal nodes 0/1 as squares)
- Edge connections with solid lines (1-edge) and dashed lines (0-edge) with arrows
- Root node designation
- Keyboard shortcuts for operations
"""

import json
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import math


class Node:
    """Represents a node in the OBDD."""
    
    def __init__(self, node_id, x, y, label, is_terminal=False):
        self.id = node_id
        self.x = x
        self.y = y
        self.label = label
        self.is_terminal = is_terminal
        self.edges_out = []  # List of (target_node_id, edge_type) where edge_type is 0 or 1
        self.is_root = False
        self.canvas_items = []  # Canvas item IDs for this node
        
    def add_edge(self, target_node_id, edge_type):
        """Add an edge to another node."""
        # Remove existing edge of same type if present
        self.edges_out = [(tid, et) for tid, et in self.edges_out if et != edge_type]
        self.edges_out.append((target_node_id, edge_type))
        
    def clear_edges(self):
        """Remove all outgoing edges."""
        self.edges_out = []

    def get_edge_target(self, edge_type):
        """Get the target node ID for a given edge type (0 or 1)."""
        for target_id, etype in self.edges_out:
            if etype == edge_type:
                return target_id
        return None


class OBDDSerializer:
    """Serialize and deserialize OBDD data to/from JSON."""

    @staticmethod
    def to_dict(nodes, root_id):
        """Convert nodes and root info to a JSON-serializable dict."""
        payload = {"nodes": [], "root": root_id}
        for node in nodes.values():
            entry = {
                "id": node.id,
                "label": node.label,
                "x": node.x,
                "y": node.y,
                "is_terminal": node.is_terminal,
            }
            if not node.is_terminal:
                entry["low"] = node.get_edge_target(0)
                entry["high"] = node.get_edge_target(1)
            payload["nodes"].append(entry)
        return payload

    @staticmethod
    def from_dict(data):
        """Build nodes and root ID from a dict representation."""
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object.")
        nodes_data = data.get("nodes")
        if not isinstance(nodes_data, list):
            raise ValueError("JSON must include a 'nodes' list.")

        nodes = {}
        for entry in nodes_data:
            if not isinstance(entry, dict):
                raise ValueError("Each node entry must be an object.")
            for key in ("id", "label", "x", "y", "is_terminal"):
                if key not in entry:
                    raise ValueError(f"Node is missing '{key}'.")
            node_id = entry["id"]
            if node_id in nodes:
                raise ValueError(f"Duplicate node id {node_id}.")
            node = Node(
                node_id,
                entry["x"],
                entry["y"],
                entry["label"],
                is_terminal=bool(entry["is_terminal"]),
            )
            nodes[node.id] = node

        terminal_labels = {node.label for node in nodes.values() if node.is_terminal}
        if "0" not in terminal_labels or "1" not in terminal_labels:
            raise ValueError("Import requires terminal nodes labeled '0' and '1'.")

        for entry in nodes_data:
            node = nodes[entry["id"]]
            if node.is_terminal:
                continue
            low = entry.get("low")
            high = entry.get("high")
            if low is not None:
                if low not in nodes:
                    raise ValueError(f"Low target {low} does not exist.")
                node.add_edge(low, 0)
            if high is not None:
                if high not in nodes:
                    raise ValueError(f"High target {high} does not exist.")
                node.add_edge(high, 1)

        root_id = data.get("root")
        if root_id is not None and root_id not in nodes:
            raise ValueError("Root node id does not exist.")
        return nodes, root_id

    @staticmethod
    def save_json(path, data):
        """Save JSON data to disk."""
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    @staticmethod
    def load_json(path):
        """Load JSON data from disk."""
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)


class OBDDVisualizer:
    """Main application class for OBDD visualization."""
    
    # Constants
    DECISION_NODE_RADIUS = 25
    TERMINAL_NODE_SIZE = 40
    DEFAULT_CANVAS_WIDTH = 800
    DEFAULT_CANVAS_HEIGHT = 600
    CONTROL_PANEL_WIDTH = 220
    ROOT_INDICATOR_OFFSET = 40
    
    def __init__(self, root):
        self.root = root
        self.root.title("OBDD Visualizer")
        
        # Data structures
        self.nodes = {}
        self.next_node_id = 0
        self.next_var_index = 0  # For generating p, q, r, s, ...
        
        # Interaction state
        self.selected_node = None
        self.selected_nodes = set()
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.connecting_mode = False
        self.connecting_edge_type = None  # 0 or 1
        self.connecting_from_node = None
        self.selecting_box = False
        self.selection_start_x = 0
        self.selection_start_y = 0
        self.selection_rect = None
        self.selection_additive = False
        self.canvas_width = self.DEFAULT_CANVAS_WIDTH
        self.canvas_height = self.DEFAULT_CANVAS_HEIGHT
        self.expand_dx = self.DEFAULT_CANVAS_WIDTH // 2
        self.expand_dy = self.DEFAULT_CANVAS_HEIGHT // 2
        
        # Setup UI
        self.setup_ui()
        
        # Create initial terminal nodes
        self.create_initial_nodes()
        
        # Setup keyboard bindings
        self.setup_keybindings()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas container (with expand buttons)
        board_frame = tk.Frame(self.main_frame)
        board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_btn = tk.Button(
            board_frame,
            text=f"Expand Up (+{self.expand_dy})",
            command=lambda: self.expand_canvas(0, self.expand_dy),
            wraplength=300,
            justify=tk.CENTER
        )
        top_btn.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        left_btn = tk.Button(
            board_frame,
            text=f"Expand Left (+{self.expand_dx})",
            command=lambda: self.expand_canvas(self.expand_dx, 0),
            wraplength=100,
            justify=tk.CENTER
        )
        left_btn.grid(row=1, column=0, sticky="ns", padx=2, pady=2)

        # Canvas
        self.canvas = tk.Canvas(
            board_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            cursor='arrow'
        )
        self.canvas.grid(row=1, column=1, padx=2, pady=2)

        right_btn = tk.Button(
            board_frame,
            text=f"Expand Right (+{self.expand_dx})",
            command=lambda: self.expand_canvas(self.expand_dx, 0),
            wraplength=100,
            justify=tk.CENTER
        )
        right_btn.grid(row=1, column=2, sticky="ns", padx=2, pady=2)

        bottom_btn = tk.Button(
            board_frame,
            text=f"Expand Down (+{self.expand_dy})",
            command=lambda: self.expand_canvas(0, self.expand_dy),
            wraplength=300,
            justify=tk.CENTER
        )
        bottom_btn.grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        board_frame.grid_columnconfigure(1, weight=1)
        board_frame.grid_rowconfigure(1, weight=1)

        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)

        # Control panel (scrollable)
        control_container = tk.Frame(self.main_frame, width=self.CONTROL_PANEL_WIDTH, bg='lightgray')
        control_container.pack(side=tk.RIGHT, fill=tk.Y)
        control_container.pack_propagate(False)

        control_canvas = tk.Canvas(control_container, bg='lightgray', highlightthickness=0)
        control_scrollbar = tk.Scrollbar(control_container, orient=tk.VERTICAL, command=control_canvas.yview)
        control_canvas.configure(yscrollcommand=control_scrollbar.set)
        control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(control_canvas, bg='lightgray')
        control_canvas.create_window((0, 0), window=control_frame, anchor='nw')

        def update_control_scrollregion(event):
            control_canvas.configure(scrollregion=control_canvas.bbox("all"))

        control_frame.bind("<Configure>", update_control_scrollregion)
        
        # Title
        title = tk.Label(control_frame, text="OBDD Visualizer", font=('Arial', 12, 'bold'), bg='lightgray')
        title.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            control_frame,
            text="Keyboard Shortcuts:",
            font=('Arial', 10, 'bold'),
            bg='lightgray',
            justify=tk.LEFT
        )
        instructions.pack(pady=5)
        
        shortcuts_text = """
N: Add decision node
R: Set root node
1: Connect 1-edge
0: Connect 0-edge
D: Delete outgoing edges
DEL/X: Delete node
E: Export JSON
I: Import JSON
ESC: Cancel operation
        """
        
        shortcuts = tk.Label(
            control_frame,
            text=shortcuts_text.strip(),
            font=('Arial', 9),
            bg='lightgray',
            justify=tk.LEFT
        )
        shortcuts.pack(pady=5)
        
        # Buttons
        tk.Button(
            control_frame,
            text="Add Node (N)",
            command=self.add_decision_node,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Set Root (R)",
            command=self.set_root_node,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Connect 1-edge (1)",
            command=lambda: self.start_edge_connection(1),
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Connect 0-edge (0)",
            command=lambda: self.start_edge_connection(0),
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Delete Edges (D)",
            command=self.delete_outgoing_edges,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Delete Node (Del/X)",
            command=self.delete_node,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Clear All",
            command=self.clear_all,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=15, padx=10, fill=tk.X)

        tk.Button(
            control_frame,
            text="Export JSON (E)",
            command=self.export_json,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)

        tk.Button(
            control_frame,
            text="Import JSON (I)",
            command=self.import_json,
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=5, padx=10, fill=tk.X)

        self.mode_label = tk.Label(
            control_frame,
            text="Mode: Ready",
            font=('Arial', 9),
            bg='lightgray',
            fg='black',
            wraplength=180
        )
        self.mode_label.pack(side=tk.BOTTOM, pady=2)
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Ready",
            font=('Arial', 9),
            bg='lightgray',
            fg='blue',
            wraplength=180
        )
        self.status_label.pack(side=tk.BOTTOM, pady=10)
        self.update_mode("Ready")
        self.fit_window_to_content()
        self.root.resizable(False, False)
        
    def setup_keybindings(self):
        """Setup keyboard shortcuts."""
        self.root.bind('n', lambda e: self.add_decision_node())
        self.root.bind('N', lambda e: self.add_decision_node())
        self.root.bind('r', lambda e: self.set_root_node())
        self.root.bind('R', lambda e: self.set_root_node())
        self.root.bind('1', lambda e: self.start_edge_connection(1))
        self.root.bind('0', lambda e: self.start_edge_connection(0))
        self.root.bind('d', lambda e: self.delete_outgoing_edges())
        self.root.bind('D', lambda e: self.delete_outgoing_edges())
        self.root.bind('<Delete>', lambda e: self.delete_node())
        self.root.bind('x', lambda e: self.delete_node())
        self.root.bind('X', lambda e: self.delete_node())
        self.root.bind('<Escape>', lambda e: self.cancel_operation())
        self.root.bind('e', lambda e: self.export_json())
        self.root.bind('E', lambda e: self.export_json())
        self.root.bind('i', lambda e: self.import_json())
        self.root.bind('I', lambda e: self.import_json())
        
    def create_initial_nodes(self):
        """Create the initial terminal nodes 0 and 1."""
        # Terminal node 0 on the left
        node0 = Node(self.get_next_node_id(), int(self.canvas_width * 0.2), int(self.canvas_height * 0.83), '0', is_terminal=True)
        self.nodes[node0.id] = node0
        self.draw_node(node0)
        
        # Terminal node 1 on the right
        node1 = Node(self.get_next_node_id(), int(self.canvas_width * 0.8), int(self.canvas_height * 0.83), '1', is_terminal=True)
        self.nodes[node1.id] = node1
        self.draw_node(node1)
        
    def get_next_node_id(self):
        """Get the next available node ID."""
        node_id = self.next_node_id
        self.next_node_id += 1
        return node_id
        
    def get_next_variable_label(self, consume=True):
        """Get the next variable label (p, q, r, s, ...)."""
        labels = ['p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        if self.next_var_index < len(labels):
            label = labels[self.next_var_index]
        else:
            # If we run out of single letters, use p1, p2, ...
            label = f'p{self.next_var_index - len(labels) + 1}'
        if consume:
            self.next_var_index += 1
        return label
        
    def add_decision_node(self):
        """Add a new decision node to the canvas."""
        # Place node in center or near selected node
        if self.selected_node and self.selected_node in self.nodes:
            x = self.nodes[self.selected_node].x
            y = self.nodes[self.selected_node].y - 80
        else:
            x = self.canvas_width // 2
            y = self.canvas_height // 3
            
        suggested_label = self.get_next_variable_label(consume=False)
        label_input = simpledialog.askstring(
            "New Decision Node",
            f"Enter node label (default: {suggested_label})",
            initialvalue=suggested_label
        )
        if label_input is None:
            self.update_status("Add node cancelled")
            return
        label = label_input.strip() or suggested_label
        self.next_var_index += 1
        node = Node(self.get_next_node_id(), x, y, label, is_terminal=False)
        self.nodes[node.id] = node
        self.draw_node(node)
        
        self.update_status(f"Added decision node '{label}'")
        self.update_mode("Ready")
        
    def draw_node(self, node):
        """Draw a node on the canvas."""
        # Clear existing canvas items for this node
        for item in node.canvas_items:
            self.canvas.delete(item)
        node.canvas_items = []
        
        if node.is_terminal:
            # Draw square for terminal nodes
            x1 = node.x - self.TERMINAL_NODE_SIZE // 2
            y1 = node.y - self.TERMINAL_NODE_SIZE // 2
            x2 = node.x + self.TERMINAL_NODE_SIZE // 2
            y2 = node.y + self.TERMINAL_NODE_SIZE // 2
            outline = 'red' if node.id in self.selected_nodes else 'black'
            
            square = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill='lightblue',
                outline=outline,
                width=3 if node.id == self.selected_node else 2,
                tags=f'node_{node.id}'
            )
            node.canvas_items.append(square)
        else:
            # Draw circle for decision nodes
            x1 = node.x - self.DECISION_NODE_RADIUS
            y1 = node.y - self.DECISION_NODE_RADIUS
            x2 = node.x + self.DECISION_NODE_RADIUS
            y2 = node.y + self.DECISION_NODE_RADIUS
            outline = 'red' if node.id in self.selected_nodes else 'black'
            
            circle = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill='lightyellow',
                outline=outline,
                width=3 if node.id == self.selected_node else 2,
                tags=f'node_{node.id}'
            )
            node.canvas_items.append(circle)
            
        # Draw label
        text = self.canvas.create_text(
            node.x, node.y,
            text=node.label,
            font=('Arial', 14, 'bold'),
            tags=f'node_{node.id}'
        )
        node.canvas_items.append(text)
        
        # Draw root indicator if this is the root
        if node.is_root:
            # Calculate offset based on node type
            if node.is_terminal:
                node_offset = self.TERMINAL_NODE_SIZE // 2
            else:
                node_offset = self.DECISION_NODE_RADIUS
                
            arrow = self.canvas.create_line(
                node.x, node.y - node_offset - self.ROOT_INDICATOR_OFFSET,
                node.x, node.y - node_offset - 5,
                arrow=tk.LAST,
                fill='red',
                width=3,
                tags=f'node_{node.id}'
            )
            node.canvas_items.append(arrow)
            
            root_text = self.canvas.create_text(
                node.x, node.y - node_offset - self.ROOT_INDICATOR_OFFSET - 10,
                text='ROOT',
                font=('Arial', 10, 'bold'),
                fill='red',
                tags=f'node_{node.id}'
            )
            node.canvas_items.append(root_text)
            
        # Make sure node items are on top
        for item in node.canvas_items:
            self.canvas.tag_raise(item)
            
    def draw_all_edges(self):
        """Redraw all edges in the OBDD."""
        # Delete all existing edges
        self.canvas.delete('edge')
        
        # Draw each edge
        for node_id, node in self.nodes.items():
            for target_id, edge_type in node.edges_out:
                if target_id in self.nodes:
                    self.draw_edge(node, self.nodes[target_id], edge_type)
                    
    def draw_edge(self, from_node, to_node, edge_type):
        """Draw an edge between two nodes."""
        # Calculate start and end points on the edge of nodes
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:
            return
            
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Calculate start point (on edge of from_node)
        if from_node.is_terminal:
            start_offset = self.TERMINAL_NODE_SIZE // 2
        else:
            start_offset = self.DECISION_NODE_RADIUS
            
        start_x = from_node.x + dx * start_offset
        start_y = from_node.y + dy * start_offset
        
        # Calculate end point (on edge of to_node)
        if to_node.is_terminal:
            end_offset = self.TERMINAL_NODE_SIZE // 2
        else:
            end_offset = self.DECISION_NODE_RADIUS
            
        end_x = to_node.x - dx * end_offset
        end_y = to_node.y - dy * end_offset
        
        # Draw line (solid for 1-edge, dashed for 0-edge)
        if edge_type == 1:
            line = self.canvas.create_line(
                start_x, start_y, end_x, end_y,
                arrow=tk.LAST,
                fill='black',
                width=2,
                tags='edge'
            )
        else:  # edge_type == 0
            line = self.canvas.create_line(
                start_x, start_y, end_x, end_y,
                arrow=tk.LAST,
                fill='gray',
                width=2,
                dash=(5, 5),
                tags='edge'
            )
            
        # Make sure edges are below nodes
        self.canvas.tag_lower('edge')
        
    def on_canvas_click(self, event):
        """Handle canvas click events."""
        # Find which node was clicked
        clicked_node = self.find_node_at(event.x, event.y)
        shift_held = bool(event.state & 0x0001)
        
        if self.connecting_mode:
            # In connection mode, connect from selected node to clicked node
            if clicked_node is not None:
                if self.connecting_from_node is not None and self.connecting_from_node in self.nodes:
                    from_node = self.nodes[self.connecting_from_node]
                    from_node.add_edge(clicked_node, self.connecting_edge_type)
                    self.draw_all_edges()
                    self.update_status(
                        f"Connected {from_node.label} to {self.nodes[clicked_node].label} "
                        f"with {self.connecting_edge_type}-edge"
                    )
                self.cancel_operation()
        else:
            # Normal click - select node and prepare for dragging
            if clicked_node is not None:
                if shift_held:
                    previous_selected = set(self.selected_nodes)
                    if clicked_node in self.selected_nodes:
                        self.selected_nodes.remove(clicked_node)
                        if self.selected_node == clicked_node:
                            self.selected_node = next(iter(self.selected_nodes), None)
                        self.update_status("Updated selection")
                    else:
                        self.selected_nodes.add(clicked_node)
                        self.selected_node = clicked_node
                        self.update_status(f"Selected node '{self.nodes[clicked_node].label}'")
                    self.refresh_selection(previous_selected)
                    self.update_mode("Ready")
                else:
                    previous_selected = set(self.selected_nodes)
                    if clicked_node in self.selected_nodes:
                        self.selected_node = clicked_node
                    else:
                        self.selected_node = clicked_node
                        self.selected_nodes = {clicked_node}
                    self.dragging = True
                    self.drag_start_x = event.x
                    self.drag_start_y = event.y
                    self.refresh_selection(previous_selected)
                    self.update_status(f"Selected node '{self.nodes[clicked_node].label}'")
            else:
                previous_selected = set(self.selected_nodes)
                if not shift_held:
                    self.selected_node = None
                    self.selected_nodes = set()
                    self.refresh_selection(previous_selected)
                self.start_selection_box(event.x, event.y, additive=shift_held)
                
    def on_canvas_drag(self, event):
        """Handle canvas drag events."""
        if self.selecting_box:
            self.update_selection_box(event.x, event.y)
            return
        if self.dragging and self.selected_node is not None:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            if self.selected_node in self.selected_nodes and len(self.selected_nodes) > 1:
                for node_id in self.selected_nodes:
                    node = self.nodes[node_id]
                    node.x += dx
                    node.y += dy
                    self.draw_node(node)
            else:
                node = self.nodes[self.selected_node]
                node.x += dx
                node.y += dy
                self.draw_node(node)
            
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Redraw edges
            self.draw_all_edges()
            
    def on_canvas_release(self, event):
        """Handle canvas button release events."""
        if self.selecting_box:
            self.finish_selection_box(event.x, event.y)
        self.dragging = False
        
    def find_node_at(self, x, y):
        """Find the node at the given canvas coordinates."""
        for node_id, node in self.nodes.items():
            if node.is_terminal:
                # Check if click is within square
                half_size = self.TERMINAL_NODE_SIZE // 2
                if (node.x - half_size <= x <= node.x + half_size and
                    node.y - half_size <= y <= node.y + half_size):
                    return node_id
            else:
                # Check if click is within circle
                dx = x - node.x
                dy = y - node.y
                if dx*dx + dy*dy <= self.DECISION_NODE_RADIUS * self.DECISION_NODE_RADIUS:
                    return node_id
        return None
        
    def set_root_node(self):
        """Set the selected node as the root."""
        if self.selected_node is None:
            messagebox.showwarning("No Selection", "Please select a node first.")
            return
            
        # Clear previous root
        for node in self.nodes.values():
            node.is_root = False
            
        # Set new root
        self.nodes[self.selected_node].is_root = True
        
        # Redraw all nodes to update root indicator
        for node in self.nodes.values():
            self.draw_node(node)
        self.draw_all_edges()
        
        self.update_status(f"Set '{self.nodes[self.selected_node].label}' as root node")
        self.update_mode("Ready")
        
    def start_edge_connection(self, edge_type):
        """Start the edge connection mode."""
        if self.selected_node is None:
            messagebox.showwarning("No Selection", "Please select a source node first.")
            return
            
        if self.nodes[self.selected_node].is_terminal:
            messagebox.showwarning("Invalid Operation", "Cannot connect from terminal nodes.")
            return
            
        self.connecting_mode = True
        self.connecting_edge_type = edge_type
        self.connecting_from_node = self.selected_node
        self.canvas.config(cursor='crosshair')
        
        self.update_status(
            f"Click on target node to connect {edge_type}-edge from "
            f"'{self.nodes[self.selected_node].label}' (ESC to cancel)"
        )
        self.update_mode(f"Connecting {edge_type}-edge from '{self.nodes[self.selected_node].label}'")
        
    def delete_outgoing_edges(self):
        """Delete all outgoing edges from the selected node."""
        if self.selected_node is None:
            messagebox.showwarning("No Selection", "Please select a node first.")
            return
            
        node = self.nodes[self.selected_node]
        if node.edges_out:
            node.clear_edges()
            self.draw_all_edges()
            self.update_status(f"Deleted outgoing edges from '{node.label}'")
        else:
            self.update_status(f"Node '{node.label}' has no outgoing edges")
        self.update_mode("Ready")

    def delete_node(self):
        """Delete the currently selected decision node."""
        if self.selected_node is None:
            messagebox.showwarning("No Selection", "Please select a node first.")
            return
            
        node_id = self.selected_node
        node = self.nodes.get(node_id)
        if node is None:
            self.update_status("Selected node not found")
            return
            
        if node.is_terminal:
            messagebox.showwarning("Invalid Operation", "Cannot delete terminal nodes 0 and 1.")
            return
            
        if not messagebox.askyesno("Delete Node", f"Delete node '{node.label}' and its edges?"):
            return
            
        # Remove outgoing edges from this node and incoming references from others
        for item in node.canvas_items:
            self.canvas.delete(item)
            
        for other in self.nodes.values():
            other.edges_out = [(tid, et) for tid, et in other.edges_out if tid != node_id]
            
        # Remove the node from the registry
        del self.nodes[node_id]
        
        # Reset selection and root status if needed
        if node.is_root:
            for remaining in self.nodes.values():
                remaining.is_root = False
        self.selected_node = None
        self.selected_nodes = set()
        self.connecting_mode = False
        self.connecting_edge_type = None
        self.connecting_from_node = None
        self.selecting_box = False
        self.selection_rect = None
        self.canvas.config(cursor='arrow')
        
        # Redraw edges to reflect removal
        self.draw_all_edges()
        self.update_status(f"Deleted node '{node.label}'")
        self.update_mode("Ready")
            
    def cancel_operation(self):
        """Cancel the current operation."""
        self.connecting_mode = False
        self.connecting_edge_type = None
        self.connecting_from_node = None
        self.canvas.config(cursor='arrow')
        self.update_status("Operation cancelled - Ready")
        self.update_mode("Ready")
        
    def clear_all(self):
        """Clear all nodes except terminal nodes."""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all decision nodes?"):
            # Keep only terminal nodes
            terminal_nodes = {nid: node for nid, node in self.nodes.items() if node.is_terminal}
            self.nodes = terminal_nodes
            
            # Reset counters
            self.next_var_index = 0
            
            # Clear canvas and redraw
            self.canvas.delete('all')
            for node in self.nodes.values():
                node.clear_edges()
                self.draw_node(node)
                
            self.selected_node = None
            self.selected_nodes = set()
            self.connecting_mode = False
            self.connecting_edge_type = None
            self.connecting_from_node = None
            self.selecting_box = False
            self.selection_rect = None
            self.canvas.config(cursor='arrow')
            self.update_status("Cleared all decision nodes")
            self.update_mode("Ready")
            
    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)

    def update_mode(self, message):
        """Update the mode label."""
        self.mode_label.config(text=f"Mode: {message}")
        
    def refresh_selection(self, previous_selected):
        """Redraw nodes affected by selection changes."""
        affected = set(previous_selected) | set(self.selected_nodes)
        for node_id in affected:
            node = self.nodes.get(node_id)
            if node is not None:
                self.draw_node(node)
        self.draw_all_edges()
        
    def start_selection_box(self, x, y, additive=False):
        """Begin a selection box drag."""
        self.selecting_box = True
        self.selection_additive = additive
        self.selection_start_x = x
        self.selection_start_y = y
        if self.selection_rect is not None:
            self.canvas.delete(self.selection_rect)
        self.selection_rect = self.canvas.create_rectangle(
            x, y, x, y,
            outline='blue',
            dash=(4, 2)
        )
        self.update_status("Box select: drag to choose nodes")
        self.update_mode("Box selecting")
        
    def update_selection_box(self, x, y):
        """Update the selection box rectangle."""
        if self.selection_rect is None:
            return
        self.canvas.coords(
            self.selection_rect,
            self.selection_start_x,
            self.selection_start_y,
            x,
            y
        )
        
    def finish_selection_box(self, x, y):
        """Finish selection box and select nodes inside it."""
        self.selecting_box = False
        if self.selection_rect is not None:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
        x1 = min(self.selection_start_x, x)
        y1 = min(self.selection_start_y, y)
        x2 = max(self.selection_start_x, x)
        y2 = max(self.selection_start_y, y)
        
        selected = set()
        for node_id, node in self.nodes.items():
            if x1 <= node.x <= x2 and y1 <= node.y <= y2:
                selected.add(node_id)
                
        previous_selected = set(self.selected_nodes)
        if self.selection_additive:
            self.selected_nodes |= selected
        else:
            self.selected_nodes = selected
        self.selected_node = next(iter(self.selected_nodes), None)
        self.refresh_selection(previous_selected)
        if selected:
            self.update_status(f"Selected {len(selected)} node(s)")
        else:
            self.update_status("Ready")
        self.update_mode("Ready")

    def fit_window_to_content(self):
        """Resize window to fit current content."""
        self.root.update_idletasks()
        width = self.main_frame.winfo_reqwidth()
        height = self.main_frame.winfo_reqheight()
        self.root.geometry(f"{width}x{height}")

    def expand_canvas(self, dx, dy):
        """Expand the canvas size and resize the window to fit."""
        self.canvas_width += dx
        self.canvas_height += dy
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.fit_window_to_content()

    def get_root_id(self):
        """Return the current root node ID, or None if not set."""
        for node in self.nodes.values():
            if node.is_root:
                return node.id
        return None

    def export_json(self):
        """Export the current OBDD to a JSON file."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export OBDD"
        )
        if not path:
            self.update_status("Export cancelled")
            return
        data = OBDDSerializer.to_dict(self.nodes, self.get_root_id())
        try:
            OBDDSerializer.save_json(path, data)
        except OSError as exc:
            messagebox.showerror("Export Failed", f"Could not save file:\n{exc}")
            return
        self.update_status(f"Exported OBDD to {path}")

    def import_json(self):
        """Import an OBDD from a JSON file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import OBDD"
        )
        if not path:
            self.update_status("Import cancelled")
            return
        try:
            data = OBDDSerializer.load_json(path)
            nodes, root_id = OBDDSerializer.from_dict(data)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            messagebox.showerror("Import Failed", f"Could not import file:\n{exc}")
            return
        self.load_from_import(nodes, root_id)
        self.update_status(f"Imported OBDD from {path}")
        self.update_mode("Ready")

    def load_from_import(self, nodes, root_id):
        """Replace the current diagram with imported nodes."""
        self.nodes = nodes
        for node in self.nodes.values():
            node.is_root = (node.id == root_id)

        if self.nodes:
            self.next_node_id = max(self.nodes.keys()) + 1
        else:
            self.next_node_id = 0
        self.next_var_index = sum(1 for node in self.nodes.values() if not node.is_terminal)

        self.selected_node = None
        self.selected_nodes = set()
        self.connecting_mode = False
        self.connecting_edge_type = None
        self.connecting_from_node = None
        self.selecting_box = False
        self.selection_rect = None
        self.canvas.config(cursor='arrow')

        self.canvas.delete('all')
        for node in self.nodes.values():
            self.draw_node(node)
        self.draw_all_edges()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = OBDDVisualizer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
