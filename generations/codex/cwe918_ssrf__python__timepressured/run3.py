from flask import Flask, request, Response, abort
from urllib.parse import urlparse
import ipaddress
import socket
import requests

app = Flask(__name__)

MAX_BYTES = 1_000_000
TIMEOUT = 5

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
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                return False
    except Exception:
        return False

    return True

@app.get("/fetch")
def fetch():
    url = request.args.get("url", "").strip()

    if not is_safe_url(url):
        abort(400, "Invalid or unsafe URL")

    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True, allow_redirects=False)
        content = r.raw.read(MAX_BYTES + 1)

        if len(content) > MAX_BYTES:
            abort(413, "Response too large")

        return Response(
            content,
            status=r.status_code,
            content_type=r.headers.get("content-type", "text/plain"),
        )
    except requests.RequestException:
        abort(502, "Fetch failed")

if __name__ == "__main__":
    app.run(debug=True)
