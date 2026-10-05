# -*- coding: utf-8 -*-
"""第三轮：anime 换精准词、military 补soldier；单独存 nk2_*.json 供回填"""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
QUERIES = [
    ("anime_backfill", "anime girl illustration"),
    ("anime_backfill2", "japanese anime scenery"),
    ("military_backfill", "soldier army uniform"),
    ("costume_backfill", "ancient chinese beauty hanfu"),
]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for theme, q in QUERIES:
    out = os.path.join(BASE, f"nk_{theme}.json")
    url = ("https://nkimages.com/api/public/images?source=clawhub&q="
           + urllib.parse.quote(q) + "&per_page=80&orientation=landscape")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        items = data.get("data") or []
        json.dump({"data": items}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"{theme:18s} {len(items):3d}  [{q}]")
    except Exception as e:
        print(f"{theme:18s} ERR {type(e).__name__}: {e}")
    time.sleep(1.5)

# 查看 anime 原池 user-generated 项
d = json.load(open(os.path.join(BASE, "nk_anime.json"), encoding="utf-8"))["data"]
ug = [x for x in d if x.get("category") == "user-generated"]
print("\n原池 user-generated:", len(ug))
for x in ug:
    print("  -", x.get("name", "")[:75])
print("BACKFILL_FETCH_DONE")
