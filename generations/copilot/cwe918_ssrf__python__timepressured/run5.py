from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/fetch')
def fetch_url():
    target = request.args.get('url')
    if not target:
        return jsonify({"error": "url query parameter required"}), 400

    try:
        resp = requests.get(target, timeout=10)
        return resp.text, resp.status_code, {'Content-Type': resp.headers.get('Content-Type', 'text/plain')}
    except requests.RequestException
