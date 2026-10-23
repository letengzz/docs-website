#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svgcontrastcheck.py —— SVG「文字与背景对比度」巡检（第 202 天新立，第 93 项巡检）

## 动机（第 N 次「某个维度整体没人看」）

本库对 SVG 已有两道门，都只问「结构对不对」：

  * 第 67 项 `svgviewboxcheck` —— 有没有 `viewBox`、缩放后字号是否过小；
  * 第 92 项 `svgtextfitcheck` —— 文字有没有横向画到画布外。

它们都不问一件更基础的事：**这段字和它背后的颜色，读者分不分得清**。而本库的示意图
是手写 SVG，配色靠人记（`#0f172a` 是正文色、`#475569` 是注释色、`#94a3b8` 是辅助线色）。
一旦把注释色 `#475569` 写到深色块上，或者把 `#e2e8f0` 写在白底上：

  * 构建全绿（XML 合法、`viewBox` 合法、字号不小、也没出画布）；
  * 桌面端「大概能看」，窄屏缩放后直接消失；
  * 截图放进 PPT 后，投影仪上一片灰。

这类缺陷不影响任何门禁，只影响读者——正是本库 90 多项巡检反复验证的那类「永久沉默」。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND     给定根目录不存在
  E1 NO_SVGS            一个 SVG 都没扫到（活性判据：拒绝在空集上给「全绿」）
  E2 NO_TEXT_MEASURED   全库没有一条可测量的文字（活性判据：防止解析器整体失效）
  W1 INVISIBLE          对比度 < 1.3 —— 基本等于看不见（同色或近似同色）
  W2 SEVERE             1.3 ≤ 对比度 < 2.0 —— 明显吃力
  W3 LOW                2.0 ≤ 对比度 < 3.0 —— 低于 WCAG AA 对大字的 3:1 要求

## 为什么内容问题只报 W（与第 92 项同一条纪律）

判据全部建立在「按字符类估宽 + 按包含关系推背景」之上：

1. **背景是推出来的，不是渲染出来的**。文字背后可能是 `<rect>`、`<path>`、渐变、
   `<image>`，本脚本只认「矩形填充」，认不出的一律不进结论（计入 `nobg`）。
2. **对比度是精确值，但「背景是什么」不精确**。同一个 `#475569`，在白底上是 8.9:1、
   在深蓝底上是 1.1:1——判错的代价是让人去改一张没问题的图。

所以：**估出来的数不能当门禁**，它的正确用法是排优先级。真正要拦的是「结构性」问题
（找不到 SVG、解析不到文字），那才是 E。

## 口径（被真实语料打出来的几条）

1. **只认矩形背景，且只认「画在文字之前」的矩形**。SVG 是按文档顺序绘制的，后画的覆盖
   先画的；文字的背景必然是它之前最后一个包含它的矩形。
2. **`fill` 缺省时跳过**，不假设黑色。`<text>` 不写 `fill` 会继承父级，父级可能带
   `fill="#fff"`，硬当黑色会制造大量假 W。
3. **`fill="url(#...)"`、`none`、带透明度的颜色一律跳过**。渐变背景的真实颜色取决于
   渐变停靠点与坐标，估不出来就别猜。
4. **`opacity` / `fill-opacity` < 0.85 跳过**：半透明文字的真实对比度还取决于混合，
   本脚本不建模。
5. **`text-anchor` 必须认**：取「文字的锚点」作为采样点，`middle` 取中点、`end` 取右端；
   只按 `start` 算会把右对齐的标题采样到框外。
6. **一个文件里没有可测量文字不报 E**：本库大量纯图形 SVG 本来就没有文字，逐文件报 E
   会一次造出几百条假 E（第 92 项踩过这个坑）。

## 用法

    python3 utils/audit/svgcontrastcheck.py [--root docs project] [--selftest] [--top 15]

