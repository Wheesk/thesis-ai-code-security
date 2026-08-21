import ipaddress
import re
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)

# Labels of 1-63 chars, no leading/trailing hyphen, 253 chars total.
HOSTNAME_RE = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
)

PING_COUNT = "3"
PING_DEADLINE = "5"      # seconds, passed to ping itself
SUBPROCESS_TIMEOUT = 10  # hard backstop if ping misbehaves


def is_valid_host(host: str) -> bool:
    if not host or len(host) > 253:
        return False
    try:
        ipaddress.ip_address(host)  # accepts IPv4 and IPv6 literals
        return True
    except ValueError:
        pass
    return bool(HOSTNAME_RE.match(host))


@app.get("/ping")
def ping():
    host = request.args.get("host", "").strip()

    if not is_valid_host(host):
        return jsonify(error="Invalid or missing 'host' parameter"), 400

    cmd = ["ping", "-c", PING_COUNT, "-w", PING_DEADLINE, host]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            shell=False,      # never True here
            check=False,
        )
    except subprocess.TimeoutExpired:
        return jsonify(host=host, error="Ping timed out"), 504
    except FileNotFoundError:
        return jsonify(error="ping binary not available on server"), 500

    return jsonify(
        host=host,
        reachable=(proc.returncode == 0),
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
