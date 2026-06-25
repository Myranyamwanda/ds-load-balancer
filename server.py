import os
from flask import Flask, jsonify

app = Flask(__name__)

# The assignment requires tracking container instances using a Server ID
SERVER_ID = os.environ.get("SERVER_ID", "Unknown")


@app.route("/home", methods=["GET"])
def home():
    # Returns a unique identifier to distinguish the container instances
    response = {
        "message": f"Hello from Server: {SERVER_ID}",
        "status": "successful",
    }
    return jsonify(response), 200


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    # Returns an empty response with a 200 status code for the load balancer health checks
    return "", 200


if __name__ == "__main__":
    # The server must accept HTTP requests on port 5000
    app.run(host="0.0.0.0", port=5000)