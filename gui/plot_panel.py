import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import Image, ImageTk


from .widgets import ScrollableText


class PlotPanel(ttk.Frame):
    """Panel for displaying simulation results and plots"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.last_results = None
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
    
    def setup_results_display(self):
        """Setup results text display"""
        results_frame = ttk.LabelFrame(self, text="Results", padding=10)
        results_frame.pack(fill=tk.X, pady=5)
        
        self.results_text = ScrollableText(results_frame, height=6, width=50)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_plot_area(self):
        """Setup embedded plot area"""
        self.plot_frame = ttk.LabelFrame(self, text="Plot", padding=10)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initially empty - plot will be added when requested
        self.canvas = None
        self.toolbar = None
        self.figure = None
        self.setup_placeholder()
    
    def setup_placeholder(self):
        """Setup placeholder content when no plot is showing"""
        self.placeholder_frame = ttk.Frame(self.plot_frame)
        self.placeholder_frame.pack(fill=tk.BOTH, expand=True)  
        # Load and resize image (replace with your image path)
        image_path = "assets/RE_TRANS.png"  # Change this to your image path
        image = Image.open(image_path)
        image = image.resize((400, 400), Image.Resampling.LANCZOS)
        self.placeholder_image = ImageTk.PhotoImage(image)
        
        # Create label with image
        image_label = ttk.Label(self.placeholder_frame, image=self.placeholder_image)
        image_label.pack(expand=True)
    
    # TODO: Check what results are displayed
    def display_results(self, results):
        """Display simulation results"""
        self.last_results = results
        
        # Clear previous results
        self.results_text.clear()
        
        # Display key metrics
        text_content = []
        text_content.append(f"Landing Velocity: {results['landing_velocity']:.2f} m/s")
        text_content.append(f"Flight Time: {results['flight_time']:.2f} seconds")
        if results['reefed_Cd'] not in (None, float('inf')):
            text_content.append(f"Estimated Reefed Cd: {results['reefed_Cd']:.2f}")

        
        # Calculate additional metrics
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
    
    def show_embedded_plot(self):
        """Show plot embedded in the GUI"""
        if self.last_results is None:
            messagebox.showwarning("No Results", "Please run a simulation first.")
            return
        
        self._create_embedded_plot()
    
    def clear_plot(self):
        """Clear the embedded plot"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        
        if self.figure:
            plt.close(self.figure)
            self.figure = None
        if hasattr(self, 'placeholder_frame'):
            self.placeholder_frame.destroy()
        self.setup_placeholder()

    def _create_matplotlib_plot(self):
        """Create external matplotlib plot"""
        fig, ax1 = plt.subplots(figsize=(12, 8))
        fig.subplots_adjust(right=0.75)
        
        self._plot_data(fig, ax1)
        
        plt.title('Parachute Simulation Results')
        plt.tight_layout()
        plt.show()
    
    def _create_embedded_plot(self):
        """Create embedded plot in the GUI"""
        # Clear any existing plot
        self.clear_plot()
        
        if hasattr(self, 'placeholder_frame'):
            self.placeholder_frame.destroy()

        # Create new figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.figure.subplots_adjust(right=0.75)
        
        ax1 = self.figure.add_subplot(111)
        
        self._plot_data(self.figure, ax1)
        
        self.figure.suptitle('Parachute Simulation Results')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
    
    def _plot_data(self, fig, ax1):
        """Plot the simulation data on given axes"""
        results = self.last_results
        
        # Plot altitude
        color = 'tab:red'
        ax1.plot(results['time'], results['altitude'], color=color, linewidth=2, label='Altitude')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Altitude (m)', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)
        
        # Plot acceleration on second y-axis
        ax2 = ax1.twinx()
        color = 'tab:blue'
        acceleration_g = [acc/9.81 for acc in results['acceleration']]
        ax2.plot(results['time'], acceleration_g, color=color, linewidth=2, label='Acceleration')
        ax2.set_ylabel('Acceleration (g)', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Plot velocity on third y-axis
        ax3 = ax1.twinx()
        color = 'tab:green'
        ax3.spines['right'].set_position(('outward', 60))
        ax3.plot(results['time'], results['velocity'], color=color, linewidth=2, label='Velocity')
        ax3.set_ylabel('Velocity (m/s)', color=color)
        ax3.tick_params(axis='y', labelcolor=color)
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        
        ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, 
                  loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # FIXME: Not Used!
    def export_plot(self, filename, dpi=300):
        """Export current plot to file"""
        if self.figure is None:
            messagebox.showwarning("No Plot", "Please create a plot first.")
            return
        
        try:
            self.figure.savefig(filename, dpi=dpi, bbox_inches='tight')
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
            'flight_time': results['flight_time']
        }