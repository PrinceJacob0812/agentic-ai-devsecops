# SecureFlow Security Dashboard

SecureFlow is the React/Vite CNAPP-style dashboard for the Agentic AI DevSecOps and Supply Chain Security Pipeline.

## Dashboard views

- **Overview:** pipeline status, vulnerability totals, SBOM component count, image-signature status, security-control status, and recent events.
- **Pipeline:** events reported by Syft, Grype, Cosign, OPA, Semgrep, DAST, and AI triage.
- **Vulnerabilities:** severity totals and chart based on the imported event data.
- **SBOM Explorer:** CycloneDX SBOM summary and validation status.
- **AI Triage:** imported AI classification, confidence, evidence, and remediation details when M2 triage events are available.
- **Settings:** workspace and monitoring information.

## Data source and refresh

The dashboard reads `public/data/events.jsonl` at runtime. Each non-empty line must be a JSON event record. The Dashboard Event Sync GitHub Actions workflow downloads the JSONL artifact from a successful `build-sbom` or `triage` workflow run, merges and deduplicates records, and commits the updated file to `main`. Use **Refresh** in the Overview to reload the current file.

The dashboard displays only data present in the JSONL file. AI triage cards remain empty until a successful M2 triage workflow has exported and synced triage events. A missing event is not proof that a control failed or passed.

## Run locally

From the repository root:

```bash
cd dashboard
npm install
npm run dev
```

Create a production build with:

```bash
npm run build
```

The `Dashboard Build` GitHub Actions workflow runs the production build for dashboard changes and pushes to `main`.

## Interpretation and limitations

- Vulnerability totals are aggregated from the severity summary events in the JSONL file; they are not a live query to Grype.
- Signature and deployment-gate status reflect the latest matching event in the synced data.
- AI classifications are decision support only. They do not automatically suppress findings or replace human security review.
- This dashboard is a project monitoring interface, not a standalone security scanner or a production authorization service.
