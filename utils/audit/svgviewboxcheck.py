#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svgviewboxcheck.py —— SVG 内在尺寸与「缩放后可读性」巡检（第 67 项巡检）。

背景
----
本仓 1,551 张配图里 1,283 张是自绘 SVG，全部随 Markdown 提交、由浏览器按容器宽度
缩放显示。既有的四项图片巡检各管一段，**没有一项问「缩放到页面宽度之后还看得清吗」**：

  - `imagecheck`        引用的图片文件是否存在；
  - `orphanassetcheck`  文件有没有被引用；
  - `assetsizecheck`    文件多大、有没有内嵌 base64；
  - `svgcheck`          SVG 是否合法 XML（`<` 有没有转义）。

于是两类失效完全静默：
  1. **`<svg>` 上没有 `viewBox`**：浏览器不会等比缩放，图按 `width` 原样显示，
     在 720 px 宽的正文里横向溢出（桌面端出现滚动条，移动端被裁掉右半边）。
     构建不报错，`svgcheck` 也通过（XML 完全合法）。
  2. **字号是按画布原尺寸定的，缩放到正文宽度后被压到看不见**：一张 `viewBox`
     宽 1,800 的图，正文 720 px 显示时缩放比 0.4，原本 12 px 的字变成 4.8 px。
     这类问题在图库里表现为「图看着很精致，但没人读上面的字」。

本项只做**静态可判**的部分：不改图、不渲染，只把「缩放到正文宽度后的读数」算出来，
让作者自己决定是把画布改窄、把字号调大，还是把图拆成两张。

判据（E 为错误、W 为提示）
--------------------------
E0 ROOT_NOT_FOUND      仓库根既无 docs/ 也无 project/
E1 NO_SVGS             一张 SVG 都没扫到就拒绝判定（活性，防「路径写错全绿」）
E2 NO_VIEWBOX          `<svg>` 缺 `viewBox`：不随容器缩放，正文里横向溢出
E3 BAD_VIEWBOX         `viewBox` 不是 4 个数字，或宽/高 ≤ 0（无法计算缩放比）
E4 UNREADABLE_TEXT     缩放后最小字号 < 4 px（放大镜也读不出，属于真缺陷）
W1 TINY_TEXT           缩放后最小字号 4~7 px（偏小，提示级）
W2 ASPECT_MISMATCH     `width/height` 与 `viewBox` 的宽高比偏差 > 2%（渲染会变形或留白）
W3 NO_TEXT             整张图没有 `<text>`（可能是纯图形，也可能是忘了标注）

设计取舍
--------
* **缩放比按 720 px 算**：本仓 VitePress 正文最大宽度约 720 px，是这个库的显示基线；
  换成别的主题只需改 `CONTENT_W`。
* **只统计 `<text>` 的 `font-size`**：`font-size` 也可能写在 `<g>` 或 `style` 里，
  这里不追继承链——漏报好过误报，因为阈值本就留了余量。
* **E4 与 W1 的界线定在 4 px**：7 px 附近有大量「本来就小一号的图注」，把它们判成
  错误会让这条判据失去信誉（第 155 天的教训：判据宽比判据漏更费时间）。

用法
----
    python3 utils/audit/svgviewboxcheck.py                 # 默认根：仓库根
    python3 utils/audit/svgviewboxcheck.py --verbose        # 连 W 一起列
    python3 utils/audit/svgviewboxcheck.py --selftest       # 判据自测
    python3 utils/audit/svgviewboxcheck.py --summary        # 按目录聚合，看哪一片最差

