import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from utils.functions import get_resource_path



from .widgets import ScrollableText


class PlotPanel(ttk.Frame):
    """Panel for displaying simulation results and plots"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.plot_altitude = tk.BooleanVar(value=True)
        self.plot_acceleration = tk.BooleanVar(value=True) 
        self.plot_velocity = tk.BooleanVar(value=True)
        self.last_results = None
        self.tab_names = ['Time-Altitude', 'Recovery Drift']
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Control buttons
        self.setup_controls()
        
        # Results display
        self.setup_results_display()
        
        # Plot area (initially empty)
        self.setup_plot_area()
    
    def setup_controls(self):
        """Setup control buttons"""
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            control_frame, 
            text="Show External Plot", 
            command=self.show_external_plot
        ).pack(side=tk.LEFT, padx=5)
                
        ttk.Button(
            control_frame, 
            text="Clear Plot", 
            command=self.clear_plot
        ).pack(side=tk.LEFT, padx=5)
        
    def setup_plot_controls(self, parent_frame):
        """Setup plot control buttons in the specified parent frame"""
        plot_control_frame = ttk.Frame(parent_frame)
        plot_control_frame.pack(fill=tk.X, pady=5)
        
        # Add checkboxes for plot visibility
        ttk.Checkbutton(plot_control_frame, text="Altitude", 
                    variable=self.plot_altitude, 
                    command=self.refresh_plot).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(plot_control_frame, text="Acceleration", 
                    variable=self.plot_acceleration, 
                    command=self.refresh_plot).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(plot_control_frame, text="Velocity", 
                    variable=self.plot_velocity, 
                    command=self.refresh_plot).pack(side=tk.LEFT, padx=5)
    
    def setup_results_display(self):
        """Setup results text display"""
        results_frame = ttk.LabelFrame(self, text="Results", padding=10)
        results_frame.pack(fill=tk.X, pady=5)
        
        self.results_text = ScrollableText(results_frame, height=6, width=50)
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def setup_plot_area(self):
        """Setup embedded plot area with tabs"""
        self.notebook = ttk.Notebook(self, padding=10)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize lists
        self.tabs = []
        self.canvas = [None] * len(self.tab_names)
        self.toolbar = [None] * len(self.tab_names)
        self.figure = [None] * len(self.tab_names)
        self.placeholder_frames = [None] * len(self.tab_names)
        
        # Create tabs with placeholders
        for i, tab_name in enumerate(self.tab_names):
            tab = ttk.Frame(self.notebook)
            self.tabs.append(tab)
            self.notebook.add(tab, text=tab_name)
            
            # Create placeholder for each tab
            placeholder = self.setup_placeholder_for_tab(tab)
            self.placeholder_frames[i] = placeholder
        
        self.setup_plot_controls(self.tabs[0])  # Setup plot controls in the first tab
        
    def setup_placeholder_for_tab(self, parent_tab):
        """Setup placeholder content for a specific tab"""
        placeholder_frame = ttk.Frame(parent_tab)
        placeholder_frame.pack(fill=tk.BOTH, expand=True)
        
        try:

            image_path = get_resource_path("assets/RE_TRANS.png")  # Change this to your image path
            image = Image.open(image_path)
            image = image.resize((400, 400), Image.Resampling.LANCZOS)
            placeholder_image = ImageTk.PhotoImage(image)
            
            # Create label with image
            image_label = ttk.Label(placeholder_frame, image=placeholder_image)
            image_label.image = placeholder_image  # Keep a reference to prevent garbage collection
            image_label.pack(expand=True)
        except Exception as e:
            # Fallback if image loading fails
            print(f"Could not load placeholder image: {e}")
            fallback_label = ttk.Label(placeholder_frame, text="No Plot Data\n\nRun a simulation to see results here")
            fallback_label.pack(expand=True)
        
        return placeholder_frame 
    
    # TODO: Check what results are displayed
    def display_results(self, results):
        """Display simulation results"""
        self.last_results = results
        
        # Clear previous results
        self.results_text.clear()
        
        # Display key metrics
        text_content = []
        if results['Dual_Event'] == True:
            text_content.append("--- FIRST EVENT ---")
            text_content.append(f"Acceleration at First Event: {results['first_event_acceleration']:.2f} g")
            text_content.append(f"Velocity at First Event: {results['first_event_velocity']:.2f} m/s")
            text_content.append(f"Estimated Reefed Cd: {results['reefed_Cd']:.2f}")
            text_content.append("--- SECOND EVENT ---")
            text_content.append(f"Acceleration at Second Event: {results['second_event_acceleration']:.2f} g")

        text_content.append(f"Landing Velocity: {results['landing_velocity']:.2f} m/s")
        text_content.append(f"Unreefed Cd: {results['unreefed_Cd']:.2f}")

        # Calculate additional metrics
        text_content.append(f"Flight Time: {results['flight_time']:.2f} seconds")            
        text_content.append(f"--- ADDITIONAL METRICS ---")
        max_velocity = max(abs(v) for v in results['velocity'])
        max_acceleration = max(abs(a) for a in results['acceleration'])  
        text_content.append(f"Max Velocity: {max_velocity:.2f} m/s")
        text_content.append(f"Max Acceleration: {max_acceleration/9.81:.2f} g")
        
        text_content.append(f"Final Altitude: {results['altitude'][-1]:.2f} m")
        text_content.append(f"Max Altitude: {max(results['altitude']):.2f} m")
        self.results_text.set_text("\n".join(text_content))
    
    def display_error(self, error_message):
        """Display error message"""
        self.results_text.clear()
        self.results_text.append(f"Error: {error_message}")
    
    def show_external_plot(self):
        """Show plot in external matplotlib window"""
        if self.last_results is None:
            messagebox.showwarning("No Results", "Please run a simulation first.")
            return
        
        self._create_matplotlib_plot()
    
    def create_plots(self):
        """Show plot embedded in the GUI"""
        if self.last_results is None:
            messagebox.showwarning("No Results", "Please run a simulation first.")
            return
        
        self._create_main_plot()
        self._create_drift_plot()
    
    
    def clear_plot(self):
        """Clear all embedded plots and show placeholders"""
        for i in range(len(self.tabs)):
            self._clear_existing_plot(i)
            self._show_placeholder(i)

    def _create_matplotlib_plot(self):
        """Create external matplotlib plot"""
        fig, ax1 = plt.subplots(figsize=(12, 8))
        fig.subplots_adjust(right=0.75)
        
        self._plot_data(fig, ax1)
        
        plt.title('Parachute Simulation Results')
        plt.tight_layout()
        plt.show()

    
    def _create_main_plot(self):
        """Create embedded plot in the GUI"""
        # Clear any existing plot completely
        self._clear_existing_plot(0) 
        
        # Create new figure
        self.figure[0] = Figure(figsize=(10, 6), dpi=100)
        self.figure[0].subplots_adjust(right=0.75)
        
        ax1 = self.figure[0].add_subplot(111)
        self._plot_data(self.figure[0], ax1)
        self.figure[0].suptitle('Parachute Simulation Results')
        
        # Hide placeholder before showing plot
        self._hide_placeholder(0)
        # Create canvas and toolbar
        self.canvas[0] = FigureCanvasTkAgg(self.figure[0], self.tabs[0])
        self.canvas[0].draw()
        self.canvas[0].get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.toolbar[0] = NavigationToolbar2Tk(self.canvas[0], self.tabs[0])
        self.toolbar[0].update()
    
    def _create_drift_plot(self):
        """Create drift plot in the GUI"""
        # Clear any existing plot completely
        self._clear_existing_plot(1) 

        # Create new figure
        self.figure[1] = Figure(figsize=(10, 6), dpi=100)
        self.figure[1].subplots_adjust(right=0.75)
        ax1 = self.figure[1].add_subplot(111)

        # Get the drift data
        results = self.last_results
        velocities = sorted(results['drift'].keys())  # Ensure consistent order
        num_vels = len(velocities)

        # Generate colormap (green to red)
        colormap = cm.get_cmap('RdYlGn_r')  # Reversed RdYlGn: green (low) to red (high)
        colors = [colormap(i) for i in np.linspace(0, 1, num_vels)]

        # Plot each drift line with corresponding color
        for idx, vel in enumerate(velocities):
            alt, drift = zip(*results['drift'][vel])
            ax1.plot(drift, alt, label=f"{vel} m/s", color=colors[idx])

        ax1.set_xlabel('Drift (m)')
        ax1.set_ylabel('Altitude (m)')
        ax1.set_title('Recovery Drift')
        ax1.legend(title="Horizontal Velocity", bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Hide placeholder before showing plot
        self._hide_placeholder(1)
        
        # Create canvas and toolbar
        self.canvas[1] = FigureCanvasTkAgg(self.figure[1], self.tabs[1])
        self.canvas[1].draw()
        self.canvas[1].get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.toolbar[1] = NavigationToolbar2Tk(self.canvas[1], self.tabs[1])
        self.toolbar[1].update()

    def _clear_existing_plot(self, tab_index):
        """Clear existing plot elements for a specific tab"""
        if tab_index < len(self.canvas) and self.canvas[tab_index]:
            self.canvas[tab_index].get_tk_widget().destroy()
            self.canvas[tab_index] = None
        
        if tab_index < len(self.toolbar) and self.toolbar[tab_index]:
            self.toolbar[tab_index].destroy()
            self.toolbar[tab_index] = None
        
        if tab_index < len(self.figure) and self.figure[tab_index]:
            plt.close(self.figure[tab_index])
            self.figure[tab_index] = None

    def _hide_placeholder(self, tab_index):
        """Hide placeholder for a specific tab"""
        if (hasattr(self, 'placeholder_frames') and 
            tab_index < len(self.placeholder_frames) and 
            self.placeholder_frames[tab_index]):
            self.placeholder_frames[tab_index].pack_forget() 

    def _show_placeholder(self, tab_index):
        """Show placeholder for a specific tab"""
        if (hasattr(self, 'placeholder_frames') and 
            tab_index < len(self.placeholder_frames) and 
            self.placeholder_frames[tab_index]):
            self.placeholder_frames[tab_index].pack(fill=tk.BOTH, expand=True)
        else:
            # Create placeholder if it doesn't exist
            if tab_index < len(self.tabs):
                placeholder = self.setup_placeholder_for_tab(self.tabs[tab_index])
                if not hasattr(self, 'placeholder_frames'):
                    self.placeholder_frames = [None] * len(self.tabs)
                self.placeholder_frames[tab_index] = placeholder
        
    def refresh_plot(self):
        """Refresh the embedded plot with current visibility settings"""
        if self.last_results:
            # Force a complete recreation of the embedded plot
            self._create_main_plot()
            self._create_drift_plot()
    
    def _plot_data(self, fig, ax1):
        """Plot the simulation data on given axes"""
        results = self.last_results
        
        lines_all = []
        labels_all = []
        
        ax1.grid(True, alpha=0.3)
        if self.plot_altitude.get():
            # Plot altitude
            color = 'tab:red'
            line = ax1.plot(results['time'], results['altitude'], color=color, linewidth=2, label='Altitude')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Altitude (m)', color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            lines_all.extend(line)
            labels_all.append('Altitude')

        ax2, ax3 = None, None
        
        if self.plot_acceleration.get():
            # Plot acceleration on second y-axis
            ax2 = ax1.twinx()
            color = 'tab:blue'
            acceleration_g = [acc/9.81 for acc in results['acceleration']]
            line = ax2.plot(results['time'], acceleration_g, color=color, linewidth=2, label='Acceleration')
            ax2.set_ylabel('Acceleration (g)', color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            lines_all.extend(line)
            labels_all.append('Acceleration')
        
        if self.plot_velocity.get():
            # Plot velocity on third y-axis
            ax3 = ax1.twinx()
            color = 'tab:green'
            if ax2:  # If acceleration axis exists, offset velocity axis further
                ax3.spines['right'].set_position(('outward', 60))
            line = ax3.plot(results['time'], results['velocity'], color=color, linewidth=2, label='Velocity')
            ax3.set_ylabel('Velocity (m/s)', color=color)
            ax3.tick_params(axis='y', labelcolor=color)
            lines_all.extend(line)
            labels_all.append('Velocity')
        
        # Add legend only if there are plots
        if lines_all:
            ax1.legend(lines_all, labels_all, loc='upper right', bbox_to_anchor=(0.98, 0.98))
        
    # FIXME: Not Used!
    def export_plot(self, filename, dpi=300):
        """Export current plot to file"""
        if self.figure[0] is None:
            messagebox.showwarning("No Plot", "Please create a plot first.")
            return
        
        try:
            self.figure[0].savefig(filename, dpi=dpi, bbox_inches='tight')
            messagebox.showinfo("Export Successful", f"Plot exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export plot: {str(e)}")
    
    #FIXME: Not Used!
    def get_plot_data_summary(self):
        """Get summary of plot data for reporting"""
        if self.last_results is None:
            return None
        
        results = self.last_results
        
        return {
            'total_points': len(results['time']),
            'time_range': (min(results['time']), max(results['time'])),
            'altitude_range': (min(results['altitude']), max(results['altitude'])),
            'velocity_range': (min(results['velocity']), max(results['velocity'])),
            'acceleration_range': (min(results['acceleration']), max(results['acceleration'])),
            'landing_velocity': results['landing_velocity'],
            'flight_time': results['flight_time'],
            'drift': results['drift']
        }