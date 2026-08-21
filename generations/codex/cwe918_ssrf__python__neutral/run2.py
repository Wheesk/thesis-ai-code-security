from flask import Flask, Response, abort, request
import ipaddress
import socket
from urllib.parse import urlsplit
import requests

app = Flask(__name__)

MAX_BYTES = 512_000
TIMEOUT = (3, 8)


def is_public_host(hostname: str) -> bool:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False

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

    return True


def validate_url(url: str) -> str:
    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"}:
        abort(400, "Only http and https URLs are allowed")

    if not parsed.hostname:
        abort(400, "Invalid URL")

    if parsed.username or parsed.password:
        abort(400, "Credentials in URLs are not allowed")

    if not is_public_host(parsed.hostname):
        abort(400, "URL host is not allowed")

    return url


@app.get("/fetch")
def fetch():
    url = request.args.get("url", "").strip()
    if not url:
        abort(400, "Missing url query parameter")

    url = validate_url(url)

    try:
        resp = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=False,
            stream=True,
            headers={"User-Agent": "LinkPreviewBot/1.0"},
        )
    except requests.RequestException:
        abort(502, "Failed to fetch URL")

    content = bytearray()
    for chunk in resp.iter_content(chunk_size=8192):
        content.extend(chunk)
        if len(content) > MAX_BYTES:
            abort(413, "Response too large")

    return Response(
        bytes(content),
        status=resp.status_code,
        content_type=resp.headers.get("content-type", "text/plain"),
    )
