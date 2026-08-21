from flask import Flask, request, jsonify
import ipaddress
import socket
from urllib.parse import urlparse
import requests

app = Flask(__name__)

ALLOWED_SCHEMES = {"http", "https"}
MAX_BYTES = 2 * 1024 * 1024  # 2 MB cap
TIMEOUT = 5


def is_public_host(hostname):
    """Resolve hostname and reject private/loopback/link-local/reserved addresses (SSRF guard)."""
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
    url = request.args.get("url")
    if not url:
        return jsonify(error="missing url parameter"), 400

    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return jsonify(error="only http/https URLs allowed"), 400
    if not parsed.hostname:
        return jsonify(error="invalid url"), 400
    if not is_public_host(parsed.hostname):
        return jsonify(error="host not permitted"), 403

    try:
        resp = requests.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=False,  # prevents redirect-based SSRF bypass
            headers={"User-Agent": "LinkPreview/1.0"},
        )
    except requests.RequestException as e:
        return jsonify(error=f"fetch failed: {e}"), 502

    content = b""
    for chunk in resp.iter_content(8192):
        content += chunk
        if len(content) > MAX_BYTES:
            content = content[:MAX_BYTES]
            break

    return app.response_class(
        content,
        status=resp.status_code,
     
   content_type=resp.headers.get("Content-Type", "application/octet-stream"),
    )
