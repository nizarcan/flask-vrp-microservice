from controllers.solver import solution_server
from flask import Flask


app = Flask(__name__)
HOST = "0.0.0.0"
PORT = 5000

app.route("/", methods=["POST"])(solution_server)

if __name__ == '__main__':
    from waitress import serve
    print(f"Serving on http://{HOST}:{PORT}")
    serve(app, host=HOST, port=PORT)
