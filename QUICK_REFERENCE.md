# OBDD Visualizer - Quick Reference

## Keyboard Shortcuts
```
╔═══════════════════════════════════════╗
║           Quick Reference             ║
╠═══════════════════════════════════════╣
║  N      Add decision node             ║
║  R      Set as root                   ║
║  1      Connect 1-edge (solid)        ║
║  0      Connect 0-edge (dashed)       ║
║  D      Delete outgoing edges         ║
║  ESC    Cancel operation              ║
╚═══════════════════════════════════════╝
```

## Mouse Operations
- **Click** node → Select
- **Drag** node → Move
- **Click** canvas → Deselect

## Node Types
- **Decision** → Yellow circle (p, q, r, ...)
- **Terminal** → Blue square (0, 1)

## Edge Types
- **1-edge** → Solid black line
- **0-edge** → Dashed gray line

## Quick Start
1. Press **N** to add nodes
2. **Drag** to position
3. Press **R** to set root
4. Press **1** or **0**, click target to connect

## Running
```bash
python3 obdd_visualizer.py
```
or
```bash
python3 run.py
```
