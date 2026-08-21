import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

ALLOWED_SCHEMES = {"http", "https"}
REQUEST_TIMEOUT = 5                     # seconds
MAX_CONTENT_BYTES = 2 * 1024 * 1024     # 2 MB cap
MAX_REDIRECTS = 5


def _ip_is_disallowed(ip) -> bool:
    """Block anything that isn't a normal, globally-routable public address."""
    return (
        ip.is_private        # 10/8, 172.16/12, 192.168/16, fc00::/7
        or ip.is_loopback    # 127/8, ::1
        or ip.is_link_local  # 169.254/16 (incl. cloud metadata), fe80::/10
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified  # 0.0.0.0, ::
    )


def validate_url(url: str) -> None:
    """Raise ValueError if the URL is unsafe to fetch."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("Only http and https URLs are allowed")
    if not parsed.hostname:
        raise ValueError("URL has no host")

    # Resolve and check EVERY address the host maps to.
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        raise ValueError("Could not resolve host")

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        # Normalize IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1) before checking.
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if _ip_is_disallowed(ip):
            raise ValueError(f"Blocked address: {ip}")


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url:
        return jsonify(error="Missing 'url' parameter"), 400

    try:
        # Follow redirects manually so we re-validate each hop.
        # (A public URL can 302 to http://169.254.169.254/ otherwise.)
        for _ in range(MAX_REDIRECTS + 1):
            validate_url(url)
            resp = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
                stream=True,
                headers={"User-Agent": "LinkPreviewBot/1.0"},
            )
            if resp.is_redirect:
                url = requests.compat.urljoin(url, resp.headers["Location"])
                resp.close()
                continue
            break
        else:
            return jsonify(error="Too many redirects"), 400
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except requests.RequestException:
        # Don't leak internal error detail back to the caller.
        return jsonify(error="Failed to fetch URL"), 502

    # Enforce the size cap while streaming so a huge body can't exhaust memory.
    chunks, total = [], 0
    for chunk in resp.iter_content(8192):
        total += len(chunk)
        if total > MAX_CONTENT_BYTES:
            resp.close()
            return jsonify(error="Response too large"), 413
        chunks.append(chunk)
    resp.close()

    content_type = resp.headers.get("Content-Type", "application/octet-stream")
    return Response(b"".join(chunks), content_type=content_type)
