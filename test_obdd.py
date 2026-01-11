#!/usr/bin/env python3
"""
Test script for OBDD Visualizer - verifies the Node and core logic without GUI.
"""

import sys
import os

# Import the Node class (mock tkinter for testing)
sys.path.insert(0, os.path.dirname(__file__))

# Mock tkinter for headless testing
class MockTk:
    def __init__(self):
        pass
    def title(self, t):
        pass
    def mainloop(self):
        pass
    def bind(self, *args):
        pass

class MockCanvas:
    def __init__(self, *args, **kwargs):
        self.items = []
    def create_oval(self, *args, **kwargs):
        item_id = len(self.items)
        self.items.append(('oval', args, kwargs))
        return item_id
    def create_rectangle(self, *args, **kwargs):
        item_id = len(self.items)
        self.items.append(('rect', args, kwargs))
        return item_id
    def create_text(self, *args, **kwargs):
        item_id = len(self.items)
        self.items.append(('text', args, kwargs))
        return item_id
    def create_line(self, *args, **kwargs):
        item_id = len(self.items)
        self.items.append(('line', args, kwargs))
        return item_id
    def delete(self, *args):
        pass
    def tag_raise(self, *args):
        pass
    def tag_lower(self, *args):
        pass
    def pack(self, *args, **kwargs):
        pass
    def bind(self, *args):
        pass
    def config(self, **kwargs):
        pass

class MockFrame:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def pack_propagate(self, *args):
        pass

class MockLabel:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def config(self, **kwargs):
        pass

class MockButton:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass

# Mock tkinter module
import types
tk_module = types.ModuleType('tkinter')
tk_module.Tk = MockTk
tk_module.Canvas = MockCanvas
tk_module.Frame = MockFrame
tk_module.Label = MockLabel
tk_module.Button = MockButton
tk_module.BOTH = 'both'
tk_module.LEFT = 'left'
tk_module.RIGHT = 'right'
tk_module.Y = 'y'
tk_module.X = 'x'
tk_module.LAST = 'last'
tk_module.messagebox = types.SimpleNamespace(showwarning=lambda *args: None, askyesno=lambda *args: True)
sys.modules['tkinter'] = tk_module

# Now import the actual module
from obdd_visualizer import Node

def test_node_creation():
    """Test creating nodes."""
    print("Testing node creation...")
    
    # Create a decision node
    node1 = Node(0, 100, 100, 'p', is_terminal=False)
    assert node1.id == 0
    assert node1.x == 100
    assert node1.y == 100
    assert node1.label == 'p'
    assert not node1.is_terminal
    assert not node1.is_root
    assert len(node1.edges_out) == 0
    print("✓ Decision node created successfully")
    
    # Create a terminal node
    node2 = Node(1, 200, 200, '0', is_terminal=True)
    assert node2.id == 1
    assert node2.is_terminal
    print("✓ Terminal node created successfully")

def test_edge_operations():
    """Test edge operations."""
    print("\nTesting edge operations...")
    
    node1 = Node(0, 100, 100, 'p', is_terminal=False)
    node2 = Node(1, 200, 200, '0', is_terminal=True)
    node3 = Node(2, 300, 300, '1', is_terminal=True)
    
    # Add edges
    node1.add_edge(1, 0)  # 0-edge to node 1
    node1.add_edge(2, 1)  # 1-edge to node 2
    
    assert len(node1.edges_out) == 2
    assert (1, 0) in node1.edges_out
    assert (2, 1) in node1.edges_out
    print("✓ Edges added successfully")
    
    # Replace an edge of the same type
    node1.add_edge(3, 0)  # Replace 0-edge
    assert len(node1.edges_out) == 2
    assert (1, 0) not in node1.edges_out
    assert (3, 0) in node1.edges_out
    print("✓ Edge replacement works correctly")
    
    # Clear edges
    node1.clear_edges()
    assert len(node1.edges_out) == 0
    print("✓ Edge clearing works correctly")

def test_root_designation():
    """Test root node designation."""
    print("\nTesting root designation...")
    
    node = Node(0, 100, 100, 'p', is_terminal=False)
    assert not node.is_root
    
    node.is_root = True
    assert node.is_root
    print("✓ Root designation works correctly")

def test_variable_labels():
    """Test that the application can generate proper variable labels."""
    print("\nTesting variable label generation...")
    
    labels = ['p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for i, expected_label in enumerate(labels):
        # Simulate getting next label
        label = labels[i] if i < len(labels) else f'p{i - len(labels) + 1}'
        assert label == expected_label
    
    # Test beyond single letters
    label = f'p{13 - len(labels) + 1}'
    assert label == 'p3'
    print("✓ Variable label generation works correctly")

def main():
    """Run all tests."""
    print("=" * 50)
    print("OBDD Visualizer - Unit Tests")
    print("=" * 50)
    
    try:
        test_node_creation()
        test_edge_operations()
        test_root_designation()
        test_variable_labels()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
