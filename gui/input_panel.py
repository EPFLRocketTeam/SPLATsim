import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import xml.dom.minidom

from .widgets import ParameterFrame


class InputPanel(ttk.Frame):
    """Panel containing all parameter input widgets"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setup_variables()
        self.setup_ui()
    
    def setup_variables(self):
        """Initialize all tkinter variables"""
        # Rocket parameters
        self.rocket_mass = tk.DoubleVar(value=20.0)
        self.rocket_diameter = tk.DoubleVar(value=1.0)
        self.rocket_drag_coeff = tk.DoubleVar(value=1.5)
        
        # Parachute parameters
        self.parachute_diameter = tk.DoubleVar(value=5.0)
        self.opening_time = tk.DoubleVar(value=10.7)
        self.reefing_ratio = tk.DoubleVar(value=0.5)
        self.spill_hole_diameter = tk.DoubleVar(value=1.0)
        self.open_cd = tk.DoubleVar(value=1.5)
        
        # Environment parameters
        self.air_density = tk.DoubleVar(value=1.124)
        self.gravity = tk.DoubleVar(value=9.81)
        
        # Flight Variables
        self.sim_type = tk.StringVar(value="Single Event")
        self.first_altitude = tk.DoubleVar(value=550.0)
        self.second_altitude = tk.DoubleVar(value=500.0)
        self.reefed = tk.BooleanVar(value=True)
        self.launch_angle = tk.DoubleVar(value=90.0)

        # Simulation parameters
        self.time_step = tk.DoubleVar(value=0.001)
        self.max_time = tk.DoubleVar(value=300.0)
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setup_rocket_parameters()
        self.setup_parachute_parameters()
        self.setup_flight_parameters()
        self.setup_environment_parameters()
        self.setup_simulation_parameters()
        self.setup_import_export_buttons()
    
    def setup_rocket_parameters(self):
        """Setup rocket parameter inputs"""
        self.rocket_frame = ParameterFrame(self, "Rocket Parameters")
        self.rocket_frame.pack(fill=tk.X, pady=5)
        
        self.rocket_frame.add_parameter("Mass (kg):", self.rocket_mass)
        self.rocket_frame.add_parameter("Diameter (m):", self.rocket_diameter)
        self.rocket_frame.add_parameter("Drag Coefficient:", self.rocket_drag_coeff)
    
    def setup_parachute_parameters(self):
        """Setup parachute parameter inputs"""
        self.parachute_frame = ParameterFrame(self, "Parachute Parameters")
        self.parachute_frame.pack(fill=tk.X, pady=5)
        
        self.parachute_frame.add_parameter("Diameter (m):", self.parachute_diameter)
        self.parachute_frame.add_parameter("Opening Time (s):", self.opening_time)
        self.parachute_frame.add_parameter("Reefing Ratio:", self.reefing_ratio)
        self.parachute_frame.add_parameter("Spill Hole Diameter (m):", self.spill_hole_diameter)
        self.parachute_frame.add_parameter("Open Cd:", self.open_cd)
    
    def setup_environment_parameters(self):
        """Setup environment parameter inputs"""
        self.env_frame = ParameterFrame(self, "Environment Parameters")
        self.env_frame.pack(fill=tk.X, pady=5)
        
        self.env_frame.add_parameter("Air Density (kg/m³):", self.air_density)
        self.env_frame.add_parameter("Gravity (m/s²):", self.gravity)

    def setup_flight_parameters(self):
        """Setup flight parameters"""
        self.flight_frame = ParameterFrame(self, "Flight Parameters")
        self.flight_frame.pack(fill=tk.X, pady=5)

        # Simulation type combobox
        self.sim_combo = self.flight_frame.add_combobox(
            "Simulation Type:", 
            self.sim_type, 
            ["Single Event", "Dual Event"]
        )
        self.sim_combo.bind("<<ComboboxSelected>>", self.on_sim_type_change)

        # Altitude parameters
        self.flight_frame.add_parameter("First Event Altitude (m):", self.first_altitude)
        
        # Second altitude (initially hidden)
        self.second_alt_entry, self.second_alt_label = self.flight_frame.add_parameter_hideable(
            "Second Event Altitude (m):", self.second_altitude)
        
        # Reefed checkbox
        self.reefed_checkbox = self.flight_frame.add_checkbox("Use Reefing", self.reefed)
        self.flight_frame.add_parameter("Launch Angle (degrees):", self.launch_angle)

    def setup_simulation_parameters(self):
        """Setup simulation parameter inputs"""
        self.sim_frame = ParameterFrame(self, "Simulation Parameters")
        self.sim_frame.pack(fill=tk.X, pady=5)

        self.sim_frame.add_parameter("Time Step (s):", self.time_step)
        self.sim_frame.add_parameter("Max Time (s):", self.max_time)
        
    def setup_import_export_buttons(self):
        """Setup import/export buttons"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Export Parameters", command=self.export_parameters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import Parameters", command=self.import_parameters).pack(side=tk.LEFT, padx=5)


    def on_sim_type_change(self, event=None):
        if self.sim_type.get() == "Dual Event":
            self.second_alt_label.grid()
            self.second_alt_entry.grid()
            self.reefed_checkbox.grid_remove()
        else:
            self.second_alt_label.grid_remove()
            self.second_alt_entry.grid_remove()
            self.reefed_checkbox.grid()
        
    def get_parameters(self):
        """Return current parameter values as a dictionary"""
        return {
            'rocket': {
                'mass': self.rocket_mass.get(),
                'diameter': self.rocket_diameter.get(),
                'drag_coefficient': self.rocket_drag_coeff.get()
            },
            'parachute': {
                'projected_diameter': self.parachute_diameter.get(),
                'open_Cd': self.open_cd.get(),
                'reefing_ratio': self.reefing_ratio.get(),
                'spill_hole_diameter': self.spill_hole_diameter.get(),
                'opening_time': self.opening_time.get()
            },
            'environment': {
                'air_density': self.air_density.get(),
                'gravity': self.gravity.get()
            },
            'simulation': {
                'type': self.sim_type.get(),
                'first_altitude': self.first_altitude.get(),
                'second_altitude': self.second_altitude.get(),
                'launch_angle': self.launch_angle.get(),
                'time_step': self.time_step.get(),
                'max_time': self.max_time.get(),
                'reefed': self.reefed.get()
            }
        }
    
    def set_parameters(self, params):
        """Set parameter values from dictionary"""
        # Set rocket parameters
        if 'rocket' in params:
            rocket = params['rocket']
            if 'mass' in rocket:
                self.rocket_mass.set(rocket['mass'])
            if 'diameter' in rocket:
                self.rocket_diameter.set(rocket['diameter'])
            if 'drag_coefficient' in rocket:
                self.rocket_drag_coeff.set(rocket['drag_coefficient'])
        
        # Set parachute parameters
        if 'parachute' in params:
            parachute = params['parachute']
            if 'projected_diameter' in parachute:
                self.parachute_diameter.set(parachute['projected_diameter'])
            if 'open_Cd' in parachute:
                self.open_cd.set(parachute['open_Cd'])
            if 'reefing_ratio' in parachute:
                self.reefing_ratio.set(parachute['reefing_ratio'])
            if 'spill_hole_diameter' in parachute:
                self.spill_hole_diameter.set(parachute['spill_hole_diameter'])
            if 'opening_time' in parachute:
                self.opening_time.set(parachute['opening_time'])
        
        # Set environment parameters
        if 'environment' in params:
            env = params['environment']
            if 'air_density' in env:
                self.air_density.set(env['air_density'])
            if 'gravity' in env:
                self.gravity.set(env['gravity'])
        
        # Set simulation parameters
        if 'simulation' in params:
            sim = params['simulation']
            if 'type' in sim:
                self.sim_type.set(sim['type'])
                self.on_sim_type_change()
            if 'first_altitude' in sim:
                self.first_altitude.set(sim['first_altitude'])
            if 'second_altitude' in sim:
                self.second_altitude.set(sim['second_altitude'])
            if 'time_step' in sim:
                self.time_step.set(sim['time_step'])
            if 'max_time' in sim:
                self.max_time.set(sim['max_time'])
            if 'reefed' in sim:
                self.reefed.set(sim['reefed'])
    
    def export_parameters(self):
        """Export all parameters to XML file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Export Parameters"
            )
            
            if not filename:
                return
            
            params = self.get_parameters()
            
            # Create XML structure
            root = ET.Element("ParachuteSimulationParameters")
            
            # Add each parameter group
            for group_name, group_params in params.items():
                group_elem = ET.SubElement(root, group_name.title())
                for key, value in group_params.items():
                    ET.SubElement(group_elem, key).text = str(value)
            
            # Pretty print XML
            rough_string = ET.tostring(root, 'unicode')
            reparsed = xml.dom.minidom.parseString(rough_string)
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(reparsed.toprettyxml(indent="  "))
            
            messagebox.showinfo("Export Successful", f"Parameters exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export parameters: {str(e)}")
    
    def import_parameters(self):
        """Import parameters from XML file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                title="Import Parameters"
            )
            
            if not filename:
                return
            
            # Parse XML file
            tree = ET.parse(filename)
            root = tree.getroot()
            
            params = {}
            
            # Parse each group
            for group_elem in root:
                group_name = group_elem.tag.lower()
                group_params = {}
                
                for param_elem in group_elem:
                    key = param_elem.tag
                    value = param_elem.text
                    
                    # Convert to appropriate type
                    try:
                        if value.lower() in ['true', 'false']:
                            group_params[key] = value.lower() == 'true'
                        else:
                            group_params[key] = float(value)
                    except ValueError:
                        group_params[key] = value
                
                params[group_name] = group_params
            
            # Set the parameters
            self.set_parameters(params)
            
            messagebox.showinfo("Import Successful", f"Parameters imported from {filename}")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import parameters: {str(e)}")
    
    def validate_parameters(self):
        """Validate all parameters and return any errors"""
        errors = []
        
        # Validate rocket parameters
        if self.rocket_mass.get() <= 0:
            errors.append("Rocket mass must be positive")
        if self.rocket_diameter.get() <= 0:
            errors.append("Rocket diameter must be positive")
        if self.rocket_drag_coeff.get() <= 0:
            errors.append("Rocket drag coefficient must be positive")
        
        # Validate parachute parameters
        if self.parachute_diameter.get() <= 0:
            errors.append("Parachute diameter must be positive")
        if self.opening_time.get() < 0:
            errors.append("Opening time must be non-negative")
        if not (0 <= self.reefing_ratio.get() <= 1):
            errors.append("Reefing ratio must be between 0 and 1")
        if self.spill_hole_diameter.get() < 0:
            errors.append("Spill hole diameter must be non-negative")
        if self.spill_hole_diameter.get() >= self.parachute_diameter.get():
            errors.append("Spill hole diameter must be smaller than parachute diameter")
        if self.reefing_ratio.get()* self.parachute_diameter.get() <= self.spill_hole_diameter.get():
            errors.append("Reefed parachute diameter is smaller than spill hole diameter")
        
        # Validate simulation parameters
        if self.first_altitude.get() <= 0:
            errors.append("First event altitude must be positive")
        if self.sim_type.get() == "Dual Event" and self.second_altitude.get() <= 0:
            errors.append("Second event altitude must be positive")
        if self.sim_type.get() == "Dual Event" and self.second_altitude.get() >= self.first_altitude.get():
            errors.append("Second event altitude must be lower than first event altitude")
        if self.time_step.get() <= 0:
            errors.append("Time step must be positive")
        if self.max_time.get() <= 0:
            errors.append("Max time must be positive")
        
        return errors