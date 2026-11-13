
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT = "agentic-ai-devsecops"

ALLOWED_SEVERITIES = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "NEGLIGIBLE", "UNKNOWN"
}

REQUIRED_FIELDS = {
    "timestamp",
    "project",
    "pipeline_run_id",
    "stage",
    "tool",
    "event_type",
    "severity",
    "rule_id",
    "file",
    "message",
    "status",
}

def create_event(
    stage: str,
    tool: str,
    event_type: str,
    message: str,
    status: str,
    pipeline_run_id: str = "local",
    severity: str | None = None,
    rule_id: str | None = None,
    file: str | None = None,
    count: int | None = None,
) -> dict[str, Any]:

    if severity is not None and severity not in ALLOWED_SEVERITIES:
        raise ValueError("Invalid severity")

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT,
        "pipeline_run_id": pipeline_run_id,
        "stage": stage,
        "tool": tool,
        "event_type": event_type,
        "severity": severity,
        "rule_id": rule_id,
        "file": file,
        "message": message,
        "status": status,
    }

    if count is not None:
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("count must be a non-negative integer")
        event["count"] = count

    return event

def write_event(event: dict[str, Any], path: str = "logs/events.jsonl") -> None:
    missing = REQUIRED_FIELDS - event.keys()
    if missing:
        raise ValueError(f"Missing event fields: {sorted(missing)}")

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")

def log_event(**kwargs: Any) -> dict[str, Any]:
    event = create_event(**kwargs)
    write_event(event)
    return event
