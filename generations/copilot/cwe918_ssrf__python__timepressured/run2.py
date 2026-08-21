from flask import Flask, request, Response
import requests

app = Flask(__name__)


@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return {"error": "url query param required"}, 400

    r = requests.get(url, timeout=15)
    return Response(r.content, status=r.status_code, content_type=r.headers.get("content-type", "text/plain"))
