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