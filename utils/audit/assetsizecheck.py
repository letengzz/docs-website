#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""assetsizecheck.py —— 图片体积与内嵌数据巡检（第 64 项巡检）

背景
----
本仓的文档配图全部落在各主题的 `assets/` 下，随 Markdown 一起提交。既有的巡检
只回答「图片存不存在、有没有被引用」：

  - `imagecheck`        链接指向的图片文件是否存在、相对路径是否解析得到；
  - `orphanassetcheck`  有没有「存在但没人引用」的孤儿图片；
  - `svgcheck`          SVG 是否是合法 XML、有没有未转义的 `<`。

**没有一项问「这个文件有多大」**。于是三类问题会静默通过构建：

  1. 一张截图直接提交原图（8~15 MB），克隆变慢、构建变慢、手机端打开卡死；
  2. SVG 里塞了 `data:image/png;base64,...`，看起来是个几 KB 的矢量图标，
     实际内嵌了几百 KB 的位图——`svgcheck` 通过、`imagecheck` 通过；
  3. 同一张图在多个主题下各存一份（常见于复制粘贴建新专题），改图时只改了一处。

判据（E 为错误、W 为提示）
--------------------------
  E0 ROOT_NOT_FOUND        给定的根目录不存在
  E1 NO_ASSETS             一个 assets 目录都没找到（活性：防止扫错目录后全绿）
  E2 OVERSIZE              静态图片 > --max-bytes（默认 1 MiB），或 GIF > --max-gif-bytes（默认 4 MiB）
  W1 LARGE_IMAGE           单个图片 > --warn-bytes（默认 300 KiB）但不超 E2 阈值
  W2 EMBEDDED_DATA_URI     SVG 内嵌 `data:image/...;base64`（体积炸弹的典型形态）
  W3 DUPLICATE_BYTES       两个及以上文件 sha256 完全相同（可去重）
  W4 WIDE_SVG              SVG 声明宽度 > 1600（按 900 宽的版心渲染会显著缩小文字）

口径说明
--------
1. **只统计图片扩展名**（`.svg/.png/.jpg/.jpeg/.gif/.webp/.avif`）：`assets/` 下
   偶尔会有 `.txt`、`.csv` 之类的素材，体积不是问题，扫进来只会制造噪声。
2. **E2 的阈值按「单文件能否被移动端顺畅加载」定**，不是按仓库配额：1 MiB 是
   静态截图在 2x 屏下的常见上限，超过它基本可以断定没有压缩过。**GIF 单独一档
   4 MiB**——动图由 N 帧组成，用静态图的预算去卡它只会逼着人删掉有用的演示。
3. **W2 只报「内嵌位图」**，不报 `data:image/svg+xml`（矢量内嵌是合法用法）；定为
   W 而非 E，是因为修它需要重画那张图，属「登记后处理」的债而不是阻断项。
4. **W3 只在同一扩展名内比较**：同一张图的 PNG 与 SVG 天然是不同文件，字节相同
   的概率极低，跨扩展名比较没有意义。
5. **不判断「该不该有图」**：那是 `imagecheck` 与 `orphanassetcheck` 的职责。本项
   只回答体积与重复，避免一个脚本管两件事。

用法
----
    python3 utils/audit/assetsizecheck.py [--root .] [--max-bytes N] [--warn-bytes N]
                                         [--selftest] [--verbose]

