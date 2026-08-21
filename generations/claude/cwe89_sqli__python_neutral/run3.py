import sqlite3
 
from flask import Flask, g, jsonify, request
 
app = Flask(__name__)
DATABASE = "app.db"
 
# Only these columns are ever sent to the client. Keep password hashes,
# reset tokens, etc. out of this list.
PUBLIC_USER_FIELDS = ("id", "username", "email", "created_at")
 
 
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db
 
 
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
 
 
@app.route("/user")
def get_user():
    username = request.args.get("username")
    if not username:
        return jsonify(error="Missing 'username' query parameter"), 400
 
    columns = ", ".join(PUBLIC_USER_FIELDS)
    # The '?' placeholder is what keeps this safe: the value is passed to
    # SQLite separately from the SQL text, so it can never be parsed as SQL.
    row = (
        get_db()
        .execute(f"SELECT {columns} FROM users WHERE username = ?", (username,))
        .fetchone()
    )
 
    if row is None:
        return jsonify(error="User not found"), 404
 
    return jsonify(dict(row))
 
 
if __name__ == "__main__":
    app.run(debug=True)

