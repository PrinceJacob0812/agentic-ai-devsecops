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


## Deployment Gate

The deployment gate is implemented in `scripts/gate.sh` and evaluates the signed container image before it can pass the OPA deployment policy.

### Required environment variables

| Variable | Purpose |
|---|---|
| `IMAGE_REF` | Container image reference pinned to an immutable `@sha256:<64-hex-digest>` digest. Tags such as `:latest` are not accepted by policy. |
| `IDENTITY` | Expected Sigstore keyless signing certificate identity. In GitHub Actions this is set to the repository's `.github/workflows/build-sbom.yml` workflow identity for the current ref. |
| `GRYPE_JSON` | Path to the Grype JSON report. In CI, this report is generated from the CycloneDX SBOM extracted from the successfully verified signed attestation—not from an arbitrary caller-provided report. |
| `ISSUER` | Optional OIDC issuer; defaults to `https://token.actions.githubusercontent.com`. |

### CI verification flow

1. Verify the image signature with Cosign using the expected certificate identity and OIDC issuer.
2. Verify the CycloneDX SBOM attestation for the same digest-pinned image.
3. Extract the SBOM predicate from the verified attestation and validate its CycloneDX structure.
4. Generate the Grype JSON report from that extracted SBOM.
5. Evaluate the OPA policy using the verified signature/attestation results and Critical finding count.

### Exit codes

- `0`: policy allows the image.
- `1`: required input/tool is missing, verification or policy evaluation fails, the report is invalid, or the policy denies the image.

A policy denial prints the specific OPA reason(s), such as an unverified signature, unverified SBOM attestation, Critical vulnerabilities, or a mutable/non-digest image reference.

**Severity policy:** Critical findings block deployment. High findings are baseline-gated: the approved baseline is 86 High findings from the initial verified pipeline scan. Any increase above 86 blocks deployment; reducing the baseline as findings are remediated makes the gate progressively stricter. Update `HIGH_FINDINGS_BASELINE` only after reviewing and approving the new baseline.