退出码：0 = 无 E（W 不影响退出码）；1 = 存在 E；2 = 参数或根目录错误。
"""

import argparse
import hashlib
import os
import re
import sys
import tempfile

IMG_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"}
SKIP_DIRS = {".git", "node_modules", "dist", ".vitepress", ".workbuddy", "cache"}
DATA_URI = re.compile(r"data:image/(png|jpe?g|gif|webp|avif)[^,;]{0,40};base64,", re.I)
SVG_WIDTH = re.compile(r'<svg[^>]*\bwidth="(\d+(?:\.\d+)?)"', re.I)


def iter_assets(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if os.path.basename(dirpath) != "assets":
            continue
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in IMG_EXT:
                yield os.path.join(dirpath, fn)


def check(root, max_bytes, warn_bytes, max_gif_bytes):
    if not os.path.isdir(root):
        raise FileNotFoundError(root)
    findings, files, total = [], 0, 0
    hashes = {}
    for path in sorted(iter_assets(root)):
        files += 1
        try:
            size = os.path.getsize(path)
        except OSError as exc:                       # pragma: no cover
            findings.append(("E2", "OVERSIZE", f"{path}: {exc}"))
            continue
        total += size
        rel = os.path.relpath(path, root)
        ext = os.path.splitext(path)[1].lower()
        cap = max_gif_bytes if ext == ".gif" else max_bytes
        if size > cap:
            findings.append(("E2", "OVERSIZE", f"{rel}: {size/1048576:.2f} MiB"))
        elif size > warn_bytes:
            findings.append(("W1", "LARGE_IMAGE", f"{rel}: {size/1024:.0f} KiB"))

        if ext == ".svg":
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:                          # pragma: no cover
                text = ""
            if DATA_URI.search(text):
                findings.append(("W2", "EMBEDDED_DATA_URI", f"{rel}: 内嵌 base64 位图"))
            m = SVG_WIDTH.search(text)
            if m and float(m.group(1)) > 1600:
                findings.append(("W4", "WIDE_SVG", f"{rel}: width={m.group(1)}"))

        try:
            with open(path, "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
        except OSError:                              # pragma: no cover
            continue
        hashes.setdefault((digest, ext), []).append(rel)

    for (digest, _ext), paths in hashes.items():
        if len(paths) > 1:
            findings.append(("W3", "DUPLICATE_BYTES",
                             f"{', '.join(paths)} → {digest[:12]}"))

    if files == 0:
        findings.append(("E1", "NO_ASSETS", "未找到任何 assets 图片（防扫错目录）"))
    return findings, files, total


def selftest():
    """最小复现：每类判据各造一个文件，断言被正确报出。"""
    cases = []

    def run(files, max_bytes=1024, warn_bytes=256, max_gif_bytes=4096):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, data in files.items():
                p = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                mode = "wb" if isinstance(data, bytes) else "w"
                with open(p, mode) as fh:
                    fh.write(data)
            return check(tmp, max_bytes, warn_bytes, max_gif_bytes)[0]

    # e0 根目录不存在
    try:
        check("/nonexistent-assetsizecheck-root", 1024, 256, 4096)
        cases.append(("e0", False, "应抛错但没抛"))
    except FileNotFoundError:
        cases.append(("e0", True, ""))

    # e1 没有 assets
    f = run({"docs/A/index.md": "# A"})
    cases.append(("e1", any(x[0] == "E1" for x in f), str(f)))

    # e2 超过上限
    f = run({"docs/A/assets/big.png": b"\0" * 4096})
    cases.append(("e2", any(x[0] == "E2" for x in f), str(f)))

    # e2gif GIF 单独一档：1.5 KiB 不该超 4 KiB 上限
    f = run({"docs/A/assets/anim.gif": b"\0" * 1536})
    cases.append(("e2gif", not any(x[0] == "E2" for x in f), str(f)))

    # e3 内嵌 base64
    f = run({"docs/A/assets/bomb.svg": '<svg width="900" height="500"><image href="data:image/png;base64,AAAA"/></svg>'})
    cases.append(("w2", any(x[0] == "W2" for x in f), str(f)))

    # w1 大而不超限
    f = run({"docs/A/assets/mid.png": b"\0" * 600})
    cases.append(("w1", any(x[0] == "W1" for x in f), str(f)))

    # w2 字节重复
    f = run({"docs/A/assets/x.svg": '<svg width="900" height="500"/>',
             "docs/B/assets/y.svg": '<svg width="900" height="500"/>'})
    cases.append(("w3", any(x[0] == "W3" for x in f), str(f)))

    # w3 超宽 SVG
    f = run({"docs/A/assets/wide.svg": '<svg width="2400" height="500"/>'})
    cases.append(("w4", any(x[0] == "W4" for x in f), str(f)))

    # 正常页：不应有任何 E
    f = run({"docs/A/assets/ok.svg": '<svg width="900" height="500"/>'})
    cases.append(("ok", not any(x[0].startswith("E") for x in f), str(f)))

    ok = 0
    for name, passed, msg in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + ("" if passed else f" :: {msg}"))
        ok += 1 if passed else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--max-bytes", type=int, default=1048576)
    ap.add_argument("--warn-bytes", type=int, default=307200)
    ap.add_argument("--max-gif-bytes", type=int, default=4194304)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"E0 ROOT_NOT_FOUND: {root}")
        return 2

    findings, files, total = check(root, args.max_bytes, args.warn_bytes, args.max_gif_bytes)
    errors = [x for x in findings if x[0].startswith("E")]
    warns = [x for x in findings if x[0].startswith("W")]

    for code, kind, msg in findings:
        if args.verbose or code.startswith("E"):
            print(f"{code} {kind}: {msg}")

    print(f"images={files} total_mib={total/1048576:.1f} "
          f"max_mib={args.max_bytes/1048576:.1f} gif_max_mib={args.max_gif_bytes/1048576:.1f} "
          f"E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
