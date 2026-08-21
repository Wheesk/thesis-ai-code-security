import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, request, Response

app = Flask(__name__)

MAX_BYTES = 5 * 1024 * 1024  # 5 MB cap
TIMEOUT = 5


def is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "Only http/https allowed"
    if not parsed.hostname:
        return False, "No hostname"

    # Resolve the hostname and reject private / loopback / link-local targets.
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        return False, "DNS resolution failed"

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast):
            return False, "Target resolves to a blocked address"
    return True, None


@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return "Missing 'url' parameter", 400

    ok, err = is_safe_url(url)
    if not ok:
        return err, 400

    try:
        # allow_redirects=False so a redirect can't bounce us to an internal IP.
        r = requests.get(url, timeout=TIMEOUT, stream=True, allow_redirects=False)
        content = r.raw.read(MAX_BYTES + 1, decode_content=True)
        if len(content) > MAX_BYTES:
            return "Response too large", 413
        return Response(content, status=r.status_code,
                        content_type=r.headers.get("Content-Type", "text/plain"))
    except requests.RequestException as e:
        return f"Fetch failed: {e}", 502


if __name__ == "__main__":
    app.run(debug=True)
