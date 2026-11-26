#!/usr/bin/env python3
"""
程序化闭环微动 GIF：基于一张静态主图做整体对称往返动画。
角色本体不重绘、不变形，首尾帧回到原图姿态，天然闭环、不跳不闪。
适用于挥手/摇头/摇摆/弹跳等 AI 序列图锁不住首尾的往复大动作。

用法:
  python3 programmatic_gif.py <静态主图> <输出.gif> [动作] [帧数] [帧延迟ms]
动作: breathe(上下呼吸) / sway(左右微摇) / bounce(小幅弹跳) / bob(左右轻移)
"""
import sys, math, io
from PIL import Image, ImageOps, ImageSequence

SIZE = 240
MAX_KB = 500

def make(static_path, out_path, motion="breathe", frames=8, delay=120):
    base = Image.open(static_path).convert("RGBA").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    cx, cy = SIZE / 2, SIZE / 2
    out_frames = []
    for i in range(frames):
        t = i / frames * 2 * math.pi
        dy = dx = angle = 0.0
        if motion == "breathe":
            dy = math.sin(t) * 3
        elif motion == "sway":
            angle = math.sin(t) * 1.8
        elif motion == "bounce":
            dy = -abs(math.sin(t)) * 4
        elif motion == "bob":
            dx = math.sin(t) * 3
        frame = base.rotate(angle, resample=Image.Resampling.BICUBIC, center=(cx, cy), expand=False)
        frame = ImageOps.expand(frame, border=6, fill=(0, 0, 0, 0))
        frame = frame.transform(
            frame.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy),
            resample=Image.Resampling.BICUBIC
        )
        w, h = frame.size
        frame = frame.crop(((w - SIZE) // 2, (h - SIZE) // 2, (w + SIZE) // 2, (h + SIZE) // 2))
        out_frames.append(frame)

    # 逐帧量化，保留透明；体积过大逐步降色
    for colors in (128, 96, 64, 48, 32):
        palette = []
        for f in out_frames:
            alpha = f.getchannel("A")
            q = f.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
            q.paste(colors - 1, mask=alpha.point(lambda v: 255 if v < 128 else 0))
            q.info["transparency"] = colors - 1
            palette.append(q)
        buf = io.BytesIO()
        palette[0].save(buf, format="GIF", save_all=True, append_images=palette[1:],
                         duration=delay, loop=0, transparency=colors - 1, disposal=2, optimize=False)
        if buf.tell() <= MAX_KB * 1024:
            open(out_path, "wb").write(buf.getvalue())
            print(f"OK {out_path}: {frames}帧 {colors}色 {buf.tell()//1024}KB 动作={motion}")
            return
    raise SystemExit("GIF 压缩后仍超 500KB，请减少帧数或简化画面")

if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2],
         motion=sys.argv[3] if len(sys.argv) > 3 else "breathe",
         frames=int(sys.argv[4]) if len(sys.argv) > 4 else 8,
         delay=int(sys.argv[5]) if len(sys.argv) > 5 else 120)
