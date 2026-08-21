from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)


@app.route('/ping')
def ping():
    host = request.args.get('host')
    if not host:
        return jsonify({'error': 'Missing host parameter'}), 400

    try:
        result = subprocess.run(
            ['ping', '-c', '4', host],
            capture_output=True,
            text=True,
            timeout=30
        )
        return jsonify({
            'host': host,
            'returncode': result.returncode,
            'output': result.stdout + result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Ping timed out'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
