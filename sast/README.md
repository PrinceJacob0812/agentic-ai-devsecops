# SAST

M4 uses Semgrep with the custom training rule in `.semgrep/rules.yml`.

## Local scan
From the repository root:

```bash
python -m pip install --upgrade semgrep
semgrep scan --config .semgrep/rules.yml --json --output sast/semgrep-results.json app/
```

## CI output
The GitHub Actions workflow `.github/workflows/semgrep.yml` runs the scan on pushes, pull requests and manual dispatch. It uploads `semgrep-results.json` as the `semgrep-sast-results` artifact when the report is produced.

The JSON report is a generated output, not currently committed to the repository. Download it from the successful workflow run and share it with M2.

Do not commit real secrets or sensitive data in scan reports. Confirm output fields and severity mapping with M2 before integration.
