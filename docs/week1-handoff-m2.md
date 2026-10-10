# Week 1 M4 → M2 handoff

## Available after the SAST workflow runs
- Sample app: `app/app.py`
- Custom training rule: `.semgrep/rules.yml`
- GitHub Actions workflow: `.github/workflows/semgrep.yml`
- Workflow artifact: `semgrep-sast-results` (JSON report, retained for 14 days)

## Finding format
The report is Semgrep JSON. The team should agree with M2 on the fields needed by the triage agent (rule ID, severity, message, file path, line range, and code snippet where available).

## Notes
- The SQL query concatenation in `app/app.py` is intentional and exists only to generate a controlled training finding.
- Run only on a local machine or isolated test environment. Do not deploy this app.
- The custom rule is a starting point; validate its match in the GitHub Actions run before treating the handoff as complete.
- Coordinate with M1 before consolidating this workflow into the main CI pipeline to avoid duplicate scans.
