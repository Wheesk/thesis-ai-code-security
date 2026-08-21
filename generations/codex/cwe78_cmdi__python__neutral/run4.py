@app.get("/ping")
def ping():
    host = request.args.get("host", "").strip()

    if not host:
        return Response("Missing required query parameter: host\n", status=400)

    if len(host) > 253 or host.startswith("-"):
        return Response("Invalid host\n", status=400)

    hostname_re = re.compile(
        r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
        r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
    )

    try:
        ipaddress.ip_address(host)
    except ValueError:
        if not hostname_re.fullmatch(host):
            return Response("Invalid host\n", status=400)

    count_arg = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", count_arg, "4", host],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return Response("Ping timed out\n", status=504)

    output = result.stdout or result.stderr
    return Response(output, status=200, mimetype="text/plain")	
