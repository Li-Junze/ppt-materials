# -*- coding: utf-8 -*-
"""用 BigModel 视觉模型核对 contact sheet，逐张提交，带重试"""
import sys, os, json, time, base64, urllib.request, urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
key = open(os.path.join(BASE, "apikey.txt")).read().strip()

PROMPT = ("这是20张(或更少)工科照片的缩略图拼图，每张下方有#两位数编号标签。逐格检查："
          "1) 空白/损坏/纯色占位图；2) 明显与工科无关(人物肖像、美食、纯风景、卡通插画)；"
          "3) 可见水印文字或logo。严格JSON输出(无markdown)："
          '{"broken":["编号"],"off_topic":[{"num":"编号","reason":"简述"}],"watermark":["编号"]}。'
          "没有则空数组。只输出JSON。")

def check(path, model):
    img = base64.b64encode(open(path, "rb").read()).decode()
    body = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}},
            {"type": "text", "text": PROMPT},
        ]}],
        "temperature": 0.1,
    }
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    last_err = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                resp = json.load(r)
            return resp["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:200]
            last_err = f"HTTP{e.code}:{detail}"
            if e.code in (429, 500, 502, 503):
                time.sleep(15 * (attempt + 1))
                continue
            raise RuntimeError(last_err)
        except Exception as e:
            last_err = f"{type(e).__name__}:{e}"
            time.sleep(10)
    return f"__FAIL__ {last_err}"

if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "glm-4.5v"
    sheets = sys.argv[2:] or [os.path.join(BASE, "check", f"sheet_{i}.jpg") for i in range(1, 5)]
    results = {}
    for s in sheets:
        print(f"--> checking {os.path.basename(s)} with {model}", flush=True)
        out = check(s, model)
        print(out[:600], flush=True)
        results[os.path.basename(s)] = out
        time.sleep(5)
    with open(os.path.join(BASE, f"vision_{model.replace('.','-')}.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("ALL_DONE")
