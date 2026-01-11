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

import tkinter as tk
from tkinter import messagebox
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


class OBDDVisualizer:
    """Main application class for OBDD visualization."""
    
    # Constants
    DECISION_NODE_RADIUS = 25
    TERMINAL_NODE_SIZE = 40
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
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
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.connecting_mode = False
        self.connecting_edge_type = None  # 0 or 1
        self.connecting_from_node = None
        
        # Setup UI
        self.setup_ui()
        
        # Create initial terminal nodes
        self.create_initial_nodes()
        
        # Setup keyboard bindings
        self.setup_keybindings()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(
            main_frame,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg='white',
            cursor='arrow'
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        # Control panel
        control_frame = tk.Frame(main_frame, width=200, bg='lightgray')
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        control_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(control_frame, text="OBDD Visualizer", font=('Arial', 14, 'bold'), bg='lightgray')
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
            text="Add Decision Node (N)",
            command=self.add_decision_node
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Set Root (R)",
            command=self.set_root_node
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Connect 1-Edge (1)",
            command=lambda: self.start_edge_connection(1)
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Connect 0-Edge (0)",
            command=lambda: self.start_edge_connection(0)
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Delete Edges (D)",
            command=self.delete_outgoing_edges
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Delete Node (Del/X)",
            command=self.delete_node
        ).pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(
            control_frame,
            text="Clear All",
            command=self.clear_all
        ).pack(pady=20, padx=10, fill=tk.X)
        
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
        
    def create_initial_nodes(self):
        """Create the initial terminal nodes 0 and 1."""
        # Terminal node 0 on the left
        node0 = Node(self.get_next_node_id(), 150, 500, '0', is_terminal=True)
        self.nodes[node0.id] = node0
        self.draw_node(node0)
        
        # Terminal node 1 on the right
        node1 = Node(self.get_next_node_id(), 650, 500, '1', is_terminal=True)
        self.nodes[node1.id] = node1
        self.draw_node(node1)
        
    def get_next_node_id(self):
        """Get the next available node ID."""
        node_id = self.next_node_id
        self.next_node_id += 1
        return node_id
        
    def get_next_variable_label(self):
        """Get the next variable label (p, q, r, s, ...)."""
        labels = ['p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        if self.next_var_index < len(labels):
            label = labels[self.next_var_index]
        else:
            # If we run out of single letters, use p1, p2, ...
            label = f'p{self.next_var_index - len(labels) + 1}'
        self.next_var_index += 1
        return label
        
    def add_decision_node(self):
        """Add a new decision node to the canvas."""
        # Place node in center or near selected node
        if self.selected_node and self.selected_node in self.nodes:
            x = self.nodes[self.selected_node].x
            y = self.nodes[self.selected_node].y - 80
        else:
            x = self.CANVAS_WIDTH // 2
            y = self.CANVAS_HEIGHT // 3
            
        label = self.get_next_variable_label()
        node = Node(self.get_next_node_id(), x, y, label, is_terminal=False)
        self.nodes[node.id] = node
        self.draw_node(node)
        
        self.update_status(f"Added decision node '{label}'")
        
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
            
            square = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill='lightblue',
                outline='black',
                width=2,
                tags=f'node_{node.id}'
            )
            node.canvas_items.append(square)
        else:
            # Draw circle for decision nodes
            x1 = node.x - self.DECISION_NODE_RADIUS
            y1 = node.y - self.DECISION_NODE_RADIUS
            x2 = node.x + self.DECISION_NODE_RADIUS
            y2 = node.y + self.DECISION_NODE_RADIUS
            
            circle = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill='lightyellow',
                outline='black',
                width=2,
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
                self.selected_node = clicked_node
                self.dragging = True
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.update_status(f"Selected node '{self.nodes[clicked_node].label}'")
            else:
                self.selected_node = None
                self.update_status("Ready")
                
    def on_canvas_drag(self, event):
        """Handle canvas drag events."""
        if self.dragging and self.selected_node is not None:
            # Move the selected node
            node = self.nodes[self.selected_node]
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            node.x += dx
            node.y += dy
            
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Redraw the node and all edges
            self.draw_node(node)
            self.draw_all_edges()
            
    def on_canvas_release(self, event):
        """Handle canvas button release events."""
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
        self.connecting_mode = False
        self.connecting_edge_type = None
        self.connecting_from_node = None
        self.canvas.config(cursor='arrow')
        
        # Redraw edges to reflect removal
        self.draw_all_edges()
        self.update_status(f"Deleted node '{node.label}'")
            
    def cancel_operation(self):
        """Cancel the current operation."""
        self.connecting_mode = False
        self.connecting_edge_type = None
        self.connecting_from_node = None
        self.canvas.config(cursor='arrow')
        self.update_status("Operation cancelled - Ready")
        
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
            self.connecting_mode = False
            self.connecting_edge_type = None
            self.connecting_from_node = None
            self.canvas.config(cursor='arrow')
            self.update_status("Cleared all decision nodes")
            
    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = OBDDVisualizer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