退出码：0 = 无 E（W 不影响退出码）；1 = 存在 E；2 = 参数或根目录错误。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)
STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
RECT_RE = re.compile(r"<(rect|circle|ellipse)\b([^>]*?)/?>", re.S)
ATTR_RE = re.compile(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"')

NAMED = {
    "white": (255, 255, 255), "black": (0, 0, 0), "red": (255, 0, 0), "green": (0, 128, 0),
    "blue": (0, 0, 255), "gray": (128, 128, 128), "grey": (128, 128, 128),
    "lightgray": (211, 211, 211), "darkgray": (169, 169, 169), "none": None,
}


def parse_color(value: str):
    """返回 (r, g, b, alpha) 或 None（无法解析 / 应跳过）。"""
    if not value:
        return None
    v = value.strip().lower()
    if v in ("none", "transparent", "currentcolor"):
        return None
    if v.startswith("url("):
        return None
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            try:
                return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
            except ValueError:
                return None
        return None
    if v.startswith("rgb"):
        nums = re.findall(r"[\d.]+", v)
        if len(nums) >= 3:
            r, g, b = (min(255, int(float(x))) for x in nums[:3])
            a = float(nums[3]) if len(nums) >= 4 else 1.0
            return (r, g, b, a)
        return None
    if v in NAMED:
        rgb = NAMED[v]
        return None if rgb is None else (*rgb, 1.0)
    return None


def luminance(rgb) -> float:
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(fg, bg) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def css_fills(src: str) -> dict:
    """极简 CSS 支持：只取 `.cls { fill: #xxx }` 与 `tag { fill: #xxx }`。

    本库的 SVG 大量用 <style> 定义 `.hd` / `.tag` 这类类名，颜色不在属性上。
    不解析它就会把「深色表头 + 白字」误判成「白底白字」——第 202 天首轮 38 条 W1
    里绝大多数都是这个假象。只解析 fill，不做级联、不做优先级计算。
    """
    rules: dict[tuple[str, str], str] = {}
    for block in STYLE_RE.findall(src):
        for sel, decl in RULE_RE.findall(block):
            m = re.search(r"fill\s*:\s*([^;]+)", decl)
            if not m:
                continue
            color = m.group(1).strip()
            for one in sel.split(","):
                one = one.strip()
                if one.startswith("."):
                    rules[("class", one[1:])] = color
                elif one.isidentifier():
                    rules[("tag", one)] = color
    return rules


def resolve_fill(d: dict, tag: str, rules: dict):
    """属性优先，其次 class，其次标签选择器；都没有返回 None（不猜）。"""
    c = parse_color(d.get("fill", ""))
    if c is not None:
        return c
    if d.get("fill", "").strip().lower() == "none":
        return None
    cls = d.get("class", "")
    if cls:
        for name in cls.split():
            if ("class", name) in rules:
                return parse_color(rules[("class", name)])
        return "UNKNOWN"
    if ("tag", tag) in rules:
        return parse_color(rules[("tag", tag)])
    return None


def attrs_of(s: str) -> dict:
    return {k: v for k, v in ATTR_RE.findall(s)}


def num(d: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(str(d.get(key, default)).replace("px", "").strip())
    except ValueError:
        return default


def scan_file(path: str):
    """返回 (measurements, skipped)。measurement = (ratio, raw_text, fg, bg)"""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    rules = css_fills(src)
    rects = []
    for m in RECT_RE.finditer(src):
        tag, raw_attrs = m.group(1), m.group(2)
        d = attrs_of(raw_attrs)
        c = resolve_fill(d, tag, rules)
        if c is None:
            continue
        if tag == "rect":
            box = (num(d, "x"), num(d, "y"), num(d, "width"), num(d, "height"))
        else:  # circle / ellipse：用外接矩形近似
            cx, cy = num(d, "cx"), num(d, "cy")
            rx = num(d, "r") or num(d, "rx")
            ry = num(d, "r") or num(d, "ry")
            box = (cx - rx, cy - ry, rx * 2, ry * 2)
        rects.append((m.start(), *box, c))

    out, skipped = [], 0
    for m in TEXT_RE.finditer(src):
        d = attrs_of(m.group(1))
        fg = resolve_fill(d, "text", rules)
        if fg is None or fg == "UNKNOWN" or fg[3] < 0.85:
            skipped += 1
            continue
        if num(d, "opacity", 1.0) < 0.85 or num(d, "fill-opacity", 1.0) < 0.85:
            skipped += 1
            continue
        x, y = num(d, "x"), num(d, "y")
        fs = num(d, "font-size", 12.0)
        if fs < 4:
            # font-size=0 的「占位」文字不参与对比度判断：它本来就不可见，
            # 报出来只是噪声（第 202 天首轮 W1 里唯一那条就是这种）。
            skipped += 1
            continue
        raw = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if not raw:
            skipped += 1
            continue
        # x 本身就是文字上的一个点：start 是左端、middle 是中心、end 是右端，
        # 三种锚点都用 x 采样即可（第 202 天首版对 middle 加了半个字宽，
        # 把「深色块上的白字」采到了块外，一次造出 36 条假 W1）。
        sx = x
        sy = y - fs * 0.35

        bg = None
        for start, rx, ry, rw, rh, c in rects:
            if start > m.start():
                break
            if rx <= sx <= rx + rw and ry <= sy <= ry + rh:
                bg = c
        if bg is None or bg == "UNKNOWN":
            skipped += 1
            continue
        out.append((contrast(fg, bg), raw, fg, bg))
    return out, skipped


def walk(roots):
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for fn in sorted(files):
                if fn.lower().endswith(".svg"):
                    yield os.path.join(dirpath, fn)


def run(roots, top=15):
    total_svg = measured = skipped_total = 0
    buckets = {"W1": [], "W2": [], "W3": []}
    for path in walk(roots):
        total_svg += 1
        try:
            rows, skipped = scan_file(path)
        except (OSError, UnicodeDecodeError):
            continue
        measured += len(rows)
        skipped_total += skipped
        for ratio, text, fg, bg in rows:
            key = "W1" if ratio < 1.3 else ("W2" if ratio < 2.0 else ("W3" if ratio < 3.0 else None))
            if key:
                buckets[key].append((ratio, path, text))

    e = 0
    if not os.path.isdir(roots[0]):
        print(f"E0 ROOT_NOT_FOUND {roots[0]}")
        e += 1
    if total_svg == 0:
        print("E1 NO_SVGS 一个 SVG 都没扫到（检查路径）")
        e += 1
    if measured == 0:
        print("E2 NO_TEXT_MEASURED 没有一条可测量的文字（解析器可能整体失效）")
        e += 1

    names = {"W1": "INVISIBLE", "W2": "SEVERE", "W3": "LOW"}
    print(f"svgs={total_svg} measured_texts={measured} skipped={skipped_total} "
          f"W1={len(buckets['W1'])} W2={len(buckets['W2'])} W3={len(buckets['W3'])}")
    for key in ("W1", "W2", "W3"):
        rows = sorted(buckets[key])[:top]
        for ratio, path, text in rows:
            short = text if len(text) <= 28 else text[:28] + "…"
            print(f"{key} {names[key]} {ratio:.2f}:1 {path} :: {short}")
        rest = len(buckets[key]) - len(rows)
        if rest > 0:
            print(f"{key} ... 另有 {rest} 条同类，未展开")
    return 1 if e else 0, buckets


# ---------------------------------------------------------------- selftest

BASE = ('<rect x="0" y="0" width="240" height="34" fill="#ffffff"/>'
        '<text x="6" y="22" fill="#111827">baseline</text>')

# (说明, 片段, 期望 W 条数, 期望出现在哪一档)
CASES = [
    ("白底黑字", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                 '<text x="10" y="80" fill="#000000">ok</text>', 0, "none"),
    ("白底白字", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                 '<text x="10" y="80" fill="#ffffff">invisible</text>', 1, "W1"),
    ("白底浅灰字", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                   '<text x="10" y="80" fill="#e2e8f0">faint</text>', 1, "W1"),
    ("白底中灰字", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                   '<text x="10" y="80" fill="#94a3b8">low</text>', 1, "W3"),
    ("深底白字", '<rect x="0" y="40" width="240" height="70" fill="#1e3a8a"/>'
                 '<text x="10" y="80" fill="#ffffff">good</text>', 0, "none"),
    ("无 fill 不猜", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                     '<text x="10" y="80">inherit</text>', 0, "none"),
    ("渐变跳过", '<rect x="0" y="40" width="240" height="70" fill="url(#g)"/>'
                 '<text x="10" y="80" fill="#ffffff">grad</text>', 0, "none"),
    ("三字简写", '<rect x="0" y="40" width="240" height="70" fill="#fff"/>'
                 '<text x="10" y="80" fill="#123">shorthand</text>', 0, "none"),
    ("middle 采样点", '<rect x="0" y="40" width="240" height="70" fill="#0f172a"/>'
                      '<text x="120" y="80" text-anchor="middle" fill="#e2e8f0">centered</text>', 0, "none"),
    ("内层深底覆盖外层", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                        '<rect x="20" y="50" width="200" height="50" fill="#0f172a"/>'
                        '<text x="40" y="80" fill="#ffffff">inner</text>', 0, "none"),
    ("无背景可推不猜", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                       '<rect x="30" y="50" width="180" height="50" fill="#0f172a"/>'
                       '<text x="40" y="80" fill="#ffffff">inner</text>'
                       '<text x="150" y="118" fill="#ffffff">no-bg</text>', 0, "none"),
    ("透明文字跳过", '<rect x="0" y="40" width="240" height="70" fill="#ffffff"/>'
                     '<text x="10" y="80" fill="#000000" opacity="0.3">faded</text>', 0, "none"),
]

def selftest() -> int:
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        for i, (name, svg, expect_n, expect_kind) in enumerate(CASES, 1):
            sub = os.path.join(td, f"c{i}")
            os.makedirs(sub, exist_ok=True)
            with open(os.path.join(sub, "a.svg"), "w", encoding="utf-8") as f:
                f.write(f'<svg viewBox="0 0 240 120">{BASE}{svg}</svg>')
            code, buckets = run([sub], top=50)
            total_w = sum(len(v) for v in buckets.values())
            kinds = [k for k, v in buckets.items() if v]
            good = (code == 0) and (total_w == expect_n) and (expect_kind == "none" or expect_kind in kinds)
            ok += 1 if good else 0
            print(f"  [{'PASS' if good else 'FAIL'}] {i:02d} {name}: W={total_w} 期望 {expect_n}/{expect_kind}")
        # 空目录 → E1
        empty = os.path.join(td, "empty")
        os.makedirs(empty, exist_ok=True)
        code, _ = run([empty])
        good = code == 1
        ok += 1 if good else 0
        print(f"  [{'PASS' if good else 'FAIL'}] 13 空目录: 退出码 {code} 期望 1（E1）")
        # 只有图形没有文字 → E2
        noText = os.path.join(td, "notext")
        os.makedirs(noText, exist_ok=True)
        with open(os.path.join(noText, "a.svg"), "w", encoding="utf-8") as f:
            f.write('<svg viewBox="0 0 10 10"><rect width="10" height="10" fill="#fff"/></svg>')
        code, _ = run([noText])
        good = code == 1
        ok += 1 if good else 0
        print(f"  [{'PASS' if good else 'FAIL'}] 14 全是无文字图: 退出码 {code} 期望 1（E2）")
        # 目录不存在 → E0
        code, _ = run([os.path.join(td, "nope")])
        good = code == 1
        ok += 1 if good else 0
        print(f"  [{'PASS' if good else 'FAIL'}] 15 目录不存在: 退出码 {code} 期望 1（E0）")
    print(f"selftest {ok}/{len(CASES) + 3} PASS")
    return 0 if ok == len(CASES) + 3 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="SVG 文字与背景对比度巡检")
    ap.add_argument("--root", nargs="+", default=["docs", "project"])
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    for r in args.root:
        if not os.path.isdir(r):
            print(f"E0 ROOT_NOT_FOUND {r}")
            return 2
    code, _ = run(args.root, top=args.top)
    return code


if __name__ == "__main__":
    sys.exit(main())
