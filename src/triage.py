from typing import Any


REQUIRED_FIELDS = {
    "id",
    "rule_id",
    "severity",
    "file",
    "line",
    "message",
    "code",
}


def validate_finding(finding: dict[str, Any]) -> None:
    """Validate the basic structure of a security finding."""

    missing = REQUIRED_FIELDS - finding.keys()

    if missing:
        raise ValueError(
            f"Finding is missing required fields: {sorted(missing)}"
        )

    if finding["severity"] not in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}:
        raise ValueError("Invalid severity value.")

    if not isinstance(finding["line"], int) or finding["line"] < 1:
        raise ValueError("Line must be a positive integer.")

    for field in ("id", "rule_id", "file", "message", "code"):
        if not isinstance(finding[field], str) or not finding[field].strip():
            raise ValueError(f"{field} must be a non-empty string.")


def prepare_finding(finding: dict[str, Any]) -> dict[str, Any]:
    """Validate a finding and exclude evaluation labels from AI input."""

    validate_finding(finding)

    # Do not reveal expected_label to the model.
    return {
        key: finding[key]
        for key in REQUIRED_FIELDS
    }