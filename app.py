from flask import Flask, jsonify, request
from models.vrp import VRP


app = Flask(__name__)
HOST = "0.0.0.0"
PORT = 5000

@app.route("/", methods=["POST"])
def return_solution():
    model = VRP(request.json)
    model.build_model()
    model.solve()
    return jsonify(model.return_solution())

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)