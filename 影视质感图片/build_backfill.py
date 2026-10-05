# -*- coding: utf-8 -*-
"""回填：真动漫(user-generated) + 军旅soldier + anime scenery + 汉服，编号从94续起"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
main = json.load(open(os.path.join(BASE, "manifest.json"), encoding="utf-8"))
used = {m["id"] for m in main}
start_idx = len(main) + 1  # 94

def load(fn):
    p = os.path.join(BASE, fn)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8")).get("data", [])

pools = [
    ("anime",        [x for x in load("nk_anime.json") if x.get("category") == "user-generated"]),
    ("anime",        load("nk_anime_backfill.json")),
    ("anime",        load("nk_anime_backfill2.json")),
    ("military",     load("nk_military_backfill.json")),
    ("costume_drama", load("nk_costume_backfill.json")),
]

backfill, seen = [], set(used)
for theme, items in pools:
    ok = [x for x in items if x.get("orientation") == "landscape"
          and (x.get("width") or 0) >= 1200 and x["id"] not in seen]
    for x in ok:
        seen.add(x["id"])
        backfill.append({"id": x["id"], "theme": theme, "url": x["url"],
                         "width": x.get("width"), "height": x.get("height"),
                         "name": x.get("name", ""), "niche": x.get("niche", ""),
                         "category": x.get("category", ""), "_idx": start_idx + len(backfill)})

json.dump(backfill, open(os.path.join(BASE, "manifest_backfill.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("backfill:", len(backfill))
from collections import Counter
print(Counter(b["theme"] for b in backfill))

# 下载（复用 download.py 逻辑，显式 _idx）
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
RAW = os.path.join(BASE, "raw")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def dl(item):
    idx = item["_idx"]
    ext = os.path.splitext(item["url"])[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    fname = f"{idx:02d}_{item['theme']}{ext}"
    path = os.path.join(RAW, fname)
    if os.path.exists(path) and os.path.getsize(path) > 50_000:
        return fname, "skip"
    try:
        req = urllib.request.Request(item["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
        if len(data) < 30_000:
            return fname, "too_small"
        open(path, "wb").write(data)
        return fname, "ok"
    except Exception as e:
        return fname, f"err:{type(e).__name__}"

ok = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = [ex.submit(dl, m) for m in backfill]
    for fu in as_completed(futs):
        fname, st = fu.result()
        if st in ("ok", "skip"):
            ok += 1
        else:
            print("FAIL", fname, st)
print(f"BACKFILL_DL_DONE ok={ok}/{len(backfill)}")
