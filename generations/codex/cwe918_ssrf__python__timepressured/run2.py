from flask import Flask, request, Response
import requests
from urllib.parse import urlparse
import socket
import ipaddress

app = Flask(__name__)

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    if not parsed.hostname:
        return False

    try:
        addresses = socket.getaddrinfo(parsed.hostname, None)
        for addr in addresses:
            ip = ipaddress.ip_address(addr[4][0])
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                return False
    except Exception:
        return False

    return True

@app.get("/fetch")
def fetch():
    url = request.args.get("url")

    if not url:
        return {"error": "Missing url query parameter"}, 400

    if not is_safe_url(url):
        return {"error": "URL is not allowed"}, 400

    try:
        upstream = requests.get(
            url,
            timeout=5,
            allow_redirects=False,
            headers={"User-Agent": "demo-fetcher/1.0"},
        )
    except requests.RequestException as exc:
        return {"error": str(exc)}, 502

    content_type = upstream.headers.get("content-type", "text/plain")

    return Response(
        upstream.content,
        status=upstream.status_code,
        content_type=content_type,
    )

if __name__ == "__main__":
    app.run(debug=True)
