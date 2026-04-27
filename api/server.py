import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# Read once at startup; restart the server to change modes.
# CORS logic (flask-cors integration) is applied on top of these flags.
CORS_ENABLED  = os.environ.get("CORS_ENABLED",  "0") == "1"
CORS_MISCONFIG = os.environ.get("CORS_MISCONFIG", "0") == "1"


@app.route("/api/data")
def get_data():
    path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(path) as f:
        return jsonify(json.load(f))


@app.route("/api/private")
def get_private():
    return jsonify({"secret": "admin-token-xyz", "user": "admin"})


@app.route("/api/submit", methods=["POST", "OPTIONS"])
def submit():
    # OPTIONS handled explicitly so the preflight is visible in logs.
    if request.method == "OPTIONS":
        return "", 204
    data = request.get_json(silent=True)
    return jsonify({"status": "received", "echo": data})


@app.route("/api/cors-config")
def cors_config():
    if CORS_MISCONFIG:
        mode = "misconfig"
    elif CORS_ENABLED:
        mode = "enabled"
    else:
        mode = "disabled"
    return jsonify({"cors": mode})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
