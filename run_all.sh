#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
    echo ""
    echo "Stopping servers..."
    kill "$(jobs -p)" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Pass through env vars so callers can override modes, e.g.:
#   CORS_ENABLED=1 ./run_all.sh
CORS_ENABLED="${CORS_ENABLED:-0}" \
CORS_MISCONFIG="${CORS_MISCONFIG:-0}" \
    python "$ROOT/api/server.py" &

CSP_MODE="${CSP_MODE:-0}" python "$ROOT/frontend/server.py" &

python "$ROOT/evil/server.py" &

echo "Servers started:"
echo "  http://frontend.local:8080"
echo "  http://api.local:8081"
echo "  http://evil.local:8082"
echo ""
echo "Override modes:  CORS_ENABLED=1  CORS_MISCONFIG=1  CSP_MODE=1|2|3"
echo "Press Ctrl+C to stop all servers."

wait
