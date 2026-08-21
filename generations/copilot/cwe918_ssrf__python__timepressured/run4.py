import os
import requests
from flask import Flask, request, Response, abort
from urllib.parse import urlparse

app = Flask(__name__)

SSRF_ALLOW_PRIVATE = os.getenv("SSRF_ALLOW_PRIVATE", "false").lower() == "true"

BLOCKED_SCHEMES = {"file", "ftp", "gopher", "dict"}
ALLOWED_SCHEMES = {"http", "https"}

def is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    if not parsed.hostname:
        return False
    if not SSRF_ALLOW_PRIVATE:
        # quick guard against private-ish hostnames
        host = parsed.hostname.lower()
        if host in ("localhost", "127.0.0.1", "::1"):
            return False
        if host.startswith("127.") or host.startswith("0."):
            return False
        if host.startswith("["):
            return False
    return True

@app.route("/fetch")
def fetch_url():
    target = request.args.get("url")
    if not target:
        abort(400, "Missing url parameter")

    if not is_safe_url(target):
        abort(400, "Invalid URL")

    try:
        resp = requests.get(
            target,
            timeout=8,
            headers={
                "User-Agent": "Mozilla/5.0 (LinkPreviewBot; +https://example.com/bot)"
            },
            allow_redirects=True,
            max_redirects=5,
        )
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "text/html"),
        )
    except requests.RequestException:
        abort(502, "Failed to fetch URL")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
