#!/usr/bin/env python3
"""build.py — 生成浏览器预览页（不改动 plugin/ 下任何文件）

产物：
  tools/ui-preview/preview.html   由 plugin/panel.html 注入 <base> + 宿主桩而来
  tools/ui-preview/manifest.js    真实磁贴清单（按 tiles/_order.json 排序）

用法：python3 tools/ui-preview/build.py
截图：bash tools/ui-preview/shot.sh
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT.parent.parent / "plugin"
TILES = PLUGIN / "tiles"

SKIP_JS = {"tile-welcome.js"}


def tile_files():
    order_raw = json.loads((TILES / "_order.json").read_text(encoding="utf-8"))
    order = order_raw.get("order", [])

    js = sorted(p.name for p in TILES.glob("*.js")
                if not p.name.endswith(".host.js") and p.name not in SKIP_JS)
    css = sorted(p.name for p in TILES.glob("*.css"))

    ordered = [n for n in order if n in js]
    rest = [n for n in js if n not in ordered]
    return ordered + rest, css


def main():
    js, css = tile_files()

    (ROOT / "manifest.js").write_text(
        "window.__PREVIEW_TILES = %s;\n"
        % json.dumps({"js": js, "css": css}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    html = (PLUGIN / "panel.html").read_text(encoding="utf-8")
    if '<base href="../../plugin/">' not in html:
        html = html.replace("<head>", '<head>\n<base href="../../plugin/">', 1)
    # 注意：preview.html 里有 <base href="../../plugin/">，所有相对路径都以 plugin/ 为基准。
    # 所以这两个脚本要写成「从 plugin/ 出发回到 tools/ui-preview/」的相对路径。
    stub = ('<script src="../tools/ui-preview/manifest.js"></script>\n'
            '<script src="../tools/ui-preview/stub.js"></script>\n')
    html = re.sub(r'(<script src="core/app\.js"></script>)', stub + r"\1", html, count=1)

    (ROOT / "preview.html").write_text(html, encoding="utf-8")
    print("preview.html / manifest.js 已生成：%d 个磁贴 JS，%d 个 CSS" % (len(js), len(css)))


if __name__ == "__main__":
    main()
