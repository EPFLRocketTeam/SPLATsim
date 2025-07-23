import tkinter as tk
from tkinter import ttk, messagebox

from models import HemisphericalParachute, RocketModel
from simulation import SingleEventSimulation, DualEventSimulation

from .input_panel import InputPanel
from .plot_panel import PlotPanel


class ParachuteSimulationGUI:
    """Main application window for parachute simulation"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_layout()
        self.setup_menu()
        self.setup_bindings()
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("SPLAT - Parachute Simulation Application")
        self.root.geometry("1200x800")
        self.root.minsize(800, 700)
        
        # Configure grid weights for resizing
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_menu(self):
        """Setup the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_configuration, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.input_panel.import_parameters, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.input_panel.export_parameters, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Run", command=self.run_simulation, accelerator="F5")
        sim_menu.add_command(label="Validate Parameters", command=self.validate_parameters)
        sim_menu.add_separator()
        sim_menu.add_command(label="Reset to Defaults", command=self.reset_to_defaults)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show External Plot", command=self.plot_panel.show_external_plot)
        view_menu.add_command(label="Show Embedded Plot", command=self.plot_panel.create_plots)
        view_menu.add_command(label="Clear Plot", command=self.plot_panel.clear_plot)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
    
    def setup_layout(self):
        """Setup the main layout with panels"""
        # Create main frames
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Configure frame weights
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Create input panel (left side)
        self.input_panel = InputPanel(left_frame)
        self.input_panel.pack(fill=tk.BOTH, expand=True)
        self.input_panel.on_sim_type_change()  # Initialize based on default type
        
        # Create control section (right top)
        self.setup_control_section(right_frame)
        
        # Create plot panel (right bottom)
        self.plot_panel = PlotPanel(right_frame)
        self.plot_panel.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
    
    def setup_control_section(self, parent):
        """Setup the simulation control section"""
        control_frame = ttk.LabelFrame(parent, text="Simulation Control", padding=10)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Run simulation button
        run_button = ttk.Button(
            control_frame, 
            text="Run Simulation", 
            command=self.run_simulation,
            style="Accent.TButton"
        )
        run_button.pack(side=tk.LEFT, padx=5)
        
        # Validate button
        validate_button = ttk.Button(
            control_frame, 
            text="Validate Parameters", 
            command=self.validate_parameters
        )
        validate_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.bind('<Control-n>', lambda e: self.new_configuration())
        self.root.bind('<Control-o>', lambda e: self.input_panel.import_parameters())
        self.root.bind('<Control-s>', lambda e: self.input_panel.export_parameters())
        self.root.bind('<F5>', lambda e: self.run_simulation())
        self.root.bind('<Escape>', lambda e: self.on_closing())
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def run_simulation(self):
        """Run the simulation with current parameters"""
        try:
            # Update status
            self.status_var.set("Running simulation...")
            self.root.update()
            
            # Validate parameters first
            errors = self.input_panel.validate_parameters()
            if errors:
                error_msg = "Parameter validation failed:\n\n" + "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("Validation Error", error_msg)
                self.status_var.set("Validation failed")
                return
            
            # Get parameters
            params = self.input_panel.get_parameters()
            
            # Create parachute model
            parachute = HemisphericalParachute(
                projected_diameter=params['parachute']['projected_diameter'],
                open_Cd=params['parachute']['open_Cd'],
                reefing_ratio=params['parachute']['reefing_ratio'],
                spill_hole_diameter=params['parachute']['spill_hole_diameter'],
                opening_time=params['parachute']['opening_time']
            )
            
            # Create rocket model
            rocket = RocketModel(
                mass=params['rocket']['mass'],
                diameter=params['rocket']['diameter'],
                parachute=parachute,
                drag_coefficient=params['rocket']['drag_coefficient']
            )
            
            # Create simulation
            if params['simulation']['type'] == "Dual Event":
                simulation = DualEventSimulation(
                    rocket=rocket,
                    parachute=parachute,
                    reefed=params['simulation']['reefed'],
                    first_event_altitude=params['simulation']['first_altitude'],
                    second_event_altitude=params['simulation']['second_altitude'],
                    time_step=params['simulation']['time_step'],
                    max_time=params['simulation']['max_time'],
                    launch_angle=params['simulation']['launch_angle']
                )
            else:
                simulation = SingleEventSimulation(
                    rocket=rocket,
                    parachute=parachute,
                    reefed=params['simulation']['reefed'],
                    first_event_altitude=params['simulation']['first_altitude'],
                    time_step=params['simulation']['time_step'],
                    max_time=params['simulation']['max_time'],
                    launch_angle=params['simulation']['launch_angle']
                )
            
            # Run simulation
            results = simulation.simulate()
            
            # Display results
            self.plot_panel.display_results(results)
            self.plot_panel.create_plots()
            self.status_var.set(f"Simulation complete - Landing: {results['landing_velocity']:.1f} m/s")
            
        except Exception as e:
            error_msg = f"Simulation failed: {str(e)}"
            self.plot_panel.display_error(error_msg)
            self.status_var.set("Simulation failed")
            messagebox.showerror("Simulation Error", error_msg)
    
    def validate_parameters(self):
        """Validate current parameters and show results"""
        errors = self.input_panel.validate_parameters()
        
        if errors:
            error_msg = "Parameter validation found issues:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showwarning("Validation Issues", error_msg)
        else:
            messagebox.showinfo("Validation Successful", "All parameters are valid!")
    
    def new_configuration(self):
        """Create a new configuration (reset to defaults)"""
        result = messagebox.askyesno(
            "New Configuration", 
            "This will reset all parameters to default values. Continue?"
        )
        
        if result:
            self.reset_to_defaults()
    
    def reset_to_defaults(self):
        """Reset all parameters to default values"""
        # Reset input panel variables to defaults
        self.input_panel.rocket_mass.set(20.0)
        self.input_panel.rocket_diameter.set(1.0)
        self.input_panel.rocket_drag_coeff.set(1.5)
        
        self.input_panel.parachute_diameter.set(5.0)
        self.input_panel.opening_time.set(10.7)
        self.input_panel.reefing_ratio.set(0.5)
        self.input_panel.spill_hole_diameter.set(1.0)
        self.input_panel.open_cd.set(1.5)
        
        self.input_panel.air_density.set(1.124)
        self.input_panel.gravity.set(9.81)
        
        self.input_panel.sim_type.set("Single Event")
        self.input_panel.first_altitude.set(550.0)
        self.input_panel.second_altitude.set(500.0)
        self.input_panel.time_step.set(0.001)
        self.input_panel.max_time.set(300.0)
        self.input_panel.reefed.set(True)
        
        # Update UI
        self.input_panel.on_sim_type_change()
        
        # Clear results
        self.plot_panel.clear_plot()
        self.plot_panel.results_text.clear()
        
        self.status_var.set("Reset to defaults")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """SPLAT - Slow Parachute Landings Avoid Trauma
  
Version: 1.0
Date: June 2025

This application was originally developed by Kelan Solomon from the EPFL Rocket Team during what was supposed to be a 30-minute study break before his Sensor Orientation exam. Its goal is to simulate rocket parachute recovery, especially for dual events employing reefing techniques.

Developed using Python, tkinter, matplotlib and Claude.ai"""
        
        messagebox.showinfo("About Parachute Simulation", about_text)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """Quick Start Guide:

1. Configure Parameters:
   • Set rocket mass, diameter, and drag coefficient
   • Configure parachute dimensions and properties
   • Adjust simulation settings

2. Run Simulation:
   • Click 'Run Simulation' or press F5
   • View results in the results panel
   • Generate plots for analysis

3. Save/Load Configurations:
   • Use File menu to save/load parameter sets
   • Export results for documentation

Keyboard Shortcuts:
• F5: Run simulation
• Ctrl+N: New configuration
• Ctrl+O: Open parameters
• Ctrl+S: Save parameters
• Esc: Exit application

For detailed information, consult the user manual."""
        
        messagebox.showinfo("Help", help_text)
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            # Clean up any resources
            if hasattr(self.plot_panel, 'figure') and self.plot_panel.figure[0]: #TODO: Close all figures
                import matplotlib.pyplot as plt
                plt.close(self.plot_panel.figure[0])
            
            self.root.destroy()