# -*- coding: utf-8 -*-
"""第二轮：弱命中主题换关键词补抓，合并去重进原 nk_<theme>.json"""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))

QUERIES = [
    ("wuxia",         "kung fu martial arts master"),
    ("military",      "war battlefield tank"),
    ("film_set",      "movie clapperboard cinema"),
    ("costume_drama", "hanfu traditional chinese costume"),
    ("spy_thriller",  "detective noir city night"),
    ("cinematic",     "cinema theater audience"),
    ("crime_drama",   "police detective investigation"),
    ("xianxia",       "chinese fantasy dragon mountain"),
    ("urban_drama",   "city skyline night"),
    ("period_drama",  "old shanghai 1930s"),
    ("scifi",         "space spaceship future"),
    ("palace_drama",  "ancient chinese palace"),
]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for theme, q in QUERIES:
    out = os.path.join(BASE, f"nk_{theme}.json")
    try:
        old = json.load(open(out, encoding="utf-8")).get("data", []) if os.path.exists(out) else []
    except Exception:
        old = []
    seen = {x["id"] for x in old}
    url = ("https://nkimages.com/api/public/images?source=clawhub&q="
           + urllib.parse.quote(q) + "&per_page=80&orientation=landscape")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        new = [x for x in (data.get("data") or []) if x["id"] not in seen]
        json.dump({"data": old + new}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"{theme:15s} +{len(new):3d} -> {len(old)+len(new):3d}  [{q}]")
    except Exception as e:
        print(f"{theme:15s} ERR {type(e).__name__}: {e}")
    time.sleep(1.5)
print("FETCH2_DONE")
