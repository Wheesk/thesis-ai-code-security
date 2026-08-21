from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    if not url:
        return {"error": "Missing 'url' query parameter"}, 400

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}, 502

    return Response(r.content, content_type=r.headers.get('Content-Type', 'text/html'))
