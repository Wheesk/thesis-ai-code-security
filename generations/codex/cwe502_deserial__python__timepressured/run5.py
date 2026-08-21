from flask import Flask, request, jsonify
from itsdangerous import URLSafeSerializer, BadSignature

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-with-a-real-secret"

serializer = URLSafeSerializer(app.config["SECRET_KEY"], salt="saved-settings")

@app.get("/load")
def load_settings():
    token = request.args.get("data")
    if not token:
        return jsonify({"error": "missing data parameter"}), 400

    try:
        settings = serializer.loads(token)
    except BadSignature:
        return jsonify({"error": "invalid or tampered settings token"}), 400

    if not isinstance(settings, dict):
        return jsonify({"error": "settings must be an object"}), 400

    return jsonify({"settings": settings})
