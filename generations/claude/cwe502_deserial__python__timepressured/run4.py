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
        return jsonify(error="invalid data"), 400

    # settings is now a plain dict/list — safe to use
    return jsonify(settings=settings)
