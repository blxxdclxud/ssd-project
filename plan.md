# SSD Project Plan — CORS & CSP Proof of Concept

## Tech Stack

| Component | Choice | Why |
|---|---|---|
| API server | Python 3 + Flask | Minimal boilerplate, trivial to toggle headers on/off, `flask-cors` available |
| Frontend server | Python 3 + Flask | Same reason — need programmatic control over CSP response headers |
| "Attacker" page | Python 3 + Flask | Consistent, same codebase |
| Frontend pages | Vanilla HTML/JS (`fetch()`) | No abstractions hiding what the browser actually does |
| Data format | JSON | Standard, matches task requirement |
| Hostname resolution | `/etc/hosts` entries | No DNS needed |
| CORS library | `flask-cors` + raw manual headers | Show both the library approach AND what the raw headers look like |
| Package management | `pip` + `requirements.txt` | Standard, reproducible |
| Demo recording | Browser DevTools visible (OBS or built-in screen record) | Experts will want to see Console + Network tab |

---

## Project Structure

```
ssd-project/
├── requirements.txt
├── run_all.sh                  ← starts all 3 servers
├── etc_hosts.txt               ← lines to add to /etc/hosts
├── frontend/
│   ├── server.py               ← Flask, serves pages, applies CSP headers
│   └── templates/
│       ├── index.html
│       ├── cors_demo.html
│       └── csp_demo.html
├── api/
│   ├── server.py               ← Flask JSON API, CORS configurable
│   └── data.json
└── evil/
    ├── server.py               ← Flask, simulates attacker origin
    └── templates/
        └── attack.html
```

Hostnames:
- `frontend.local:8080`
- `api.local:8081`
- `evil.local:8082`

---

## Member 1 — Infrastructure & Project Skeleton

**Goal:** Everyone else can clone and run immediately. No one else sets up servers.

### Tasks

1. Create the full directory structure above.
2. Add to `/etc/hosts` (document in `etc_hosts.txt`):
   ```
   127.0.0.1  frontend.local
   127.0.0.1  api.local
   127.0.0.1  evil.local
   ```
3. Write `requirements.txt`:
   ```
   flask>=3.0
   flask-cors>=4.0
   ```
4. Write `run_all.sh` that launches all 3 servers in separate processes.
5. Implement `api/server.py` — base API server (CORS **off** by default, toggled via `CORS_ENABLED` env variable):
   - `GET /api/data` → returns `data.json`
   - `GET /api/private` → returns `{"secret": "admin-token-xyz"}` (used in CORS attack demo)
   - `POST /api/submit` → accepts JSON body, returns `{"status": "received"}` (triggers preflight)
   - `GET /api/cors-config` → returns what CORS mode is currently active (for demo clarity)
6. Write `api/data.json` with realistic-looking sample data (e.g., list of users/products).
7. Write base `frontend/server.py` that serves templates (CSP headers off by default, toggled by `CSP_ENABLED` env variable).
8. Write `frontend/templates/index.html` — landing page with links to both demo pages and a short description of each scenario.
9. Write `README.md` covering: how to install deps, how to add `/etc/hosts` entries, how to run.

### Deliverable
Running skeleton where all 3 servers start and `index.html` loads at `http://frontend.local:8080`.

---

## Member 2 — CORS: Same-Origin Policy & Default Blocked Behavior

**Goal:** Demonstrate and explain what the browser does *before* any CORS headers are added.

### Tasks

1. Implement `frontend/templates/cors_demo.html` split into sections:
   - **Section A:** same-origin request — show it works.
   - **Section B:** cross-origin GET to `api.local:8081/api/data` — show it fails when CORS is off.
   - **Section C:** cross-origin POST to `api.local:8081/api/submit` — show preflight fails.
   - Each section has a "Run" button, a live results box, and a console output mirror.
2. Write all JS using raw `fetch()` — catch errors and display them on-page so they are visible in the recording (not just buried in DevTools).
3. Add a visible banner that reads the current CORS mode from `GET /api/cors-config` and displays `CORS: OFF` / `CORS: ON`.
4. Document (inline in HTML or a linked `cors_background.md`) the explanation of:
   - What Same-Origin Policy is (scheme + host + port triple).
   - Why the browser enforces it (not the server).
   - What the browser error message means (`CORS policy: No 'Access-Control-Allow-Origin'`).
   - The difference between "simple" and "non-simple" requests.
5. Prepare 3–4 presentation slides covering SOP and the default blocked behavior, using exact error messages and DevTools screenshots from the demo.

### Deliverable
With `CORS_ENABLED=0`, the demo page clearly shows and explains blocked cross-origin requests. Presentation slides for the "what is SOP / default behavior" section.

---

## Member 3 — CORS: Headers, Configuration & Attack/Misconfiguration Scenarios

