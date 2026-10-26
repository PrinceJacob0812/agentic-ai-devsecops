"""Baseline DAST test (M1): SQL injection check on /lookup.

Contract: standard library only, target from TARGET_URL.
Exit codes: 0 = no issue found, 1 = vulnerability confirmed, 2 = test error.
Only run this against the sandboxed training app.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

TARGET = os.environ.get("TARGET_URL", "http://127.0.0.1:5000").rstrip("/")


def get(path, params):
    url = TARGET + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode())


try:
    normal = get("/lookup", {"username": "alice"})
    injected = get("/lookup", {"username": "' OR '1'='1"})
    n = len(normal.get("results", []))
    i = len(injected.get("results", []))
except Exception as exc:
    print("ERROR: " + str(exc))
    sys.exit(2)

if n == 1 and i > n:
    print("FINDING: SQL injection on /lookup: normal query returned %d row(s), injected query returned %d row(s)" % (n, i))
    sys.exit(1)

print("OK: no SQL injection detected (normal=%d, injected=%d)" % (n, i))
sys.exit(0)