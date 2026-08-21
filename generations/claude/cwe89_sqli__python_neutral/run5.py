import sqlite3
 
from flask import Flask, g, jsonify, request
 
app = Flask(__name__)
DATABASE = "app.db"
 
# Only columns that are safe to expose publicly. Never SELECT * here —
# that would leak password hashes, tokens, etc. as soon as someone adds them.
PUBLIC_USER_COLUMNS = ("id", "username", "email", "created_at")
 
 
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
        return jsonify(error="Missing required query parameter: username"), 400
 
    columns = ", ".join(PUBLIC_USER_COLUMNS)
    # The '?' placeholder is the important part: sqlite3 sends the value
    # separately from the SQL, so it can never be parsed as SQL.
    row = get_db().execute(
        f"SELECT {columns} FROM users WHERE username = ?",
        (username,),
    ).fetchone()
 
    if row is None:
        return jsonify(error="User not found"), 404
 
    return jsonify(dict(row))
 
 
if __name__ == "__main__":
    app.run(debug=True)

