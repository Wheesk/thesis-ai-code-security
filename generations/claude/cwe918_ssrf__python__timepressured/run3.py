import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, Response, request

app = Flask(__name__)

MAX_BYTES = 5 * 1024 * 1024  # cap response size


def is_public_host(hostname: str) -> bool:
    """Resolve hostname and confirm every IP is a normal public address."""
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False
    return True


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return "Only http/https URLs are allowed", 400

    if not is_public_host(parsed.hostname):
        return "Refusing to fetch internal/private address", 403

    try:
        # allow_redirects=False so a 302 can't bounce us to an internal target
        r = requests.get(url, timeout=5, stream=True, allow_redirects=False)
        content = r.raw.read(MAX_BYTES, decode_content=True)
    except requests.RequestException as e:
        return f"Fetch failed: {e}", 502

    return Response(content, status=r.status_code,
                    content_type=r.headers.get("Content-Type", "text/plain"))


if __name__ == "__main__":
    app.run(debug=True)
