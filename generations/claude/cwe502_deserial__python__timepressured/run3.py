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
        decoded = base64.b64decode(raw, validate=True)
        settings = json.loads(decoded)
    except (binascii.Error, ValueError):
        return jsonify(error="invalid token"), 400

    # Optional but recommended: make sure it's the shape you expect
    if not isinstance(settings, dict):
        return jsonify(error="invalid settings format"), 400

    return jsonify(settings)
