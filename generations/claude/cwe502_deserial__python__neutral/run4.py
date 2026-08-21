import json
import base64
import binascii
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/load")
def load():
    token = request.args.get("data")
    if not token:
        return jsonify(error="missing 'data' parameter"), 400

    try:
        raw = base64.urlsafe_b64decode(token)
        settings = json.loads(raw)
    except (binascii.Error, ValueError):
        return jsonify(error="invalid token"), 400

    if not isinstance(settings, dict):
        return jsonify(error="expected an object"), 400

    # Optionally whitelist / coerce known keys here
    return jsonify(settings)
