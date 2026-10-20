# Deployment instructions

Repository: https://github.com/shoumick-sudo/shoumickhassan
Branch: cxb-real-data-release (isolated from STP main-branch deployment)
Project directory: portal/cxb-intelligence
Runtime: Python; free Render web service; Singapore.

Build: `cd portal/cxb-intelligence && pip install -r requirements.txt && python -m pytest -q tests`
Start: `cd portal/cxb-intelligence && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set DATABASE_URL using the cxb_web role in the separate cxb_public database, through Render's secret environment configuration. Never put owner credentials in Render or any credentials in Git/Drive logs. Python 3.12 is selected through PYTHON_VERSION.

GET /health must return HTTP 200 and engine PostgreSQL / Neon; compare its release SHA-256 with data/release.json. Check the actual deploy status is live for the recorded commit before describing hosting as completed. Then open the page without authentication, test population, date, camp, sector, map layer and map camp filters, CSV/PDF/SVG exports, source links and narrow-screen layout.

Rollback is a code deployment action, not a database rollback. Version the release before refresh. The present loader targets this dedicated project only; do not repoint it at STP. Free hosting may sleep and require a cold start; no availability SLA is claimed.
