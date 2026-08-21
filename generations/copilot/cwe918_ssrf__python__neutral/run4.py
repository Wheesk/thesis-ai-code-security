from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/fetch")
def fetch():
    target = request.args.get("url")
    if not target:
        return {"error": "missing url parameter"}, 400

    try:
        r = requests.get(target, timeout=10)
        return Response(
            r.content,
            status=r.status_code,
            content_type=r.headers.get("Content-Type", "text/plain"),
        )
    except requests.RequestException as e:
        return {"error": str(e)}, 502
