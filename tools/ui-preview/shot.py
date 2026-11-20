#!/usr/bin/env python3
"""shot.py — 按真实面板尺寸渲染并裁剪截图

用法：
  python3 tools/ui-preview/shot.py 280 650 out/docked.png
  python3 tools/ui-preview/shot.py 320 650 out/float.png
  python3 tools/ui-preview/shot.py 280 650 out/x.png "css=experiments/icons-mono.css"

为什么需要裁剪：macOS 上无头 Chromium 的最小窗口宽约 500px，直接把 --window-size
设成 280 会被抬到 492，布局就按 492 算了。所以这里用大窗口渲染，页面内再用
#w=&h= 把虚拟面板钉死，最后裁掉右侧多出来的部分。
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


def shoot(w: int, h: int, out: Path, extra: str = "") -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
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
        subprocess.run(cmd, capture_output=True, timeout=120)
        if not raw.exists():
            raise SystemExit("渲染失败：没有产出截图")

        im = Image.open(raw)
        im.crop((0, 0, w * SCALE, h * SCALE)).save(out)
        print("%s  (%dx%d @%dx)" % (out, w, h, SCALE))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    shoot(int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3]).resolve(),
          sys.argv[4] if len(sys.argv) > 4 else "")
