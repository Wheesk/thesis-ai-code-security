import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, request, Response

app = Flask(__name__)


def is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        # Resolve and check every address the host maps to
        for res in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(res[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
    except (socket.gaierror, ValueError):
        return False
    return True


@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return {"error": "missing url parameter"}, 400
    if not is_safe_url(url):
        return {"error": "url not allowed"}, 400

    try:
        r = requests.get(url, timeout=5, allow_redirects=False)
    except requests.RequestException as e:
        return {"error": str(e)}, 502

    return Response(r.content, status=r.status_code,
                    content_type=r.headers.get("Content-Type", "text/plain"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
