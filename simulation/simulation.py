from abc import ABC, abstractmethod
import math

class SimulationEngine(ABC):
    GRAVITY = 9.81
    AIR_DENSITY = 1.124  # kg/m^3 
    
    def __init__(self, rocket, parachute, reefed=True):
        self.rocket = rocket
        self.parachute = parachute
        self.reefed = reefed
    
    def calculate_recovery_forces(self, Cd, area, velocity):
        drag_force = 0.5 * self.AIR_DENSITY * velocity**2 * Cd * area
        weight = self.rocket.mass * self.GRAVITY

        net_force = drag_force - weight  
        return net_force
    
    def store_state(self, times, altitudes, velocities, accelerations, time, altitude, velocity, acceleration):
        """Store current simulation state"""
        times.append(time)
        altitudes.append(altitude)
        velocities.append(velocity)
        accelerations.append(acceleration)
    
    def simulate_freefall_phase(self, altitude, velocity, time, time_step, times, altitudes, velocities, accelerations):
        """Simulate free fall until parachute deployment"""
        while altitude > 0 and time < self.parachute.opening_time:
            area = math.pi * (self.rocket.diameter / 2) ** 2
            Cd = self.rocket.drag_coefficient
            acceleration = self.calculate_recovery_forces(Cd, area, velocity) / self.rocket.mass
            self.store_state(times, altitudes, velocities, accelerations, time, altitude, velocity, acceleration)
            
            # Update state
            velocity += acceleration * time_step
            altitude += velocity * time_step
            time += time_step
        
        return altitude, velocity, time
    
    def simulate_parachute_phase(self, altitude, velocity, time, time_step, max_time, times, altitudes, velocities, accelerations, end_altitude=0):
        """Simulate parachute descent until landing"""
        while altitude > end_altitude and time < max_time:
            if self.reefed:
                if self.parachute.reefed_projected_area is None:
                    raise ValueError("Reefed parachute does not have a projected area defined. Check reefing ratio")
                area = self.parachute.reefed_projected_area
                Cd = self.parachute.reefed_Cd
            else:
                area = self.parachute.open_projected_area
                Cd = self.parachute.open_Cd

            acceleration = self.calculate_recovery_forces(Cd, area, velocity) / self.rocket.mass
            self.store_state(times, altitudes, velocities, accelerations, time, altitude, velocity, acceleration)
            
            # Update state
            velocity += acceleration * time_step
            altitude += velocity * time_step
            time += time_step
        
        return altitude, velocity, time
    
    @abstractmethod
    def simulate(self, initial_velocity=0.0, time_step=0.1, max_time=300):
        None


class SingleEventSimulation(SimulationEngine):
    def __init__(self, rocket, parachute, reefed, first_event_altitude):
        super().__init__(rocket, parachute, reefed)
        self.first_event_altitude = first_event_altitude
      
    def simulate(self, initial_velocity=0.0, time_step=0.1, max_time=300):
        """Run single event simulation with two phases"""
        # Initialize simulation state
        time = 0.0
        altitude = self.first_event_altitude
        velocity = initial_velocity
        
        # Storage for results
        times = []
        altitudes = []
        velocities = []
        accelerations = []
        
        # Phase 1: Free fall until parachute deployment
        altitude, velocity, time = self.simulate_freefall_phase(
            altitude, velocity, time, time_step, times, altitudes, velocities, accelerations
        )
        
        # Phase 2: Parachute descent until landing
        altitude, velocity, time = self.simulate_parachute_phase(
            altitude, velocity, time, time_step, max_time, times, altitudes, velocities, accelerations
        )

        return {
            'time': times,
            'altitude': altitudes,
            'velocity': velocities,
            'acceleration': accelerations,
            'landing_velocity': velocity,
            'flight_time': time,
            'reefed_Cd': self.parachute.reefed_Cd if self.reefed else None,
        }


class DualEventSimulation(SimulationEngine):
    def __init__(self, rocket, parachute, reefed, first_event_altitude, second_event_altitude):
        super().__init__(rocket, parachute, reefed)
        self.first_event_altitude = first_event_altitude
        self.second_event_altitude = second_event_altitude
      
    def simulate(self, initial_velocity=0.0, time_step=0.1, max_time=300):
        """Run single event simulation with two phases"""
        # Initialize simulation state
        time = 0.0
        altitude = self.first_event_altitude
        velocity = initial_velocity
        
        # Storage for results
        times = []
        altitudes = []
        velocities = []
        accelerations = []
        
        # Phase 1: Free fall until parachute deployment
        altitude, velocity, time = self.simulate_freefall_phase(
            altitude, velocity, time, time_step, times, altitudes, velocities, accelerations
        )
        
        # Phase 2: Reefed Parachute descent until landing
        self.reefed = True
        altitude, velocity, time = self.simulate_parachute_phase(
            altitude, velocity, time, time_step, max_time, times, altitudes, velocities, accelerations, end_altitude=self.second_event_altitude
        )

        # Phase 2: Unreefed parachute descent until landing
        self.reefed = False
        altitude, velocity, time = self.simulate_parachute_phase(
            altitude, velocity, time, time_step, max_time, times, altitudes, velocities, accelerations, end_altitude=0
        )
        
        return {
            'time': times,
            'altitude': altitudes,
            'velocity': velocities,
            'acceleration': accelerations,
            'landing_velocity': velocity,
            'flight_time': time,
            'reefed_Cd': self.parachute.reefed_Cd,
        }


