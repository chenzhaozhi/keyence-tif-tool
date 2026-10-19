# -*- coding: utf-8 -*-
"""
KeyenceTifTool — 基恩士深度图(16bit TIFF) 一键转 PNG/BMP 小工具
- 拖文件/文件夹到 exe 上即可转换；双击 exe 弹出窗口选文件
- 自动对比度拉伸（默认 0.1%~99.9% 分位，ImageJ 风格），16bit→8bit
- 输出 <原名>_stretched.png（同目录），原图不动
纯 Pillow，无 numpy，打包体积小。
"""
import sys
import os
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

LO_PCT, HI_PCT = 0.1, 99.9


def auto_stretch(im):
    """16bit/任意单通道图 → 自动拉伸 8bit 灰度图。彩色图直接转 L 不拉伸。"""
    if im.mode in ("RGB", "RGBA", "P"):
        return im.convert("L")
    if im.mode in ("I;16", "I;16B", "I;16L", "I;16BE", "I;16LE", "I", "F"):
        arr = np.array(im)
        lo, hi = np.percentile(arr, [LO_PCT, HI_PCT])
        if hi <= lo:
            hi = lo + 1
        out = np.clip((arr.astype(np.float32) - lo) * 255.0 / (hi - lo), 0, 255)
        return Image.fromarray(out.astype(np.uint8), "L")
    return im.convert("L")


def convert_one(src: Path, out_ext=".png", both=False) -> Path:
    im = Image.open(src)
    im.load()
    out = auto_stretch(im)
    dst = src.with_name(src.stem + "_stretched" + out_ext)
    out.save(dst)
    if both and out_ext.lower() != ".bmp":
        out.save(src.with_name(src.stem + "_stretched.bmp"))
    return dst


def iter_targets(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for ext in ("*.tif", "*.tiff", "*.TIF", "*.TIFF"):
                files.extend(sorted(p.rglob(ext)))
        elif p.suffix.lower() in (".tif", ".tiff"):
            files.append(p)
    return files


def run_batch(paths, log=print, out_ext=".png", both=False):
    files = iter_targets(paths)
    if not files:
        log("未找到 tif/tiff 文件。")
        return []
    done, failed = [], []
    for i, f in enumerate(files, 1):
        try:
            dst = convert_one(f, out_ext=out_ext, both=both)
            done.append(dst)
            log(f"[{i}/{len(files)}] OK  {f.name} -> {dst.name}")
        except Exception as e:
            failed.append(f)
            log(f"[{i}/{len(files)}] 失败 {f.name}: {e}")
    log(f"完成 {len(done)}/{len(files)}" + (f"，失败 {len(failed)}" if failed else ""))
    return done


def main():
    argv_files = [a for a in sys.argv[1:] if not a.startswith("-")]
    if argv_files:
        # 拖放模式：转换完弹窗确认
        import tkinter as tk
        from tkinter import messagebox

        results = []
        run_batch(argv_files, log=results.append)
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "KeyenceTifTool", "\n".join(results[-30:]) or "没有可转换的文件"
        )
        root.destroy()
        return

    # 窗口模式
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("KeyenceTifTool — 基恩士深度图 16bit TIFF 转 PNG/BMP")
    root.geometry("640x440")

    txt = tk.Text(root, wrap="word")
    txt.pack(fill="both", expand=True, padx=8, pady=8)
    bar = ttk.Frame(root)
    bar.pack(fill="x", padx=8, pady=(0, 8))

    def log(m):
        txt.insert("end", m + "\n")
        txt.see("end")
        root.update_idletasks()

    def pick_files():
        fs = filedialog.askopenfilenames(
            title="选择 TIFF 文件",
            filetypes=[("TIFF", "*.tif *.tiff"), ("所有文件", "*.*")],
        )
        if fs:
            run_batch(list(fs), log=log)

    def pick_dir():
        d = filedialog.askdirectory(title="选择文件夹（含子文件夹）")
        if d:
            run_batch([d], log=log)

    ttk.Button(bar, text="选择文件…", command=pick_files).pack(side="left")
    ttk.Button(bar, text="选择文件夹…", command=pick_dir).pack(side="left", padx=8)
    ttk.Button(bar, text="清空日志", command=lambda: txt.delete("1.0", "end")).pack(
        side="left"
    )
    ttk.Label(
        bar,
        text="也可以直接把 tif/文件夹拖到这个 exe 上",
    ).pack(side="right")

    txt.insert("end", "等待选择文件…\n")
    root.mainloop()


if __name__ == "__main__":
    main()
