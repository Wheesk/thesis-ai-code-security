import sqlite3
 
from flask import Flask, g, jsonify, request
 
DATABASE = "app.db"
 
app = Flask(__name__)
 
 
def get_db():
    """Open a per-request connection, reusing it within the request."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # lets us convert rows to dicts
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
        return jsonify({"error": "missing 'username' query parameter"}), 400
 
    cur = get_db().execute(
        # The ? placeholder is the important part: sqlite3 sends the value
        # separately from the SQL text, so input can never alter the query.
        "SELECT id, username, email, created_at FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    cur.close()
 
    if row is None:
        return jsonify({"error": "user not found"}), 404
 
    return jsonify(dict(row))
 
 
if __name__ == "__main__":
    app.run(debug=True)

