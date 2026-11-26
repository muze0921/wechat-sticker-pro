#!/usr/bin/env python3
"""给透明主体叠加红填充金边中文祝福文字，输出带文字静态帧。"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

# 候选中文字体路径，按顺序尝试；都找不到则回退 PIL 默认字体
FONT_CANDIDATES = [
    "/opt/vm/preinstall/npm-global/lib/node_modules/@larksuite/whiteboard-cli/dist/fonts/NotoSansSC-Bold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/SimHei.ttf",
]
RED = (216, 30, 6, 255)
GOLD = (245, 197, 66, 255)

def _load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def add_text(src, dst, text, canvas=1536):
    im = Image.open(src).convert("RGBA")
    # 居中放到正方形画布
    side = max(im.size)
    sq = Image.new("RGBA", (side, side), (0,0,0,0))
    sq.paste(im, ((side-im.width)//2, (side-im.height)//2), im)
    im = sq.resize((canvas, canvas), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(im)
    font_size = int(canvas * 0.095)
    font = _load_font(font_size)
    bbox = d.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (canvas - tw)//2
    y = canvas - th - int(canvas*0.07)
    outline = max(2, font_size//14)
    # 金色描边：多方向偏移
    for ox in range(-outline, outline+1):
        for oy in range(-outline, outline+1):
            if ox*ox+oy*oy <= outline*outline:
                d.text((x+ox, y+oy), text, font=font, fill=GOLD)
    d.text((x, y), text, font=font, fill=RED)
    im.save(dst)
    print("OK", dst)

if __name__ == "__main__":
    add_text(sys.argv[1], sys.argv[2], sys.argv[3])
