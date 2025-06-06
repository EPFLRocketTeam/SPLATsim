# Sudgested code structure

rocket_sim/
├── main.py                 # Entry point and main window
├── models/
│   ├── __init__.py
│   ├── rocket.py          # Rocket physics model
│   └── parachute.py      # Parachute dynamics
├── simulation/
│   ├── __init__.py
│   └── simulation.py     
├── gui/
│   ├── __init__.py
│   ├── main_window.py    # Main application window
│   ├── input_panel.py    # Parameter input widgets
│   ├── plot_panel.py     # Graph display area
│   └── widgets.py        # Custom UI components
├── data/
│   ├── __init__.py
│   └── results.py        # Data storage and export
└── utils/
    ├── __init__.py
    ├── config.py         # Configuration settings
    └── validators.py     # Input validation