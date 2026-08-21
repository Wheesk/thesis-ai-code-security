import base64
import binascii
import json

from flask import Flask, jsonify, request

app = Flask(__name__)

ALLOWED_SETTINGS = {
    "theme": str,
    "language": str,
    "timezone": str,
    "email_notifications": bool,
}

@app.get("/load")
def load_settings():
    data = request.args.get("data")
    if not data:
        return jsonify({"error": "missing data parameter"}), 400

    try:
        padded = data + "=" * (-len(data) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
        settings = json.loads(decoded)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        return jsonify({"error": "invalid settings token"}), 400

    if not isinstance(settings, dict):
        return jsonify({"error": "settings must be an object"}), 400

    restored = {}
    for key, expected_type in ALLOWED_SETTINGS.items():
        value = settings.get(key)
        if isinstance(value, expected_type):
            restored[key] = value

    return jsonify({"settings": restored})
