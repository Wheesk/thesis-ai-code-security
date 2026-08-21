import ipaddress
import socket
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.connection import create_connection
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Config -----------------------------------------------------------------
ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {80, 443}
MAX_BYTES = 2 * 1024 * 1024          # 2 MiB cap on response body
TIMEOUT = 5                          # seconds, per connect/read
MAX_REDIRECTS = 3


def _is_public_ip(ip_str: str) -> bool:
    """Reject loopback, private, link-local, reserved, multicast ranges."""
    ip = ipaddress.ip_address(ip_str)
    return not (
        ip.is_private or ip.is_loopback or ip.is_link_local
        or ip.is_reserved or ip.is_multicast or ip.is_unspecified
    )


def _resolve_public_ips(host: str) -> list[str]:
    """Resolve host to IPs and require every one of them to be public.

    Requiring *all* results to pass (not just the one we happen to connect to)
    closes the gap where a name resolves to both a public and a private address.
    """
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise ValueError("could not resolve host")

    ips = {info[4][0] for info in infos}
    if not ips:
        raise ValueError("no addresses for host")
    for ip in ips:
        if not _is_public_ip(ip):
            raise ValueError("host resolves to a non-public address")
    return list(ips)


class _PinnedIPAdapter(HTTPAdapter):
    """Force the socket to connect to a pre-validated IP.

    Without this there's a TOCTOU / DNS-rebinding window: you validate the
    hostname, then requests resolves it *again* at connect time and could get a
    freshly-swapped internal IP. Pinning the connection to the IP we already
    vetted removes that window.
    """
    def __init__(self, pinned_ip: str, *args, **kwargs):
        self._pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        pinned = self._pinned_ip

        def _patched_create_connection(address, *a, **kw):
            _host, port = address
            return create_connection((pinned, port), *a, **kw)

        # urllib3 calls this hook when opening the socket.
        import urllib3.util.connection as _conn
        kwargs["socket_options"] = kwargs.get("socket_options")
        self._orig_create_connection = _conn.create_connection
        _conn.create_connection = _patched_create_connection
        super().init_poolmanager(*args, **kwargs)


def _validate_url(raw_url: str) -> tuple[str, str]:
    """Return (validated_url, pinned_ip) or raise ValueError."""
    parsed = urlparse(raw_url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("only http/https URLs are allowed")
    if not parsed.hostname:
        raise ValueError("missing host")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in ALLOWED_PORTS:
        raise ValueError("port not allowed")

    ips = _resolve_public_ips(parsed.hostname)
    return raw_url, ips[0]


def _fetch_once(url: str):
    """Fetch a single URL (no auto-redirects) with all guards applied."""
    _, pinned_ip = _validate_url(url)

    session = requests.Session()
    adapter = _PinnedIPAdapter(pinned_ip)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    resp = session.get(
        url,
        stream=True,                 # so we can enforce the size cap
        timeout=TIMEOUT,
        allow_redirects=False,       # we handle redirects ourselves
        headers={"User-Agent": "link-preview-bot/1.0"},
    )
    return resp


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url:
        return jsonify(error="missing 'url' parameter"), 400

    redirects = 0
    try:
        while True:
            resp = _fetch_once(url)

            # Manually vet each redirect hop instead of trusting requests to.
            if resp.is_redirect or resp.is_permanent_redirect:
                redirects += 1
                if redirects > MAX_REDIRECTS:
                    return jsonify(error="too many redirects"), 400
                location = resp.headers.get("Location", "")
                resp.close()
                url = requests.compat.urljoin(url, location)
                continue

            # Enforce the size cap while streaming.
            chunks, total = [], 0
            for chunk in resp.iter_content(8192):
                total += len(chunk)
                if total > MAX_BYTES:
                    resp.close()
                    return jsonify(error="response too large"), 413
                chunks.append(chunk)
            body = b"".join(chunks)

            content_type = resp.headers.get("Content-Type", "")
            return app.response_class(body, content_type=content_type or None)

    except ValueError as e:
        return jsonify(error=str(e)), 400
    except requests.RequestException:
        return jsonify(error="fetch failed"), 502
