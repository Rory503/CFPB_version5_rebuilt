Deploying the CFPB Consumer Complaint Dashboard

One‑Click Render Deploy
- Click: https://render.com/deploy?repo=https://github.com/Rory503/CFPB_VERSION5/tree/restore-website
- Render reads `render.yaml` and sets everything up automatically.

Streamlit Community Cloud
- New app → Repo `Rory503/CFPB_VERSION5`, Branch `restore-website`
- Main file: `web_dashboard.py`
- Python: 3.11 (picked up from `runtime.txt`)

Notes
- Do not commit large datasets. The app downloads the official CFPB ZIP at runtime.
- Root directory is the repo root `./`.
