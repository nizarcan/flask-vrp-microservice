from flask import request, jsonify
from models.vrp import VRP
from errors import InvalidInputError, NoSolutionError

def vrp_solver(data):
    model = VRP()
    model.load_data(data)
    model.build_model()
    model.solve()
    return model.get_solution()

def solution_server():
    try:
        solution = vrp_solver(request.json)
        return jsonify(solution)
    except InvalidInputError:
        return jsonify({"message": "The request body did not have the appropriate structure. Please retry the request with a valid structure."}), 422
    except NoSolutionError:
        return jsonify({"message": "With the sent request body there were no feasible solution."}), 422
    except Exception:
        return jsonify({"message": "A unidentified problem occured."}), 500
