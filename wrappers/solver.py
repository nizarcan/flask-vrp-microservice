from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from errors import InvalidInputError


def get_search_parameters(node_count):
    """
    For solution strategy, `PATH_CHEAPEST_ARC` for first solution and 
    `GUIDED_LOCAL_SEARCH` for local search are used. For more, see; 
        https://developers.google.com/optimization/routing/routing_options?hl=en#first_sol_options
        https://developers.google.com/optimization/routing/routing_options?hl=en#local_search_options
    """

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    
    """
    There is a calculation for time limit of solving. After ~500 node 
    problem, 1 second starts to get insufficient, making the tool unable 
    to solve the problem, returning no solution. That is why, for every 
    500 nodes, another second is given for model. Of course the solving 
    time will be quadratic in time with increasing node amounts, but 
    unless the problem is gigantic, this solution here works fine for now. 
    """
    
    time_limit = node_count // 500 + 1
    search_parameters.time_limit.FromSeconds(time_limit)
    
    return search_parameters

def generate_vrp_model(times, vehicles, jobs):
    """
    This function serves `routing_manager` and `routing_model` to
    the VRP class. 
    
    The agruments of this function are instances of;
    > times:        TimeMatrix
    > vehicles:     VehicleCollection
    > jobs:         JobCollection

    In the function below the only case that or-tools throws 
    an error is when there is a size mismatch, which indicates 
    invalid input. That is why the function throws InvalidInputError. 
    """
    try:
        routing_manager = pywrapcp.RoutingIndexManager(len(times),
                                                    len(vehicles),
                                                    vehicles.start_index,
                                                    vehicles.end_index
                                                    )

        def time_callback(from_index, to_index):
            """
            Time callback for objective function.
            In the objective function that is going to be minimized,
            service times are included. 
            """

            from_node = routing_manager.IndexToNode(from_index)
            to_node = routing_manager.IndexToNode(to_index)
            return times.matrix[from_node][to_node] + jobs.service_times[to_node]

        def demand_callback(from_index):
            """
            The demand callback is for the only constraint to the model.
            """

            from_node = routing_manager.IndexToNode(from_index)
            return jobs.demands[from_node]

        routing_model = pywrapcp.RoutingModel(routing_manager)

        transit_callback_index = routing_model.RegisterTransitCallback(time_callback)

        # Objective function of the model
        routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        demand_callback_index = routing_model.RegisterUnaryTransitCallback(demand_callback)

        # Adding the demand constraint to the model
        routing_model.AddDimensionWithVehicleCapacity(
            demand_callback_index,      # evaluator_index
            0,                          # max_slack, which is 0 for our case
            vehicles.capacities,        # vehicle capacity list
            True,                       # the cumulative value of met demand starts from 0
            "Capacity"                  # constraint name
            )

        return routing_manager, routing_model
    except Exception:
        raise InvalidInputError

def render_solution(vrp_model):
    if vrp_model.solution:
        total_delivery_duration = 0
        routes = {}
        # Looping over every vehicle
        for vehicle_idx, vehicle in enumerate(vrp_model.vehicles):
            vehicle_jobs = []
            vehicle_delivery_duration = 0

            current_node = vrp_model.routing_model.Start(vehicle_idx)
            vehicle_id = vehicle.id

            # Looping over every node in route of solution for selected vehicle
            while not vrp_model.routing_model.IsEnd(current_node):
                next_node = vrp_model.solution.Value(vrp_model.routing_model.NextVar(current_node))
                node_idx = vrp_model.routing_manager.IndexToNode(current_node)
                
                # If there is a job for specified location, then the jobs are added to the solution dictionary. 
                if node_idx in vrp_model.jobs.reverse_map.keys():
                    for job_id in vrp_model.jobs.reverse_map[node_idx]:
                        vehicle_jobs.append(str(job_id))
                vehicle_delivery_duration += vrp_model.routing_model.GetArcCostForVehicle(current_node, next_node, vehicle_idx)
                current_node = next_node;

            total_delivery_duration += vehicle_delivery_duration
            routes[str(vehicle_id)] = {
                "jobs": vehicle_jobs,
                "delivery_duration": vehicle_delivery_duration
            }

        rendered_solution = {
            "total_delivery_duration": total_delivery_duration,
            "routes": routes
        }

    return rendered_solution if vrp_model.solution else None
