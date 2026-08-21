from flask import Flask, request, Response, jsonify
import ipaddress
import socket
from urllib.parse import urlparse, urljoin

import requests

app = Flask(__name__)

MAX_BYTES = 2_000_000
TIMEOUT = 5
MAX_REDIRECTS = 3


def is_public_host(hostname: str) -> bool:
    try:
        addresses = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False

    for addr in addresses:
        ip = ipaddress.ip_address(addr[4][0])
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
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are allowed")

    if not parsed.hostname:
        raise ValueError("URL must include a hostname")

    if not is_public_host(parsed.hostname):
        raise ValueError("Host is not allowed")

    return url


@app.get("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return jsonify(error="Missing url query parameter"), 400

    try:
        url = validate_url(url)

        for _ in range(MAX_REDIRECTS + 1):
            resp = requests.get(
                url,
                timeout=TIMEOUT,
                stream=True,
                allow_redirects=False,
                headers={"User-Agent": "demo-fetcher/1.0"},
            )

            if resp.is_redirect:
                location = resp.headers.get("Location")
                if not location:
                    break
                url = validate_url(urljoin(url, location))
                continue

            content = b""
            for chunk in resp.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > MAX_BYTES:
                    return jsonify(error="Response too large"), 413

            return Response(
                content,
                status=resp.status_code,
                content_type=resp.headers.get("content-type", "text/plain"),
            )

        return jsonify(error="Too many redirects"), 400

    except ValueError as e:
        return jsonify(error=str(e)), 400
    except requests.RequestException as e:
        return jsonify(error=f"Fetch failed: {e}"), 502


if __name__ == "__main__":
    app.run(debug=True)
