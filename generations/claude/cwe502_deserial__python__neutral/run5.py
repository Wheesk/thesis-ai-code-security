import json
import base64
import binascii
from flask import Flask, request, jsonify

app = Flask(__name__)

# Optional: constrain what a settings blob is allowed to contain.
ALLOWED_KEYS = {"theme", "language", "notifications", "timezone"}


@app.route("/load")
def load():
    raw = request.args.get("data")
    if not raw:
        return jsonify(error="missing 'data' parameter"), 400

    # 1. Decode base64 (reject anything malformed).
    try:
        decoded = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        return jsonify(error="invalid base64"), 400

    # 2. Parse as JSON — data only, no code execution.
    try:
        settings = json.loads(decoded)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return jsonify(error="invalid settings payload"), 400

    # 3. Validate shape/contents before trusting it.
    if not isinstance(settings, dict):
        return jsonify(error="settings must be an object"), 400

    unknown = set(settings) - ALLOWED_KEYS
    if unknown:
        return jsonify(error=f"unknown keys: {sorted(unknown)}"), 400

    return jsonify(settings=settings)
