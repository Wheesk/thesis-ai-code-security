from flask import Flask, request, jsonify, g
import sqlite3

app = Flask(__name__)
DATABASE = "app.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/user")
def user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    cur = get_db().execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    cur.close()

    if row is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(row)), 200
