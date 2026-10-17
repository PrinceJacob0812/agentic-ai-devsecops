# Common Security Event Log Schema

Use one JSON object per event (JSON Lines / JSONL) so events can be appended and processed by the pipeline and dashboard.

## Required fields

| Field | Type | Description |
|---|---|---|
| timestamp | string | UTC timestamp in ISO 8601 format |
| project | string | Project identifier |
| pipeline_run_id | string | CI run identifier, when available |
| stage | string | Pipeline stage, e.g. `sast`, `dependency-scan`, `sbom`, `signature` |
| tool | string | Tool that emitted the event, e.g. `semgrep` |
| event_type | string | e.g. `finding`, `scan_summary`, `verification` |
| severity | string or null | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`, or null |
| rule_id | string or null | Tool rule identifier |
| file | string or null | Repository-relative file path |
| message | string | Short finding or event description |
| status | string | e.g. `OPEN`, `REVIEWED`, `RESOLVED`, `PASSED`, `FAILED` |

## Example

```json
{
  "timestamp": "2026-10-09T12:00:00Z",
  "project": "agentic-ai-devsecops",
  "pipeline_run_id": "local-example",
  "stage": "sast",
  "tool": "semgrep",
  "event_type": "finding",
  "severity": "HIGH",
  "rule_id": "example-rule-id",
  "file": "app/example.py",
  "message": "Example finding for schema illustration",
  "status": "OPEN"
}
```

This is a proposed starting contract. Confirm it with M1 and M2 before using it as a strict interface. Do not put secrets, tokens, or sensitive user data in logs.
