import json
import os
import secrets

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

CSP_MODE_DEFAULT = os.environ.get("CSP_MODE", "0")

_csp_report_log = []


def _build_csp_header(mode, nonce=None):
    """Return the Content-Security-Policy header value for the given mode, or
    None when CSP is off. The nonce parameter is required for mode 2."""
    if mode == "1":
        return "default-src 'self'"
    if mode == "2":
        return f"default-src 'self'; script-src 'nonce-{nonce}'"
    if mode == "3":
        return None 
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cors-demo")
def cors_demo():
    return render_template("cors_demo.html")


@app.route("/csp-demo")
def csp_demo():
    mode  = request.args.get("mode", CSP_MODE_DEFAULT)
    nonce = secrets.token_urlsafe(16)

    resp = render_template("csp_demo.html", mode=mode, nonce=nonce)

    csp_value = _build_csp_header(mode, nonce)
    if mode == "3":
        report_only = (
            "default-src 'self'; "
            "report-uri /csp-report"
        )
        response = app.make_response(resp)
        response.headers["Content-Security-Policy-Report-Only"] = report_only
        return response

    if csp_value:
        response = app.make_response(resp)
        response.headers["Content-Security-Policy"] = csp_value
        return response

    return resp


@app.route("/csp-report", methods=["POST"])
def csp_report():
    body = request.get_json(force=True, silent=True) or {}
    _csp_report_log.append(body)
    return "", 204


@app.route("/csp-report/log")
def csp_report_log():
    return jsonify(_csp_report_log)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)