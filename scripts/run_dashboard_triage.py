"""Generate AI triage JSONL data for the SecureFlow dashboard."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent import error_result, triage_finding
from src.triage_events import export_triage_events, load_findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SecureFlow AI triage events.")
    parser.add_argument("--input", default="samples/sast_findings.json")
    parser.add_argument("--format", choices=["normalized", "semgrep"], default="normalized")
    parser.add_argument("--pipeline-run-id", default="local-dashboard-run")
    parser.add_argument("--output", default="dashboard/public/data/ai-triage-events.jsonl")
    args = parser.parse_args()

    findings = load_findings(args.input, args.format)
    results = []
    for index, finding in enumerate(findings, start=1):
        finding_id = finding.get("id", "unknown") if isinstance(finding, dict) else "unknown"
        print(f"Triaging finding {index}/{len(findings)}: {finding_id}")
        try:
            results.append(triage_finding(finding))
        except Exception as exc:
            print(f"  Triage unavailable: {exc}")
            results.append(error_result(finding, exc))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("", encoding="utf-8")
    events = export_triage_events(
        findings, results, output_path=output_path,
        pipeline_run_id=args.pipeline_run_id,
    )
    print(f"\nExported {len(events)} triage events to {output_path}")


if __name__ == "__main__":
    main()
