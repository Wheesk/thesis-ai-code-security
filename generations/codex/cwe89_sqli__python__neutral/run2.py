@app.get("/user")
def get_user():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "username query parameter is required"}), 400

    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        conn.close()

    if user is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify(dict(user))
