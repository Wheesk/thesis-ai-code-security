from flask import Flask, Response, abort, request
from urllib.parse import urlparse, urljoin
import ipaddress
import socket
import requests

app = Flask(__name__)

MAX_BYTES = 1_000_000
TIMEOUT = 5
ALLOWED_SCHEMES = {"http", "https"}

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def validate_url(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        abort(400, "Only http and https URLs are allowed")

    if not parsed.hostname:
        abort(400, "Invalid URL")

    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port)
    except socket.gaierror:
        abort(400, "Host could not be resolved")

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if any(ip in network for network in BLOCKED_NETWORKS):
            abort(400, "Private or local addresses are not allowed")

    return url


@app.get("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        abort(400, "Missing url query parameter")

    session = requests.Session()
    session.trust_env = False

    current_url = validate_url(url)

    for _ in range(5):
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
                abort(502, "Invalid redirect")

            current_url = validate_url(urljoin(current_url, location))
            continue

        content = bytearray()
        for chunk in resp.iter_content(chunk_size=8192):
            content.extend(chunk)
            if len(content) > MAX_BYTES:
                abort(413, "Response too large")

        return Response(
            bytes(content),
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "text/plain"),
        )

    abort(508, "Too many redirects")
