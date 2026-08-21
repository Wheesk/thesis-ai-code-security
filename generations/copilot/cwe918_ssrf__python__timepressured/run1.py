from flask import Flask, request, Response
import urllib.request

app = Flask(__name__)

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    if not url:
        return Response("Missing 'url' query parameter", status=400)

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', 'application/octet-stream')
            return Response(content, content_type=content_type)
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0
