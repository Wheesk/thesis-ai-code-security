from flask import Flask, request, abort, Response
import ipaddress
import socket
from urllib.parse import urljoin, urlparse
import requests

app = Flask(__name__)

MAX_BYTES = 1_000_000
MAX_REDIRECTS = 3
TIMEOUT = (2, 5)


def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    if not parsed.hostname:
        return False

    try:
        addresses = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        return False

    for addr in addresses:
        ip = ipaddress.ip_address(addr[4][0])
        if not ip.is_global:
            return False

    return True


@app.get("/fetch")
def fetch():
    url = request.args.get("url", "").strip()

    if not url or not is_safe_url(url):
        abort(400, "Invalid URL")

    session = requests.Session()
    current_url = url

    for _ in range(MAX_REDIRECTS + 1):
        if not is_safe_url(current_url):
            abort(400, "Unsafe redirect URL")

        resp = session.get(
            current_url,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=False,
            headers={"User-Agent": "LinkPreviewBot/1.0"},
        )

        if resp.is_redirect:
            location = resp.headers.get("Location")
            if not location:
                abort(502, "Bad redirect")

            current_url = urljoin(current_url, location)
            continue

        content = b""
        for chunk in resp.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > MAX_BYTES:
                abort(413, "Response too large")

        return Response(
            content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "text/plain"),
        )

    abort(508, "Too many redirects")
