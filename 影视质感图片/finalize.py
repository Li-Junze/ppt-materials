# -*- coding: utf-8 -*-
"""整理最终交付：剔除视觉核对不合格图，按主题均衡精选50张，其余入备选"""
import os, shutil, json
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
FINAL = os.path.join(BASE, "精选50张")
SPARE = os.path.join(BASE, "备选")
REJECT = os.path.join(BASE, "rejected")
for d in (FINAL, SPARE, REJECT):
    os.makedirs(d, exist_ok=True)

REJECTED = {"02","03","05","51","71","72","83"}  # 02纯文档 03健身 05聚会 51美甲 71卧室 72装书架 83无语境人像

files = sorted(f for f in os.listdir(RAW) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))

# 分流
good = []
for fn in files:
    num = fn.split("_", 1)[0]
    dst = REJECT if num in REJECTED else None
    if dst:
        shutil.move(os.path.join(RAW, fn), os.path.join(dst, fn))
        print(f"rejected -> {fn}")
    else:
        good.append(fn)

# 按主题配额精选 50（每主题优先保留，超出均入备选）
TARGET = 50
from collections import defaultdict
by_theme = defaultdict(list)
for fn in good:
    theme = fn.split("_", 1)[1].rsplit(".", 1)[0]
    by_theme[theme].append(fn)

quota = {t: max(1, round(TARGET * len(v) / len(good))) for t, v in by_theme.items()}
# 归一化到恰好50
sel = []
spare = []
for t, v in sorted(by_theme.items()):
    k = min(len(v), quota[t])
    sel.extend(v[:k]); spare.extend(v[k:])
# 微调到恰好 50
i = 0
while len(sel) > TARGET and spare:
    spare.append(sel.pop())  # 不该发生，防御
while len(sel) < TARGET and spare:
    sel.append(spare.pop(0))

for fn in sel:
    shutil.move(os.path.join(RAW, fn), os.path.join(FINAL, fn))
for fn in spare:
    shutil.move(os.path.join(RAW, fn), os.path.join(SPARE, fn))

# 生成清单
rows = []
for fn in sorted(sel):
    p = os.path.join(FINAL, fn)
    with Image.open(p) as im:
        w, h = im.size
    kb = os.path.getsize(p) // 1024
    rows.append((fn, w, h, kb))

with open(os.path.join(BASE, "清单.md"), "w", encoding="utf-8") as f:
    f.write("# 理科数学质感图片 · 精选50张清单\n\n")
    f.write("| # | 文件 | 分辨率 | 大小(KB) | 主题 |\n|---|------|--------|----------|------|\n")
    for i, (fn, w, h, kb) in enumerate(rows, 1):
        theme = fn.split("_", 1)[1].rsplit(".", 1)[0]
        f.write(f"| {i} | {fn} | {w}x{h} | {kb} | {theme} |\n")

print(f"\nFINAL={len(sel)} SPARE={len(spare)} REJECT={len(REJECTED)}")
print("good pool was:", len(good))
