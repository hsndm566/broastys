import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ["CF_TOKEN"]
ZONE = os.environ["CF_ZONE_ID"]
RESULT_PATH = os.environ.get("RESULT_PATH", "/result")
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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != RESULT_PATH:
            self.send_response(404)
            self.end_headers()
            return
        result = {
            "verify": request_json("https://api.cloudflare.com/client/v4/user/tokens/verify"),
            "zone": request_json(f"https://api.cloudflare.com/client/v4/zones/{ZONE}"),
            "broast": request_json(
                f"https://api.cloudflare.com/client/v4/zones/{ZONE}/dns_records?name=broast.hsndm.me"
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
