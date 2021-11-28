from errors import NoSolutionError
from models.vehicle_collection import VehicleCollection
from models.job_collection import JobCollection
from models.time_matrix import TimeMatrix
import wrappers.solver as VRPSolverWrapper


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
        class elements for easier data access. If the payload
        is not in desired structure, InvalidInputError is throwed.
        """

        self.times = TimeMatrix(input_dict["matrix"])
        self.vehicles = VehicleCollection(input_dict["vehicles"], len(self.times))
        self.jobs = JobCollection(input_dict["jobs"], len(self.times))

    def build_model(self):
        """
        The model object and route indexer is set 
        as an attribute in the object to be 
        later used in solution getting phase.         
        """

        self.routing_manager, self.routing_model = VRPSolverWrapper.generate_vrp_model(
            self.times,
            self.vehicles,
            self.jobs
        )

    def solve(self):

        self.solution = self.routing_model.SolveWithParameters(
            VRPSolverWrapper.get_search_parameters(
                len(self.times)
                )
            )

    def get_solution(self):
        """
        Method that returns the solution at the structure stated in README.
        """

        rendered_solution = VRPSolverWrapper.render_solution(self)

        self.flush_model()

        if not rendered_solution:
            raise NoSolutionError

        return rendered_solution

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
    print(model.get_solution())
