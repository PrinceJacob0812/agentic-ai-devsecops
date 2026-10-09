# Agentic AI DevSecOps & Supply Chain Security Pipeline

## Project overview
This project aims to build an intelligent DevSecOps CI/CD pipeline that scans application code, helps triage security findings with an AI agent, generates and validates a Software Bill of Materials (SBOM), and uses cryptographic signing and policy checks to protect software artifacts.

## Team responsibilities
- **M1 — DevSecOps & CI/CD:** GitHub Actions, Docker, pipeline hardening, SBOM generation.
- **M2 — Agentic AI Security:** AI-assisted SAST triage and security-test generation.
- **M3 — Supply Chain Security:** Cosign/Sigstore, dependency security, infrastructure-as-code and OPA policies.
- **M4 — Security Platform & Red Team:** Sample application, SAST integration, common logging, dashboard, evaluation support and authorized red-team exercise.

## Week 1 goals
- Agree on the sample application's language and scope.
- Prepare a sample application for controlled security testing.
- Integrate Semgrep and save machine-readable findings.
- Define a common JSON format for pipeline/security events.
- Coordinate the SAST handoff to M2.

## Planned repository structure
```text
.
├── app/                 # Sample application (team will choose Python or Node.js)
├── .github/workflows/   # CI workflows
├── sast/                # SAST configuration and sample outputs
├── logs/                # Example pipeline/security event logs
├── docs/                # Architecture and team documentation
├── dashboard/           # Dashboard implementation (later phase)
├── tests/               # Application and security tests
├── .gitignore
└── README.md
```

## Security and safety
The sample app is for controlled, local testing only. Do not deploy intentionally vulnerable code to a public or production environment. Never commit credentials, tokens, private keys, or real sensitive data.

## Collaboration
- Keep `main` stable.
- Work on short-lived feature branches.
- Use clear, focused commit messages.
- Open pull requests and request review before merging.
- Coordinate interfaces and file formats with the relevant team member before changing them.

## Current status
Repository foundation created. Week 1 implementation is in progress.
