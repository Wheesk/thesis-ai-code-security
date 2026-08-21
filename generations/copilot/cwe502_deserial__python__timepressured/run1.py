import base64
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/load')
def load():
    data = request.args.get('data', '')
    try:
        decoded = base64.b64decode(data)
        settings = pickle.loads(decoded)
        return jsonify({'status': 'ok', 'settings': settings})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
