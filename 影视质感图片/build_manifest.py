# -*- coding: utf-8 -*-
"""影视主题：候选清单（配额制，跨主题ID去重）"""
import json, os, random
from collections import Counter

random.seed(410)
BASE = os.path.dirname(os.path.abspath(__file__))

# (theme, 文件, 配额)  配额按图源库存微调，保证 16 类型全覆盖
QUOTA = [
    ("anime",          8),
    ("costume_drama",  5),
    ("palace_drama",   7),
    ("urban_drama",    8),
    ("crime_drama",    5),
    ("scifi",          6),
    ("period_drama",   6),
    ("wuxia",          3),
    ("spy_thriller",   4),
    ("workplace",      7),
    ("romance",        7),
    ("family_drama",   7),
    ("military",       4),
    ("xianxia",        5),
    ("film_set",       7),
    ("cinematic",      4),
]

def load(theme):
    p = os.path.join(BASE, f"nk_{theme}.json")
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p, encoding="utf-8")).get("data", [])
    except Exception:
        return []

manifest, seen = [], set()
for theme, quota in QUOTA:
    items = [x for x in load(theme)
             if x.get("orientation") == "landscape"
             and (x.get("width") or 0) >= 1200
             and x["id"] not in seen]
    random.shuffle(items)
    for x in items[:quota]:
        seen.add(x["id"])
        manifest.append({"id": x["id"], "theme": theme, "url": x["url"],
                         "width": x.get("width"), "height": x.get("height"),
                         "name": x.get("name", ""), "niche": x.get("niche", ""),
                         "category": x.get("category", "")})

json.dump(manifest, open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("total:", len(manifest))
for t, c in Counter(m["theme"] for m in manifest).items():
    print(f"  {t:15s} {c}")
