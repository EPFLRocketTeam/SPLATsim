#!/usr/bin/env python3
"""
Parachute Simulation Application
Main entry point for the parachute simulation GUI application.
"""

import tkinter as tk
import sys
import os
from PIL import Image, ImageTk

# Add current directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui import ParachuteSimulationGUI


def main():
    """Main application entry point"""
    try:
        # Create the main window
        root = tk.Tk()
        ico = Image.open('assets/ERT_SMALL.png')
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)
        # Create and start the application
        app = ParachuteSimulationGUI(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all required modules are available:")
        print("- parachute.py")
        print("- rocket.py") 
        print("- simulation.py")
        print("- GUI.py")
        sys.exit(1)
        
    except Exception as e:
        print(f"Application Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
