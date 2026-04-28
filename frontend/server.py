import os
import secrets

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

CSP_MODE_DEFAULT = os.environ.get("CSP_MODE", "0")
VALID_MODES      = {"0", "1", "2", "3"}

_csp_report_log = []


def _csp_header_for(mode, nonce):
    if mode == "1":
        return "Content-Security-Policy", "default-src 'self'"
    if mode == "2":
        return "Content-Security-Policy", f"default-src 'self'; script-src 'nonce-{nonce}'"
    if mode == "3":
        return (
            "Content-Security-Policy-Report-Only",
            "default-src 'self'; report-uri /csp-report",
        )
    return None, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cors-demo")
def cors_demo():
    return render_template("cors_demo.html")


@app.route("/csp-demo")
def csp_demo():
    mode = request.args.get("mode", CSP_MODE_DEFAULT)
    if mode not in VALID_MODES:
        mode = "0"
    nonce = secrets.token_urlsafe(16)

    header_name, header_value = _csp_header_for(mode, nonce)

    body = render_template(
        "csp_demo.html",
        mode=mode,
        nonce=nonce,
        csp_header_name=header_name,
        csp_header_value=header_value,
    )
    response = app.make_response(body)
    if header_name:
        response.headers[header_name] = header_value
    return response


@app.route("/csp-report", methods=["POST"])
def csp_report():
    body = request.get_json(force=True, silent=True) or {}
    _csp_report_log.append(body)
    return "", 204


@app.route("/csp-report/log")
def csp_report_log():
    return jsonify(_csp_report_log)


@app.route("/csp-report/clear", methods=["POST"])
def csp_report_clear():
    _csp_report_log.clear()
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
