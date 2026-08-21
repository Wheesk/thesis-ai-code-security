from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = "app.db"


def get_db():
    return sqlite3.connect(DATABASE)


@app.route("/user", methods=["GET"])
def get_user():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username parameter is required"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, username, email FROM users WHERE username = ?",
        (username,),
    )
    row = cursor.fetchone()
    db.close()

    if row is None:
        return jsonify({"error": "user not found"}), 404

    return jsonify({
        "id": row[0],
        "username": row[1],
        "email": row[2],
    })


if __name__ == "__main__":
    app.run(debug=True)
