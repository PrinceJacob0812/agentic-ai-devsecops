import json

import pytest

from src.triage_events import export_triage_events


@pytest.fixture
def findings():
    return [
        {
            "id": "SEMGR-0001",
            "rule_id": "python.lang.security.audit.sql-injection",
            "severity": "HIGH",
            "file": "app/database.py",
            "line": 12,
            "message": "Possible SQL injection.",
            "code": "cursor.execute(query + user_input)",
        }
    ]


@pytest.fixture
def results():
    return [
        {
            "finding_id": "SEMGR-0001",
            "classification": "TRUE_POSITIVE",
            "risk_level": "HIGH",
            "confidence": 92,
            "evidence": ["User input is concatenated into the SQL query."],
            "explanation": "The query construction is vulnerable to SQL injection.",
            "remediation": "Use parameterized SQL queries.",
        }
    ]


def test_exports_common_and_ai_fields(tmp_path, findings, results):
    output = tmp_path / "ai-triage-events.jsonl"

    events = export_triage_events(
        findings, results, output_path=output, pipeline_run_id="run-123"
    )

    assert len(events) == 1
    event = events[0]

    assert event["project"] == "agentic-ai-devsecops"
    assert event["pipeline_run_id"] == "run-123"
    assert event["stage"] == "sast-triage"
    assert event["tool"] == "ai-triage"
    assert event["event_type"] == "finding"
    assert event["severity"] == "HIGH"
    assert event["rule_id"] == findings[0]["rule_id"]
    assert event["file"] == findings[0]["file"]
    assert event["status"] == "OPEN"

    assert event["finding_id"] == "SEMGR-0001"
    assert event["classification"] == "TRUE_POSITIVE"
    assert event["confidence"] == 92
    assert event["evidence"] == results[0]["evidence"]
    assert event["remediation"] == results[0]["remediation"]

    saved_event = json.loads(output.read_text(encoding="utf-8").strip())
    assert saved_event == event


def test_false_positive_remains_reviewed(tmp_path, findings, results):
    results[0]["classification"] = "FALSE_POSITIVE"

    events = export_triage_events(
        findings, results, output_path=tmp_path / "events.jsonl"
    )

    assert events[0]["status"] == "REVIEWED"


def test_insufficient_evidence_remains_reviewed(tmp_path, findings, results):
    results[0]["classification"] = "INSUFFICIENT_EVIDENCE"

    events = export_triage_events(
        findings, results, output_path=tmp_path / "events.jsonl"
    )

    assert events[0]["status"] == "REVIEWED"


def test_error_details_are_preserved(tmp_path, findings, results):
    results[0]["error"] = "API unavailable"
    results[0]["classification"] = "INSUFFICIENT_EVIDENCE"
    results[0]["risk_level"] = "INFO"
    results[0]["confidence"] = 0
    results[0]["evidence"] = []

    events = export_triage_events(
        findings, results, output_path=tmp_path / "events.jsonl"
    )

    assert events[0]["triage_error"] == "API unavailable"
    assert events[0]["status"] == "REVIEWED"


def test_missing_result_is_rejected(tmp_path, findings):
    with pytest.raises(ValueError, match="Missing triage results"):
        export_triage_events(
            findings, [], output_path=tmp_path / "events.jsonl"
        )


def test_duplicate_finding_id_is_rejected(tmp_path, findings, results):
    duplicate_findings = findings + [findings[0].copy()]

    with pytest.raises(ValueError, match="Duplicate finding ID"):
        export_triage_events(
            duplicate_findings,
            results,
            output_path=tmp_path / "events.jsonl",
        )


def test_non_string_evidence_is_rejected(tmp_path, findings, results):
    results[0]["evidence"] = ["valid", 123]

    with pytest.raises(ValueError, match="Invalid evidence"):
        export_triage_events(
            findings, results, output_path=tmp_path / "events.jsonl"
        )
