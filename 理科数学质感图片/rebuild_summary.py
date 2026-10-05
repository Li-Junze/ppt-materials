# -*- coding: utf-8 -*-
"""根据最终目录结构重建两个 _参数总表.md（精选50 + 备选20）"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))

def one_liner(md_dir, stem):
    p = os.path.join(md_dir, stem + ".md")
    if not os.path.exists(p):
        return "-"
    for line in open(p, encoding="utf-8"):
        if line.startswith("**一句话**"):
            return line.replace("**一句话**", "").lstrip("*：: ").strip()
    return "-"

for pair in (("精选50张", "工科质感照片-description"),
             ("备选", "工科质感照片-description-备选")):
    img_dir, md_dir = os.path.join(BASE, pair[0]), os.path.join(BASE, pair[1])
    rows = []
    for f in sorted(os.listdir(img_dir)):
        if not f.lower().endswith(".jpg"):
            continue
        stem = os.path.splitext(f)[0]
        with Image.open(os.path.join(img_dir, f)) as im:
            w, h = im.size
        rows.append((f, f"{w}x{h}", os.path.getsize(os.path.join(img_dir, f))//1024,
                     one_liner(md_dir, stem)))
    out = os.path.join(md_dir, "_参数总表.md")
    with open(out, "w", encoding="utf-8") as fo:
        fo.write(f"# {pair[0]} · 参数总表（{len(rows)}张）\n\n")
        fo.write("| # | 文件 | 分辨率 | 大小(KB) | 一句话描述 |\n|---|------|--------|------|------------|\n")
        for i, r in enumerate(rows, 1):
            fo.write(f"| {i} | {r[0]} | {r[1]} | {r[2]} | {r[3]} |\n")
    print(f"rebuilt {out} ({len(rows)} rows)")
