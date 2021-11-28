from flask import request, jsonify
from models.vrp import VRP
from errors import InvalidInputError, NoSolutionError

def vrp_solver():
    try:
        model = VRP()
        model.load_data(request.json)
        model.build_model()
        model.solve()
        solution = model.get_solution()
        return jsonify(solution)
    except InvalidInputError:
        return jsonify({"message": "The request body did not have the appropriate structure. Please retry the request with a valid structure."}), 422
    except NoSolutionError:
        return jsonify({"message": "With the sent request body there were no feasible solution."}), 422
    except Exception:
        return jsonify({"message": "A unidentified problem occured."}), 500
