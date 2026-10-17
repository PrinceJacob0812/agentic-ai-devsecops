"""Intentionally vulnerable training app for local security scanning only.

Do not deploy this application or expose it to an untrusted network.
"""
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("training.db")


def initialize_db():
    """Create a tiny local training database with non-sensitive demo data."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users "
            "(id INTEGER PRIMARY KEY, username TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (1, 'alice')"
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (2, 'bob')"
        )


@app.get("/")
def index():
    return jsonify(
        {
            "name": "DevSecOps SAST Training App",
            "warning": "Intentionally vulnerable demo. Local testing only.",
            "routes": ["/health", "/lookup?username=alice"],
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/lookup")
def lookup_user():
    username = request.args.get("username", "")

    # INTENTIONAL VULNERABILITY FOR SEMGREP TRAINING:
    # User input is concatenated into SQL instead of using a parameterized query.
    # Never copy this pattern into a real application.
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username = '" + username + "'")
        rows = cursor.fetchall()

    return jsonify({"results": [{"id": row[0], "username": row[1]} for row in rows]})


if __name__ == "__main__":
    initialize_db()
    # Bind to loopback only; this training service is not for network exposure.
    app.run(host="127.0.0.1", port=5000, debug=False)
