from flask import Flask, request, Response, abort
import requests

app = Flask(__name__)

@app.get("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        abort(400, "Missing url query parameter")

    resp = requests.get(
        url,
        timeout=5,
        headers={"User-Agent": "LinkPreviewBot/1.0"},
    )
    resp.raise_for_status()

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "text/plain"),
    )
