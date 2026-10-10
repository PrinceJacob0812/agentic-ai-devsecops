# Python sample application

This Flask app contains a deliberate SQL query string-concatenation issue so the team can validate SAST detection in a controlled environment.

## Run locally
From the repository root:

```bash
python -m pip install -r app/requirements.txt
python app/app.py
```

Visit `http://127.0.0.1:5000/`. The app binds to loopback only.

## Safety
This app is intentionally vulnerable. Use only for local training and security scanning. Never deploy it, expose it to an untrusted network, or use real data. The SQL query should be replaced with a parameterized query in production code.

M4 Week 1 handoff: share the app and the Semgrep JSON report with M2 for AI-triage development.
