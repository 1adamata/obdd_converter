# OBDD Visualizer - Application Structure

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OBDD Visualizer                                  │
├──────────────────────────────────────────┬──────────────────────────────────┤
│                                          │  OBDD Visualizer                 │
│                                          │                                  │
│              Canvas Area                 │  Keyboard Shortcuts:             │
│           (800x600 pixels)               │    N: Add decision node          │
│                                          │    R: Set root node              │
│         ROOT                             │    1: Connect 1-edge             │
│          ↓                               │    0: Connect 0-edge             │
│        ╭───╮                             │    D: Delete outgoing edges      │
│        │ p │  ← Decision node (circle)   │    ESC: Cancel operation         │
│        ╰───╯                             │                                  │
│       ╱     ╲                            │  [Add Decision Node (N)]         │
│     0╱       ╲1                          │  [Set Root (R)]                  │
│     ╱(dashed) ╲(solid)                   │  [Connect 1-Edge (1)]            │
│    ╱           ╲                         │  [Connect 0-Edge (0)]            │
│  ┌───┐        ╭───╮                      │  [Delete Edges (D)]              │
│  │ 0 │        │ q │                      │                                  │
│  └───┘        ╰───╯                      │  [Clear All]                     │
│  Terminal    ╱     ╲                     │                                  │
│  node       ╱       ╲                    │  Status: Ready                   │
│  (square)  ╱         ╲                   │                                  │
│         ┌───┐      ┌───┐                 │                                  │
│         │ 0 │      │ 1 │                 │                                  │
│         └───┘      └───┘                 │                                  │
│                                          │                                  │
│                                          │                                  │
└──────────────────────────────────────────┴──────────────────────────────────┘
```

## Node Types

### Decision Node (Circle)
```
  ╭───╮
  │ p │  ← Variable label (p, q, r, s, ...)
  ╰───╯
 ╱     ╲
0       1  ← Two outgoing edges (0-edge and 1-edge)
```

### Terminal Node (Square)
```
┌───┐
│ 0 │  ← Terminal value (0 or 1)
└───┘
```

### Root Indicator
```
  ROOT  ← Red text
   ↓    ← Red arrow
 ╭───╮
 │ p │  ← Root node
 ╰───╯
```

## Edge Types

### 1-Edge (Solid Line with Arrow)
```
     ╲
      ╲  ← Solid black line
       ↓  ← Arrow pointing to target
```

### 0-Edge (Dashed Line with Arrow)
```
     ╱
    ╱   ← Dashed gray line
   ↓    ← Arrow pointing to target
```

## Example OBDD Diagrams

### Simple AND Function: f(p, q) = p AND q

```
        ROOT
         ↓
       ╭───╮
       │ p │
       ╰───╯
      ╱     ╲
    0╱       ╲1
    ╱         ╲
 ┌───┐       ╭───╮
 │ 0 │       │ q │
 └───┘       ╰───╯
            ╱     ╲
          0╱       ╲1
          ╱         ╲
       ┌───┐       ┌───┐
       │ 0 │       │ 1 │
       └───┘       └───┘
```

Evaluation:
- f(0, 0) = 0: Follow p's 0-edge → terminal 0
- f(0, 1) = 0: Follow p's 0-edge → terminal 0
- f(1, 0) = 0: Follow p's 1-edge → q, then q's 0-edge → terminal 0
- f(1, 1) = 1: Follow p's 1-edge → q, then q's 1-edge → terminal 1

### XOR Function: f(p, q) = p XOR q

```
           ROOT
            ↓
          ╭───╮
          │ p │
          ╰───╯
         ╱     ╲
       0╱       ╲1
       ╱         ╲
    ╭───╮       ╭───╮
    │ q │       │ q │
    ╰───╯       ╰───╯
   ╱     ╲     ╱     ╲
 0╱       ╲1 0╱       ╲1
 ╱         ╲ ╱         ╲
┌───┐    ┌───┐       ┌───┐
│ 0 │    │ 1 │       │ 0 │
└───┘    └───┘       └───┘
```

Evaluation:
- f(0, 0) = 0: p=0 → left q, q=0 → 0
- f(0, 1) = 1: p=0 → left q, q=1 → 1
- f(1, 0) = 1: p=1 → right q, q=0 → 1
- f(1, 1) = 0: p=1 → right q, q=1 → 0

## Color Scheme

- **Decision Nodes**: Light yellow circles with black outline
- **Terminal Nodes**: Light blue squares with black outline
- **Node Labels**: Black, bold, Arial 14pt
- **Root Indicator**: Red arrow and text
- **1-Edges**: Black solid lines with arrows
- **0-Edges**: Gray dashed lines with arrows
- **Canvas**: White background
- **Control Panel**: Light gray background

## Interaction States

### Normal Mode
- Cursor: Arrow
- Click on node: Select it
- Click and drag node: Move it

### Connection Mode (after pressing 1 or 0)
- Cursor: Crosshair
- Status: "Click on target node to connect..."
- Click on node: Create edge to that node
- Press ESC: Cancel

## File Structure

```
obdd_converter/
├── .gitignore              # Python gitignore
├── README.md               # Quick start guide
├── USER_GUIDE.md           # Comprehensive user manual
├── VISUAL_GUIDE.md         # This file (visual documentation)
├── requirements.txt        # Python dependencies
├── obdd_visualizer.py      # Main application
├── run.py                  # Launcher with dependency checking
├── test_obdd.py            # Unit tests
└── examples.py             # Example OBDD structures
```

## Technical Details

### Canvas Dimensions
- Width: 800 pixels
- Height: 600 pixels

### Node Dimensions
- Decision node radius: 25 pixels
- Terminal node size: 40x40 pixels

### Colors (RGB/Hex)
- Decision node fill: #FFFFE0 (lightyellow)
- Terminal node fill: #ADD8E6 (lightblue)
- Node outline: #000000 (black)
- 1-edge: #000000 (black)
- 0-edge: #808080 (gray)
- Root indicator: #FF0000 (red)
- Control panel: #D3D3D3 (lightgray)

### Control Panel
- Width: 200 pixels
- Position: Right side of window
- Background: Light gray

## Keyboard Shortcut Reference Card

```
╔═══════════════════════════════════════╗
║  OBDD Visualizer - Keyboard Shortcuts ║
╠═══════════════════════════════════════╣
║  N    Add new decision node           ║
║  R    Set selected node as root       ║
║  1    Connect with 1-edge (solid)     ║
║  0    Connect with 0-edge (dashed)    ║
║  D    Delete outgoing edges           ║
║  ESC  Cancel current operation        ║
╚═══════════════════════════════════════╝
```

## Mouse Operations

```
╔══════════════════════════════════════════════╗
║  Mouse Action      │  Result                 ║
╠══════════════════════════════════════════════╣
║  Click node        │  Select node            ║
║  Click + Drag      │  Move node              ║
║  Click canvas      │  Deselect node          ║
║  Click target      │  Complete edge          ║
║  (connection mode) │  connection             ║
╚══════════════════════════════════════════════╝
```
