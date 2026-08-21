@app.get("/user")
def get_user():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"error": "username query parameter is required"}), 400

    db = sqlite3.connect("app.db")
    db.row_factory = sqlite3.Row

    try:
        user = db.execute(
            "SELECT id, username, email, created_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        db.close()

    if user is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(user))
