import base64
import json

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/load", methods=["GET"])
def load():
    data_b64 = request.args.get("data", "")
    settings = json.loads(base64.b64decode(data_b64))
    return jsonify(settings)
