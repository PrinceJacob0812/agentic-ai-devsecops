import json

from src.semgrep_adapter import load_semgrep_report
from src.triage import prepare_finding


def test_semgrep_finding_can_be_prepared_for_triage(tmp_path):
    """Verify that a Semgrep finding can pass through the adapter and triage preparation."""

    report = {
        "version": "1.182.1",
        "results": [
            {
                "check_id": "python.lang.security.audit.exec-detected",
                "path": "app/app.py",
                "start": {"line": 24, "col": 1},
                "extra": {
                    "severity": "ERROR",
                    "message": "Possible unsafe execution of untrusted input.",
                    "metadata": {
                        "cwe": ["CWE-95"],
                        "confidence": "HIGH",
                    },
                },
            }
        ],
        "errors": [],
    }

    report_path = tmp_path / "semgrep_report.json"
    report_path.write_text(
        json.dumps(report),
        encoding="utf-8",
    )

    report_data = load_semgrep_report(
        str(report_path),
        repo_root=tmp_path
    )
    findings = report_data["findings"]

    assert len(findings) == 1

    prepared = prepare_finding(findings[0])

    assert prepared["id"] == "SEMGR-0001"
    assert prepared["rule_id"] == "python.lang.security.audit.exec-detected"
    assert prepared["severity"] == "HIGH"
    assert prepared["file"] == "app/app.py"
    assert prepared["line"] == 24
    assert "code" in prepared
    assert "message" in prepared
    assert "expected_label" not in prepared