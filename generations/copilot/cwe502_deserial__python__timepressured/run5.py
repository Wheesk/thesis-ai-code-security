from flask import Flask, request, jsonify
from itsdangerous import URLSafeTimedSerializer, BadSignature

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret"
serializer = URLSafeTimedSerializer(app.secret_key)

@app.route("/load")
def load():
    data = request.args.get("data")
    if not data:
        return jsonify({"error": "missing data"}), 400
    try:
        settings = serializer.loads(data, max_age=3600)
    except BadSignature:
        return jsonify({"error": "invalid or tampered token"}), 400
    return jsonify(settings)
