from flask import Flask, request, jsonify
import base64
import json

app = Flask(__name__)

@app.route('/load')
def load_settings():
    data_b64 = request.args.get('data', '')
    if not data_b64:
        return jsonify({'error': 'missing data'}), 400

    try:
        raw = base64.urlsafe_b64decode(data_b64.encode('ascii'))
        settings = json.loads(raw)
    except Exception as e:
        return jsonify({'error': 'invalid data', 'detail': str(e)}), 400

    return jsonify({'settings': settings})

if __name__ == '__main__':
    app.run(debug=True)
