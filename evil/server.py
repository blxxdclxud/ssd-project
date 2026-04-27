import base64

from flask import Flask, render_template, Response

app = Flask(__name__)

_PIXEL_PNG = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhf"
    b"DwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@app.route("/")
def index():
    return render_template("attack.html")


@app.route("/evil.js")
def evil_js():
    """External script loaded by the CSP demo to test script-src enforcement."""
    js = (
        "(function () {"
        "  var el = document.getElementById('csp-external-script-result');"
        "  if (el) el.textContent = '[evil.js] External script from evil.local:8082 executed.';"
        "})();"
    )
    return Response(js, mimetype="application/javascript")


@app.route("/pixel.png")
def pixel():
    """Tracking pixel loaded by the CSP demo to test img-src enforcement."""
    return Response(_PIXEL_PNG, mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)
