# -*- coding: utf-8 -*-
"""人文社科主题：候选清单（配额制，URL去重）"""
import json, os, random
from collections import Counter

random.seed(300)
BASE = os.path.dirname(os.path.abspath(__file__))

QUOTA = [
    ("history",        "nk_history.json",        7),
    ("law",            "nk_law.json",            7),
    ("law_court",      "nk_law_justice_courtroom.json", 2),
    ("justice",        "nk_justice.json",        4),
    ("finance",        "nk_finance.json",        7),
    ("finance_stock",  "nk_finance_stock_market.json", 3),
    ("economics",      "nk_economics.json",      4),
    ("politics",       "nk_politics.json",       5),
    ("politics_gov",   "nk_politics_government_building.json", 2),
    ("philosophy",     "nk_philosophy.json",     6),
    ("psychology",     "nk_psychology.json",     4),
    ("literature",     "nk_literature.json",     4),
    ("architecture",   "nk_architecture_classical.json", 5),
    ("statue",         "nk_statue_marble.json",  4),
    ("museum",         "nk_museum_artifact.json", 4),
    ("bookshelf",      "nk_bookshelf.json",      4),
    ("money_coins",    "nk_money_coins.json",    4),
    ("vintage_map",    "nk_vintage_map.json",    3),
    ("parliament",     "nk_parliament.json",     3),
    ("gov_building",   "nk_government.json",     2),
]

def load(fn):
    p = os.path.join(BASE, fn)
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p, encoding="utf-8")).get("data", [])
    except Exception:
        return []

manifest, seen = [], set()
for theme, fn, quota in QUOTA:
    items = [x for x in load(fn)
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
    print(f"  {t:16s} {c}")
