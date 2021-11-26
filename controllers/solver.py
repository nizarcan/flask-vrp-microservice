from flask import request, jsonify
from models.vrp import VRP

def vrp_solver():
    model = VRP(request.json)
    model.build_model()
    model.solve()
    return jsonify(model.return_solution())
