import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ALLOWED_SCHEMES = {"http", "https"}
MAX_BYTES = 2 * 1024 * 1024      # 2 MB cap
TIMEOUT = 5                       # seconds
MAX_REDIRECTS = 3


def is_public_ip(ip_str: str) -> bool:
    """Reject loopback, private, link-local, and other reserved ranges."""
    ip = ipaddress.ip_address(ip_str)
    return not (
        ip.is_private or ip.is_loopback or ip.is_link_local
        or ip.is_multicast or ip.is_reserved or ip.is_unspecified
    )


def resolve_and_validate(hostname: str) -> str:
    """Resolve a hostname and ensure every resolved IP is public.

    Returns a validated IP to connect to, closing the TOCTOU gap
    where DNS re-resolves to a different address after the check.
    """
    infos = socket.getaddrinfo(hostname, None)
    ips = {info[4][0] for info in infos}
    if not ips:
        raise ValueError("could not resolve host")
    for ip in ips:
        if not is_public_ip(ip):
            raise ValueError(f"resolves to non-public address: {ip}")
    return next(iter(ips))


def safe_fetch(url: str) -> requests.Response:
    """Fetch a URL, re-validating the target at every redirect hop."""
    for _ in range(MAX_REDIRECTS + 1):
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            raise ValueError(f"scheme not allowed: {parsed.scheme!r}")
        if not parsed.hostname:
            raise ValueError("missing hostname")

        # Validate before connecting. We resolve here, then pin the
        # connection to a validated IP so DNS can't be rebound between
        # the check and the request.
        validated_ip = resolve_and_validate(parsed.hostname)

        # Connect to the validated IP directly, but send the original
        # Host header so virtual hosting / TLS SNI still works.
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        connect_url = parsed._replace(
            netloc=f"{validated_ip}:{port}"
        ).geturl()

        resp = requests.get(
            connect_url,
            headers={"Host": parsed.hostname},
            timeout=TIMEOUT,
            allow_redirects=False,           # we handle redirects manually
            stream=True,
            verify=True,
        )

        if resp.is_redirect or resp.is_permanent_redirect:
            url = resp.headers["Location"]
            # Resolve relative redirects against the current URL
            url = requests.compat.urljoin(connect_url, url)
            resp.close()
            continue

        return resp

    raise ValueError("too many redirects")


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url:
        return jsonify(error="missing 'url' parameter"), 400

    try:
        resp = safe_fetch(url)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except requests.RequestException as e:
        return jsonify(error=f"fetch failed: {e}"), 502

    # Enforce the size cap while streaming so a huge/slow body can't
    # exhaust memory.
    chunks, total = [], 0
    for chunk in resp.iter_content(8192):
        total += len(chunk)
        if total > MAX_BYTES:
            resp.close()
            return jsonify(error="response too large"), 413
        chunks.append(chunk)
    resp.close()

    body = b"".join(chunks)
    content_type = resp.headers.get("Content-Type", "application/octet-stream")
    return app.response_class(body, content_type=content_type)


if __name__ == "__main__":
    app.run(debug=True)
