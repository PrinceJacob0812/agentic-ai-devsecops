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
## Digest-based SBOM (Week 2)
- build-sbom.yml builds and pushes the image once; the SBOM is generated from image@digest, so it describes exactly the pushed image. The job exposes digest and image as outputs for the signing job (M3).
- Grype scans the SBOM on every run (report-only, fail-build: false). Findings of severity medium or higher were reported on the first run; the blocking policy is left to M3's OPA rule.
- Each push adds a new image tag; old tags may need a cleanup rule later.
- Trade-off: the single job holds packages: write and id-token: write for all steps; a separate signing job would keep write access narrower.
## Week 2 status 
- Done: SBOM validation, Grype scan, digest-based SBOM, SAST triage stage (verified).
- Pending: signing job (waiting for M3's working signing file), Week 2 PR review, AGENT_REF switch (waiting for PR #2).

## Week 3 notes

### Dependabot updates reviewed and merged
- docker/login-action 4.6.0 to 4.7.0 (PR #14): one-line change, commit ID checked against the v4.7.0 tag with git ls-remote.
- actions/setup-python 5 to 7 (PR #16): commit ID checked against the v7.1.0 tag. The same PR changes M2's m2-tests.yml, which uses a version tag and not a commit ID.
- sigstore/cosign-installer 3.10.1 to 4.1.2 (PR #15): this moves Cosign from version 2 to 3. Before merging, I checked that Dependabot's run for this change had sign, attest and verify all green and that the signed-sbom artifact was uploaded. The run on main after the merge was green.

### Grype findings with a high numeric score
- Three findings have a security-severity score of 9.0 or higher: CVE-2005-2541 in tar (10.0), CVE-2019-1010022 in libc6 and libc-bin (9.8).
- All three are packages of the Debian base image. Grype labels all three low (level: note in the SARIF file).
- Decision agreed with M3 for the OPA deploy gate: block on Grype's Critical label, show a score of 9.0 or higher as a warning, and keep a High threshold configurable.
- A score-only rule would deny our own image on every build.
- The SARIF report mostly carries the numeric score, so a second Grype scan saves a JSON report (artifact grype-json-<sha>) that has the severity labels.

### Pull requests opened in Week 3
- Docker base image pinned by digest, HEALTHCHECK and Python environment settings (merged).
- Docker layer caching with cache-from and cache-to type=gha (PR #19, waiting for review).
- Dependabot entry for the docker ecosystem (waiting for review).
- Grype JSON report with severity labels (waiting for review).

### Repository hygiene
- Two unused branches created by GitHub's Revert button exist: revert-3-M1/week1-cicd-pipeline and revert-9-M1-cosign-signing. No revert PR was opened, and main still has the pipeline and signing. A mistaken merge would remove a security control, so unused revert branches should be deleted once M3 confirms.

### Review delays
- Several of my PRs were waiting for review, and M3's gate (PR #13) had no ALLOWED and DENIED results yet. For the audit report this is a process finding: a second reviewer should be named for when the first is not available.
