# -*- coding: utf-8 -*-
"""
逐张图片生成详细参数 + 视觉描述文件
用法: python describe.py <图片目录> <输出目录> [起始编号]
依赖: 同目录 apikey.txt (GLM_API_KEY), PIL
"""
import sys, os, json, time, base64, io, urllib.request, urllib.error
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
key = open(os.path.join(BASE, "apikey.txt")).read().strip()

SRC = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

PROMPT = (
    "你是PPT素材编目员,对这张工科照片输出中文描述,严格按以下markdown格式,不要任何多余内容:\n"
    "**一句话**: 用一句话概括画面内容\n"
    "**主体细节**: 画面核心物体及其细节(材质/部件/状态),2-3句\n"
    "**色调光照**: 主色调、色彩倾向、光源方向与氛围\n"
    "**构图视角**: 景别(特写/中景/全景)、拍摄角度、焦点与景深\n"
    "**质感风格**: 画面传达的质感关键词(如冷峻/精密/硬朗),适合的设计风格\n"
    "**建议用途**: 适合作什么主题PPT的什么位置(封面/章节页/背景)"
)

def top_colors(im, n=5):
    small = im.convert("RGB").resize((64, 64))
    q = small.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    out = []
    for cnt, idx in counts[:n]:
        r, g, b = pal[idx*3:idx*3+3]
        out.append(("#%02x%02x%02x" % (r, g, b), cnt))
    return out

def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)

def ratio_str(w, h):
    g = gcd(w, h)
    rw, rh = w // g, h // g
    if rw > 32 or rh > 32:  # 近似常用比例
        r = w / h
        for name, v in (("16:9", 16/9), ("3:2", 1.5), ("4:3", 4/3), ("21:9", 21/9)):
            if abs(r - v) / v < 0.02:
                return f"≈{name} ({r:.2f})"
        return f"{r:.2f} : 1"
    return f"{rw}:{rh} ({w/h:.2f})"

def vision_md(im):
    buf = io.BytesIO()
    im2 = im.copy(); im2.thumbnail((1280, 1280))
    im2.convert("RGB").save(buf, "JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    body = {"model": "glm-4v-flash", "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        {"type": "text", "text": PROMPT}]}], "temperature": 0.2}
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    last = None
    for att in range(6):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            last = f"HTTP{e.code}:{e.read().decode(errors='replace')[:120]}"
            if e.code in (429, 500, 502, 503):
                time.sleep(12 * (att + 1)); continue
            raise RuntimeError(last)
        except Exception as e:
            last = f"{type(e).__name__}:{e}"; time.sleep(8)
    return f"> 视觉描述生成失败: {last}"

summary = []
files = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
done = 0
for fn in files:
    stem = os.path.splitext(fn)[0]
    md_path = os.path.join(OUT, stem + ".md")
    if os.path.exists(md_path):
        done += 1
        continue
    p = os.path.join(SRC, fn)
    with Image.open(p) as im:
        im.load()
        w, h = im.size
        mode, fmt = im.mode, im.format
        dpi = im.info.get("dpi")
        colors = top_colors(im)
        desc = vision_md(im)
    kb = os.path.getsize(p) / 1024
    mp = w * h / 1e6
    theme = fn.split("_", 1)[1].rsplit(".", 1)[0] if "_" in fn else "-"
    dpi_s = f"{int(dpi[0])} x {int(dpi[1])}" if dpi else "未记录(网络图无DPI)"
    color_s = "、".join(f"`{c}`" for c, _ in colors)
    one_liner = ""
    for line in desc.splitlines():
        if line.startswith("**一句话**"):
            one_liner = line.replace("**一句话**", "").lstrip("*：: ").strip()
            break
    md = (
        f"# {fn}\n\n"
        f"## 基本参数\n\n"
        f"| 项 | 值 |\n|---|---|\n"
        f"| 文件名 | {fn} |\n"
        f"| 主题标签 | {theme} |\n"
        f"| 文件格式 | {fmt} ({mode}) |\n"
        f"| 分辨率 | {w} x {h} px |\n"
        f"| 宽高比 | {ratio_str(w, h)} |\n"
        f"| 总像素 | {mp:.2f} MP |\n"
        f"| 文件大小 | {kb:.0f} KB |\n"
        f"| DPI | {dpi_s} |\n"
        f"| 主色调(前5) | {color_s} |\n\n"
        f"## 视觉描述\n\n{desc}\n"
    )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    summary.append((fn, f"{w}x{h}", f"{kb:.0f}KB", colors[0][0], one_liner))
    done += 1
    print(f"[{done}/{len(files)}] {fn} -> {stem}.md", flush=True)
    time.sleep(2)

with open(os.path.join(OUT, "_参数总表.md"), "w", encoding="utf-8") as f:
    f.write("| # | 文件 | 分辨率 | 大小 | 主色 | 一句话描述 |\n|---|------|--------|------|------|------------|\n")
    for i, r in enumerate(summary, 1):
        f.write(f"| {i} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |\n")
print(f"ALL_DONE {done} files, summary -> _参数总表.md")
