import json
import base64
import binascii
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
        return jsonify(error="invalid token"), 400

    if not isinstance(settings, dict):
        return jsonify(error="settings must be an object"), 400

    # optionally validate expected keys here
    return jsonify(settings=settings)
