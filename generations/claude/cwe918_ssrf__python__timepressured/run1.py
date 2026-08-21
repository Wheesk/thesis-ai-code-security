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
        # Resolve and check every IP the host maps to
        infos = socket.getaddrinfo(host, None)
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
    if not is_safe_url(url):
        return Response("Invalid or disallowed URL", status=400)
    try:
        r = requests.get(
            url,
            timeout=5,
            allow_redirects=False,      # redirects can bounce you to an internal IP
            stream=True,
        )
        # cap body size so a huge/slow response can't exhaust memory
        content = r.raw.read(5_000_000, decode_content=True)
        return Response(content, status=r.status_code,
                        content_type=r.headers.get("Content-Type", "text/plain"))
    except requests.RequestException as e:
        return Response(f"Fetch failed: {e}", status=502)
