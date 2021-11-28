from models.vehicle import Vehicle
from errors import InvalidInputError

class VehicleCollection:
    def __init__(self, vehicle_list, location_count):
        try:
            # Initiate vehicle list
            self.vehicles = []
            for vehicle in vehicle_list:
                self.add(vehicle)

            # Vehicle capacities extracted
            self.capacities = [vehicle.capacity for vehicle in self.vehicles]

            # Starting index are extracted from `self.vehicles` and `end_index` is set as the dummy node
            self.start_index = [vehicle.start_idx for vehicle in self.vehicles]
            self.end_index = len(self) * [location_count - 1]
        except Exception:
            raise InvalidInputError

    def __len__(self):
        return len(self.vehicles)

    def __iter__(self):
        return iter(self.vehicles)

    def add(self, vehicle_data):
        new_vehicle = Vehicle(vehicle_data)
        self.vehicles.append(new_vehicle)
