# -*- coding: utf-8 -*-
"""理科/数学主题：从 nk_*.json 构建候选清单（配额制，去重）"""
import json, os, random
from collections import Counter

random.seed(2026)
BASE = os.path.dirname(os.path.abspath(__file__))

QUOTA = [
    ("math_general",        "nk_mathematics.json",                6),
    ("math_formula",        "nk_formula.json",                    7),
    ("blackboard_chalk",    "nk_blackboard_chalk.json",           7),
    ("geometry",            "nk_geometry.json",                   8),
    ("math_graph",          "nk_math_graph_function.json",        3),
    ("math_blackboard",     "nk_mathematics_formula_blackboard.json", 2),
    ("math_equation",       "nk_math_equations_chalkboard.json",  1),
    ("chemistry_general",   "nk_chemistry.json",                  6),
    ("chem_lab_glass",      "nk_chemistry_laboratory_glassware.json", 2),
    ("chem_test_tubes",     "nk_laboratory_test_tubes.json",      4),
    ("chem_molecule",       "nk_molecule_structure_science.json", 2),
    ("physics_general",     "nk_physics_science.json",            3),
    ("physics_quantum",     "nk_atom_particle_quantum.json",      2),
    ("biology_microscope",  "nk_biology_microscope.json",         6),
    ("lab_microscope",      "nk_microscope_laboratory.json",      5),
    ("sci_research",        "nk_scientific_research.json",        6),
    ("space_nebula",        "nk_space_stars_nebula.json",         2),
    ("astro_space",         "nk_astronomy_space.json",            2),
    ("telescope",           "nk_telescope_observatory.json",      2),
    ("planets",             "nk_planets_solar_system.json",       2),
    ("dna_helix",           "nk_dna_helix.json",                  2),
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
                         "thumb": x.get("thumbnailUrl") or x["url"],
                         "width": x.get("width"), "height": x.get("height"),
                         "name": x.get("name", ""), "niche": x.get("niche", ""),
                         "category": x.get("category", "")})

json.dump(manifest, open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("total:", len(manifest))
for t, c in Counter(m["theme"] for m in manifest).items():
    print(f"  {t:22s} {c}")
