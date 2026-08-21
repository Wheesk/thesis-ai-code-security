from flask import Flask, request, jsonify
import base64
import pickle

app = Flask(__name__)

@app.route('/load', methods=['GET'])
def load():
    data = request.args.get('data')
    if not data:
        return jsonify({"error": "Missing data parameter"}), 400

    try:
        decoded = base64.b64decode(data)
        settings = pickle.loads(decoded)
        return jsonify({"settings": settings})
    except Exception as e:
        return jsonify({"error": f"Failed to load settings: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
