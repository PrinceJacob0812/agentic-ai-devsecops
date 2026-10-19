
import pytest

from src.triage import validate_finding, prepare_finding
from src.agent import validate_ai_response


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


# --------------------------------------------------
# Finding validation tests
# --------------------------------------------------

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


def test_non_dictionary_finding_is_rejected():
    with pytest.raises(ValueError, match="dictionary"):
        validate_finding(["not", "a", "finding"])


def test_boolean_line_is_rejected(valid_finding):
    valid_finding["line"] = True

    with pytest.raises(ValueError, match="positive integer"):
        prepare_finding(valid_finding)


# --------------------------------------------------
# AI response validation tests
# --------------------------------------------------

@pytest.fixture
def valid_ai_response():
    return {
        "finding_id": "F-1",
        "classification": "TRUE_POSITIVE",
        "risk_level": "HIGH",
        "confidence": 90,
        "evidence": [
            "User input is concatenated directly into SQL."
        ],
        "explanation": "The query may be vulnerable to SQL injection.",
        "remediation": "Use a parameterized SQL query.",
    }


def test_valid_ai_response_is_accepted(valid_ai_response):
    result = validate_ai_response(valid_ai_response, "F-1")

    assert result == valid_ai_response


def test_non_string_evidence_is_rejected(valid_ai_response):
    valid_ai_response["evidence"] = ["Valid evidence", 123]

    with pytest.raises(ValueError, match="evidence item"):
        validate_ai_response(valid_ai_response, "F-1")


def test_missing_ai_response_field_is_rejected(valid_ai_response):
    del valid_ai_response["remediation"]

    with pytest.raises(ValueError, match="schema"):
        validate_ai_response(valid_ai_response, "F-1")


def test_unexpected_ai_response_field_is_rejected(valid_ai_response):
    valid_ai_response["extra"] = "unexpected"

    with pytest.raises(ValueError, match="schema"):
        validate_ai_response(valid_ai_response, "F-1")


def test_incorrect_finding_id_is_rejected(valid_ai_response):
    with pytest.raises(ValueError, match="finding ID"):
        validate_ai_response(valid_ai_response, "F-2")
