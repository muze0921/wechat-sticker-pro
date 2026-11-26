#!/usr/bin/env python3
"""
赞赏素材规范化：赞赏引导图(750×560, ≤100KB)、赞赏致谢图(750×750, ≤200KB)、赞赏引导语校验。
两张图均为场景图：cover 裁切填满规定尺寸、合成到不透明背景、压缩到体积上限；风格须与表情一致。

用法:
  python3 tip_assets.py guide  <src.png> <out.png>
  python3 tip_assets.py thanks <src.png> <out.png>
  python3 tip_assets.py line   "引导语文案"
"""
import sys, io, re
from PIL import Image, ImageOps

GUIDE_SIZE = (750, 560)
GUIDE_KB = 100
THANKS_SIZE = (750, 750)
THANKS_KB = 200


def _fit_opaque(src, size, limit_kb, bg=(255, 245, 235)):
    im = Image.open(src).convert("RGBA")
    im = ImageOps.fit(im, size, method=Image.Resampling.LANCZOS)
    base = Image.new("RGBA", size, bg)
    base.alpha_composite(im)
    im = base.convert("RGB")
    for colors in (256, 192, 128, 96, 64):
        out = io.BytesIO()
        im.quantize(colors=colors, method=Image.Quantize.FASTOCTREE).save(
            out, format="PNG", optimize=True)
        if out.tell() <= limit_kb * 1024:
            return out.getvalue()
    out = io.BytesIO()
    im.save(out, format="JPEG", quality=70, optimize=True)
    return out.getvalue()


def fit_guide(src, dst):
    data = _fit_opaque(src, GUIDE_SIZE, GUIDE_KB)
    open(dst, "wb").write(data)
    print(f"OK 赞赏引导图 {dst} {GUIDE_SIZE} {len(data)//1024}KB")


def fit_thanks(src, dst):
    data = _fit_opaque(src, THANKS_SIZE, THANKS_KB)
    open(dst, "wb").write(data)
    print(f"OK 赞赏致谢图 {dst} {THANKS_SIZE} {len(data)//1024}KB")


def check_line(text):
    """赞赏引导语：5–15 汉字，仅中英文与常见标点，不含表情符号/特殊字符。"""
    text = text.strip()
    han = len(re.findall(r"[一-鿿]", text))
    bad = re.findall(r"[^\u4e00-\u9fffA-Za-z0-9，。！？、~～]", text)
    ok = 5 <= han <= 15 and not bad
    print(("PASS" if ok else "FAIL"), f"引导语「{text}」 汉字 {han} 个" +
          ("" if ok else f"，异常字符 {set(bad)}"))
    return ok


if __name__ == "__main__":
    if sys.argv[1] == "guide":
        fit_guide(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "thanks":
        fit_thanks(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "line":
        check_line(sys.argv[2])
