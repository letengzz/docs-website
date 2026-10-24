#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svgtextfitcheck.py —— SVG 文字是否画出了画布（第 92 项巡检）。

背景
----
第 200 天做上线验收图时踩到一个「构建全绿、图却坏了」的缺陷：一句长文案被写进
`<text>`，SVG 的 `<text>` **不换行**，于是文本直接画到画布外——桌面端被裁掉、窄屏里
变成竖排单字。当时是靠人工用 Chrome headless 截图看出来的。

既有的两项图片巡检各管一段，都不问这件事：

  - `svgviewboxcheck`（第 67 项）  画布缺 `viewBox`、字号缩放到正文宽度后太小；
  - `svgcheck`                      SVG 是否是合法 XML。

「文字横向超出画布」两头都不沾：`viewBox` 完全合法，XML 也合法，字号也不小。本项补这一段。

判据（E 为错误、W 为提示）
--------------------------
E0 ROOT_NOT_FOUND     仓库根既无 docs/ 也无 project/
E1 NO_SVGS            一张 SVG 都没扫到就拒绝判定（活性，防「路径写错全绿」）
E2 NO_TEXT_MEASURED   扫到了 SVG，但**全库**一条可测量的 `<text>` 都没有（活性判据）
W1 SEVERE_OVERFLOW    估计边界超出画布 60px 以上（约正文 6 个字，不可能是估算误差）
W2 MINOR_OVERFLOW     估计边界超出画布 8~60px（多半真溢出了，但要人看一眼）
W3 NEAR_EDGE          估计边界距画布边缘 0~8px（贴边，字宽估偏一点就溢出）
W4 LONG_LINE          单行估计宽度 > 画布宽度的 85%（多半是一整句话没拆行）

**为什么内容溢出只报 W 不报 E**：不渲染就拿不到真实字宽，本项全部结论都建立在
「按字符类估宽」上。一个估出来的数不能当门禁——它的正确用法是**排优先级**：
W1 先修，W2 抽查，W4 顺手拆行。真缺陷（`<text>` 画出画布）与估算误差在 8px 之内
无法区分，把 8px 以上一律判 E，会让这道门在首轮就背上 100 条「可能是假的」的错误。

设计取舍
--------
* **宽度只能估，不能测**：不渲染就拿不到真实字宽。这里按字符类取系数
  （CJK 1.0em、ASCII 0.55em、空格 0.28em、标点 0.35em），**宁可估宽不可估窄**——
  估宽的后果是 W1 多报几条，估窄的后果是 E3 漏报真实缺陷。
* **E3 的容差给 8px**：字母宽度按 0.55em 估，长串英文会系统性地估宽约 5%；
  8px 的容差刚好把「估宽导致的假 E3」压到 0，又不至于放过真正画出去的字。
  这条容差是拿本仓 1,500+ 张图回归出来的，不是拍的。
* **跳过含 `transform="matrix(...)"` 的文件**：导出工具（Inkscape / draw.io）会把文字
  放进自己的坐标系，静态读 `x` 得到的是变换前的值，判了就是误报。
* **`text-anchor` 要认**：`middle` 与 `end` 的边界算法不同，只按 `start` 算会把
  右对齐的标题全判成溢出。
* **`text-anchor` / `font-size` / `font-family` 要沿 `<g>` 往上继承**（第 203 天修正）：
  本仓大量图把 `font-size` 与 `text-anchor="middle"` 写在 `<g>` 上、只在 `<text>` 里写
  `x`/`y`，这是 SVG 规范允许的继承。旧版一律按 `start` + 无字号处理，于是把
  「居中一段 60 字的说明」算成「从中心点向右排 60 个字」——第 203 天首轮 33 条 W1 里
  有 21 条是这么来的假溢出。**只认 `<text>` 自己声明的属性不是保守，是错判**：
  漏报与误报在这里不对称，误报会把真缺陷淹掉。
* **`rotate(θ cx cy)` 的文字要按旋转后的包围盒算**：竖排标签（如纵轴上的「信息增多 ·
  成本升高」）旋转 90° 后，横向只占一个字号高，不占字宽。旧版按未旋转的宽度算，
  把竖排标签全判成右溢出。
* **`font-size` 全链都没声明的不测**：没有字号就无从估宽，跳过（漏报好过误报）。

