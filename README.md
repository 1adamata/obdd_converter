# OBDD Converter

A Python 3 Tkinter application for visually creating Ordered Binary Decision Diagrams (OBDDs).

## Features

- **Visual Canvas**: Interactive canvas for creating and manipulating OBDDs
- **Node Types**:
  - Decision nodes: Circles labeled with variables (p, q, r, s, ...)
  - Terminal nodes: Squares labeled 0 and 1 (present at startup)
- **Draggable Nodes**: Click and drag any node to reposition it
- **Edge Connections**:
  - Solid arrows for 1-edges
  - Dashed arrows for 0-edges
- **Root Node**: Designate any node as the root (shown with red arrow indicator)
- **Keyboard Shortcuts**: Fast operations using keyboard commands

## Requirements

- Python 3.x
- tkinter (usually included with Python)

## Running the Application

```bash
python3 main.py
```

## Keyboard Shortcuts

- **N**: Add a new decision node
- **R**: Set the selected node as root
- **1**: Connect selected node with a 1-edge (solid line)
- **0**: Connect selected node with a 0-edge (dashed line)
- **D**: Delete all outgoing edges from selected node
- **ESC**: Cancel current operation
- **E**: Export OBDD to JSON
- **I**: Import OBDD from JSON

## Usage

1. **Adding Nodes**: Press 'N' or click "Add Decision Node" to create a new decision node
2. **Selecting Nodes**: Click on any node to select it
3. **Moving Nodes**: Click and drag a node to reposition it
4. **Setting Root**: Select a node and press 'R' to designate it as the root
5. **Creating Edges**:
   - Select the source node (must be a decision node, not terminal)
   - Press '1' for a 1-edge or '0' for a 0-edge
   - Click on the target node to complete the connection
6. **Deleting Edges**: Select a node and press 'D' to remove all its outgoing edges
7. **Export/Import**:
   - Press 'E' to export the diagram to JSON
   - Press 'I' to import a JSON file and rebuild the diagram

## Terminal Nodes

The application starts with two terminal nodes:
- Node **0** (square, left side)
- Node **1** (square, right side)

These represent the false and true terminal values in the OBDD.
