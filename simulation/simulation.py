from abc import ABC, abstractmethod
import math

class SimulationEngine(ABC):
    GRAVITY = 9.81
    AIR_DENSITY = 1.124  # kg/m^3 
    
    def __init__(self, rocket, parachute, reefed=True, initial_velocity=0.0, time = 0.0, time_step = 0.001, max_time=300, drift_time_step=1):
        # --- Configuration / Input parameters ---
        self.rocket = rocket
        self.parachute = parachute
        self.reefed = reefed
        self.time = time
        self.time_step = time_step
        self.max_time = max_time

        # --- Initial state ---
        self.altitude = None  # to be set in derived classes
        self.velocity = initial_velocity
        self.acceleration = -self.GRAVITY  # assuming GRAVITY is defined in the class

        # --- Time-series tracking ---
        self.times = []
        self.altitudes = []
        self.velocities = []
        self.accelerations = []

        # --- Drift simulation parameters ---
        self.max_drift_velocity = 20     # m/s
        self.drift_time_step = drift_time_step  # seconds
        self.drift_velocity_step = 2     # m/s
        self.drift = self.generate_drift_dict()
        self.step_count = 0

    def generate_drift_dict(self):
        """Generate a dictionary with drift velocities as keys and [0] as values."""
        drift_dict = {}
        for velocity in range(0, self.max_drift_velocity + 1, self.drift_velocity_step):
            drift_dict[velocity] = [[self.altitude, 0.0]]
        return drift_dict
    
    def calculate_recovery_forces(self, Cd, area):
        drag_force = 0.5 * self.AIR_DENSITY * self.velocity**2 * Cd * area
        weight = self.rocket.mass * self.GRAVITY
        net_force = drag_force - weight  
        return net_force
    
    def store_state(self):
        """Store current simulation state"""
        self.times.append(self.time)
        self.altitudes.append(self.altitude)
        self.velocities.append(self.velocity)
        self.accelerations.append(self.acceleration)
    
    def simulate_drift_step(self):
        """Simulate drift based on wind velocities"""
        if self.step_count % int(round(self.drift_time_step / self.time_step)) == 0 : 
            for wind_velocity in self.drift.keys():
                old_position = self.drift[wind_velocity][-1][1]
                new_position = old_position + wind_velocity * self.drift_time_step
                self.drift[wind_velocity].append([self.altitude,new_position])


    def update_state(self):
        """Update the state of the simulation"""
        self.altitude += self.velocity * self.time_step
        self.velocity += self.acceleration * self.time_step
        self.time += self.time_step
        self.step_count += 1
        

    def simulate_freefall_phase(self):
        """Simulate free fall until parachute deployment"""
        while self.altitude > 0 and self.time < self.parachute.opening_time and self.time < self.max_time:
            self.simulate_drift_step()
            area = math.pi * (self.rocket.diameter / 2) ** 2
            Cd = self.rocket.drag_coefficient
            self.acceleration = self.calculate_recovery_forces(Cd, area) / self.rocket.mass
            self.store_state()
            self.update_state()
        
        return self.altitude, self.velocity, self.time
    
    def simulate_parachute_phase(self, end_altitude=0):
        """Simulate parachute descent until landing"""
        while self.altitude > end_altitude and self.time < self.max_time:
            self.simulate_drift_step()
            if self.reefed:
                if self.parachute.reefed_projected_area is None:
                    raise ValueError("Reefed parachute does not have a projected area defined. Check reefing ratio")
                area = self.parachute.reefed_projected_area
                Cd = self.parachute.reefed_Cd
            else:
                area = self.parachute.open_projected_area
                Cd = self.parachute.open_Cd

            self.acceleration = self.calculate_recovery_forces(Cd, area) / self.rocket.mass
            self.store_state()           
            self.update_state()
        
        return self.altitude, self.velocity, self.time
    
    @abstractmethod
    def simulate(self):
        None


class SingleEventSimulation(SimulationEngine):
    def __init__(self, rocket, parachute, first_event_altitude, reefed=True, initial_velocity=0.0, time = 0.0, time_step = 0.001, max_time=300, drift_time_step = 1):
        super().__init__(rocket, parachute, reefed, initial_velocity, time, time_step, max_time, drift_time_step)
        self.altitude = first_event_altitude
      
    def simulate(self):
        """Run single event simulation with two phases"""       
        # Phase 1: Free fall until parachute deployment
        self.simulate_freefall_phase()
        
        # Phase 2: Parachute descent until landing
        self.simulate_parachute_phase()
        return {
            'time': self.times,
            'altitude': self.altitudes,
            'velocity': self.velocities,
            'acceleration': self.accelerations,
            'landing_velocity': self.velocity,
            'flight_time': self.time,
            'reefed_Cd': self.parachute.reefed_Cd if self.reefed else None,
            'drift': self.drift
        }


class DualEventSimulation(SimulationEngine):
    def __init__(self, rocket, parachute, first_event_altitude, second_event_altitude, reefed=True, initial_velocity=0.0, time = 0.0, time_step = 0.001, max_time=300, drift_time_step = 1):
        super().__init__(rocket, parachute, reefed, initial_velocity, time, time_step, max_time, drift_time_step)
        self.altitude = first_event_altitude
        self.second_event_altitude = second_event_altitude
      
    def simulate(self, initial_velocity=0.0, time_step=0.1, max_time=300):
        """Run dual event simulation with three phases"""
        # Phase 1: Free fall until parachute deployment
        self.simulate_freefall_phase()
        
        # Phase 2: Reefed Parachute descent until landing
        self.reefed = True
        self.simulate_parachute_phase(end_altitude=self.second_event_altitude)

        # Phase 2: Unreefed parachute descent until landing
        self.reefed = False
        self.simulate_parachute_phase()
        
        return {
            'time': self.times,
            'altitude': self.altitudes,
            'velocity': self.velocities,
            'acceleration': self.accelerations,
            'landing_velocity': self.velocity,
            'flight_time': self.time,
            'reefed_Cd': self.parachute.reefed_Cd,
            'drift': self.drift
        }


