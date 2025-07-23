from abc import ABC, abstractmethod
import math

class SimulationEngine(ABC):
    GRAVITY = - 9.81
    AIR_DENSITY = 1.124  # kg/m^3 
    
    def __init__(self, rocket, parachute, reefed=True, initial_velocity=0.0, time = 0.0, time_step = 0.001, max_time=300, drift_time_step=1, launch_angle=90):
        # --- Configuration / Input parameters ---
        self.rocket = rocket
        self.parachute = parachute
        self.reefed = reefed
        self.time = time
        self.time_step = time_step
        self.max_time = max_time
        self.launch_angle = launch_angle * math.pi/180

        # --- Initial state ---
        self.altitude = None  # to be set in derived classes
        self.vvelocity = initial_velocity
        self.hvelocity = 0.0
        # self.vacceleration = self.GRAVITY  # assuming GRAVITY is defined in the class
        # self.hacceleration = 0.0
        self.parachute_force = 0.0
        # self.acceleration = -self.GRAVITY

        # --- Time-series tracking ---
        self.times = []
        self.altitudes = []
        self.vvelocities = []
        self.hvelocities = []
        self.velocities = []
        self.accelerations = []

        # --- Drift simulation parameters ---
        self.max_drift_velocity = 20     # m/s
        self.drift_time_step = drift_time_step  # seconds
        self.drift_velocity_step = 2     # m/s
        self.drift = self.generate_drift_dict()
        self.step_count = 0
    
    @property
    def velocity(self):
        """Calculate the total velocity of the rocket."""
        try:
            return  math.sqrt(self.vvelocity**2 + self.hvelocity**2)
        except:
            raise ValueError("Error calculating velocity.Try reducing time step")
    
    @property
    def flight_angle(self):
        """Calculate flight angle based on vertical and horizontal velocities. -> Angle from horizontal axis."""
        if self.hvelocity == 0:
            return - math.pi / 2
        return math.atan2(self.vvelocity, self.hvelocity)

    @property
    def acceleration(self):
        """total acceleration magnitude"""
        return math.sqrt(self.vacceleration**2 + self.hacceleration**2)  
    
    @property
    def vacceleration(self):
        """Vertical acceleration"""
        return math.sin(abs(self.flight_angle)) * self.parachute_force + self.GRAVITY
    
    @property
    def hacceleration(self):
        """Horizontal acceleration"""
        return round(math.cos(abs(self.flight_angle)) * self.parachute_force, 10)


    
    def get_initial_horizontal_velocity(self):
        """Set the horizontal velocity of the rocket at parachute opening. Neglecting friction and wind."""
        Vv = math.sqrt(2 * abs(self.GRAVITY) * self.altitude)  # vertical velocity at launch
        if self.launch_angle == math.pi / 2:
            return 0.0
        Vh = Vv / math.tan(self.launch_angle)  # horizontal velocity
        return Vh
        
    def generate_drift_dict(self):
        """Generate a dictionary with drift velocities as keys and [0] as values."""
        drift_dict = {}
        for velocity in range(0, self.max_drift_velocity + 1, self.drift_velocity_step):
            drift_dict[velocity] = [[self.altitude, 0.0]]
        return drift_dict
    
    def calculate_parachute_force(self, Cd, area):
        return 0.5 * self.AIR_DENSITY * self.velocity**2 * Cd * area
    
    def store_state(self):
        """Store current simulation state"""
        self.times.append(self.time)
        self.altitudes.append(self.altitude)
        self.velocities.append(self.velocity)
        self.accelerations.append(self.acceleration)
        self.vvelocities.append(self.vvelocity)
        self.hvelocities.append(self.hvelocity)
    
    def simulate_drift_step(self):
        """Simulate drift based on wind velocities"""
        if self.step_count % int(round(self.drift_time_step / self.time_step)) == 0 : 
            for wind_velocity in self.drift.keys():
                old_position = self.drift[wind_velocity][-1][1]
                new_position = old_position + wind_velocity * self.drift_time_step
                self.drift[wind_velocity].append([self.altitude,new_position])


    def update_state(self):
        """Update the state of the simulation"""

        self.vvelocity += self.vacceleration * self.time_step
        self.hvelocity -= self.hacceleration * self.time_step
        self.altitude += self.vvelocity * self.time_step
        self.time += self.time_step
        self.step_count += 1
        

    def simulate_freefall_phase(self):
        """Simulate free fall until parachute deployment"""
        area = math.pi * (self.rocket.diameter / 2) ** 2
        Cd = self.rocket.drag_coefficient
        while self.altitude > 0 and self.time < self.parachute.opening_time and self.time < self.max_time:
            self.simulate_drift_step()  
            self.parachute_force = self.calculate_parachute_force(Cd, area) / self.rocket.mass
            # self.hacceleration = round(math.cos(abs(self.flight_angle)) * self.parachute_force, 10)
            # self.vacceleration = math.sin(abs(self.flight_angle)) * parachute_force + self.GRAVITY
            # self.acceleration = math.sqrt(self.vacceleration**2 + self.hacceleration**2)  # total acceleration magnitude
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

            self.parachute_force = self.calculate_parachute_force(Cd, area) / self.rocket.mass
            # self.hacceleration = round(math.cos(abs(self.flight_angle)) * self.parachute_force, 10)
            # self.vacceleration = math.sin(abs(self.flight_angle)) * self.parachute_force + self.GRAVITY
            # self.acceleration = math.sqrt(self.vacceleration**2 + self.hacceleration**2)  # total acceleration magnitude

            self.store_state()           
            self.update_state()
        
        return self.altitude, self.velocity, self.time
    
    @abstractmethod
    def simulate(self):
        None


