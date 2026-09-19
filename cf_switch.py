import json
import os
import urllib.parse
import urllib.request

TOKEN = os.environ["CF_TOKEN"]
ZONE = os.environ.get("CF_ZONE_ID", "1b359977185c0289fab954a706c01a37")
HOST = "broast.hsndm.me"
OLD_TARGET = "custom-domains.chatgpt.site"
NEW_TARGET = "zyicl1u0.up.railway.app"
BASE = f"https://api.cloudflare.com/client/v4/zones/{ZONE}/dns_records"
HEADERS = {"Authorization":"Bearer "+TOKEN,"Content-Type":"application/json"}

def request(url, method="GET", body=None):
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(url,data=data,headers=HEADERS,method=method)
    with urllib.request.urlopen(req,timeout=30) as response:
        raw=response.read().decode()
        return json.loads(raw) if raw else {}

lookup=request(BASE+"?name="+urllib.parse.quote(HOST))
records=lookup.get("result",[])
if len(records)!=1:
    raise SystemExit(f"Expected one record; found {len(records)}")
record=records[0]
if record.get("type")!="CNAME":
    raise SystemExit("Refusing non-CNAME record")
current=(record.get("content") or "").rstrip(".")
if current==NEW_TARGET:
    print("Cloudflare DNS already points Broast to Railway.")
elif current==OLD_TARGET:
    payload={"type":"CNAME","name":HOST,"content":NEW_TARGET,"ttl":1,"proxied":False,
             "comment":"Broast Today hardened production hosting on Railway"}
    out=request(BASE+"/"+record["id"],method="PUT",body=payload)
    if not out.get("success"):
        raise SystemExit("DNS cutover failed")
    print("Cloudflare DNS cutover to Railway completed successfully.")
else:
    raise SystemExit(f"Refusing unexpected target: {current}")
