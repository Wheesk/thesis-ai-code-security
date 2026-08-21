from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row  # optional, enables dict-like rows


@app.route("/user")
def user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    conn = get_db()
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(row))