**Goal:** Demonstrate what enabling CORS does, how to configure it correctly, and what misconfiguration looks like.

### Tasks

1. Extend `api/server.py` with full CORS logic (triggered when `CORS_ENABLED=1`):
   - Use `flask-cors` for the proper configuration.
   - Add a manual raw-headers route (`/api/data-manual`) that sets headers by hand to show exactly what `Access-Control-Allow-Origin` etc. look like.
   - Configure: specific origin whitelist (`frontend.local:8080`), allowed methods, allowed headers, `max_age`.
   - Add `Access-Control-Allow-Credentials: true` variant on `/api/private`.
2. Add an explicit OPTIONS preflight handler:
   - Log each preflight to stdout so it is visible during the demo.
   - Return `Access-Control-Max-Age` and explain caching.
3. Implement `evil/templates/attack.html`:
   - Page at `evil.local:8082` that tries to `fetch()` `api.local:8081/api/private`.
   - With CORS off or correctly configured: shows "blocked".
   - With CORS misconfigured (`Access-Control-Allow-Origin: *` + `credentials: 'include'`): browser refuses — explain why `*` + credentials is invalid per spec.
   - Second attack variant: `Access-Control-Allow-Origin: evil.local:8082` (overly permissive whitelist).
4. Implement `evil/server.py`.
5. Add a CORS misconfiguration mode (`CORS_MISCONFIG=1`) to `api/server.py`:
   - Reflects the `Origin` header back blindly (allows any origin).
   - Show this lets `evil.local` steal data from the API.
6. Prepare 4–5 presentation slides: proper CORS flow diagram (request → preflight → actual request → response), misconfiguration consequences, the `*` + credentials paradox.

### Deliverable
With `CORS_ENABLED=1` the allowed origin works; with `CORS_MISCONFIG=1` the attack from `evil.local` succeeds; with correct config it is blocked. Presentation slides for the CORS configuration section.

---

## Member 4 — CSP: Default Behavior, Headers, Nonces & Report-Only

**Goal:** Demonstrate what the browser allows by default and what CSP progressively locks down.

### Tasks

1. Implement `frontend/templates/csp_demo.html` with 4 progressive demo scenarios:
   - **Scenario 0 (no CSP):** Inline `<script>` executes freely; external script from `evil.local` loads; simulated XSS payload (`alert('XSS')` or DOM write) runs — show this is dangerous.
   - **Scenario 1 (strict CSP):** Add `Content-Security-Policy: default-src 'self'` via `frontend/server.py` response header — inline script blocked, external script blocked, browser console shows `Refused to execute inline script`.
   - **Scenario 2 (nonce-based CSP):** `script-src 'nonce-<random>'` — server generates a nonce per request and injects it into the template; legitimate inline script with matching nonce runs, injected script without nonce is still blocked.
   - **Scenario 3 (report-only mode):** Switch header to `Content-Security-Policy-Report-Only` with a `report-uri /csp-report` endpoint — violations are reported (logged server-side) but not blocked; show the violation report JSON in the UI live.
2. Extend `frontend/server.py`:
   - Generate cryptographically random nonces per request (`secrets.token_urlsafe(16)`).
   - Accept `GET /csp-demo?mode=0|1|2|3` and return the page with the appropriate `Content-Security-Policy` header.
   - Implement `POST /csp-report` that receives and logs CSP violation reports.
   - Implement `GET /csp-report/log` that returns violation log as JSON so the demo page can display them live.
3. Add a `connect-src` sub-demo inside Scenario 1: show that `fetch()` to `evil.local` is blocked by CSP (in addition to CORS — explain they are independent, orthogonal mechanisms).
4. Add an `img-src` sub-demo: show a tracking pixel from `evil.local` being blocked.
5. Prepare 4–5 presentation slides: CSP header anatomy, directive hierarchy (`default-src` fallback), nonce flow diagram, report-only use case (gradual rollout), CSP vs CORS — CSP is a server-to-own-page policy; CORS is a server-to-other-origins policy.

### Deliverable
`csp_demo.html` with all 4 scenarios working. `CSP_ENABLED` env variable (or `?mode=` query param) controls the active scenario. Presentation slides for the full CSP section.

---

## Integration Points

| Member | Depends on | Provides to |
|---|---|---|
| M1 | — | M2, M3, M4 (all servers running) |
| M2 | M1 skeleton + `api/server.py` base routes | M3 (extends cors_demo.html) |
| M3 | M1, M2 | M4 (evil.local scripts for CSP img/script demos) |
| M4 | M1 frontend server | M3 (evil.local script for CSP connect-src demo) |

**Suggested order:** M1 finishes first (Day 1–2), then M2 + M3 + M4 work in parallel, final integration pass together before recording the demo.
