import ipaddress
import re
import socket
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)

PING_COUNT = 4
PING_DEADLINE = 5        # seconds, passed to ping
SUBPROCESS_TIMEOUT = 10  # hard backstop if ping misbehaves
BLOCK_NON_GLOBAL = True  # refuse loopback/private/link-local targets

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}\.?$)"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\.?$"
)


def resolve_target(host):
    """Return (ip_address, None) or (None, error_message)."""
    if not host or not HOSTNAME_RE.match(host):
        return None, "invalid host"

    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return None, "could not resolve host"

    ip = ipaddress.ip_address(infos[0][4][0])
    if BLOCK_NON_GLOBAL and not ip.is_global:
        return None, "target address not allowed"
    return ip, None


@app.get("/ping")
def ping():
    host = request.args.get("host", "").strip()

    ip, err = resolve_target(host)
    if err:
        return jsonify(error=err), 400

    cmd = [
        "ping",
        "-6" if ip.version == 6 else "-4",
        "-c", str(PING_COUNT),
        "-w", str(PING_DEADLINE),
        "-n",                      # no reverse DNS on the output
        str(ip),
    ]

    try:
        proc = subprocess.run(
            cmd,
            shell=False,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return jsonify(error="ping timed out"), 504
    except FileNotFoundError:
        return jsonify(error="ping not available on server"), 500

    return jsonify(
        host=host,
        address=str(ip),
        reachable=proc.returncode == 0,
        exit_code=proc.returncode,
        output=proc.stdout[-4000:],
    )
