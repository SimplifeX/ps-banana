#!/usr/bin/env python3
"""展开面板溢出审计。

对每个面板 id 渲染一次，读出「被面板右边界切掉的元素」清单。
280 和 320 两个宽度都跑，因为面板停靠态是 280、浮动态是 320，
有些行只在 280 下溢出。

用法：
    python3 tools/ui-preview/audit.py prompt params presets records center
    python3 tools/ui-preview/audit.py --all        # 全部展开面板
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDGE = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"

# 面板 id 与「展开后大概多高」，高度只影响截断不影响宽度审计，统一给 900。
PANELS = [
    "prompt", "params", "presets", "records", "center", "refimages",
    "batch", "settings", "scene", "poster", "translate", "light",
    "codex", "chat", "canvas", "colorgrade", "layout", "log", "recyclebin",
]


def run(panel: str, w: int) -> dict:
    url = "file://%s/preview.html#w=%d&h=900&debug=1&open=%s" % (HERE, w, panel)
    dom = subprocess.run(
        [EDGE, "--headless=new", "--no-sandbox", "--disable-gpu",
         "--disable-gpu-sandbox", "--window-size=560,980",
         "--virtual-time-budget=20000", "--dump-dom", url],
        capture_output=True, text=True, timeout=180,
    ).stdout
    m = re.search(r"<title>(.*?)</title>", dom, re.S)
    if not m:
        return {"error": "no-title"}
    raw = m.group(1).strip()
    if not raw.startswith("{"):
        return {"error": "no-debug", "raw": raw[:80]}
    try:
        return json.loads(raw.replace("&quot;", '"').replace("&amp;", "&"))
    except json.JSONDecodeError as exc:
        return {"error": "bad-json:%s" % exc, "raw": raw[:120]}


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] == "--all":
        panels = PANELS
    else:
        panels = args

    total = 0
    for panel in panels:
        for w in (280, 320):
            d = run(panel, w)
            if "error" in d:
                print("%-12s %3d  ⚠ %s" % (panel, w, d.get("error")))
                continue
            exp = d.get("exp") or {}
            if exp.get("id") not in (panel, panel + "Host"):
                # 面板没打开（id 不存在或渲染失败），跳过不报错
                print("%-12s %3d  · 未展开（exp=%s）" % (panel, w, exp.get("id")))
                continue
            clip = d.get("clip") or []
            if not clip:
                print("%-12s %3d  ✓ 无溢出" % (panel, w))
                continue
            total += len(clip)
            print("%-12s %3d  ✗ %d 处溢出" % (panel, w, d.get("clipN", len(clip))))
            for c in clip:
                print("               %5dpx  %-28s %s" % (c["over"], c["c"] or "(无类名)", c["t"]))
    print("\n合计溢出元素：%d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
