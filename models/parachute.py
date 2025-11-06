from abc import ABC, abstractmethod
import math

class ParachuteModel(ABC):
    def __init__(self, projected_diameter, open_Cd = 1.5, reefing_ratio = None, spill_hole_diameter=None, opening_time=8):
        self.projected_diameter = projected_diameter
        self.open_Cd = open_Cd
        self.reefing_ratio = reefing_ratio
        self.spill_hole_diameter = spill_hole_diameter
        self.opening_time = opening_time 
    
    @property
    @abstractmethod
    def open_projected_area(self):
        pass

    @property
    def reefed_projected_area(self):
        return None
    
    @property
    def reefed_Cd(self):
        if self.reefing_ratio is not None:         
            return self.drag_area_ratio * self.open_Cd * self.open_projected_area / self.reefed_projected_area
        return None
    
    @property
    def drag_area_ratio(self):
        return None
            


class HemisphericalParachute(ParachuteModel):
    @property
    def open_projected_area(self):
        A = math.pi * (self.projected_diameter / 2) ** 2
        if self.spill_hole_diameter:
            A -= math.pi * (self.spill_hole_diameter / 2) ** 2
        return A
    
    @property
    def reefed_projected_area(self):
        if self.reefing_ratio is not None:
            A = math.pi * (self.projected_diameter * self.reefing_ratio / 2) ** 2
            if self.spill_hole_diameter:
                A -= math.pi * (self.spill_hole_diameter / 2) ** 2
            return A
        return None

    @property
    def drag_area_ratio(self):
        if self.reefing_ratio is not None:
            return 1.43*self.reefing_ratio - 0.12 # found empirically 
        
