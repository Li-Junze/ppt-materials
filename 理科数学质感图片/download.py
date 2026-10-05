# -*- coding: utf-8 -*-
"""并发下载 manifest.json 中的图片到 raw/ 目录"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
os.makedirs(RAW, exist_ok=True)

with open(os.path.join(BASE, "manifest.json"), encoding="utf-8") as f:
    manifest = json.load(f)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def dl(item):
    idx = item["_idx"]
    ext = os.path.splitext(item["url"])[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    fname = f"{idx:02d}_{item['theme']}{ext}"
    path = os.path.join(RAW, fname)
    if os.path.exists(path) and os.path.getsize(path) > 50_000:
        return fname, "skip", os.path.getsize(path)
    try:
        req = urllib.request.Request(item["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
        if len(data) < 30_000:
            return fname, "too_small", len(data)
        with open(path, "wb") as f:
            f.write(data)
        return fname, "ok", len(data)
    except Exception as e:
        return fname, f"err:{type(e).__name__}", 0

for i, m in enumerate(manifest, 1):
    m["_idx"] = i

ok = fail = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(dl, m): m for m in manifest}
    for fu in as_completed(futs):
        fname, status, size = fu.result()
        if status in ("ok", "skip"):
            ok += 1
        else:
            fail += 1
            print(f"FAIL {fname} {status}")
        if ok % 20 == 0 and status == "ok":
            print(f"progress: {ok} ok / {fail} fail")

print(f"DONE ok={ok} fail={fail}")
