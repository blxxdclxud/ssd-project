import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

CORS_ENABLED   = os.environ.get("CORS_ENABLED",   "0") == "1"
CORS_MISCONFIG = os.environ.get("CORS_MISCONFIG",  "0") == "1"

ALLOWED_ORIGIN = "http://frontend.local:8080"

if CORS_ENABLED:
    from flask_cors import CORS
    CORS(
        app,
        origins=[ALLOWED_ORIGIN],
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
        max_age=3600,
    )


@app.before_request
def log_preflight():
    if request.method == "OPTIONS":
        print(
            f"[PREFLIGHT] OPTIONS {request.path}"
            f"  origin={request.headers.get('Origin', '-')}"
            f"  req-method={request.headers.get('Access-Control-Request-Method', '-')}"
            f"  req-headers={request.headers.get('Access-Control-Request-Headers', '-')}",
            flush=True,
        )


@app.after_request
def cors_misconfig_hook(response):
    if not CORS_MISCONFIG:
        return response
    
    origin = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Origin"]      = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"]     = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"]     = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"]           = "3600"
    return response


@app.route("/api/data")
def get_data():
    path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(path) as f:
        return jsonify(json.load(f))


@app.route("/api/data-manual", methods=["GET", "OPTIONS"])
def get_data_manual():
    """Same data as /api/data but CORS headers are written by hand, not via flask-cors.
    Used in the demo to show the raw header names and values explicitly."""
    if request.method == "OPTIONS":
        resp = app.make_response("")
        resp.status_code = 204
        if CORS_ENABLED:
            resp.headers["Access-Control-Allow-Origin"]  = ALLOWED_ORIGIN
            resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
            resp.headers["Access-Control-Max-Age"]       = "3600"
        return resp

    path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(path) as f:
        resp = jsonify(json.load(f))
    if CORS_ENABLED:
        resp.headers["Access-Control-Allow-Origin"]      = ALLOWED_ORIGIN
        resp.headers["Access-Control-Allow-Methods"]     = "GET, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"]     = "Content-Type"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


@app.route("/api/private")
def get_private():
    return jsonify({"secret": "admin-token-xyz", "user": "admin"})


@app.route("/api/submit", methods=["POST", "OPTIONS"])
def submit():
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
