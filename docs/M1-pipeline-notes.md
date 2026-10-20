# M1 Pipeline Notes

Owner: M1 (DevSecOps & CI/CD Engineer)

## Week 1 tasks
- [ ] Dockerfile for the sample app
- [ ] Hardened GitHub Actions pipeline (least privilege, no long-lived secrets)
- [ ] SBOM generation on every commit (Syft, CycloneDX)
- M4 pinned app/requirements.txt after M1 reported the version range. CI build and SBOM now show the pinned versions, so builds are reproducible.
## Hardening done (Week 1)
- Workflow permissions: contents: read by default; only the publish job has packages: write and id-token: write.
- Runner pinned to ubuntu-24.04 instead of ubuntu-latest.
- All 5 actions pinned to full commit SHAs (checkout v7.0.1, setup-buildx v4.4.1, build-push v7.4.0, login v4.6.0, sbom-action v0.24.3).
- Dependabot enabled for GitHub Actions (weekly).
- Registry auth uses the per-run GITHUB_TOKEN, no stored credentials.
## Week 2
- SBOM validated in CI (CycloneDX format, non-empty components).
- Grype scans the SBOM on every run; the report is stored as an artifact (report-only for now; blocking is handled by M3's OPA policy).
## Triage stage (Week 2)
- triage.yml runs Semgrep on app/ and then Suravi's agent (src/agent.py) on the JSON report. The Groq key is an Actions secret passed to that one step only; the agent-tests job uses a fake key.
- Result: SEMGR-0001 (SQL concatenation, app.py) classified TRUE_POSITIVE, risk HIGH, confidence 80, with the real code line as evidence and a parameterized-query fix. The AI suggested %s placeholders; the app uses SQLite, which needs ? (shows why AI output needs human review).
- Finding 1: the agent's default model (llama-3.3-70b-versatile) was retired by Groq on 16 Aug 2026, so every AI call returned model_not_found while the agent still exited successfully. The result check in the pipeline caught it; fixed by setting GROQ_MODEL.
- Finding 2: Semgrep without a login replaces the code snippet with "requires login". A workflow step reads the real line from app/ before the agent runs.
- Known gaps: agent dependencies are installed by name (no requirements.txt yet); the agent runs from feature/ai-security-triage until PR #2 is merged, then AGENT_REF changes to main; only the flagged snippet is sent to the model, not surrounding code.