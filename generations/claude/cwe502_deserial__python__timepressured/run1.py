import json
import base64
import binascii
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/save")
def save():
    # Example: whatever settings dict you want to persist in the token
    settings = {"theme": "dark", "font_size": 14, "notifications": True}
    raw = json.dumps(settings).encode("utf-8")
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return jsonify({"data": token})


@app.route("/load")
def load():
    token = request.args.get("data")
    if not token:
        return jsonify({"error": "missing 'data' parameter"}), 400

    try:
        raw = base64.urlsafe_b64decode(token)
        settings = json.loads(raw)
    except (binascii.Error, ValueError):
        return jsonify({"error": "invalid token"}), 400

    # Optional but recommended: validate shape before trusting it
    if not isinstance(settings, dict):
        return jsonify({"error": "malformed settings"}), 400

    return jsonify({"settings": settings})
