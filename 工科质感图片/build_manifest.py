# -*- coding: utf-8 -*-
"""从 nk_*.json 元数据构建候选图片清单，按主题配额挑选，输出 manifest.json"""
import json, glob, os, random

random.seed(42)
BASE = os.path.dirname(os.path.abspath(__file__))

# 主题配额（总计 ~62，留冗余）
QUOTA = [
    ("circuit_board",          "nk_circuit_board.json", 8),
    ("mechanical_gear",        "nk_mechanical_gear.json", 7),
    ("robot_arm_industrial",   "nk_robot_arm_industrial.json", 6),
    ("engineering_blueprint",  "nk_engineering_blueprint.json", 5),
    ("microcontroller_solder", "nk_microcontroller_soldering.json", 6),
    ("power_grid_energy",      "nk_power_grid_energy.json", 4),
    ("cnc_machine",            "nk_cnc_machine.json", 7),
    ("factory_automation",     "nk_factory_automation.json", 5),
    ("steel_welding",          "nk_steel_structure_welding.json", 4),
    ("aerospace",              "nk_aerospace_engineering.json", 3),
    ("printer_3d",             "nk_3d_printer.json", 3),
    ("bridge_engineering",     "nk_bridge_engineering.json", 4),
    ("turbine_engine",         "nk_engine_turbine_mechanical.json", 1),
    ("blueprint_construction", "nk_architecture_blueprint_construction.json", 3),
    ("car_engine",             "nk_car_engine_bay.json", 3),
    ("wind_turbine",           "nk_wind_turbine_energy.json", 4),
    ("server_data",            "nk_technology_server_data.json", 0),  # 0 张，跳过
]

def load(fn):
    p = os.path.join(BASE, fn)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("data", [])

manifest, seen = [], set()
for theme, fn, quota in QUOTA:
    if quota <= 0:
        continue
    items = load(fn)
    # 过滤：横图、宽>=1200、非重复
    pool = [x for x in items
            if x.get("orientation") == "landscape"
            and (x.get("width") or 0) >= 1200
            and x["id"] not in seen]
    random.shuffle(pool)
    picked = pool[:quota]
    for x in picked:
        seen.add(x["id"])
        manifest.append({
            "id": x["id"],
            "theme": theme,
            "url": x["url"],
            "thumb": x.get("thumbnailUrl") or x["url"],
            "width": x.get("width"),
            "height": x.get("height"),
            "name": x.get("name", ""),
            "niche": x.get("niche", ""),
            "category": x.get("category", ""),
        })

with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)

print("total candidates:", len(manifest))
from collections import Counter
for t, c in Counter(m["theme"] for m in manifest).items():
    print(f"  {t:24s} {c}")