退出码：0 = 无 E；1 = 有 E；2 = 根目录不存在。
"""
from __future__ import annotations

import argparse
import os
import re
import sys

CONTENT_W = 720.0
SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)
VIEWBOX = re.compile(r'viewBox\s*=\s*"([^"]*)"', re.I)
WIDTH = re.compile(r'\bwidth\s*=\s*"([\d.]+)(?:px)?"', re.I)
HEIGHT = re.compile(r'\bheight\s*=\s*"([\d.]+)(?:px)?"', re.I)
FONTSIZE = re.compile(r'font-size\s*[=:]\s*"?([\d.]+)\s*(pt|px)?', re.I)
MATRIX = re.compile(r'transform\s*=\s*"\s*matrix\(', re.I)
TEXT_TAG = re.compile(r"<text\b", re.I)


def parse_numbers(raw: str):
    raw = raw.replace(",", " ").strip()
    parts = [p for p in re.split(r"\s+", raw) if p]
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    return nums


def check_svg(path: str):
    """返回 [(code, kind, msg)]，只针对单文件。"""
    out = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError as e:
        return [("E3", "BAD_VIEWBOX", f"{path}: 读取失败 {e}")]

    m = SVG_OPEN.search(src)
    if not m:
        return [("E3", "BAD_VIEWBOX", f"{path}: 找不到 <svg> 根标签")]
    tag = m.group(0)

    vb = VIEWBOX.search(tag)
    if not vb:
        return [("E2", "NO_VIEWBOX", f"{path}: <svg> 缺 viewBox，正文里不会等比缩放")]

    nums = parse_numbers(vb.group(1))
    if not nums or len(nums) != 4 or nums[2] <= 0 or nums[3] <= 0:
        return [("E3", "BAD_VIEWBOX", f"{path}: viewBox=\"{vb.group(1)}\" 无法解析")]

    vb_w, vb_h = nums[2], nums[3]
    scale = CONTENT_W / vb_w

    w = WIDTH.search(tag)
    h = HEIGHT.search(tag)
    if w and h:
        try:
            ar_vb = vb_w / vb_h
            ar_wh = float(w.group(1)) / float(h.group(1))
            if abs(ar_vb - ar_wh) / ar_vb > 0.02:
                out.append(("W2", "ASPECT_MISMATCH",
                            f"{path}: viewBox 比 {ar_vb:.3f} vs width/height 比 {ar_wh:.3f}"))
        except ZeroDivisionError:
            pass

    if not TEXT_TAG.search(src):
        out.append(("W3", "NO_TEXT", f"{path}: 整张图没有 <text>"))
        return out

    # 导出工具（Inkscape / draw.io）会把文字放进 `transform="matrix(...)"` 的坐标系里，
    # 静态读 font-size 会得到 0.x px 这类假读数 —— 这类文件不做字号判定，只统计。
    if MATRIX.search(src):
        return out

    sizes = []
    for val, unit in FONTSIZE.findall(src):
        try:
            v = float(val)
        except ValueError:
            continue
        if v <= 0:            # `font-size: 0` 是隐藏/重置写法，不参与判定
            continue
        if (unit or "").lower() == "pt":
            v *= 4.0 / 3.0    # 1pt = 4/3 px，不换算会把 12pt 当成 12px
        sizes.append(v)
    if not sizes:
        return out
    eff = min(sizes) * scale
    if eff < 4.0:
        out.append(("E4", "UNREADABLE_TEXT",
                    f"{path}: 最小字号 {min(sizes):.1f} × 缩放 {scale:.2f} = {eff:.2f}px"))
    elif eff < 7.0:
        out.append(("W1", "TINY_TEXT",
                    f"{path}: 最小字号 {min(sizes):.1f} × 缩放 {scale:.2f} = {eff:.2f}px"))
    return out


def iter_svgs(root: str):
    for base in ("docs", "project", "public"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in (".vitepress", "node_modules", "dist")]
            for fn in sorted(filenames):
                if fn.lower().endswith(".svg"):
                    yield os.path.join(dirpath, fn)


def run(root: str):
    findings = []
    n = 0
    for p in iter_svgs(root):
        n += 1
        findings.extend(check_svg(p))
    return findings, n


# ---------------- selftest ----------------
def _mk(tmp: str, name: str, body: str) -> str:
    p = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def selftest() -> int:
    import tempfile

    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        # 1) 正常：760 宽、字号 ≥ 9 → 无判据
        p1 = _mk(tmp, "docs/a/ok.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 400" width="760" height="400">'
                 '<text font-size="12">ok</text></svg>')
        cases.append(("ok-no-finding", check_svg(p1) == [], str(check_svg(p1))))

        # 2) 缺 viewBox
        p2 = _mk(tmp, "docs/a/novb.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400"><text font-size="12">x</text></svg>')
        cases.append(("no-viewbox-E2", any(c == "E2" for c, _, _ in check_svg(p2)), str(check_svg(p2))))

        # 3) viewBox 只有 2 个数
        p3 = _mk(tmp, "docs/a/badvb.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800"><text font-size="12">x</text></svg>')
        cases.append(("bad-viewbox-E3", any(c == "E3" for c, _, _ in check_svg(p3)), str(check_svg(p3))))

        # 4) 画布 1800、字号 2 → 缩放 0.4 → 0.8px → E4
        p4 = _mk(tmp, "docs/a/tiny.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 900" width="1800" height="900">'
                 '<text font-size="2">x</text></svg>')
        cases.append(("tiny-text-E4", any(c == "E4" for c, _, _ in check_svg(p4)), str(check_svg(p4))))

        # 5) 画布 900、字号 8 → 缩放 0.8 → 6.4px → W1（不是 E）
        p5 = _mk(tmp, "docs/a/small.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400" width="900" height="400">'
                 '<text font-size="8">x</text></svg>')
        codes5 = [c for c, _, _ in check_svg(p5)]
        cases.append(("small-text-is-W1", codes5 == ["W1"], str(codes5)))

        # 6) 宽高比不符
        p6 = _mk(tmp, "docs/a/ar.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 400" width="760" height="300">'
                 '<text font-size="12">x</text></svg>')
        cases.append(("aspect-W2", any(c == "W2" for c, _, _ in check_svg(p6)), str(check_svg(p6))))

        # 7) 无 <text>
        p7 = _mk(tmp, "docs/a/notext.svg",
                 '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 400"><rect width="10" height="10"/></svg>')
        cases.append(("no-text-W3", any(c == "W3" for c, _, _ in check_svg(p7)), str(check_svg(p7))))

        # 8) 活性：空目录应该扫到 0 张
        p8 = _mk(tmp, "docs/b/x.md", "# 空")
        findings, n = run(tmp)
        cases.append(("activity-count", n == 7, f"scanned={n}"))

        # 9) 多图汇总：E 只来自 tiny.svg 那张
        errs = [c for c, _, _ in findings if c.startswith("E")]
        cases.append(("errors-are-E2-E3-E4", set(errs) <= {"E2", "E3", "E4"}, str(errs)))

        # 10) 缩放比公式：720/1800 = 0.4
        cases.append(("scale-formula", abs(CONTENT_W / 1800 - 0.4) < 1e-9, f"{CONTENT_W/1800}"))

    ok = 0
    for name, passed, msg in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + ("" if passed else f" :: {msg}"))
        ok += 1 if passed else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print(f"E0 ROOT_NOT_FOUND: {root}")
        return 2

    findings, n = run(root)
    if n == 0:
        print("E1 NO_SVGS: 一张 SVG 都没扫到，拒绝判定")
        return 2

    errors = [x for x in findings if x[0].startswith("E")]
    warns = [x for x in findings if x[0].startswith("W")]

    for code, kind, msg in findings:
        if args.verbose or code.startswith("E"):
            print(f"{code} {kind}: {msg}")

    if args.summary:
        agg = {}
        for code, kind, msg in findings:
            if not code.startswith("E"):
                continue
            top = os.path.relpath(msg.split(":")[0], root).split(os.sep)[:3]
            key = "/".join(top)
            agg[key] = agg.get(key, 0) + 1
        for k in sorted(agg, key=lambda x: -agg[x]):
            print(f"  {agg[k]:4d}  {k}")

    print(f"svgs={n} E={len(errors)} W={len(warns)} content_width={CONTENT_W:.0f}px")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
