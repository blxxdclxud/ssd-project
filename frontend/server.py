import os

from flask import Flask, render_template

app = Flask(__name__)

# CSP_MODE is read per-request (not at startup) so the demo page can switch
# modes via query param without a server restart. Member 4 will extend this
# with nonce generation, report-uri handling, and actual header injection.
CSP_MODE_DEFAULT = os.environ.get("CSP_MODE", "0")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cors-demo")
def cors_demo():
    return render_template("cors_demo.html")


@app.route("/csp-demo")
def csp_demo():
    return render_template("csp_demo.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
