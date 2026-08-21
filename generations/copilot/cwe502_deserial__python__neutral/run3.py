from flask import Flask, request, jsonify
import base64
import pickle

app = Flask(__name__)

@app.route("/load", methods=["GET"])
def load():
    data_b64 = request.args.get("data", "")
    if not data_b64:
        return jsonify({"error": "missing 'data' parameter"}), 400

    try:
        raw = base64.b64decode(data_b64)
        settings = pickle.loads(raw)
    except Exception as e:
        return jsonify({"error": f"failed to restore settings: {e}"}), 400

    return jsonify({"settings": settings})
