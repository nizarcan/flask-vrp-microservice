from flask import request, jsonify
from models.vrp import VRP

def vrp_solver():
    model = VRP()
    model.load_data(request.json)
    model.generate_model_data()
    model.build_model()
    model.solve()
    solution_dict = model.return_solution()
    model.flush_model()
    return jsonify(solution_dict)
