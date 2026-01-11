#!/usr/bin/env python3
"""
Launcher script for OBDD Visualizer with dependency checking.
"""

import sys


def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import tkinter
        return True, None
    except ImportError as e:
        return False, str(e)


def main():
    """Main entry point."""
    print("OBDD Visualizer Launcher")
    print("=" * 50)
    
    # Check dependencies
    deps_ok, error = check_dependencies()
    
    if not deps_ok:
        print("\n❌ ERROR: Required dependency not found!")
        print(f"\n{error}\n")
        print("To fix this issue, install tkinter:")
        print("\nOn Ubuntu/Debian:")
        print("  sudo apt-get install python3-tk")
        print("\nOn Fedora:")
        print("  sudo dnf install python3-tkinter")
        print("\nOn macOS (with Homebrew):")
        print("  brew install python-tk")
        print("\nOn Windows:")
        print("  Tkinter is usually included with Python")
        print("  Try reinstalling Python from python.org")
        print("\n" + "=" * 50)
        return 1
    
    # All dependencies available, launch the application
    print("✓ All dependencies found")
    print("Launching OBDD Visualizer...\n")
    
    import obdd_visualizer
    obdd_visualizer.main()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
