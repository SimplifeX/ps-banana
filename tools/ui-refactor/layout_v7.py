#!/usr/bin/env python3
"""layout_v7.py — 重排默认布局（只改 defaults/default-layout.js）

为什么改：顶栏（1,1,4x1）占住第 1 行后，原布局里 presets / bodypreset 这两块
2x3 被挤到最底部，于是主区第 2~3 行空出 142px 的空白带；同时「生成中心」
占 4 行（260px），在 650 高的面板里几乎吃掉一半。

新布局原则：
  1. 第 1 行留给顶栏，内容从第 2 行开始，不留空行；
  2. 常用的参数 / 参考图 / 提示词贴顶；
  3. 两张大磁贴（预设、身体预设）放在中段；
  4. 「生成中心」高度 4 → 2 行，把空间还给主功能。

用法：python3 tools/ui-refactor/layout_v7.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "plugin" / "defaults" / "default-layout.js"

# tile id -> (col, row, w, h)
NEW = {
    "params":      (1, 2, 2, 1),
    "prompt":      (3, 2, 2, 4),
    "refimages":   (1, 3, 2, 1),
    "light":       (1, 4, 1, 1),
    "hemisynth":   (2, 4, 1, 1),
    "batchworks":  (1, 5, 1, 1),
    "records":     (2, 5, 1, 1),
    "presets":     (1, 6, 2, 3),
    "bodypreset":  (3, 6, 2, 3),
    "center":      (1, 9, 4, 2),
    "log":         (1, 11, 1, 1),
    "settings":    (2, 11, 1, 1),
    "billing":     (3, 11, 1, 1),
    "dock":        (4, 11, 1, 1),
    "scope":       (1, 12, 1, 1),
    "drawer":      (2, 12, 1, 1),
    "netdoctor":   (3, 12, 1, 1),
}

HEADER = """/* defaults/default-layout.js — 插件默认布局
 * v6.5.8: 取自用户手工配置的「6.5.8新测试布局」+ Dock 配置(2026-08-02)
 * v7:     重排主区。原来 presets/bodypreset 被顶栏挤到底部，导致第 2~3 行空 142px；
 *         生成中心 4 行 → 2 行。只调位置，不动任何磁贴功能。
 * 含磁贴位置/尺寸/颜色/展开模式/外观 + Dock(钉选按钮/位置/大小/透明度)
 * 已剔除开发工具磁贴(perftest); 用户有任何存储值都会覆盖这些默认
 */
"""


def main() -> None:
    src = TARGET.read_text(encoding="utf-8")
    body = re.search(r"window\._DEFAULT_LAYOUT\s*=\s*(\{.*?\});\s*\}\)\(\);", src, re.S)
    if not body:
        raise SystemExit("没有匹配到 window._DEFAULT_LAYOUT 对象")
    data = json.loads(body.group(1))
    layout = data["__tile_layout_v6"]

    changed = 0
    for tid, (col, row, w, h) in NEW.items():
        if tid not in layout:
            print("  跳过（布局里没有）:", tid)
            continue
        old = (layout[tid]["col"], layout[tid]["row"], layout[tid]["w"], layout[tid]["h"])
        if old != (col, row, w, h):
            layout[tid].update({"col": col, "row": row, "w": w, "h": h})
            changed += 1

    out = HEADER + "(function() {\n'use strict';\nwindow._DEFAULT_LAYOUT = " \
        + json.dumps(data, ensure_ascii=False, indent=2) + ";\n})();\n"
    TARGET.write_text(out, encoding="utf-8")
    print("重排完成，改动 %d 块磁贴 -> %s" % (changed, TARGET))


if __name__ == "__main__":
    main()
