#!/usr/bin/env python3
"""shot.py — 按真实面板尺寸渲染并裁剪截图

用法：
  python3 tools/ui-preview/shot.py 280 650 out/docked.png
  python3 tools/ui-preview/shot.py 320 650 out/float.png
  python3 tools/ui-preview/shot.py 280 650 out/x.png "css=experiments/icons-mono.css"
  python3 tools/ui-preview/shot.py 280 650 out/x.png "open=settings"

为什么需要裁剪：macOS 上无头 Chromium 的最小窗口宽约 500px，直接把 --window-size
设成 280 会被抬到 492，布局就按 492 算了。所以这里用大窗口渲染，页面内再用
#w=&h= 把虚拟面板钉死，最后裁掉右侧多出来的部分。

为什么有重试：无头渲染偶尔会拍到「磁贴还没渲染完」的空画面（同一命令重跑就好），
纯色占比过高时自动重试，避免把空图当成改坏了。
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

EDGE = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview.html"
SCALE = 2
TRIES = 3


def is_blank(im: Image.Image) -> bool:
    """画面几乎只有一个颜色 → 判定为没渲染出来。"""
    small = im.convert("RGB").resize((40, 40), Image.NEAREST)
    colors = small.getcolors(maxcolors=40 * 40)
    if not colors:
        return False
    total = 40 * 40
    top = max(colors, key=lambda c: c[0])[0]
    return top / total > 0.93


def render(w: int, h: int, extra: str) -> Image.Image:
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw.png"
        url = "file://%s#w=%d&h=%d%s" % (PREVIEW, w, h, ("&" + extra) if extra else "")
        cmd = [
            EDGE, "--headless=new", "--no-sandbox", "--disable-gpu",
            "--disable-gpu-sandbox", "--hide-scrollbars",
            "--force-prefers-reduced-motion",
            "--force-device-scale-factor=%d" % SCALE,
            "--window-size=%d,%d" % (w + 260, h + 60),   # 窗口必须大于面板
            "--virtual-time-budget=20000",
            "--screenshot=%s" % raw,
            url,
        ]
        subprocess.run(cmd, capture_output=True, timeout=150)
        if not raw.exists():
            raise SystemExit("渲染失败：没有产出截图")
        return Image.open(raw).convert("RGB").crop((0, 0, w * SCALE, h * SCALE))


def shoot(w: int, h: int, out: Path, extra: str = "") -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    im = None
    for i in range(TRIES):
        im = render(w, h, extra)
        if not is_blank(im):
            break
        print("  第 %d 次渲染是空画面，重试…" % (i + 1))
    im.save(out)
    print("%s  (%dx%d @%dx)" % (out, w, h, SCALE))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    shoot(int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3]).resolve(),
          sys.argv[4] if len(sys.argv) > 4 else "")
