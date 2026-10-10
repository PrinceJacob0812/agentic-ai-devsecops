# Agentic AI DevSecOps & Supply Chain Security Pipeline

## Project overview
This project aims to build an intelligent DevSecOps CI/CD pipeline that scans application code, helps triage security findings with an AI agent, generates and validates a Software Bill of Materials (SBOM), and uses cryptographic signing and policy checks to protect software artifacts.

## Team responsibilities
- **M1 — Josmimol-baby:** DevSecOps & CI/CD — GitHub Actions, Docker, pipeline hardening, SBOM generation.
- **M2 — suravi29:** Agentic AI Security — AI-assisted SAST triage and security-test generation.
- **M3 — manpreet881449-arch:** Supply Chain Security — Cosign/Sigstore, dependency security, infrastructure-as-code and OPA policies.
- **M4 — PrinceJacob0812:** Security Platform & Red Team — sample application, SAST integration, common logging, dashboard, evaluation support and authorized red-team exercise.

## Week 1 status
- [x] Repository foundation and M4 feature branch created.
- [x] Python/Flask training app added with an intentionally vulnerable SQL query for controlled SAST testing.
- [x] Custom Semgrep training rule added.
- [x] GitHub Actions workflow added to produce a JSON SAST report artifact.
- [x] Common security event log schema proposed.
- [ ] Validate the workflow run and share its report with M2.
- [ ] Confirm common log fields with M1 and M2.

## Repository structure
```text
.
├── app/                     # Python/Flask training app
├── .github/workflows/       # CI workflows
├── .semgrep/rules.yml       # Custom Semgrep training rule
├── sast/                    # SAST handoff documentation and report location
├── logs/                    # Pipeline log documentation
├── docs/                    # Architecture, logging schema and handoff notes
├── dashboard/               # Dashboard implementation (later phase)
├── tests/                   # Application and security tests
├── .gitignore
└── README.md
```

## Local SAST scan
Install Python 3.12 or a compatible version, then run:

```bash
python -m pip install --upgrade semgrep
semgrep scan --config .semgrep/rules.yml app/
```

To run the training app locally:

```bash
python -m pip install -r app/requirements.txt
python app/app.py
```

Then open `http://127.0.0.1:5000/`. Keep it bound to loopback; do not expose it to a network.

## Security and safety
The app contains a deliberate SQL injection training example to test the SAST workflow. It is intentionally vulnerable and is for isolated local testing only. Do not deploy it to production or expose it publicly. Never commit credentials, tokens, private keys, or real sensitive data.

## Collaboration
- Keep `main` stable.
- Work on short-lived feature branches.
- Use clear, focused commit messages.
- Open pull requests and request review before merging.
- Coordinate pipeline ownership and interfaces with M1, M2 and M3 before merging overlapping changes.

## Current status
Week 1 implementation is in progress. The SAST workflow must run and its output must be checked before the M2 handoff is considered complete.
