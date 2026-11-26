#!/usr/bin/env python3
"""批量抠图：把白底/浅底源图转为透明PNG，覆盖回原文件。用法: python3 matting_batch.py <目录>"""
import sys, subprocess, json, urllib.request, os, glob, io
from PIL import Image

def alpha_ratio(path):
    im = Image.open(path).convert("RGBA")
    h = im.getchannel("A").histogram()
    return sum(h[:128]) / (im.size[0]*im.size[1]) * 100

def cut_one(path):
    abs_path = os.path.abspath(path)
    r = subprocess.run(
        ["mediakit-cli", "image", "remove-image-background",
         "--image-url", abs_path, "--scene", "general", "--output-format", "png"],
        capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print("  FAIL", path, r.stderr[-200:]); return False
    data = json.loads(r.stdout)
    url = data.get("image_url")
    if not url:
        print("  FAIL 无url", path); return False
    urllib.request.urlretrieve(url, path)
    print(f"  OK {os.path.basename(path)} 透明{alpha_ratio(path):.1f}%")
    return True

if __name__ == "__main__":
    folder = sys.argv[1]
    files = sorted(glob.glob(os.path.join(folder, "*.png")))
    print(f"共 {len(files)} 张待抠")
    for f in files:
        cut_one(f)
