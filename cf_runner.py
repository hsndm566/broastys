import json
import os
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ["CF_TOKEN"]
ZONE = os.environ["CF_ZONE_ID"]
RESULT_PATH = os.environ.get("RESULT_PATH", "/result")
HOSTNAME = "broast.hsndm.me"
TARGET = "custom-domains.chatgpt.site"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def request_json(url, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode()
            return {"status": response.status, "body": json.loads(raw) if raw else None}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw
        return {"status": exc.code, "body": parsed}
    except Exception as exc:
        return {"status": 0, "body": {"error": type(exc).__name__, "message": str(exc)}}

def ensure_cname():
    base = f"https://api.cloudflare.com/client/v4/zones/{ZONE}/dns_records"
    current = request_json(base + "?name=" + urllib.parse.quote(HOSTNAME))
    if current["status"] != 200:
        return {"lookup": current, "action": "lookup_failed"}

    records = current.get("body", {}).get("result", [])
    if records:
        record = records[0]
        if record.get("type") == "CNAME" and record.get("content", "").rstrip(".") == TARGET:
            return {"lookup": current, "action": "already_correct", "record": record}
        return {"lookup": current, "action": "conflict", "record": record}

    created = request_json(
        base,
        method="POST",
        body={
            "type": "CNAME",
            "name": HOSTNAME,
            "content": TARGET,
            "ttl": 1,
            "proxied": False,
            "comment": "ChatGPT Sites custom domain routing for Broast Today",
        },
    )
    return {"lookup": current, "action": "created", "create": created}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != RESULT_PATH:
            self.send_response(404)
            self.end_headers()
            return

        result = {
            "verify": request_json("https://api.cloudflare.com/client/v4/user/tokens/verify"),
            "cname": ensure_cname(),
            "after": request_json(
                f"https://api.cloudflare.com/client/v4/zones/{ZONE}/dns_records?name={urllib.parse.quote(HOSTNAME)}"
            ),
        }

        payload = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_):
        pass

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
