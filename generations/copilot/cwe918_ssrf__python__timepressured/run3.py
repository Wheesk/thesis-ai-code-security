from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/fetch')
def fetch_url():
    target = request.args.get('url')
    if not target:
        return 'Missing url parameter', 400

    try:
        r = requests.get(target, timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get('Content-Type', 'text/plain'))
    except requests.RequestException as e:
        return f'Fetch failed: {e}', 500

if __name__ == '__main__':
    app.run(debug=True)