class SingleEventSimulation(SimulationEngine):
    def __init__(self, rocket, parachute, first_event_altitude, **kwargs):
        super().__init__(rocket, parachute, **kwargs)
        self.altitude = first_event_altitude
        self.hvelocity = self.get_initial_horizontal_velocity()  # Set initial horizontal velocity
      
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
            'vvelocity': self.vvelocities,
            'hvelocity': self.hvelocities,
            'acceleration': self.accelerations,
            'landing_velocity': self.velocity,
            'flight_time': self.time,
            'reefed_Cd': self.parachute.reefed_Cd if self.reefed else None,
            'drift': self.drift
        }


class DualEventSimulation(SimulationEngine):
    def __init__(self, rocket, parachute, first_event_altitude, second_event_altitude, **kwargs):
        super().__init__(rocket, parachute, **kwargs)
        self.altitude = first_event_altitude
        self.second_event_altitude = second_event_altitude
        self.hvelocity = self.get_initial_horizontal_velocity()  # Set initial horizontal velocity
        print("Initial horizontal velocity:", self.velocity)

      
    def simulate(self, initial_velocity=0.0, time_step=0.1, max_time=300):
        """Run dual event simulation with three phases"""
        # Phase 1: Free fall until parachute deployment
        self.simulate_freefall_phase()
        print("Free fall phase completed. Current altitude:", self.altitude, "Current velocity:", self.velocity, "Time:", self.time)
        
        # Phase 2: Reefed Parachute descent until landing
        self.reefed = True
        self.simulate_parachute_phase(end_altitude=self.second_event_altitude)
        print("Reefed parachute phase completed. Current altitude:", self.altitude, "Current velocity:", self.velocity, "Time:", self.time)

        # Phase 2: Unreefed parachute descent until landing
        self.reefed = False
        self.simulate_parachute_phase()
        print("Unreefed parachute phase completed. Current altitude:", self.altitude, "Current velocity:", self.velocity, "Time:", self.time)
        
        return {
            'time': self.times,
            'altitude': self.altitudes,
            'velocity': self.velocities,
            'vvelocity': self.vvelocities,
            'hvelocity': self.hvelocities,
            'acceleration': self.accelerations,
            'landing_velocity': self.velocity,
            'flight_time': self.time,
            'reefed_Cd': self.parachute.reefed_Cd,
            'drift': self.drift
        }


