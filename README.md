# Agentic AI DevSecOps & Supply Chain Security Pipeline

## Project Overview

This project aims to build an intelligent DevSecOps CI/CD pipeline that automates application security scanning, AI-assisted vulnerability analysis, security-test generation, SBOM management, and software supply chain protection.

It integrates security tools and AI capabilities into the software development lifecycle to identify vulnerabilities, reduce manual security review, and improve software integrity.

## Key Features

- **Automated CI/CD:** Security workflows using GitHub Actions and Docker.
- **SAST Scanning:** Source code vulnerability detection using Semgrep.
- **AI Security Triage:** AI-assisted classification of security findings and false-positive analysis.
- **Security-Test Generation:** AI-assisted generation of security tests for application changes.
- **SBOM Management:** Software Bill of Materials generation and dependency scanning.
- **Supply Chain Security:** Artifact signing and verification using Cosign/Sigstore.
- **Policy Enforcement:** Security policy evaluation using Open Policy Agent (OPA).
- **Security Monitoring:** Common event logging and dashboard-based visibility.

## Team Responsibilities

| Member | Role | Responsibilities |
|---|---|---|
| M1 — Josmimol-baby | DevSecOps & CI/CD | GitHub Actions, Docker, pipeline hardening and SBOM generation. |
| M2 — suravi29 | Agentic AI Security | AI-assisted SAST triage and security-test generation. |
| M3 — manpreet881449-arch | Supply Chain Security | Cosign/Sigstore, dependency security, IaC and OPA policies. |
| M4 — PrinceJacob0812 | Security Platform & Red Team | Sample application, SAST integration, common logging, dashboard and authorized red-team exercises. |

## Repository Structure

```text
.
├── app/                     # Python/Flask training application
├── .github/workflows/       # CI/CD and security workflows
├── .semgrep/                # Custom Semgrep rules
├── sast/                    # SAST reports and handoff documentation
├── logs/                    # Security event logs
├── docs/                    # Architecture and project documentation
├── dashboard/               # Security dashboard
├── src/                     # AI triage and supporting modules
├── samples/                 # Sample security findings and datasets
├── tests/                   # Automated tests
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- Docker
- Semgrep
- GitHub account

Additional tools such as Syft, Grype, Cosign and OPA are required for their respective security components.

### Clone the Repository

```bash
git clone https://github.com/PrinceJacob0812/agentic-ai-devsecops.git
cd agentic-ai-devsecops
```

### Install Dependencies

```bash
python -m venv venv
```

Activate the environment:

**Windows:**
```powershell
venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Configure AI API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Keep API keys and credentials private. Never commit the `.env` file.

## Security and Safety

- The training application contains intentionally vulnerable code for controlled security testing.
- Run vulnerable examples only in isolated local environments.
- Do not expose the training application publicly or deploy it to production.
- AI-generated security assessments should be reviewed before making security decisions.
- Keep API keys, credentials and private keys out of source control.
- Perform red-team exercises only in authorized environments.

## Collaboration

- Keep `main` stable.
- Use feature branches for individual contributions.
- Follow clear and focused commit messages.
- Open pull requests and request reviews before merging.
- Coordinate shared interfaces and integration changes with the responsible team members.

## Project Status

The project integrates CI/CD automation, SAST scanning, AI-assisted security triage, security-test generation, supply chain security controls, and centralized security monitoring.

Individual components are developed and integrated by their respective team members. Final functionality and end-to-end integration are validated through automated tests and CI/CD workflows.
