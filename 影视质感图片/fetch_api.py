# -*- coding: utf-8 -*-
"""影视方向：按关键词抓取 nkimages 元数据 -> nk_<theme>.json"""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))

QUERIES = [
    ("anime",          "anime animation art"),
    ("costume_drama",  "ancient chinese costume drama"),
    ("palace_drama",   "imperial palace interior"),
    ("urban_drama",    "urban city life street"),
    ("crime_drama",    "crime scene investigation"),
    ("scifi",          "sci-fi futuristic"),
    ("period_drama",   "vintage retro nostalgia"),
    ("wuxia",          "martial arts sword"),
    ("spy_thriller",   "spy thriller noir detective"),
    ("workplace",      "modern office workplace"),
    ("romance",        "romantic couple sunset"),
    ("family_drama",   "family living room"),
    ("military",       "military soldiers"),
    ("xianxia",        "chinese fantasy immortal"),
    ("film_set",       "film set cinema camera"),
    ("cinematic",      "cinematic movie scene"),
]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for theme, q in QUERIES:
    out = os.path.join(BASE, f"nk_{theme}.json")
    if os.path.exists(out) and os.path.getsize(out) > 500:
        print(f"skip {theme} (cached)")
        continue
    url = ("https://nkimages.com/api/public/images?source=clawhub&q="
           + urllib.parse.quote(q) + "&per_page=80&orientation=landscape")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        items = data.get("data") or []
        json.dump({"data": items}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"{theme:15s} {len(items):3d} items  [{q}]")
    except Exception as e:
        print(f"{theme:15s} ERR {type(e).__name__}: {e}")
    time.sleep(1.5)
print("FETCH_DONE")
