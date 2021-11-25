from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# todo: add input validity check
INPUT_KEYS = ["vehicles", "jobs", "matrix"]
VEHICLE_KEYS = ["id", "start_index", "capacity"]
JOB_KEYS = ["id", "location_index", "delivery", "service"]


class VRP:
    def __init__(self, input_json):
        self.vehicles = input_json["vehicles"]
        self.jobs = input_json["jobs"]
        self.time_matrix = input_json["matrix"]

        ############################################################################

        location_count = len(self.time_matrix)
        self.num_vehicles = len(self.vehicles)
        self.time_matrix = [distance_row + [0] for distance_row in input_json["matrix"]]
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

        ############################################################################

        self.solution = None
        self.routing_manager = None
        self.routing_model = None

    def build_model(self):
        self.routing_manager = pywrapcp.RoutingIndexManager(len(self.time_matrix),
                                                            len(self.vehicles),
                                                            self.start_index,
                                                            self.end_index
                                                            )

        self.routing_model = pywrapcp.RoutingModel(self.routing_manager)

        def time_callback(from_index, to_index):
            from_node = self.routing_manager.IndexToNode(from_index)
            to_node = self.routing_manager.IndexToNode(to_index)
            return self.time_matrix[from_node][to_node] + self.service_time[to_node]

        transit_callback_index = self.routing_model.RegisterTransitCallback(time_callback)

        self.routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        def demand_callback(from_index):
            from_node = self.routing_manager.IndexToNode(from_index)
            return self.demands[from_node]

        demand_callback_index = self.routing_model.RegisterUnaryTransitCallback(demand_callback)

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
            solution_dict = {}
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


if __name__ == "__main__":
    import json
    json_data = json.load(open("input.json", encoding="utf-8"))
    model = VRP(json_data)
    model.build_model()
    model.solve()
    print(model.return_solution())
