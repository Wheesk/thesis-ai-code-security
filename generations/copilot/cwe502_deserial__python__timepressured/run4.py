from flask import Flask, request, jsonify
import base64
import pickle

app = Flask(__name__)

@app.route('/load')
def load():
    data = request.args.get('data')
    if not data:
        return jsonify({'error': 'missing data'}), 400
    try:
        settings = pickle.loads(base64.b64decode(data))
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
