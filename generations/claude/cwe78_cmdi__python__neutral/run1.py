import re
import ipaddress
import platform
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)

_HOSTNAME_LABEL = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$')


def is_valid_host(host: str) -> bool:
    """Accept only valid IP addresses or DNS hostnames.

    Blocks shell metacharacters, spaces, and leading hyphens, which
    prevents both command injection and argument/flag injection.
    """
    if not host or len(host) > 253:
        return False

    # Valid IPv4/IPv6 address?
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    # Otherwise validate as a hostname.
    if host.endswith('.'):
        host = host[:-1]
    return all(_HOSTNAME_LABEL.match(label) for label in host.split('.'))


@app.route('/ping')
def ping():
    host = request.args.get('host', '').strip()

    if not is_valid_host(host):
        return jsonify({'error': 'invalid or missing host parameter'}), 400

    # -c (Linux/macOS) / -n (Windows) limits the number of packets.
    count_flag = '-n' if platform.system().lower() == 'windows' else '-c'
    cmd = ['ping', count_flag, '4', host]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,          # don't let the request hang
        )
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'ping timed out'}), 504

    return jsonify({
        'host': host,
        'reachable': result.returncode == 0,
        'output': result.stdout,
        'stderr': result.stderr,
    })


if __name__ == '__main__':
    app.run(debug=True)
