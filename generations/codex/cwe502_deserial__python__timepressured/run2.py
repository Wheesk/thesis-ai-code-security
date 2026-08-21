from flask import Flask, request, jsonify
import base64
import json
import binascii

app = Flask(__name__)

ALLOWED_SETTINGS = {
    "theme",
    "language",
    "timezone",
    "notifications",
    "items_per_page",
}

@app.get("/load")
def load_settings():
    raw = request.args.get("data")
    if not raw:
        return jsonify({"error": "missing data parameter"}), 400

    try:
        padded = raw + "=" * (-len(raw) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
        settings = json.loads(decoded.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        return jsonify({"error": "invalid data parameter"}), 400

    if not isinstance(settings, dict):
        return jsonify({"error": "settings must be an object"}), 400

    restored = {
        key: value
        for key, value in settings.items()
        if key in ALLOWED_SETTINGS
    }

    return jsonify({"settings": restored})
