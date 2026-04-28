#!/usr/bin/env python3
"""
Usage:
    python start.py                  # default (CORS disabled, CSP off)
    python start.py cors             # CORS enabled
    python start.py misconfig        # CORS misconfigured
    python start.py cors csp=1       # CORS enabled + CSP mode 1
"""
import os
import sys
import subprocess
import signal

root = os.path.dirname(os.path.abspath(__file__))
py   = sys.executable

args = set(sys.argv[1:])

csp_mode = "0"
for a in args:
    if a.startswith("csp="):
        csp_mode = a.split("=", 1)[1]

# Set directly on os.environ so Flask's debug reloader inherits them
# when it copies the environment to spawn its worker process.
os.environ["CORS_ENABLED"]   = "1" if "cors"      in args else "0"
os.environ["CORS_MISCONFIG"] = "1" if "misconfig" in args else "0"
os.environ["CSP_MODE"]       = csp_mode

print(f"Starting servers  CORS_ENABLED={os.environ['CORS_ENABLED']}  "
      f"CORS_MISCONFIG={os.environ['CORS_MISCONFIG']}  CSP_MODE={csp_mode}")
print("  http://frontend.local:8080")
print("  http://api.local:8081")
print("  http://evil.local:8082")
print("Press Ctrl+C to stop.\n")

procs = [
    subprocess.Popen([py, os.path.join(root, "api",      "server.py")]),
    subprocess.Popen([py, os.path.join(root, "frontend", "server.py")]),
    subprocess.Popen([py, os.path.join(root, "evil",     "server.py")]),
]

def stop(sig=None, frame=None):
    print("\nStopping servers...")
    for p in procs:
        p.terminate()

signal.signal(signal.SIGINT,  stop)
signal.signal(signal.SIGTERM, stop)

try:
    for p in procs:
        p.wait()
except Exception:
    stop()
