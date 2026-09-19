from pathlib import Path
import time, urllib.request

BASE="https://broast-today.adam72695.chatgpt.site/assets/"
FILES=["logo.webp","hero.webp","broast.webp","broast-spicy.webp","bucket.webp","bucket-spicy.webp","fillet.webp","shrimp.webp","strips.webp","strips-spicy.webp","chicken-burger.webp","chicken-meal.webp","beef-burger.webp","beef-meal.webp","zinger.webp","zinger-meal.webp","nuggets-wrap.webp","nuggets-meal.webp","fish-wrap.webp","fish-meal.webp","shrimp-wrap.webp","shrimp-meal.webp","zinger-wrap.webp","wrap-meal.webp","fries.webp","coleslaw.webp","spicy-sauce.webp","garlic.webp","storefront.webp","interior.webp","counter.webp","broast-today-menu.pdf"]
OUT=Path("assets")
OUT.mkdir(exist_ok=True)

headers={
    "User-Agent":"Mozilla/5.0 (compatible; BroastTodayBuild/1.0)",
    "Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
}

for name in FILES:
    dest=OUT/name
    ok=False
    last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(BASE+name,headers=headers)
            with urllib.request.urlopen(req,timeout=45) as r:
                data=r.read()
                if len(data)<100:
                    raise RuntimeError(f"too small: {len(data)} bytes")
                tmp=dest.with_suffix(dest.suffix+".tmp")
                tmp.write_bytes(data)
                tmp.replace(dest)
                print(f"{name}: {len(data)} bytes")
                ok=True
                break
        except Exception as e:
            last=e
            time.sleep(1.5*(attempt+1))
    if not ok:
        raise SystemExit(f"Failed to download {name}: {last}")
print("All production assets synced.")
