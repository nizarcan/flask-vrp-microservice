class Vehicle:
    def __init__(self, vehicle_data):
        """
        Deconstructing vehicle_data dictionary into `Vehicle` attributes
        """
        
        self.id = vehicle_data["id"]
        self.start_idx = vehicle_data["start_index"]
        self.capacity = vehicle_data["capacity"][0]
