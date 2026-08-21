from flask import Flask, request, Response, abort
from urllib.parse import urlsplit, urljoin
import ipaddress
import socket
import requests

app = Flask(__name__)

MAX_BYTES = 2_000_000
TIMEOUT = (3, 10)
REDIRECTS = {301, 302, 303, 307, 308}


def validate_url(url: str) -> None:
    if not url:
        abort(400, "Missing url query parameter")

    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"}:
        abort(400, "Only http and https URLs are allowed")

    if not parsed.hostname:
        abort(400, "Invalid URL")

    if parsed.username or parsed.password:
        abort(400, "Credentials in URLs are not allowed")

    try:
        port = parsed.port
    except ValueError:
        abort(400, "Invalid port")

    if port is not None and port not in {80, 443}:
        abort(400, "Only ports 80 and 443 are allowed")

    try:
        infos = socket.getaddrinfo(parsed.hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        abort(400, "Could not resolve host")

    ips = {info[4][0] for info in infos}
    if not ips:
        abort(400, "Could not resolve host")

    for ip_text in ips:
        ip = ipaddress.ip_address(ip_text)
        if not ip.is_global or ip.is_multicast:
            abort(400, "Host must resolve to a public IP address")


def fetch_checked(url: str):
    current_url = url

    for _ in range(5):
        validate_url(current_url)

        resp = requests.get(
            current_url,
            stream=True,
            timeout=TIMEOUT,
            allow_redirects=False,
            headers={"User-Agent": "demo-fetcher/1.0"},
        )

        if resp.status_code in REDIRECTS and resp.headers.get("Location"):
            next_url = urljoin(current_url, resp.headers["Location"])
            resp.close()
            current_url = next_url
            continue

        return resp

    abort(508, "Too many redirects")


@app.get("/fetch")
def fetch():
    url = request.args.get("url", "")

    try:
        resp = fetch_checked(url)
    except requests.RequestException as exc:
        abort(502, f"Fetch failed: {exc}")

    with resp:
        body = bytearray()

        for chunk in resp.iter_content(chunk_size=8192):
            if not chunk:
                continue

            body.extend(chunk)

            if len(body) > MAX_BYTES:
                abort(413, "Response too large")

        return Response(
            bytes(body),
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/octet-stream"),
        )


if __name__ == "__main__":
    app.run(debug=True)
