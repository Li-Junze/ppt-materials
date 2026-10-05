# -*- coding: utf-8 -*-
"""生成带编号的 contact sheet（每张 4:3 格缩略图 + 编号），供视觉核对"""
import os, math
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "check")

files = sorted(f for f in os.listdir(RAW) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
N = len(files)
COLS, ROWS = 5, 4          # 每张 20 格
TH_W, TH_H = 320, 240      # 缩略图尺寸
LABEL_H = 28

font = None
for fp in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 20)
        break

per_sheet = COLS * ROWS
n_sheets = math.ceil(N / per_sheet)
for s in range(n_sheets):
    batch = files[s*per_sheet:(s+1)*per_sheet]
    sheet = Image.new("RGB", (COLS*TH_W, ROWS*(TH_H+LABEL_H)), "#f0f0f0")
    d = ImageDraw.Draw(sheet)
    for i, fn in enumerate(batch):
        num = s*per_sheet + i + 1
        col, row = i % COLS, i // COLS
        x0, y0 = col*TH_W, row*(TH_H+LABEL_H)
        try:
            im = Image.open(os.path.join(RAW, fn)).convert("RGB")
            im.thumbnail((TH_W, TH_H))
            im = im.crop((0, 0, min(im.width, TH_W), min(im.height, TH_H)))
            sheet.paste(im, (x0, y0))
        except Exception as e:
            d.text((x0+8, y0+90), f"BROKEN {fn}", fill="red", font=font)
        label = f"#{num:02d} {fn.split('_',1)[1][:22]}"
        d.rectangle([x0, y0+TH_H, x0+TH_W, y0+TH_H+LABEL_H], fill="#222")
        d.text((x0+6, y0+TH_H+4), label, fill="white", font=font)
        d.rectangle([x0, y0, x0+TH_W-1, y0+TH_H+LABEL_H-1], outline="#999", width=1)
    out_path = os.path.join(OUT, f"sheet_{s+1}.jpg")
    sheet.save(out_path, quality=82)
    print("saved", out_path, f"({len(batch)} imgs)")
print("total sheets:", n_sheets)
