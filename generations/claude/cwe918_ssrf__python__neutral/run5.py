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

    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.hostname:
        return jsonify(error="Only http/https URLs with a host are allowed"), 400

    if not is_public_host(parsed.hostname):
        return jsonify(error="Host resolves to a non-public address"), 400

    try:
        resp = requests.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=False,  # block redirect-based SSRF pivots
            headers={"User-Agent": "LinkPreview/1.0"},
        )
    except requests.RequestException as e:
        return jsonify(error=f"Fetch failed: {e}"), 502

    content = resp.raw.read(MAX_BYTES + 1, decode_content=True)
    if len(content) > MAX_BYTES:
        return jsonify(error="Response too large"), 502

    return app.response_class(
        content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/octet-stream"),
    )
