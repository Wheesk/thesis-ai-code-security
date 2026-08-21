from flask import Flask, request, Response
from urllib.parse import urlparse
import ipaddress
import socket
import requests

app = Flask(__name__)

MAX_BYTES = 1_000_000

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    if not parsed.hostname:
        return False

    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if not ip.is_global:
                return False
    except Exception:
        return False

    return True

@app.get("/fetch")
def fetch():
    url = request.args.get("url", "").strip()

    if not url:
        return {"error": "Missing url query parameter"}, 400

    if not is_safe_url(url):
        return {"error": "URL is not allowed"}, 400

    try:
        r = requests.get(
            url,
            timeout=5,
            allow_redirects=False,
            stream=True,
            headers={"User-Agent": "demo-fetcher/1.0"},
        )

        content = r.raw.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            return {"error": "Response too large"}, 413

        return Response(
            content,
            status=r.status_code,
            content_type=r.headers.get("content-type", "text/plain"),
        )

    except requests.RequestException as e:
        return {"error": str(e)}, 502

if __name__ == "__main__":
    app.run(debug=True)
