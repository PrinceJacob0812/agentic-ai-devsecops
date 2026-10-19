
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

ALLOWED_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}


def validate_finding(finding: Any) -> None:
    """Validate the type, required fields, and values of a finding."""

    # Check the type before accessing keys or fields.
    if not isinstance(finding, dict):
        raise ValueError("Finding must be a dictionary.")

    missing = REQUIRED_FIELDS - finding.keys()
    if missing:
        raise ValueError(
            f"Finding is missing required fields: {sorted(missing)}"
        )

    severity = finding["severity"]
    if not isinstance(severity, str) or severity not in ALLOWED_SEVERITIES:
        raise ValueError("Invalid severity value.")

    line = finding["line"]
    if (
        not isinstance(line, int)
        or isinstance(line, bool)
        or line < 1
    ):
        raise ValueError("Line must be a positive integer.")

    for field in ("id", "rule_id", "file", "message", "code"):
        value = finding[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string.")


def prepare_finding(finding: Any) -> dict[str, Any]:
    """Validate a finding and exclude evaluation labels from AI input."""

    validate_finding(finding)

    # Only pass the approved fields to the AI model.
    return {
        key: finding[key]
        for key in (
            "id",
            "rule_id",
            "severity",
            "file",
            "line",
            "message",
            "code",
        )
    }
