from flask import Flask, jsonify


app = Flask(__name__)

HOST = "0.0.0.0"
PORT = 5000

@app.route("/")
def return_solution():
    return jsonify({"message": "solution will be here"})

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)