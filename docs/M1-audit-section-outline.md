# Audit report section: SBOM and pipeline (M1)

Status: outline.

1. What the pipeline does: build once, SBOM from the pushed image digest, validate, scan, sign, verify (build-sbom.yml).
2. SBOM: CycloneDX from Syft, validated with jq. Artifacts per run: sbom, grype-report, grype-json, signed-sbom.
3. Vulnerability scanning: Grype reads the SBOM, report-only. One Critical finding (CVE-2026-115557 in Python 3.12.15) was cleared by refreshing the base image digest to 3.12.16.
4. Signing: keyless Cosign signs the image by digest and attaches the SBOM as a signed attestation. Verified against the workflow identity. Cosign upgraded from 2 to 3.
5. Hardening: least privilege, pinned actions, non-root container, base image pinned by digest, HEALTHCHECK, Dependabot.
6. Pipeline fixes: Docker layer caching (build step 21 s to 6 s); runs on main are never cancelled (PR #26).
7. DAST in a sandbox: baseline test and M2's generated test both report FINDING on /lookup.
8. Red team exercise: to fill in after the exercise.
9. Limitations: signing proves who built the image, not that its contents are safe; DAST tests a local rebuild; blocking is the deploy gate (M3).
