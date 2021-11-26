from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class VRP:
    def __init__(self):
        # Initiating all attributes upon creating an instance
        # Raw input data #
        self.vehicles = None
        self.jobs = None
        self.time_matrix = None

        # Data to be generated for problem solving model #
        self.num_locations = None
        self.num_vehicles = None
        self.time_matrix = None
        self.time_matrix = None
        self.vehicle_capacities = None
        self.start_index = None
        self.end_index = None
        self.demands = None
        self.service_time = None
        self.location_job_pair = None

        # Model instance and variables #
        self.solution = None
        self.routing_manager = None
        self.routing_model = None

    def load_data(self, input_dict):
        # Destructure the data into class attributes
        self.vehicles = input_dict["vehicles"]
        self.jobs = input_dict["jobs"]
        self.time_matrix = input_dict["matrix"]

    def generate_model_data(self):
        location_count = len(self.time_matrix)
        self.num_vehicles = len(self.vehicles)
        self.time_matrix = [distance_row + [0] for distance_row in self.time_matrix]
        self.time_matrix += [(location_count + 1) * [0]]
        self.vehicle_capacities = [vehicle["capacity"][0] for vehicle in self.vehicles]
        self.start_index = [vehicle["start_index"] for vehicle in self.vehicles]
        self.end_index = self.num_vehicles * [location_count]

        self.demands = (location_count + 1) * [0]
        self.service_time = len(self.time_matrix) * [0]
        self.location_job_pair = {}
        for job in self.jobs:
            self.demands[job["location_index"]] += job["delivery"][0]
            self.service_time[job["location_index"]] += job["service"]
            if job["location_index"] in self.location_job_pair.keys():
                self.location_job_pair[job["location_index"]].append(job["id"])
            else:
                self.location_job_pair[job["location_index"]] = [job["id"]]

    def time_callback(self, from_index, to_index):
        from_node = self.routing_manager.IndexToNode(from_index)
        to_node = self.routing_manager.IndexToNode(to_index)
        return self.time_matrix[from_node][to_node] + self.service_time[to_node]

    def demand_callback(self, from_index):
        from_node = self.routing_manager.IndexToNode(from_index)
        return self.demands[from_node]

    def build_model(self):
        self.routing_manager = pywrapcp.RoutingIndexManager(len(self.time_matrix),
                                                            len(self.vehicles),
                                                            self.start_index,
                                                            self.end_index
                                                            )

        self.routing_model = pywrapcp.RoutingModel(self.routing_manager)

        transit_callback_index = self.routing_model.RegisterTransitCallback(self.time_callback)

        self.routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        demand_callback_index = self.routing_model.RegisterUnaryTransitCallback(self.demand_callback)

        self.routing_model.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            self.vehicle_capacities,
            True,
            "Capacity")

    def solve(self):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.FromSeconds(1)

        self.solution = self.routing_model.SolveWithParameters(search_parameters)

    def return_solution(self):
        if self.solution:
            solution_dict = {
                "total_delivery_duration": 0,
                "routes": {
                    vehicle["id"]: {
                    "jobs": [],
                    "delivery_duration": 0
                    } 
                for vehicle in self.vehicles}
                }
            solution_dict["total_delivery_duration"] = 0
            solution_dict["routes"] = {vehicle["id"]: {
                "jobs": [],
                "delivery_duration": 0
            } for vehicle in self.vehicles}

            for vehicle_idx in range(self.num_vehicles):
                current_node = self.routing_model.Start(vehicle_idx)
                vehicle_id = self.vehicles[vehicle_idx]["id"]
                while not self.routing_model.IsEnd(current_node):
                    next_node = self.solution.Value(self.routing_model.NextVar(current_node))
                    node_idx = self.routing_manager.IndexToNode(current_node)
                    if node_idx in self.location_job_pair.keys():
                        for job_id in self.location_job_pair[node_idx]:
                            solution_dict["routes"][vehicle_id]["jobs"].append(job_id)
                    solution_dict["routes"][vehicle_id]["delivery_duration"] += self.routing_model.GetArcCostForVehicle(current_node, next_node, vehicle_idx)
                    current_node = next_node;
                solution_dict["total_delivery_duration"] += solution_dict["routes"][vehicle_id]["delivery_duration"]
            
            return solution_dict

    def flush_model(self):
        '''
        This method is added to fix a memory leak.
        Prior to usage of this method, routing_model attribute prevented
        the garbage collector from collecting the whole object.
        '''
        self.routing_model = None


if __name__ == "__main__":
    import json
    json_data = json.load(open("data/sample_input.json", encoding="utf-8"))
    model = VRP()
    model.load_data(json_data)
    model.generate_model_data()
    model.build_model()
    model.solve()
    print(model.return_solution())
