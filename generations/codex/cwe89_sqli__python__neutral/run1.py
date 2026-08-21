import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["DATABASE"] = "users.db"


def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/user")
def get_user():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "username is required"}), 400

    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if user is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(user))
