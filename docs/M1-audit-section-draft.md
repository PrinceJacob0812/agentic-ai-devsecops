# Audit report section: SBOM and pipeline (M1)

Status: draft. Parts 1 to 6 written. Part 7 waits for the red team exercise. Parts 8 and 9 are still to write.

## 1. What the pipeline does

The pipeline is a single GitHub Actions workflow, build-sbom.yml, that runs on every push. It builds the container image once and pushes it to a private GitHub Container Registry package, tagged with the commit ID. It then generates the SBOM from the pushed image's digest, so the SBOM describes exactly the image that was pushed. The SBOM is validated and scanned with Grype, and the image is signed and verified with keyless Cosign.

## 2. SBOM

Syft produces a CycloneDX JSON SBOM. A jq check fails the build if the file is missing, empty, not CycloneDX, or has no components. Each run stores the SBOM as sbom-<sha>.cdx.json and the signed SBOM, with its attestation, as signed-sbom-<sha>. The first SBOM listed Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, MarkupSafe 3.0.4, itsdangerous 2.2.0, click 8.5.0, blinker 1.9.0 and pip 25.0.1 (from the base image).

## 3. Vulnerability scanning

Grype scans the SBOM in report-only mode, so findings produce a warning and do not fail the build. Two reports are saved: a SARIF report with numeric scores and a JSON report with severity labels. On one run on main the labels were Critical 1, High 57, Medium 59, Low 12 and Negligible 47. The Critical finding was CVE-2026-115557 in Python 3.12.15, the interpreter in the base image, with a fix in 3.12.16. Refreshing the base image digest cleared it (Critical 0, Medium 58). The deploy gate agreed with M3 blocks on the Critical label and shows a score of 9.0 or higher as a warning.

## 4. Signing and verification

After the scan, the pipeline signs the image by its digest with keyless Cosign. Keyless means the signature uses the workflow's short-lived GitHub identity token, so there is no private key to store, rotate or leak. The SBOM is then attached to the image as a signed CycloneDX attestation (cosign attest --type cyclonedx). A verify step checks both against the expected certificate identity, which is this workflow file on the branch that ran, and against the GitHub token issuer. The verified attestation is saved with the SBOM as the artifact signed-sbom-<sha>. A key-based attest example from M3 was not used, because it would need a stored private key. Cosign was upgraded from version 2 to 3 through a Dependabot update of cosign-installer (3.10.1 to 4.1.2). Before merging, the update's own run (run #45) showed sign, attest and verify all green with the signed artifact uploaded, and the run on main after the merge was green. Two limits apply. Sigstore's public log records the signing identity (workflow path and repository name), even for a private repository, which was accepted as a trade-off. And a signature proves who built the image, not that its contents are safe.

## 5. Hardening

The workflow token is read-only by default, and the build job adds only packages: write and id-token: write. No long-lived credentials are stored: registry login uses the per-run token, and the only stored secret, the Groq API key, is passed to a single step. Every third-party action is pinned to a full commit ID with a version comment, and each new ID is checked against the real release tag before a Dependabot update is approved. The runner is pinned to ubuntu-24.04, and checkout does not persist credentials. Dependabot checks GitHub Actions and the Docker base image weekly. The container is built in two stages, runs as a non-root user (appuser, UID 10001, no login shell), pins its base image by digest, sets Python environment variables, and has a health check against /health. The sample app is intentionally vulnerable, so its package stays private, it listens on loopback only, and it is never deployed. Pinning has a cost: the digest does not update by itself. In October a new Critical finding appeared in the pinned image (CVE-2026-115557 in Python 3.12.15), and a deliberate digest refresh to 3.12.16 cleared it. Dependabot also proposed a jump to Python 3.15, which was not merged because the build and scan do not test the app on a new Python line.

## 6. Pipeline fixes

Three changes improved the pipeline. First, Docker layer caching (cache-from and cache-to with type=gha). In one measured pair of runs, the build step dropped from 21 s to 6 s and the total from 2m 50s to 2m 27s, with several layers marked as cached. The total gain is small because most of a run goes to other steps, such as the Grype scan, which took 1m 29s in an older run. Second, a second Grype scan saves a JSON report with severity labels, because the SARIF report mostly carries numeric scores. This lets the deploy gate block on the label. Third, a concurrency fix. In Week 2, run #30 on main was marked cancelled when run #31 started, although every step, including signing and verification, had completed. The image is pushed before it is signed, so a cancel in between could leave an unsigned image. The concurrency group on main now includes the run ID, so no run on main is cancelled. After the change, two manual runs started about 20 seconds apart both completed green. Runs on other branches still cancel older runs to save time.

## 7. Red team exercise

To write after the exercise: what was changed, what the SBOM showed, what Grype found, what the signature proved, and what the gate decided.

## 8. Findings and fixes

To write.

## 9. Known limitations

To write.
