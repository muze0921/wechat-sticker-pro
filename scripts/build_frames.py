#!/usr/bin/env python3
"""批量：透明小羊主体 + 红填充金边祝福文字 -> frames/NN.png（带文字静态帧）。"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from add_text import add_text

WORK = Path(__file__).resolve().parent.parent  # 项目根（scripts/ 的上一级）
pack = json.loads((WORK / "pack.json").read_text(encoding="utf-8"))
src_dir = WORK / "programmatic"
dst_dir = WORK / "frames"
dst_dir.mkdir(exist_ok=True)

for i, s in enumerate(pack["stickers"], 1):
    src = src_dir / f"{i:02d}.png"
    dst = dst_dir / f"{i:02d}.png"
    if not src.exists():
        print(f"缺主体 {src.name}"); continue
    add_text(str(src), str(dst), s["word"])
