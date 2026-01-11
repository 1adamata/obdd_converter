# OBDD Visualizer - User Guide

## Overview

The OBDD Visualizer is a graphical tool for creating and visualizing Ordered Binary Decision Diagrams (OBDDs), which are data structures used in formal verification, logic synthesis, and Boolean function manipulation.

## What is an OBDD?

An Ordered Binary Decision Diagram (OBDD) is a directed acyclic graph used to represent Boolean functions. It consists of:

- **Decision Nodes**: Labeled with Boolean variables (p, q, r, etc.), shown as circles
- **Terminal Nodes**: Represent the constant values 0 (false) and 1 (true), shown as squares
- **Edges**: Connect nodes, where:
  - **0-edge** (dashed line): The path taken when the variable is false
  - **1-edge** (solid line): The path taken when the variable is true
- **Root Node**: The starting point for evaluating the Boolean function

## Installation

### Requirements

- Python 3.x
- tkinter (Python's standard GUI library)

### Installing tkinter

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS (with Homebrew):**
```bash
brew install python-tk
```

**Windows:**
Tkinter is usually included with Python installations from python.org

## Running the Application

There are two ways to run the application:

### Option 1: Using the launcher (recommended)
```bash
python3 run.py
```
The launcher checks dependencies and provides helpful error messages.

### Option 2: Direct execution
```bash
python3 obdd_visualizer.py
```

## User Interface

### Main Components

1. **Canvas** (left side): The main drawing area where you create and manipulate your OBDD
2. **Control Panel** (right side): Contains buttons and displays keyboard shortcuts
3. **Status Bar** (bottom of control panel): Shows current operation status

### Initial State

When you start the application, two terminal nodes are present:
- **Node 0** (square, left side): Represents FALSE
- **Node 1** (square, right side): Represents TRUE

## Basic Operations

### 1. Adding Decision Nodes

**Keyboard:** Press `N`  
**Mouse:** Click "Add Decision Node (N)" button

- Creates a new decision node with the next available variable label (p, q, r, s, ...)
- Node appears in the center or near the currently selected node
- Node is represented as a yellow circle

### 2. Selecting Nodes

**Mouse:** Click on any node

- Selected node will be used for subsequent operations
- Status bar shows which node is selected

### 3. Moving Nodes

**Mouse:** Click and drag any node

- All nodes (including terminal nodes) can be repositioned
- Edges automatically update as nodes move

### 4. Setting the Root Node

**Keyboard:** Press `R`  
**Mouse:** Click "Set Root (R)" button

**Requirements:**
- A node must be selected first

**Result:**
- A red arrow labeled "ROOT" appears above the designated root node
- Only one node can be the root at a time

### 5. Creating Edges

#### Creating a 1-Edge (solid line)

**Keyboard:** Press `1`  
**Mouse:** Click "Connect 1-Edge (1)" button

#### Creating a 0-Edge (dashed line)

**Keyboard:** Press `0`  
**Mouse:** Click "Connect 0-Edge (0)" button

**Requirements:**
- Source node must be selected (and must be a decision node, not terminal)
- Cursor changes to crosshair to indicate connection mode

**Steps:**
1. Select the source node
2. Press `1` or `0` to initiate connection
3. Click on the target node
4. Edge is created with an arrow pointing to the target

**Notes:**
- Each decision node can have at most one 0-edge and one 1-edge
- Creating a new edge of the same type replaces the old one
- Terminal nodes cannot be source nodes

### 6. Deleting Edges

**Keyboard:** Press `D`  
**Mouse:** Click "Delete Edges (D)" button

**Requirements:**
- Source node must be selected

**Result:**
- All outgoing edges from the selected node are removed

### 7. Canceling Operations

**Keyboard:** Press `ESC`

- Cancels edge connection mode
- Returns cursor to normal

### 8. Clearing All

**Mouse:** Click "Clear All" button

- Removes all decision nodes
- Keeps terminal nodes 0 and 1
- Prompts for confirmation

## Keyboard Shortcuts Summary

| Key | Action |
|-----|--------|
| N | Add new decision node |
| R | Set selected node as root |
| 1 | Connect 1-edge (solid) from selected node |
| 0 | Connect 0-edge (dashed) from selected node |
| D | Delete all outgoing edges from selected node |
| ESC | Cancel current operation |

## Example: Creating a Simple OBDD

Let's create an OBDD for the Boolean function `f(p, q) = p AND q`:

1. **Press N** twice to create two decision nodes (labeled 'p' and 'q')

2. **Position the nodes:**
   - Drag 'p' to the top center
   - Drag 'q' below and to the right of 'p'
   - Terminal '0' is on the left
   - Terminal '1' is on the right

3. **Set the root:**
   - Click on node 'p'
   - Press R

4. **Create edges from 'p':**
   - Click on node 'p'
   - Press 0 (for 0-edge)
   - Click on terminal node '0'
   - Click on node 'p' again
   - Press 1 (for 1-edge)
   - Click on node 'q'

5. **Create edges from 'q':**
   - Click on node 'q'
   - Press 0
   - Click on terminal node '0'
   - Click on node 'q' again
   - Press 1
   - Click on terminal node '1'

**Result:** You now have an OBDD representing p AND q:
- If p=0, follow dashed edge to 0 (result is false)
- If p=1, follow solid edge to q
  - If q=0, follow dashed edge to 0 (result is false)
  - If q=1, follow solid edge to 1 (result is true)

## Tips and Best Practices

1. **Node Placement:** Arrange nodes in levels, with the root at top and terminals at bottom
2. **Variable Ordering:** The order of variables (top to bottom) matters for OBDD efficiency
3. **Save Your Work:** The application currently doesn't save diagrams, so take screenshots
4. **Testing:** Use the examples.py script to see OBDD structures programmatically

## Running Examples

To see example OBDD structures:
```bash
python3 examples.py
```

This demonstrates OBDDs for common Boolean functions like AND and XOR.

## Running Tests

To verify the core functionality:
```bash
python3 test_obdd.py
```

This runs unit tests on the Node class and edge operations.

## Troubleshooting

### "No module named 'tkinter'"
Install tkinter using the instructions in the Installation section above.

### Nodes won't move
Make sure you're clicking directly on the node shape, not between nodes.

### Can't connect edges
Ensure:
1. The source node is selected
2. The source node is a decision node (not a terminal node)
3. You've pressed 1 or 0 to enter connection mode

### Lost the terminal nodes
Click "Clear All" to reset the canvas with fresh terminal nodes.

## Advanced Features

### Multiple Variables
The application supports up to 26 variables (p through z). After that, it generates labels like p1, p2, etc.

### Complex Diagrams
You can create arbitrarily complex OBDDs by:
- Adding many decision nodes
- Creating intricate edge patterns
- Using the same variable multiple times (though this is non-canonical)

## Future Enhancements

Potential features for future versions:
- Save/load diagrams to/from files
- Export to various formats (image, text, DOT)
- OBDD reduction/canonicalization
- Truth table generation
- Boolean expression input

## Support

For issues, questions, or contributions, visit the GitHub repository:
https://github.com/1adamata/obdd_converter
