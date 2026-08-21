import sqlite3
from flask import Flask, jsonify, request, g

app = Flask(__name__)
DATABASE = "app.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us build a dict from the row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/user")
def get_user():
    username = request.args.get("username")
    if not username:
        return jsonify(error="username query parameter is required"), 400

    cur = get_db().execute(
        "SELECT id, username, email, created_at FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    cur.close()

    if row is None:
        return jsonify(error="user not found"), 404

    return jsonify(dict(row))
