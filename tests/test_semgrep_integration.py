import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RULES_FILE = PROJECT_ROOT / ".semgrep" / "rules.yml"


@pytest.fixture
def sql_test_files(tmp_path):
    vulnerable_file = tmp_path / "vulnerable.py"
    safe_file = tmp_path / "safe.py"

    vulnerable_file.write_text(
        """
import sqlite3

def lookup_user(username):
    cursor = sqlite3.connect(":memory:").cursor()
    cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
""",
        encoding="utf-8",
    )

    safe_file.write_text(
        """
import sqlite3

def lookup_user(username):
    cursor = sqlite3.connect(":memory:").cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    )
""",
        encoding="utf-8",
    )

    return vulnerable_file, safe_file


@pytest.mark.skipif(
    shutil.which("semgrep") is None,
    reason="Semgrep is not installed",
)
def test_semgrep_detects_vulnerable_sql(sql_test_files):
    vulnerable_file, _ = sql_test_files

    result = subprocess.run(
        [
            "semgrep",
            "scan",
            "--config",
            str(RULES_FILE),
            "--json",
            str(vulnerable_file),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode in (0, 1), result.stderr

    report = json.loads(result.stdout)
    finding_ids = {
        finding["check_id"]
        for finding in report.get("results", [])
    }

    assert "semgrep.training-sql-query-string-concat" in finding_ids


@pytest.mark.skipif(
    shutil.which("semgrep") is None,
    reason="Semgrep is not installed",
)
def test_semgrep_does_not_flag_parameterized_sql(sql_test_files):
    _, safe_file = sql_test_files

    result = subprocess.run(
        [
            "semgrep",
            "scan",
            "--config",
            str(RULES_FILE),
            "--json",
            str(safe_file),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode in (0, 1), result.stderr

    report = json.loads(result.stdout)
    finding_ids = {
        finding["check_id"]
        for finding in report.get("results", [])
    }

    assert "semgrep.training-sql-query-string-concat" not in finding_ids