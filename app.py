from controllers.solver import vrp_solver
from flask import Flask


app = Flask(__name__)
HOST = "0.0.0.0"
PORT = 5000

app.route("/", methods=["POST"])(vrp_solver)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)