import argparse
import json
from pathlib import Path
from typing import Any

from src.event_logger import create_event, write_event
from src.semgrep_adapter import load_semgrep_report


ALLOWED_CLASSIFICATIONS = {
    "TRUE_POSITIVE",
    "FALSE_POSITIVE",
    "INSUFFICIENT_EVIDENCE",
}

ALLOWED_RISKS = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO",
}


def load_findings(path: str | Path, input_format: str) -> list[dict[str, Any]]:
    """Load normalized findings or adapt a native Semgrep report."""

    if input_format == "semgrep":
        data = load_semgrep_report(path)
    else:
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)

    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        raise ValueError("Findings input must contain a findings list.")

    return data["findings"]


def export_triage_events(
    findings: list[dict[str, Any]],
    results: list[dict[str, Any]],
    output_path: str | Path = "logs/ai-triage-events.jsonl",
    pipeline_run_id: str = "local",
) -> list[dict[str, Any]]:
    """Convert AI triage results into M4-compatible JSONL events."""

    if not isinstance(findings, list) or not isinstance(results, list):
        raise ValueError("Findings and results must both be lists.")

    findings_by_id: dict[str, dict[str, Any]] = {}

    for finding in findings:
        if not isinstance(finding, dict):
            raise ValueError("Every finding must be an object.")

        finding_id = finding.get("id")
        if not isinstance(finding_id, str) or not finding_id:
            raise ValueError("Every finding must have a non-empty id.")

        if finding_id in findings_by_id:
            raise ValueError(f"Duplicate finding ID: {finding_id}")

        findings_by_id[finding_id] = finding

    results_by_id: dict[str, dict[str, Any]] = {}

    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Every triage result must be an object.")

        finding_id = result.get("finding_id")
        if not isinstance(finding_id, str) or not finding_id:
            raise ValueError("Every triage result must have a finding_id.")

        if finding_id in results_by_id:
            raise ValueError(f"Duplicate triage result ID: {finding_id}")

        if finding_id not in findings_by_id:
            raise ValueError(f"No original finding found for {finding_id}")

        results_by_id[finding_id] = result

    missing_results = set(findings_by_id) - set(results_by_id)
    if missing_results:
        raise ValueError(
            f"Missing triage results for findings: {sorted(missing_results)}"
        )

    events = []

    for finding_id, result in results_by_id.items():
        finding = findings_by_id[finding_id]

        classification = result.get("classification")
        if classification not in ALLOWED_CLASSIFICATIONS:
            raise ValueError(
                f"Invalid classification for {finding_id}: {classification}"
            )

        risk_level = result.get("risk_level")
        if risk_level not in ALLOWED_RISKS:
            raise ValueError(
                f"Invalid risk level for {finding_id}: {risk_level}"
            )

        confidence = result.get("confidence")
        if (
            not isinstance(confidence, int)
            or isinstance(confidence, bool)
            or not 0 <= confidence <= 100
        ):
            raise ValueError(f"Invalid confidence for {finding_id}")

        evidence = result.get("evidence")
        if not isinstance(evidence, list) or not all(
            isinstance(item, str) for item in evidence
        ):
            raise ValueError(f"Invalid evidence list for {finding_id}")

        explanation = result.get("explanation")
        remediation = result.get("remediation")

        if not isinstance(explanation, str) or not isinstance(remediation, str):
            raise ValueError(f"Invalid explanation or remediation for {finding_id}")

        # Keep positive findings open. AI-dismissed and uncertain findings
        # remain available for human review rather than being auto-suppressed.
        status = (
            "OPEN"
            if classification == "TRUE_POSITIVE"
            else "REVIEWED"
        )

        event = create_event(
            stage="sast-triage",
            tool="ai-triage",
            event_type="finding",
            message=explanation,
            status=status,
            pipeline_run_id=pipeline_run_id,
            severity=risk_level,
            rule_id=finding.get("rule_id"),
            file=finding.get("file"),
        )

        # Preserve AI-specific details alongside M4's common event fields.
        event.update({
            "finding_id": finding_id,
            "classification": classification,
            "confidence": confidence,
            "evidence": evidence,
            "remediation": remediation,
        })

        if result.get("error"):
            event["triage_error"] = str(result["error"])

        events.append(event)

    for event in events:
        write_event(event, path=str(output_path))

    return events


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export AI triage results as common security JSONL events."
    )
    parser.add_argument("--findings", required=True)
    parser.add_argument(
        "--format",
        choices=["normalized", "semgrep"],
        default="normalized",
    )
    parser.add_argument("--results", required=True)
    parser.add_argument(
        "--output",
        default="logs/ai-triage-events.jsonl",
    )
    parser.add_argument("--pipeline-run-id", default="local")

    args = parser.parse_args()

    findings = load_findings(args.findings, args.format)

    with Path(args.results).open("r", encoding="utf-8") as file:
        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError("Triage results file must contain a JSON list.")

    events = export_triage_events(
        findings=findings,
        results=results,
        output_path=args.output,
        pipeline_run_id=args.pipeline_run_id,
    )

    print(f"Exported {len(events)} AI triage events to {args.output}")


if __name__ == "__main__":
    main()
