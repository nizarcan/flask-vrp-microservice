from flask import request, jsonify
from models.vrp import VRP
from errors import InvalidRequestError, NoSolutionError

def vrp_solver():
    try:
        model = VRP()
        model.load_data(request.json)
        model.generate_model_data()
        model.build_model()
        model.solve()
        solution_dict = model.return_solution()
        model.flush_model()
        return jsonify(solution_dict)
    except InvalidRequestError:
        return jsonify({"message": "The request body did not have the appropriate structure. Please retry the request with a valid structure."}), 422
    except NoSolutionError:
        return jsonify({"message": "With the sent request body there were no feasible solution."}), 422
    except Exception:
        return jsonify({"message": "A unidentified problem occured."}), 500
