#!/usr/bin/env python3
"""
Example demonstrating the OBDD Visualizer structure.

This script shows how to programmatically work with OBDD nodes and edges,
which mirrors what the GUI application does visually.
"""

# Simple Node class for demonstration (without GUI dependencies)
class Node:
    """Represents a node in the OBDD."""
    
    def __init__(self, node_id, x, y, label, is_terminal=False):
        self.id = node_id
        self.x = x
        self.y = y
        self.label = label
        self.is_terminal = is_terminal
        self.edges_out = []
        self.is_root = False
        
    def add_edge(self, target_node_id, edge_type):
        """Add an edge to another node."""
        self.edges_out = [(tid, et) for tid, et in self.edges_out if et != edge_type]
        self.edges_out.append((target_node_id, edge_type))
        
    def clear_edges(self):
        """Remove all outgoing edges."""
        self.edges_out = []


def example_simple_obdd():
    """
    Create a simple OBDD for the Boolean function: f(p, q) = p AND q
    
    Structure:
          ROOT
           p
          / \\
        0/   \\1
        /     \\
       0       q
              / \\
            0/   \\1
            /     \\
           0       1
    """
    print("Creating OBDD for: f(p, q) = p AND q")
    print("-" * 40)
    
    # Create terminal nodes
    node_0 = Node(0, 100, 400, '0', is_terminal=True)
    node_1 = Node(1, 300, 400, '1', is_terminal=True)
    
    # Create decision nodes
    node_q = Node(2, 300, 250, 'q', is_terminal=False)
    node_p = Node(3, 200, 100, 'p', is_terminal=False)
    
    # Set root
    node_p.is_root = True
    
    # Add edges
    # p's 0-edge goes to terminal 0
    node_p.add_edge(0, 0)  # (target_id, edge_type)
    # p's 1-edge goes to q
    node_p.add_edge(2, 1)
    
    # q's 0-edge goes to terminal 0
    node_q.add_edge(0, 0)
    # q's 1-edge goes to terminal 1
    node_q.add_edge(1, 1)
    
    # Display structure
    print(f"Root node: {node_p.label}")
    print(f"\nNode '{node_p.label}' edges:")
    for target_id, edge_type in node_p.edges_out:
        nodes = {0: node_0, 1: node_1, 2: node_q, 3: node_p}
        target_label = nodes[target_id].label
        edge_name = "1-edge (solid)" if edge_type == 1 else "0-edge (dashed)"
        print(f"  {edge_name} -> {target_label}")
    
    print(f"\nNode '{node_q.label}' edges:")
    for target_id, edge_type in node_q.edges_out:
        nodes = {0: node_0, 1: node_1, 2: node_q, 3: node_p}
        target_label = nodes[target_id].label
        edge_name = "1-edge (solid)" if edge_type == 1 else "0-edge (dashed)"
        print(f"  {edge_name} -> {target_label}")
    
    print("\nEvaluation:")
    print("  f(0, 0) = 0  (p=0, follow 0-edge to 0)")
    print("  f(0, 1) = 0  (p=0, follow 0-edge to 0)")
    print("  f(1, 0) = 0  (p=1, follow 1-edge to q, then q=0, follow 0-edge to 0)")
    print("  f(1, 1) = 1  (p=1, follow 1-edge to q, then q=1, follow 1-edge to 1)")


def example_xor_obdd():
    """
    Create an OBDD for: f(p, q) = p XOR q
    
    Structure:
          ROOT
           p
          / \\
        0/   \\1
        /     \\
       q       q'
      / \\     / \\
    0/   \\1 1/   \\0
    /     \\ /     \\
   0       1       0
    """
    print("\n\n" + "="*40)
    print("Creating OBDD for: f(p, q) = p XOR q")
    print("-" * 40)
    
    # Create terminal nodes
    node_0 = Node(0, 100, 400, '0', is_terminal=True)
    node_1 = Node(1, 300, 400, '1', is_terminal=True)
    
    # Create decision nodes
    node_q_left = Node(2, 150, 250, 'q', is_terminal=False)
    node_q_right = Node(3, 350, 250, 'q', is_terminal=False)
    node_p = Node(4, 250, 100, 'p', is_terminal=False)
    
    # Set root
    node_p.is_root = True
    
    # Add edges
    node_p.add_edge(2, 0)  # p's 0-edge to left q
    node_p.add_edge(3, 1)  # p's 1-edge to right q
    
    node_q_left.add_edge(0, 0)   # left q's 0-edge to 0
    node_q_left.add_edge(1, 1)   # left q's 1-edge to 1
    
    node_q_right.add_edge(1, 0)  # right q's 0-edge to 1
    node_q_right.add_edge(0, 1)  # right q's 1-edge to 0
    
    print(f"Root node: {node_p.label}")
    print("\nThis OBDD represents XOR: output is 1 when p and q differ")
    print("\nEvaluation:")
    print("  f(0, 0) = 0  (different values: False)")
    print("  f(0, 1) = 1  (different values: True)")
    print("  f(1, 0) = 1  (different values: True)")
    print("  f(1, 1) = 0  (different values: False)")


def main():
    """Run the examples."""
    print("="*40)
    print("OBDD Structure Examples")
    print("="*40)
    print("\nThese examples show OBDD structures that you can")
    print("create using the GUI application (obdd_visualizer.py)")
    print()
    
    example_simple_obdd()
    example_xor_obdd()
    
    print("\n" + "="*40)
    print("To create these visually, run:")
    print("  python3 obdd_visualizer.py")
    print("="*40)


if __name__ == '__main__':
    main()
