# -*- coding: utf-8 -*-
"""影视批分流（基于人工逐格视觉核对结论）：精选50 / 备选16 / rejected / rejected2"""
import os, shutil
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw")
FINAL = os.path.join(BASE, "精选50张")
SPARE = os.path.join(BASE, "备选")
REJ = os.path.join(BASE, "rejected")
REJ2 = os.path.join(BASE, "rejected2")
for d in (FINAL, SPARE, REJ, REJ2):
    os.makedirs(d, exist_ok=True)

# rejected：明确偏题/污染（视觉核对剔除）
REJECTED = {
    "01","02","03","04","05","07",              # anime 池污染：美甲×5、蝴蝶拼贴
    "17",                                        # 玻璃拱廊（建筑非宫廷）
    "30",                                        # 复古警察海报插画
    "34","39",                                   # 液态金属抽象纹理
    "40","44",                                   # 街机
    "42",                                        # 游戏卡带墙
    "74","76","77",                              # 误标 military：村庄/石墙田野/庄园
    "84",                                        # 绿板纯纹理
    "89",                                        # 宝莱坞海报（含片名字样）
    "108","109","110","111","112","114","115","116","117",  # 动物照片×4、眼球拼贴、美甲×4
    "120","121",                                 # 兵马俑（历史题材非影视）
}

# 精选50（16类型均衡，人工挑选）
SELECTED = {
    # 漫剧/动漫 5
    "06","95","101","104","113",
    # 古装剧 4
    "09","10","123","126",
    # 宫廷 3
    "15","16","18",
    # 都市剧 4
    "21","22","25","28",
    # 刑侦/悬疑 3
    "29","31","32",
    # 科幻 3
    "36","37","38",
    # 年代 2
    "41","45",
    # 武侠 3
    "46","47","48",
    # 谍战 3
    "50","51","52",
    # 职场 3
    "54","55","57",
    # 甜宠 3
    "60","62","64",
    # 家庭 3
    "67","68","70",
    # 军旅/战争 2
    "75","122",
    # 仙侠 3
    "78","81","82",
    # 片场/影院 4
    "85","86","87","88",
    # 电影感 2
    "90","93",
}

# 备选16（次优可用）
SPARE_SET = {
    "08","11","12","14","19","23","33","35",
    "43","61","72","91","94","100","118","124",
}

files = sorted((f for f in os.listdir(RAW) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))),
               key=lambda f: int(f.split("_")[0]))
moves = {"sel": [], "spare": [], "rej": [], "rej2": []}
for fn in files:
    num = fn.split("_", 1)[0]
    if num in REJECTED:
        moves["rej"].append(fn)
    elif num in SELECTED:
        moves["sel"].append(fn)
    elif num in SPARE_SET:
        moves["spare"].append(fn)
    else:
        moves["rej2"].append(fn)   # 同类重复/弱相关

dst_map = {"sel": FINAL, "spare": SPARE, "rej": REJ, "rej2": REJ2}
for key, fns in moves.items():
    for fn in fns:
        shutil.move(os.path.join(RAW, fn), os.path.join(dst_map[key], fn))

print(f"FINAL={len(moves['sel'])} SPARE={len(moves['spare'])} "
      f"REJECTED={len(moves['rej'])} REJ2={len(moves['rej2'])}")
sel_themes = Counter(f.split("_", 1)[1].rsplit(".", 1)[0] for f in moves["sel"])
print("精选主题分布:", dict(sel_themes))
