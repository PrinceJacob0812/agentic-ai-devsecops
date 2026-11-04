git add docs/M1-audit-section-draft.md# Audit report section: SBOM and pipeline (M1)

Status: draft. Parts 1 to 6 written. Part 7 waits for the red team exercise. Parts 8 and 9 are still to write.

## 1. What the pipeline does

The pipeline is a single GitHub Actions workflow, build-sbom.yml, that runs on every push. It builds the container image once and pushes it to a private GitHub Container Registry package, tagged with the commit ID. It then generates the SBOM from the pushed image's digest, so the SBOM describes exactly the image that was pushed. The SBOM is validated and scanned with Grype, and the image is signed and verified with keyless Cosign.

## 2. SBOM

Syft produces a CycloneDX JSON SBOM. A jq check fails the build if the file is missing, empty, not CycloneDX, or has no components. Each run stores the SBOM as sbom-<sha>.cdx.json and the signed SBOM, with its attestation, as signed-sbom-<sha>. The first SBOM listed Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, MarkupSafe 3.0.4, itsdangerous 2.2.0, click 8.5.0, blinker 1.9.0 and pip 25.0.1 (from the base image).

## 3. Vulnerability scanning

Grype scans the SBOM in report-only mode, so findings produce a warning and do not fail the build. Two reports are saved: a SARIF report with numeric scores and a JSON report with severity labels. On one run on main the labels were Critical 1, High 57, Medium 59, Low 12 and Negligible 47. The Critical finding was CVE-2026-115557 in Python 3.12.15, the interpreter in the base image, with a fix in 3.12.16. Refreshing the base image digest cleared it (Critical 0, Medium 58). The fix reached main through the deploy gate PR (#13), which pins python:3.12.16-slim by digest, so my separate refresh PR (#24) became redundant. The deploy gate agreed with M3 blocks on the Critical label and shows a score of 9.0 or higher as a warning.

## 4. Signing and verification

After the scan, the pipeline signs the image by its digest with keyless Cosign. Keyless means the signature uses the workflow's short-lived GitHub identity token, so there is no private key to store, rotate or leak. The SBOM is then attached to the image as a signed CycloneDX attestation (cosign attest --type cyclonedx). A verify step checks both against the expected certificate identity, which is this workflow file on the branch that ran, and against the GitHub token issuer. The verified attestation is saved with the SBOM as the artifact signed-sbom-<sha>. A key-based attest example from M3 was not used, because it would need a stored private key. Cosign was upgraded from version 2 to 3 through a Dependabot update of cosign-installer (3.10.1 to 4.1.2). Before merging, the update's own run (run #45) showed sign, attest and verify all green with the signed artifact uploaded, and the run on main after the merge was green. Two limits apply. Sigstore's public log records the signing identity (workflow path and repository name), even for a private repository, which was accepted as a trade-off. And a signature proves who built the image, not that its contents are safe.

## 5. Hardening

The workflow token is read-only by default, and the build job adds only packages: write and id-token: write. No long-lived credentials are stored: registry login uses the per-run token, and the only stored secret, the Groq API key, is passed to a single step. Every third-party action is pinned to a full commit ID with a version comment, and each new ID is checked against the real release tag before a Dependabot update is approved. The runner is pinned to ubuntu-24.04, and checkout does not persist credentials. Dependabot checks GitHub Actions and the Docker base image weekly. The container is built in two stages, runs as a non-root user (appuser, UID 10001, no login shell), pins its base image by digest, sets Python environment variables, and has a health check against /health. The sample app is intentionally vulnerable, so its package stays private, it listens on loopback only, and it is never deployed. Pinning has a cost: the digest does not update by itself. In October a new Critical finding appeared in the pinned image (CVE-2026-115557 in Python 3.12.15), and a deliberate digest refresh to 3.12.16 cleared it. Dependabot also proposed a jump to Python 3.15, which was not merged because the build and scan do not test the app on a new Python line.

## 6. Pipeline fixes

Four changes improved the pipeline. First, Docker layer caching (cache-from and cache-to with type=gha). In one measured pair of runs, the build step dropped from 21 s to 6 s and the total from 2m 50s to 2m 27s, with several layers marked as cached. The total gain is small because most of a run goes to other steps, such as the Grype scan, which took 1m 29s in an older run. Second, a second Grype scan saves a JSON report with severity labels, because the SARIF report mostly carries numeric scores. This lets the deploy gate block on the label. Third, a concurrency fix. In Week 2, run #30 on main was marked cancelled when run #31 started, although every step, including signing and verification, had completed. The image is pushed before it is signed, so a cancel in between could leave an unsigned image. The concurrency group on main now includes the run ID, so no run on main is cancelled. After the change, two manual runs started about 20 seconds apart both completed green. Runs on other branches still cancel older runs to save time. Fourth, the OPA deployment gate (scripts/gate.sh, from PR #13) was wired into the pipeline after the signed SBOM upload. It installs a pinned OPA, runs the policy tests, verifies the signature and attestation again, counts Critical findings in the Grype JSON, and denies the image when the count is above zero. High findings only warn. On the first run on main after the merge of PR #36 (build-sbom #87) it printed ALLOWED with Critical 0 and High 60, and the five policy tests passed.

## 7. Red team exercise

To write after the exercise: what was changed, what the SBOM showed, what Grype found, what the signature proved, and what the gate decided.

## 8. Findings and fixes

Eight findings came out of building and running the pipeline.

1. Unpinned dependency range. app/requirements.txt allowed any Flask version in a range, so builds were not reproducible. The SBOM showed the versions that were actually installed, and M4 pinned exact versions.
2. Hidden code snippets. Semgrep replaces the code snippet with a login message when it runs without an account, so the AI agent saw no code. A workflow step now reads the real line from app/ before the agent runs.
3. Silent AI failure. Groq retired the agent's default model, and the agent still exited with success while every AI call failed. A result check now fails the run when the output is empty or every finding has an error, and the model is set explicitly.
4. Triage failure on main. After the first triage merge, the agent failed with a missing-module error. Starting it as python -m src.agent fixed the import path.
5. Cancelled run. A run on main was marked cancelled by a newer run after its signing steps had finished. The concurrency group on main now includes the run ID, and two later runs started 20 seconds apart both completed.
6. Score versus label. Three findings (CVE-2005-2541 in tar, CVE-2019-1010022 in libc6 and libc-bin) have numeric scores of 10.0 and 9.8 but Grype labels them low. A score-only gate rule would deny every image built on this base, so the agreed rule blocks on the Critical label and shows a score of 9.0 or higher as a warning.
7. New Critical CVE in the pinned base image. A new finding, CVE-2026-115557 in Python 3.12.15, appeared after the digest was pinned. A refresh to 3.12.16 cleared it on the test branch (Critical 1 to 0). The same fix reached main through the gate PR (#13), which pins python:3.12.16-slim by digest, and PR #24 became redundant.
8. Major Python bump proposed. Dependabot proposed moving the base image to Python 3.15. It was not merged, because the build and scan do not test the application on a new Python line.

## 9. Known limitations

- Permissions. One job holds both packages: write and id-token: write. A separate signing job would narrow this.
- What a signature proves. A valid signature shows who built the image, not that its contents are safe.
- Scanning limits. Grype scans the SBOM, so findings are only as complete as the SBOM, and only known CVEs are detected. A malicious package with no published CVE would pass the scan.
- Gate coverage. Grype findings do not fail the build. Blocking is the deploy gate (M3), which blocks only on the Critical label, so High and Medium findings pass. The base image has 57 High findings. The gate is merged (PR #13) and runs in build-sbom after the signed SBOM upload (PR #36).
- DAST. The sandbox tests a local rebuild, not the pushed and signed image, and findings do not fail the run because the sample app is intentionally vulnerable.
- External AI. Flagged code snippets are sent to an external AI service, which is acceptable for a training app and not for real code.
- Public log. Sigstore's public log records the signing identity, even for a private repository.
- Manual digest refresh. Pinning the base image by digest gives repeatable builds, but new fixes only arrive when someone refreshes the digest.
- Measurement. The caching result comes from one pair of runs.
- Gate input. gate.sh trusts the Grype JSON file it is given. Nothing ties that file to the image digest, so a report from a clean image could be passed with a vulnerable one.
- Gate independence. The gate runs in the same job that built and signed the image, so it is not an independent check at deploy time.