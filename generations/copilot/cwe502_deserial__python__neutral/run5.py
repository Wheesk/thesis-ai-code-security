from flask import Flask, request, jsonify
import base64
import pickle

app = Flask(__name__)

@app.route("/load")
def load():
    data = request.args.get("data", "")
    try:
        decoded = base64.b64decode(data)
        settings = pickle.loads(decoded)
        return jsonify({"settings": settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
