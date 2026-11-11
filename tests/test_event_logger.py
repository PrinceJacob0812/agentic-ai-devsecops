
import json
import pytest

from src.event_logger import create_event, write_event


def test_create_valid_event():
    event = create_event(
        stage="sast",
        tool="semgrep",
        event_type="finding",
        message="SQL injection detected",
        status="OPEN",
        severity="HIGH",
        rule_id="python.sql-injection",
        file="app/app.py",
    )

    assert event["stage"] == "sast"
    assert event["severity"] == "HIGH"
    assert event["project"] == "agentic-ai-devsecops"
    assert "timestamp" in event


def test_negligible_severity_is_supported():
    event = create_event(
        stage="dependency-scan",
        tool="grype",
        event_type="finding",
        message="Negligible vulnerability",
        status="OPEN",
        severity="NEGLIGIBLE",
    )

    assert event["severity"] == "NEGLIGIBLE"


def test_gate_stage_and_optional_count():
    event = create_event(
        stage="gate",
        tool="opa",
        event_type="verification",
        message="Deployment gate passed",
        status="PASSED",
        count=0,
    )

    assert event["stage"] == "gate"
    assert event["count"] == 0


def test_invalid_severity_rejected():
    with pytest.raises(ValueError):
        create_event(
            stage="sast",
            tool="semgrep",
            event_type="finding",
            message="Test",
            status="OPEN",
            severity="UNKNOWN",
        )


def test_invalid_count_rejected():
    with pytest.raises(ValueError):
        create_event(
            stage="gate",
            tool="opa",
            event_type="verification",
            message="Test",
            status="PASSED",
            count=-1,
        )


def test_write_event_creates_jsonl(tmp_path):
    event = create_event(
        stage="sast",
        tool="semgrep",
        event_type="finding",
        message="Test finding",
        status="OPEN",
        severity="HIGH",
    )

    output = tmp_path / "events.jsonl"
    write_event(event, str(output))

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["message"] == "Test finding"
