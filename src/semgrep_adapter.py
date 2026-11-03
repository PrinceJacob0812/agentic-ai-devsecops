
import json
from pathlib import Path
from typing import Any


# Map Semgrep severities to the levels accepted by src/triage.py.
SEVERITY_MAP = {
    "ERROR": "HIGH",
    "WARNING": "MEDIUM",
    "INFO": "INFO",
}



def _get_source_snippet(
    result: dict[str, Any],
    repo_root: Path,
) -> str:
    """Prefer the actual source file over potentially misleading report text."""

    relative_path = result.get("path")

    if isinstance(relative_path, str) and relative_path.strip():
        try:
            root = repo_root.resolve()
            source_path = (root / relative_path).resolve()

            # Prevent paths outside the repository from being read.
            if not source_path.is_relative_to(root):
                return "[Source snippet unavailable: path outside repository]"

            if source_path.is_file():
                source_lines = source_path.read_text(
                    encoding="utf-8"
                ).splitlines()

                start = result.get("start") or {}
                end = result.get("end") or {}

                start_line = start.get("line")
                end_line = end.get("line", start_line)

                if (
                    isinstance(start_line, int)
                    and not isinstance(start_line, bool)
                    and start_line >= 1
                ):
                    if (
                        not isinstance(end_line, int)
                        or isinstance(end_line, bool)
                        or end_line < start_line
                    ):
                        end_line = start_line

                    if start_line <= len(source_lines):
                        end_line = min(
                            end_line,
                            start_line + 49,
                            len(source_lines),
                        )

                        snippet = "\n".join(
                            source_lines[start_line - 1:end_line]
                        )

                        if snippet.strip():
                            return snippet

        except (OSError, UnicodeError, ValueError, RuntimeError):
            pass

    # Fall back to Semgrep's snippet only if it appears usable.
    extra = result.get("extra") or {}
    code = extra.get("lines")

    if isinstance(code, str) and code.strip():
        return code

    return "[Source snippet unavailable]"


def adapt_semgrep_report(
    report: dict[str, Any],
    repo_root: str | Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Convert a native Semgrep JSON report into the input format expected
    by the AI triage agent.

    The expected output format is:
        {"findings": [{id, rule_id, severity, file, line, message, code}]}

    Additional scanner metadata is retained for traceability.
    """

    if not isinstance(report, dict):
        raise ValueError("Semgrep report must be a JSON object.")

    results = report.get("results")

    if not isinstance(results, list):
        raise ValueError("Semgrep report must contain a results list.")

    root = Path(repo_root) if repo_root is not None else Path.cwd()
    findings = []

    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            raise ValueError(
                f"Semgrep result at index {index - 1} must be an object."
            )

        extra = result.get("extra") or {}
        if not isinstance(extra, dict):
            extra = {}

        metadata = extra.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}

        start = result.get("start") or {}
        if not isinstance(start, dict):
            start = {}

        raw_severity = str(
            extra.get("severity", "INFO")
        ).upper()

        severity = SEVERITY_MAP.get(raw_severity, "INFO")

        rule_id = result.get("check_id", "unknown-rule")
        file_path = result.get("path", "unknown-file")
        line = start.get("line", 1)

        if not isinstance(rule_id, str):
            rule_id = "unknown-rule"

        if not isinstance(file_path, str):
            file_path = "unknown-file"

        if (
            not isinstance(line, int)
            or isinstance(line, bool)
            or line < 1
        ):
            line = 1

        message = extra.get("message", "No scanner message provided.")
        if not isinstance(message, str):
            message = "No scanner message provided."

        code = _get_source_snippet(result, root)

        findings.append({
            "id": f"SEMGR-{index:04d}",
            "rule_id": rule_id,
            "severity": severity,
            "file": file_path,
            "line": line,
            "message": message,
            "code": code,

            # Retain the original scanner details.
            "source": "semgrep",
            "raw_severity": raw_severity,
            "cwe": metadata.get("cwe"),
            "scanner_confidence": metadata.get("confidence"),
        })

    return {"findings": findings}


def load_semgrep_report(
    path: str | Path,
    repo_root: str | Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Load and adapt a Semgrep JSON report from disk."""

    report_path = Path(path)

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    return adapt_semgrep_report(report, repo_root=repo_root)
