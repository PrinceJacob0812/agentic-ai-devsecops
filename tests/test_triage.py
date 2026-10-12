import pytest

from src.triage import validate_finding, prepare_finding


@pytest.fixture
def valid_finding():
    return {
        "id": "TEST-001",
        "rule_id": "python.lang.security.audit.exec-detected",
        "severity": "HIGH",
        "file": "app.py",
        "line": 24,
        "message": "Possible unsafe use of exec().",
        "code": "exec(user_input)",
        "expected_label": "TRUE_POSITIVE",
    }


def test_valid_finding_is_accepted(valid_finding):
    validate_finding(valid_finding)


def test_expected_label_is_excluded(valid_finding):
    prepared = prepare_finding(valid_finding)
    assert "expected_label" not in prepared


def test_missing_field_is_rejected(valid_finding):
    del valid_finding["code"]

    with pytest.raises(ValueError, match="missing required fields"):
        validate_finding(valid_finding)


def test_invalid_severity_is_rejected(valid_finding):
    valid_finding["severity"] = "EXTREME"

    with pytest.raises(ValueError, match="Invalid severity"):
        validate_finding(valid_finding)


def test_invalid_line_is_rejected(valid_finding):
    valid_finding["line"] = 0

    with pytest.raises(ValueError, match="positive integer"):
        validate_finding(valid_finding)


def test_empty_code_is_rejected(valid_finding):
    valid_finding["code"] = "   "

    with pytest.raises(ValueError, match="non-empty string"):
        validate_finding(valid_finding)