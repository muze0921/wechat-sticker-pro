#!/usr/bin/env python3
"""
表情动画质检：尺寸/体积/帧数/循环/首尾闭环/动作幅度。
用法:
  python3 check_loop.py <gif 或 sheet.png> [--sheet]
输出每项 PASS/WARN/FAIL 与建议；首尾差 >18 判为循环跳变。
"""
import sys, io, os
from PIL import Image, ImageChops, ImageStat, ImageSequence

SIZE = 240
MAX_KB = 500
LOOP_THRESHOLD = 18.0   # 首尾帧差阈值，>18 循环会跳
MIN_MOTION = 1.0        # 段内平均帧差下限，<1 动作过小

def flat(im, idx):
    im.seek(idx)
    fr = im.convert("RGBA")
    b = Image.new("RGBA", fr.size, "white")
    b.alpha_composite(fr)
    return b.convert("RGB")

def diff(a, b):
    return ImageStat.Stat(ImageChops.difference(a, b).convert("L")).mean[0]

def load_frames(path, is_sheet):
    if is_sheet:
        s = Image.open(path).convert("RGBA")
        w, h = s.width // 4, s.height // 4
        frames = []
        for y in range(4):
            for x in range(4):
                t = s.crop((x*w, y*h, (x+1)*w, (y+1)*h)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                b = Image.new("RGBA", t.size, "white"); b.alpha_composite(t)
                frames.append(b.convert("RGB"))
        return frames
    im = Image.open(path)
    return [flat(im, i) for i in range(im.n_frames)]

def best_segment(frames):
    """在 4–10 帧连续段里找首尾差最小的一段，返回 (start1,end1,首尾差,段内帧差)。"""
    n = len(frames); best = None
    for L in range(4, min(10, n) + 1):
        for st in range(n - L + 1):
            en = st + L - 1
            d = diff(frames[st], frames[en])
            inner = sum(diff(frames[i], frames[i+1]) for i in range(st, en)) / (L - 1)
            if best is None or d < best[2]:
                best = (st + 1, en + 1, d, inner, L)
    return best

def alpha_ratio(path):
    im = Image.open(path).convert("RGBA")
    h = im.getchannel("A").histogram()
    return sum(h[:128]) / (im.size[0] * im.size[1]) * 100

def main():
    path = sys.argv[1]
    is_sheet = "--sheet" in sys.argv
    frames = load_frames(path, is_sheet)
    n = len(frames)
    size_kb = os.path.getsize(path) / 1024

    print(f"== 质检 {os.path.basename(path)} ==")
    # 尺寸（sheet 按切片参考，GIF 必须 240×240）
    probe = Image.open(path)
    if not is_sheet:
        print(("PASS" if probe.size == (SIZE, SIZE) else "FAIL"),
              f"尺寸 {probe.size[0]}×{probe.size[1]} ({SIZE}×{SIZE})")
        trans = alpha_ratio(path)
        print(("PASS" if trans > 20 else "FAIL"),
              f"透明通道 透明占比 {trans:.1f}% (>20%)")
    # 体积（sheet 只参考，GIF 才卡 500KB）
    if not is_sheet:
        print(("PASS" if size_kb <= MAX_KB else "FAIL"), f"体积 {size_kb:.0f}KB (≤{MAX_KB})")
    print(("PASS" if n >= 2 else "FAIL"), f"帧数 {n}")

    first, last = frames[0], frames[-1]
    head_tail = diff(first, last)
    inner = sum(diff(frames[i], frames[i+1]) for i in range(n-1)) / max(1, n-1)

    if head_tail <= LOOP_THRESHOLD:
        print("PASS", f"首尾闭环 首尾差 {head_tail:.1f} (≤{LOOP_THRESHOLD})，循环不跳")
    else:
        print("FAIL", f"首尾跳变 首尾差 {head_tail:.1f} (>{LOOP_THRESHOLD})")
        st, en, d, inner2, L = best_segment(frames)
        print(f"      最佳连续段 keep_frames=[{st},{en}]，{L}帧，段首尾差 {d:.1f}，段内帧差 {inner2:.1f}")
        if d > LOOP_THRESHOLD:
            print("      建议：该动作裁帧无法闭环，改为程序化闭环微动，或重抽序列图")

    if inner < MIN_MOTION:
        print("WARN", f"动作过小 段内帧差 {inner:.1f} (<{MIN_MOTION})，可能看着不动")
    else:
        print("PASS", f"动作幅度 段内帧差 {inner:.1f}")

if __name__ == "__main__":
    main()
