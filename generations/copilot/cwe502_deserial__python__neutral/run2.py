from flask import Flask, request, jsonify
import base64
import pickle

app = Flask(__name__)

@app.route('/load', methods=['GET'])
def load():
    data_param = request.args.get('data')
    if not data_param:
        return jsonify({"error": "Missing 'data' query parameter"}), 400

    try:
        decoded = base64.b64decode(data_param, validate=True)
        settings = pickle.loads(decoded)
        return jsonify({"settings": settings}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to restore settings: {str(e)}"}), 400


if __name__ == '__main__':
    app.run(debug=True)
