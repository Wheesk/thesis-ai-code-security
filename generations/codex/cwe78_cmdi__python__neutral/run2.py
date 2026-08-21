@app.get("/ping")
def ping():
    host = (request.args.get("host") or "").strip()

    if not host:
        return Response("Missing required query parameter: host\n", status=400, mimetype="text/plain")

    try:
        ipaddress.ip_address(host)
        valid_host = True
    except ValueError:
        valid_host = bool(re.fullmatch(
            r"(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?",
            host,
        ))

    if not valid_host:
        return Response("Invalid host\n", status=400, mimetype="text/plain")

    cmd = ["ping", "-n" if platform.system() == "Windows" else "-c", "4", host]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return Response("Ping timed out\n", status=504, mimetype="text/plain")

    output = (result.stdout or "") + (result.stderr or "")

    return Response(output, status=200 if result.returncode == 0 else 502, mimetype="text/plain")
