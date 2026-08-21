import base64
import binascii
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/load")
def load():
    raw = request.args.get("data")
    if not raw:
        return jsonify(error="missing 'data' parameter"), 400

    try:
        decoded = base64.urlsafe_b64decode(raw)
        settings = json.loads(decoded)
    except (binascii.Error, ValueError):
        return jsonify(error="invalid data"), 400

    if not isinstance(settings, dict):
        return jsonify(error="expected a settings object"), 400

    # Optionally whitelist keys so unexpected fields can't slip in:
    allowed = {"theme", "language", "notifications"}
    settings = {k: v for k, v in settings.items() if k in allowed}

    return jsonify(settings=settings)

