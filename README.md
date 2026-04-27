# CORS & CSP Proof of Concept

A minimal three-origin HTTP environment for demonstrating CORS and CSP browser security mechanisms.

## Architecture

| Server | Origin | Purpose |
|--------|--------|---------|
| Frontend | `http://frontend.local:8080` | Demo pages served to the browser |
| API | `http://api.local:8081` | JSON API (the target resource) |
| Evil | `http://evil.local:8082` | Simulated attacker origin |

All three hostnames resolve to `127.0.0.1` via `/etc/hosts`.

## Setup

### 1. Python environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Local hostname resolution

Append the contents of `etc_hosts.txt` to your system hosts file:

- **Linux / macOS:** `sudo tee -a /etc/hosts < etc_hosts.txt`
- **Windows:** edit `C:\Windows\System32\drivers\etc\hosts` as Administrator

### 3. Run

```bash
./run_all.sh
```

Open `http://frontend.local:8080` in your browser.

## Demo modes

All modes are set as environment variables and require a server restart to take effect.

| Variable | Values | Effect |
|----------|--------|--------|
| `CORS_ENABLED` | `0` (default), `1` | Enable correct CORS on the API |
| `CORS_MISCONFIG` | `0` (default), `1` | Enable misconfigured CORS (reflects any origin) |
| `CSP_MODE` | `0`–`3` | `0`=off, `1`=strict, `2`=nonce-based, `3`=report-only |

Example:
```bash
CORS_ENABLED=1 ./run_all.sh
```
