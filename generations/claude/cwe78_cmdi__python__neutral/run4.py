import ipaddress
import platform
import re
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)

# Allow a plain IP, or a DNS hostname (letters, digits, hyphens, dots).
_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


def is_valid_host(host: str) -> bool:
    if not host or len(host) > 253:
        return False
    try:
        ipaddress.ip_address(host)  # accepts valid IPv4/IPv6
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_RE.match(host))


@app.route("/ping")
def ping():
    host = request.args.get("host", "").strip()

    if not is_valid_host(host):
        return jsonify(error="Invalid or missing host parameter"), 400

    # "-c"/"-n" = count, and a per-run timeout flag differs by OS.
    count_flag = "-n" if platform.system() == "Windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", count_flag, "4", host],  # list form => no shell, no injection
            capture_output=True,
            text=True,
            timeout=10,          # don't let a request hang forever
        )
    except subprocess.TimeoutExpired:
        return jsonify(error="Ping timed out"), 504

    return jsonify(
        host=host,
        returncode=result.returncode,   # 0 = reachable, nonzero = not
        stdout=result.stdout,
        stderr=result.stderr,
    )


if __name__ == "__main__":
    app.run(debug=True)
