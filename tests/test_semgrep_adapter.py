
from src.semgrep_adapter import adapt_semgrep_report


def test_semgrep_report_is_converted(tmp_path):
    report = {
        "results": [
            {
                "check_id": "semgrep.training-sql-query-string-concat",
                "path": "app/app.py",
                "start": {"line": 54},
                "extra": {
                    "message": "Possible SQL injection.",
                    "severity": "ERROR",
                    "metadata": {
                        "cwe": "CWE-89",
                        "confidence": "HIGH",
                    },
                },
            }
        ]
    }

    # Use an empty temporary directory so the adapter cannot
    # find app/app.py and must use its fallback source snippet.
    adapted = adapt_semgrep_report(report, repo_root=tmp_path)
    finding = adapted["findings"][0]

    assert finding["rule_id"] == (
        "semgrep.training-sql-query-string-concat"
    )
    assert finding["file"] == "app/app.py"
    assert finding["line"] == 54
    assert finding["severity"] == "HIGH"
    assert finding["raw_severity"] == "ERROR"
    assert finding["cwe"] == "CWE-89"
    assert "unavailable" in finding["code"]


def test_empty_results_are_supported():
    report = {"results": []}

    adapted = adapt_semgrep_report(report)

    assert adapted["findings"] == []
