from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from errors import InvalidRequestError, NoSolutionError
from models.vehicle_collection import VehicleCollection
from models.job_collection import JobCollection
from models.time_matrix import TimeMatrix


class VRP:
    def __init__(self):
        """
        Initiating all attributes upon creating an instance
        """
        
        # Input classes
        self.vehicles = None
        self.jobs = None
        self.times = None

        # Model instance and variables
        self.solution = None
        self.routing_manager = None
        self.routing_model = None

    def load_data(self, input_dict):
        """
        In this method, payload gets destructured into 
        class elements for easier data access.
        """
        try:
            self.times = TimeMatrix(input_dict["matrix"])
            self.vehicles = VehicleCollection(input_dict["vehicles"], len(self.times))
            self.jobs = JobCollection(input_dict["jobs"], len(self.times))
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
        return self.times.matrix[from_node][to_node] + self.jobs.service_times[to_node]

    def demand_callback(self, from_index):
        """
        The demand callback is for the only constraint to the model.
        """

        from_node = self.routing_manager.IndexToNode(from_index)
        return self.jobs.demands[from_node]

    def build_model(self):
        """
        The model object and route indexer is set 
        as an attribute in the object to be 
        later used in solution returning phase.         
        """

        try:
            self.routing_manager = pywrapcp.RoutingIndexManager(len(self.times),
                                                                len(self.vehicles),
                                                                self.vehicles.start_index,
                                                                self.vehicles.end_index
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
                self.vehicles.capacities,   # vehicle capacity list
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

        if not self.solution:
            self.flush_model()
            raise NoSolutionError


    def return_solution(self):
        """
        Method that returns the solution at the structure stated in README.
        """

        total_delivery_duration = 0
        routes = {}
        # Looping over every vehicle
        for vehicle_idx, vehicle in enumerate(self.vehicles):
            vehicle_jobs = []
            vehicle_delivery_duration = 0

            current_node = self.routing_model.Start(vehicle_idx)
            vehicle_id = vehicle.id

            # Looping over every node in route of solution for selected vehicle
            while not self.routing_model.IsEnd(current_node):
                next_node = self.solution.Value(self.routing_model.NextVar(current_node))
                node_idx = self.routing_manager.IndexToNode(current_node)
                
                # If there is a job for specified location, then the jobs are added to the solution dictionary. 
                if node_idx in self.jobs.reverse_map.keys():
                    for job_id in self.jobs.reverse_map[node_idx]:
                        vehicle_jobs.append(str(job_id))
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
        
        # self.flush_model()

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
    model.build_model()
    model.solve()
    print(model.return_solution())
