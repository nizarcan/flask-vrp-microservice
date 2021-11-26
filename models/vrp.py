from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from errors import InvalidRequestError, NoSolutionError


class VRP:
    def __init__(self):
        """
        Initiating all attributes upon creating an instance
        """
        
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
        """
        In this method, payload gets destructured into 
        class elements for easier data access.
        """
        try:        
            self.vehicles = input_dict["vehicles"]
            self.jobs = input_dict["jobs"]
            self.time_matrix = input_dict["matrix"]
        except:
            raise InvalidRequestError

    def generate_model_data(self):
        """
        In this method, the raw data goes through
        the data prep to be fed to the model.

        Things to look out: 
        > This is a location-based model. In data prep phase, demands for same locations are pooled.
        > Since this is a location-based model, job-location pairs are kept for desired output format.
        > A return to starting point is not necessary for vehicles. Thus, a dummy node is created, its time
            to other nodes are set to 0 and set as the ending node for each vehicle. 
        """

        try:
            # `num_locations` counts the dummy node too.
            self.num_locations = len(self.time_matrix) + 1
            self.num_vehicles = len(self.vehicles)

            # Dummy node creation on the time matrix
            self.time_matrix = [distance_row + [0] for distance_row in self.time_matrix]
            self.time_matrix += [(self.num_locations) * [0]]

            # Vehicle capacities extracted
            self.vehicle_capacities = [vehicle["capacity"][0] for vehicle in self.vehicles]

            # Starting index are extracted from `self.vehicles` and `end_index` is set as the dummy node
            self.start_index = [vehicle["start_index"] for vehicle in self.vehicles]
            self.end_index = self.num_vehicles * [self.num_locations - 1]

            # Demands and service times are pooled w.r.t. location.
            # Upon pooling, location-job info is kept in a dictionary.
            self.demands = (self.num_locations) * [0]
            self.service_time = (self.num_locations) * [0]
            self.location_job_pair = {}
            for job in self.jobs:
                location_index = job["location_index"]
                self.demands[location_index] += job["delivery"][0]
                self.service_time[location_index] += job["service"]
                if location_index in self.location_job_pair.keys():
                    self.location_job_pair[location_index].append(job["id"])
                else:
                    self.location_job_pair[location_index] = [job["id"]]
        except:
            raise InvalidRequestError

    def time_callback(self, from_index, to_index):
        """
        Time callback for objective function.
        In the objective function that is going to be minimized,
        service times are included. 
        """

        from_node = self.routing_manager.IndexToNode(from_index)
        to_node = self.routing_manager.IndexToNode(to_index)
        return self.time_matrix[from_node][to_node] + self.service_time[to_node]

    def demand_callback(self, from_index):
        """
        The demand callback is for the only constraint to the model.
        """

        from_node = self.routing_manager.IndexToNode(from_index)
        return self.demands[from_node]

    def build_model(self):
        """
        The model object and route indexer is set 
        as an attribute in the object to be 
        later used in solution returning phase.         
        """

        try:
            self.routing_manager = pywrapcp.RoutingIndexManager(self.num_locations,
                                                                self.num_vehicles,
                                                                self.start_index,
                                                                self.end_index
                                                                )

            self.routing_model = pywrapcp.RoutingModel(self.routing_manager)

            transit_callback_index = self.routing_model.RegisterTransitCallback(self.time_callback)

            # Objective function of the model
            self.routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            demand_callback_index = self.routing_model.RegisterUnaryTransitCallback(self.demand_callback)

            # Adding the demand constraint to the model
            self.routing_model.AddDimensionWithVehicleCapacity(
                demand_callback_index,      # evaluator_index
                0,                          # max_slack, which is 0 for our case
                self.vehicle_capacities,    # vehicle capacity list
                True,                       # the cumulative value of met demand starts from 0
                "Capacity"                  # constraint name
                )
        except:
            raise InvalidRequestError

    def solve(self):
        """
        For solution strategy, `PATH_CHEAPEST_ARC` for first solution and 
        `GUIDED_LOCAL_SEARCH` for local search are used. For more, see; 
            https://developers.google.com/optimization/routing/routing_options?hl=en#first_sol_options
            https://developers.google.com/optimization/routing/routing_options?hl=en#local_search_options
        """

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.FromSeconds(1)

        self.solution = self.routing_model.SolveWithParameters(search_parameters)

    def return_solution(self):
        """
        Method that returns the solution at the structure stated in README.
        """

        if not self.solution:
            raise NoSolutionError
        else:    
            total_delivery_duration = 0
            routes = {}
            # Looping over every vehicle
            for vehicle_idx in range(self.num_vehicles):
                vehicle_jobs = []
                vehicle_delivery_duration = 0

                current_node = self.routing_model.Start(vehicle_idx)
                vehicle_id = self.vehicles[vehicle_idx]["id"]

                # Looping over every node in route of solution for selected vehicle
                while not self.routing_model.IsEnd(current_node):
                    next_node = self.solution.Value(self.routing_model.NextVar(current_node))
                    node_idx = self.routing_manager.IndexToNode(current_node)
                    
                    # If there is a job for specified location, then the jobs are added to the solution dictionary. 
                    if node_idx in self.location_job_pair.keys():
                        for job_id in self.location_job_pair[node_idx]:
                            vehicle_jobs.append(job_id)
                    vehicle_delivery_duration += self.routing_model.GetArcCostForVehicle(current_node, next_node, vehicle_idx)
                    current_node = next_node;

                total_delivery_duration += vehicle_delivery_duration
                routes[vehicle_id] = {
                    "jobs": vehicle_jobs,
                    "delivery_duration": vehicle_delivery_duration
                }

            solution_dict = {
                "total_delivery_duration": total_delivery_duration,
                "routes": routes
            }
            
            return solution_dict

    def flush_model(self):
        '''
        This method is added to fix a memory leak.
        Before addition of this method, `routing_model` attribute 
        prevented the garbage collector from collecting the object.
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
