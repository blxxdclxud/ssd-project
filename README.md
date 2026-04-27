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
