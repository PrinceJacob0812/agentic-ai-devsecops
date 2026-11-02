"""Generated DAST test: boolean-based SQL injection on /lookup.

Uses only the Python standard library.
Run only against the sandboxed training application.

Exit codes:
0 = no vulnerability detected
1 = vulnerability confirmed
2 = test error
"""

import json
import os
import sys
import urllib.parse
import urllib.request

TARGET = os.environ.get(
    "TARGET_URL", "http://127.0.0.1:5000"
).rstrip("/")


def get_results(username):
    """Request /lookup and validate its JSON response."""
    params = urllib.parse.urlencode({"username": username})
    url = f"{TARGET}/lookup?{params}"

    with urllib.request.urlopen(url, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Unexpected response: expected a JSON object")

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError("Unexpected response: 'results' must be a list")

    return results


def main():
    try:
        normal_results = get_results("alice")

        # A different boolean-based SQL injection payload from the baseline.
        injected_results = get_results("alice' OR 1=1 -- ")

        if len(normal_results) != 1:
            print(
                "ERROR: Baseline request returned an unexpected number "
                f"of results: {len(normal_results)}"
            )
            return 2

        if len(injected_results) > len(normal_results):
            print(
                "FINDING: Boolean-based SQL injection detected on /lookup; "
                f"normal request returned {len(normal_results)} result(s), "
                f"injected request returned {len(injected_results)}"
            )
            return 1

        print(
            "OK: Boolean-based SQL injection was not detected; "
            f"normal={len(normal_results)}, "
            f"injected={len(injected_results)}"
        )
        return 0

    except Exception as exc:
        print(f"ERROR: DAST test could not complete: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
