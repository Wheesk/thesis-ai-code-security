@app.get("/user")
def get_user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username query parameter is required"}), 400

    db = sqlite3.connect("app.db")
    db.row_factory = sqlite3.Row

    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    db.close()

    if user is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(user))