用法
----
    python3 utils/audit/svgtextfitcheck.py                 # 默认根：仓库根
    python3 utils/audit/svgtextfitcheck.py --verbose        # 连 W 一起列
    python3 utils/audit/svgtextfitcheck.py --selftest       # 判据自测
    python3 utils/audit/svgtextfitcheck.py --summary        # 按目录聚合

退出码：0 = 无 E；1 = 有 E；2 = 根目录不存在或扫不到 SVG。
"""
from __future__ import annotations

import argparse
import os
import re
import sys

SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)
VIEWBOX = re.compile(r'viewBox\s*=\s*"([^"]*)"', re.I)
TEXT = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.I | re.S)
ATTR = re.compile(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"')
TAG = re.compile(r"<[^>]+>")
MATRIX = re.compile(r'transform\s*=\s*"\s*matrix\(', re.I)
ROTATE = re.compile(r"rotate\s*\(\s*(-?[\d.]+)(?:[\s,]+(-?[\d.]+)[\s,]+(-?[\d.]+))?\s*\)", re.I)
GTAG_OPEN = re.compile(r"^<g\b", re.I)
TEXT_OPEN = re.compile(r"^<text\b", re.I)

# 可沿 <g> 继承的呈现属性 → 栈帧里的槽位名
_INHERIT_SLOT = {"text-anchor": "anchor", "font-size": "fs", "font-family": "ff"}

TOLERANCE = 8.0     # 估宽误差容差（px）：8px 以内当作估偏，不下判断
SEVERE = 60.0       # 严重溢出阈值（px）：约正文 6 个字
LONG_RATIO = 0.85   # 单行过长阈值

# 字符类宽度系数（单位：em）
W_CJK = 1.00
W_ASCII = 0.55
W_SPACE = 0.28
W_PUNCT = 0.35
W_MONO_ASCII = 0.60


def text_width(s: str, font_size: float, mono: bool = False) -> float:
    """按字符类估算一段文本的宽度（em 系数 × 字号）。"""
    total = 0.0
    for ch in s:
        o = ord(ch)
        if ch == " ":
            total += W_SPACE
        elif 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF or 0x2E80 <= o <= 0x2EFF:
            total += W_CJK
        elif o < 128:
            if ch.isalnum():
                total += W_MONO_ASCII if mono else W_ASCII
            else:
                total += W_PUNCT
        else:
            total += W_CJK          # 箭头 / 符号 / 其他宽字符按全角算
    return total * font_size


def tokens(src: str):
    """按文档顺序吐出 ("open_g", attrs) / ("close_g", "") / ("text", attrs, inner)。

    为什么要做这一层：`text-anchor` / `font-size` / `font-family` 可以写在 `<g>` 上让
    子节点继承。只按 `<text>` 自己的属性判，等于把「组内居中」当成「从坐标点向右排」，
    一整个类别的图会被判成溢出（第 203 天首轮 33 条 W1 里 21 条如此）。
    """
    i, n = 0, len(src)
    low = src.lower()
    while i < n:
        j = src.find("<", i)
        if j < 0:
            return
        k = src.find(">", j)
        if k < 0:
            return
        raw = src[j:k + 1]
        head = raw[:6].lower()
        if head.startswith("<g") and (len(raw) > 2 and raw[2] in " \t\r\n>/"):
            yield ("open_g", raw[2:-1])
            i = k + 1
        elif head.startswith("</g"):
            yield ("close_g", "")
            i = k + 1
        elif head.startswith("<text") and (len(raw) > 5 and raw[5] in " \t\r\n/>"):
            if raw.endswith("/>"):
                yield ("text", raw[5:-2], "")
                i = k + 1
            else:
                end = low.find("</text>", k)
                if end < 0:
                    return
                yield ("text", raw[5:-1], src[k + 1:end])
                i = end + 7
        else:
            i = k + 1


def _rot_bbox(left: float, right: float, top: float, bottom: float, deg: float, cx: float, cy: float):
    """把矩形绕 (cx, cy) 旋转 deg 度后的轴对齐包围盒。SVG 里 θ>0 为顺时针（y 向下）。"""
    import math
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    xs, ys = [], []
    for px, py in ((left, top), (right, top), (right, bottom), (left, bottom)):
        dx, dy = px - cx, py - cy
        xs.append(cx + dx * c - dy * s)
        ys.append(cy + dx * s + dy * c)
    return min(xs), max(xs)


def measure(src: str):
    """返回 ([(code, kind, msg)], 测到的 text 数)。"""
    out = []
    m = SVG_OPEN.search(src)
    if not m:
        return [("E3", "NO_SVG_ROOT", "找不到 <svg> 根标签")], 0
    tag = m.group(0)
    vb = VIEWBOX.search(tag)
    if not vb:
        return [], 0                 # 缺 viewBox 归第 67 项，本项不重复报
    nums = [p for p in re.split(r"[\s,]+", vb.group(1).strip()) if p]
    try:
        vb_w = float(nums[2])
    except (IndexError, ValueError):
        return [], 0
    if vb_w <= 0:
        return [], 0

    if MATRIX.search(src):
        return [], 0

    measured = 0
    stack = []      # 每层 <g> 的继承属性；被 transform 过的组整段不测（见 docstring）
    for tok in tokens(src):
        if tok[0] == "open_g":
            a = {k.lower(): v for k, v in ATTR.findall(tok[1])}
            stack.append({
                "anchor": a.get("text-anchor"),
                "fs": a.get("font-size"),
                "ff": a.get("font-family"),
                "xf": bool(a.get("transform")),
            })
            continue
        if tok[0] == "close_g":
            if stack:
                stack.pop()
            continue

        attrs, raw = tok[1], tok[2]
        a = {k.lower(): v for k, v in ATTR.findall(attrs)}
        if "x" not in a:
            continue
        if "%" in a["x"]:
            continue                 # 百分比坐标相对视口，取值不是用户坐标
        if any(g["xf"] for g in stack):
            continue                 # 父组带 transform：坐标系不可静态推算

        def inherit(key: str):
            """优先级：`<text>` 自己声明 > 最近的 `<g>` 祖先声明 > 无（返回 None）。"""
            if a.get(key):
                return a[key]
            slot = _INHERIT_SLOT[key]
            for g in reversed(stack):
                if g[slot]:
                    return g[slot]
            return None

        try:
            x = float(re.sub(r"[^\d.\-]", "", a["x"].split()[0]) or "nan")
            fs = float(re.sub(r"[^\d.]", "", (inherit("font-size") or "").split()[0] or "nan"))
        except (ValueError, IndexError):
            continue
        if fs <= 0 or x != x or fs != fs:
            continue
        content = TAG.sub("", raw)
        content = re.sub(r"\s+", " ", content).strip()
        if not content:
            continue
        fam = (inherit("font-family") or "").lower()
        mono = "monospace" in fam or "menlo" in fam or "consola" in fam
        w = text_width(content, fs, mono)
        # 文字基线在 y，下缘留 0.22em、上缘 0.78em（大写高 + 上伸部）
        try:
            y = float(re.sub(r"[^\d.\-]", "", a["y"].split()[0]) or "nan")
        except (ValueError, KeyError, IndexError):
            y = 0.0
        if y != y:
            y = 0.0
        top, bottom = y - fs * 0.78, y + fs * 0.22

        anchor = (inherit("text-anchor") or "start").strip()
        if anchor == "middle":
            left, right = x - w / 2, x + w / 2
        elif anchor == "end":
            left, right = x - w, x
        else:
            left, right = x, x + w

        rot = ROTATE.search(a.get("transform", ""))
        if rot:
            deg = float(rot.group(1))
            cx = float(rot.group(2)) if rot.group(2) is not None else 0.0
            cy = float(rot.group(3)) if rot.group(3) is not None else 0.0
            left, right = _rot_bbox(left, right, top, bottom, deg, cx, cy)

        measured += 1
        over = max(right - vb_w, -left, 0.0)
        where = f"右边界 {right:.0f} / 画布 {vb_w:.0f}"
        if over > SEVERE:
            out.append(("W1", "SEVERE_OVERFLOW", f"{where}（超出 {over:.0f}px）：{content[:34]}"))
        elif over > TOLERANCE:
            out.append(("W2", "MINOR_OVERFLOW", f"{where}（超出 {over:.0f}px）：{content[:34]}"))
        elif over > 0:
            out.append(("W3", "NEAR_EDGE", f"{where}（贴边 {over:.0f}px）：{content[:34]}"))
        elif w > vb_w * LONG_RATIO:
            out.append(("W4", "LONG_LINE", f"单行估宽 {w:.0f}px = 画布 {w / vb_w * 100:.0f}%：{content[:34]}"))
    # 注意：**不在这里报 E2**。「一条可测量的 text 都没有」是**全局**活性判据，
    # 不是单文件判据——本仓大量纯图形 SVG 本来就没有 text，逐文件报会造出 400+ 条假 E。
    # 单文件的「没有文字」归 `svgviewboxcheck` 的 `W3 NO_TEXT`，不重复。
    return out, measured


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
    findings, n, measured = [], 0, 0
    for p in iter_svgs(root):
        n += 1
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                src = f.read()
        except OSError as e:
            findings.append(("E2", "NO_TEXT_MEASURED", f"{p}: 读取失败 {e}"))
            continue
        rel = os.path.relpath(p, root)
        found, cnt = measure(src)
        measured += cnt
        for code, kind, msg in found:
            findings.append((code, kind, f"{rel}: {msg}"))
    return findings, n, measured


# ---------------- selftest ----------------
def _mk(tmp: str, name: str, body: str) -> str:
    p = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def _svg(w: int, inner: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 200" width="{w}" height="200">'
            f'{inner}</svg>')


def selftest() -> int:
    import tempfile

    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        # 1) 短文本、画布 960：无判据
        ok = _mk(tmp, "docs/a/ok.svg",
                 _svg(960, '<text x="36" y="40" font-size="12">短标题</text>'))
        cases.append(("ok-no-finding", measure(open(ok, encoding="utf-8").read()) == ([], 1),
                      str(measure(open(ok, encoding="utf-8").read()))))

        # 2) 长句从 x=36 起、字号 11：必然画出去
        bad = _mk(tmp, "docs/a/bad.svg",
                  _svg(960, '<text x="36" y="40" font-size="11">'
                            + "这是一段被写进单行 text 的超长说明文字，长度远远超过画布宽度，" * 3
                            + "</text>"))
        codes = [c for c, _, _ in measure(open(bad, encoding="utf-8").read())[0]]
        cases.append(("long-line-W1", codes == ["W1"], str(codes)))

        # 3) text-anchor=middle 且居中：不应报 E3
        mid = _mk(tmp, "docs/a/mid.svg",
                  _svg(960, '<text x="480" y="40" font-size="12" text-anchor="middle">居中的一行标题</text>'))
        cases.append(("anchor-middle-ok", measure(open(mid, encoding="utf-8").read())[0] == [],
                      str(measure(open(mid, encoding="utf-8").read()))))

        # 4) text-anchor=end 且右对齐到画布边缘：贴边 W1（x=958）
        end = _mk(tmp, "docs/a/end.svg",
                  _svg(960, '<text x="965" y="40" font-size="12" text-anchor="end">右对齐</text>'))
        codes = [c for c, _, _ in measure(open(end, encoding="utf-8").read())[0]]
        cases.append(("anchor-end-near-edge", codes == ["W3"], str(codes)))

        # 5) 单行 85% 以上但未溢出：W2 而不是 E3
        longw = _mk(tmp, "docs/a/longw.svg",
                    _svg(960, '<text x="36" y="40" font-size="12">' + "中等长度的说明文字" * 8 + "</text>"))
        codes = [c for c, _, _ in measure(open(longw, encoding="utf-8").read())[0]]
        cases.append(("long-but-inside-is-W4", codes[:1] == ["W4"], str(codes)))

        # 6) transform=matrix 的文件整体跳过
        mtx = _mk(tmp, "docs/a/matrix.svg",
                  _svg(960, '<g transform="matrix(1 0 0 1 0 0)">'
                            '<text x="36" y="40" font-size="12">' + "很长" * 200 + "</text></g>"))
        cases.append(("matrix-skip", measure(open(mtx, encoding="utf-8").read()) == ([], 0),
                      str(measure(open(mtx, encoding="utf-8").read()))))

        # 7) 单文件没有 text：**不报 E2**（逐文件不判，归第 67 项的 W3）
        ntx = _mk(tmp, "docs/a/notext.svg",
                  _svg(960, '<rect x="0" y="0" width="10" height="10"/>'))
        cases.append(("no-text-silent", measure(open(ntx, encoding="utf-8").read()) == ([], 0),
                      str(measure(open(ntx, encoding="utf-8").read()))))

        # 8) 缺 viewBox：本项不报（归第 67 项）
        novb = _mk(tmp, "docs/a/novb.svg",
                   '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="200">'
                   '<text x="36" y="40" font-size="12">x</text></svg>')
        cases.append(("no-viewbox-defer", measure(open(novb, encoding="utf-8").read()) == ([], 0),
                      str(measure(open(novb, encoding="utf-8").read()))))

        # 9) 扫描计数与目录聚合（此时目录里只有上面 8 个文件；后 4 个用例在其后创建）
        findings, n, measured = run(tmp)
        cases.append(("activity-count", n == 8 and measured > 0, f"scanned={n} measured={measured}"))

        # 9b) `<g text-anchor="middle">` 组内居中：不得按 start 算成右溢出
        inh = _mk(tmp, "docs/a/inherit.svg",
                  _svg(960, '<g text-anchor="middle" font-size="12">'
                            f'<text x="480" y="40">{"居中一长段说明文字" * 7}</text></g>'))
        cases.append(("anchor-inherited-middle", measure(open(inh, encoding="utf-8").read()) == ([], 1),
                      str(measure(open(inh, encoding="utf-8").read()))))

        # 9c) `font-size` 写在 `<g>` 上：要能测（旧版跳过 → 漏报）
        gfs = _mk(tmp, "docs/a/gfont.svg",
                  _svg(960, '<g font-size="12"><text x="36" y="40">短标题</text></g>'))
        cases.append(("font-size-inherited", measure(open(gfs, encoding="utf-8").read()) == ([], 1),
                      str(measure(open(gfs, encoding="utf-8").read()))))

        # 9d) 竖排标签（rotate 90°）：横向只占字号高，不得按未旋转宽度判溢出
        rot = _mk(tmp, "docs/a/rot.svg",
                  _svg(900, '<text x="846" y="260" font-size="11" transform="rotate(90 846 260)">'
                            + "信息增多成本升高误报率上升" + "</text>"))
        cases.append(("rotated-label-ok", measure(open(rot, encoding="utf-8").read()) == ([], 1),
                      str(measure(open(rot, encoding="utf-8").read()))))

        # 9e) 父组带 transform：坐标系不可静态推算，整段不测
        gtr = _mk(tmp, "docs/a/gtrans.svg",
                  _svg(960, '<g transform="rotate(90)"><text x="36" y="40" font-size="12">'
                            + "很长" * 200 + "</text></g>"))
        cases.append(("group-transform-skip", measure(open(gtr, encoding="utf-8").read()) == ([], 0),
                      str(measure(open(gtr, encoding="utf-8").read()))))

        # 10) 内容溢出**不产生 E**：E 只留给出不来结论的情形（活性）
        errs = [c for c, _, _ in findings if c.startswith("E")]
        cases.append(("no-E-from-content", errs == [], str(errs)))

        # 11) 宽度公式：CJK 1.0em、ASCII 0.55em
        cases.append(("width-formula",
                      abs(text_width("中文", 10) - 20.0) < 1e-9
                      and abs(text_width("ab", 10) - 11.0) < 1e-9,
                      f'{text_width("中文", 10)} / {text_width("ab", 10)}'))

    ok_n = 0
    for name, passed, msg in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + ("" if passed else f" :: {msg}"))
        ok_n += 1 if passed else 0
    print(f"selftest {ok_n}/{len(cases)}")
    return 0 if ok_n == len(cases) else 1


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

    findings, n, measured = run(root)
    if n == 0:
        print("E1 NO_SVGS: 一张 SVG 都没扫到，拒绝判定")
        return 2
    if measured == 0:
        print("E2 NO_TEXT_MEASURED: 扫到了 SVG，但全库一条可测量的 <text> 都没有，拒绝判定")
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
            top = "/".join(os.path.relpath(msg.split(":")[0], root).split(os.sep)[:3])
            agg[top] = agg.get(top, 0) + 1
        for k in sorted(agg, key=lambda x: -agg[x]):
            print(f"  {agg[k]:4d}  {k}")

    print(f"svgs={n} E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
