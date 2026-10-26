#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svgrefcheck.py —— SVG 内部引用完整性巡检（第 100 项巡检）

## 动机（本仓「图能编译，不代表图能画对」的第四例）

本仓配图以自绘 SVG 为主，靠 `id` + `url(#id)` 互相引用：箭头靠 `marker-end`、
渐变靠 `fill="url(#g)"`、裁剪靠 `clip-path="url(#c)"`。已有的四项 SVG 巡检各看一段：

  * `svgcheck`（历史名）    —— 是否合法 XML（`<` 有没有转义）；
  * `svgviewboxcheck`       —— 有没有 `viewBox`、缩放到正文宽度后字号还看得清吗；
  * `svgtextfitcheck`       —— 文字有没有溢出容器；
  * `svgcontrastcheck`      —— 文字与背景的对比度够不够。

四项**全部假设「引用本身指向存在的 id」**。于是三类失效完全静默：

  1. **`marker-end="url(#arrow)"` 而 `<marker id="ar">`**：改过 id 一半，箭头消失，
     图从「A → B」变成「A   B」，读者靠猜。**这是最贵的一类**——它不报错、不影响
     构建、文字与对比度全部合规，只是语义丢了。
  2. **`fill="url(#g1)"` 而渐变被删**：按 SVG 规范 `url()` 解析失败时该属性置为
     `none`，矩形直接「消失」，看起来像「我少画了一个块」。
  3. **同一个 id 在一个文件里出现两次**：浏览器取第一个，作者以为自己改了第二个。

## 判据（E = 错误；W = 提示；N = 计数）

  E0 ROOT_NOT_FOUND        仓库根既无 docs/ 也无 project/
  E1 NO_SVGS               一张 SVG 都没扫到就拒绝判定（活性，防「路径写错全绿」）
  E2 DANGLING_PAINT_REF    `fill`/`stroke`/`filter`/`clip-path`/`mask`/`style` 里的
                           `url(#x)` 指向不存在的 id（渲染降级为 `none`，图形消失）
  E3 DANGLING_MARKER_REF   `marker-start|mid|end` 里的 `url(#x)` 不存在（**箭头静默消失**）
  E4 DANGLING_USE_REF      `<use href="#x">` / `xlink:href="#x"` 指向不存在的 id
  E5 DUPLICATE_ID          同一文件内 `id` 重复（后者永不生效）
  W1 UNUSED_DEF            `<marker>` / `*Gradient` / `pattern` / `filter` / `clipPath` /
                           `mask` / `symbol` 定义了却没有任何引用（死定义，读完图找不到出处）
  W2 UNSAFE_ID             `id` 含空白、括号、`#`、引号，或以数字开头（`url(#...)` 会解析失败）
  N1 NO_REFS               没有任何内部引用的 SVG 数量（只计数，不判错）

## 关键口径（三条，都来自真实语料）

1. **注释先剔除**。本库大量页面在 SVG 注释里写着「原来这里是 `url(#arrow)`」，
   不剔除会把注释当引用，产生一批假 E。
2. **只认本文件内的引用**。`url(#x)` 天然是文件内引用；跨文件不可能生效，
   所以「找不到就报 E」在这里是安全的（不存在「别处定义」的可能）。
3. **`W1` 只认「定义类」元素**。`<rect id="panel">` 这种「给元素起名」的 id 常见于
   调试残留，但删掉它不影响渲染，判成未使用会制造噪声；只对 `defs` 语义的元素报。

## 纪律

只读、不改图、不自动修 id。「这个 id 该叫什么」是作者判断；本项只负责把
「哪个文件的第几行、哪个属性、指向哪个不存在的 id」列出来。

用法
----
    python3 utils/audit/svgrefcheck.py            # 巡检
    python3 utils/audit/svgrefcheck.py --selftest # 自测（12 例）
"""

from __future__ import annotations

import argparse
import os
import re
import sys

SKIP_DIRS = {".git", ".vitepress", "node_modules", "dist", "cache"}
PAINT_ATTRS = {"fill", "stroke", "filter", "clip-path", "mask", "style", "marker"}
MARKER_ATTRS = {"marker-start", "marker-mid", "marker-end"}
DEF_TAGS = {
    "marker", "lineargradient", "radialgradient", "pattern", "filter",
    "clippath", "mask", "symbol",
}

TAG_RE = re.compile(r"<([A-Za-z][\w:.-]*)((?:\s+[^<>]*?)?)\s*/?>", re.S)
ATTR_RE = re.compile(r"([A-Za-z_:][-\w:.]*)\s*=\s*(\"([^\"]*)\"|'([^']*)')", re.S)
URL_RE = re.compile(r"url\(\s*['\"]?#([^)'\"\s]+)['\"]?\s*\)")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def iter_svgs(root):
    for base in ("docs", "project", "public"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in sorted(filenames):
                if fn.lower().endswith(".svg"):
                    yield os.path.join(dirpath, fn)


def parse_tags(src):
    """返回 [(tag, attrs_dict, offset)]，注释已剔除。"""
    cleaned = COMMENT_RE.sub(lambda m: " " * len(m.group(0)), src)
    out = []
    for m in TAG_RE.finditer(cleaned):
        tag = m.group(1).lower()
        raw = m.group(2) or ""
        attrs = {}
        for am in ATTR_RE.finditer(raw):
            val = am.group(3) if am.group(3) is not None else am.group(4)
            attrs[am.group(1).lower()] = val
        out.append((tag, attrs, m.start()))
    return out


def line_of(src, offset):
    return src.count("\n", 0, offset) + 1


def unsafe_id(i):
    if not i:
        return "空 id"
    if re.search(r"[\s()#'\"]", i):
        return "含空白/括号/#/引号"
    if i[0].isdigit():
        return "以数字开头"
    return ""


def check_src(src, name="<mem>"):
    """返回 findings 列表 [(code, message)]。"""
    findings = []
    tags = parse_tags(src)

    ids = {}
    dup = []
    for tag, attrs, off in tags:
        i = attrs.get("id")
        if i is None:
            continue
        if i in ids:
            dup.append((i, line_of(src, off)))
        else:
            ids[i] = (tag, off)

    refs = []          # (kind, id, lineno)
    for tag, attrs, off in tags:
        ln = line_of(src, off)
        for a, v in attrs.items():
            for m in URL_RE.finditer(v or ""):
                rid = m.group(1)
                if a in MARKER_ATTRS:
                    refs.append(("marker", rid, ln))
                elif a == "href" or a.endswith(":href"):
                    refs.append(("use", rid, ln))
                else:
                    refs.append(("paint", rid, ln))
        for a in ("href", "xlink:href"):
            v = attrs.get(a)
            if v and v.strip().startswith("#"):
                refs.append(("use", v.strip()[1:], ln))

    used = set()
    for kind, rid, ln in refs:
        used.add(rid)
        if rid in ids:
            continue
        if kind == "marker":
            findings.append(("E3", f"{name}:{ln} marker 指向未定义的 #{rid}（箭头会静默消失）"))
        elif kind == "use":
            findings.append(("E4", f"{name}:{ln} <use> 指向未定义的 #{rid}"))
        else:
            findings.append(("E2", f"{name}:{ln} 绘制属性 url(#{rid}) 未定义（该属性会降级为 none）"))

    for i, ln in dup:
        findings.append(("E5", f"{name}:{ln} id=\"{i}\" 重复定义（后者永不生效）"))

    for i, (tag, off) in ids.items():
        if tag in DEF_TAGS and i not in used:
            findings.append(("W1", f"{name}:{line_of(src, off)} <{tag} id=\"{i}\"> 定义后无人引用"))
        why = unsafe_id(i)
        if why:
            findings.append(("W2", f"{name}:{line_of(src, off)} id=\"{i}\" 不安全：{why}"))
    return findings, len(refs)


def run(root):
    if not (os.path.isdir(os.path.join(root, "docs")) or os.path.isdir(os.path.join(root, "project"))):
        print("E0 ROOT_NOT_FOUND  仓库根既无 docs/ 也无 project/")
        return 1

    findings = []
    n = 0
    no_refs = 0
    total_refs = 0
    for p in iter_svgs(root):
        n += 1
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                src = f.read()
        except OSError as e:
            findings.append(("E1", f"{p}: 读取失败 {e}"))
            continue
        rel = os.path.relpath(p, root)
        f2, nref = check_src(src, rel)
        findings.extend(f2)
        total_refs += nref
        if nref == 0:
            no_refs += 1

    if n == 0:
        print("E1 NO_SVGS  一张 SVG 都没扫到，拒绝给全绿")
        return 1

    errs = [x for x in findings if x[0].startswith("E")]
    warns = [x for x in findings if x[0].startswith("W")]
    for code, msg in errs + warns:
        print(f"{code} {msg}")
    print(f"\nsvgs={n} refs={total_refs} no_refs={no_refs} E={len(errs)} W={len(warns)}")
    return 1 if errs else 0


# --------------------------------------------------------------------------
# 自测：12 例，覆盖每一类判据与三条关键口径。
# 部分用例会同时命中两条（例如「id 含空格」必然让引用失效，于是既报 W2 又报 W1），
# 期望集合写的是「完整期望」，不是「主判据」——自测的价值就在这里。
# --------------------------------------------------------------------------
CASES = [
    # (名称, svg 源码, 期望出现的判据集合)
    ("ok-marker", '<svg viewBox="0 0 10 10"><defs><marker id="ar"/></defs>'
                  '<line marker-end="url(#ar)"/></svg>', set()),
    ("dangling-marker", '<svg viewBox="0 0 10 10"><defs><marker id="ar"/></defs>'
                        '<line marker-end="url(#arrow)"/></svg>', {"E3", "W1"}),
    ("dangling-fill", '<svg viewBox="0 0 10 10"><rect fill="url(#g1)"/></svg>', {"E2"}),
    ("ok-fill", '<svg viewBox="0 0 10 10"><defs><linearGradient id="g1"/></defs>'
                '<rect fill="url(#g1)"/></svg>', set()),
    ("dup-id", '<svg viewBox="0 0 10 10"><marker id="ar"/><marker id="ar"/></svg>', {"E5", "W1"}),
    ("unused-def", '<svg viewBox="0 0 10 10"><defs><marker id="ar"/></defs></svg>', {"W1"}),
    ("unsafe-id", '<svg viewBox="0 0 10 10"><defs><marker id="my arrow"/></defs>'
                  '<line marker-end="url(#my arrow)"/></svg>', {"W1", "W2"}),
    ("ok-style-url", '<svg viewBox="0 0 10 10"><defs><linearGradient id="g1"/></defs>'
                     '<rect style="fill:url(#g1)"/></svg>', set()),
    ("ok-use", '<svg viewBox="0 0 10 10"><defs><symbol id="s1"/></defs>'
               '<use href="#s1"/></svg>', set()),
    ("dangling-use", '<svg viewBox="0 0 10 10"><use href="#nope"/></svg>', {"E4"}),
    ("comment-skip", '<svg viewBox="0 0 10 10"><!-- 原来写的是 url(#arrow) -->'
                     '<line stroke="#333"/></svg>', set()),
    ("single-quote", "<svg viewBox='0 0 10 10'><rect fill='url(#g2)'/></svg>", {"E2"}),
]


def selftest():
    passed = 0
    for name, src, expect in CASES:
        got, _ = check_src(src, name)
        codes = {c for c, _ in got}
        ok = codes == expect
        print(f"{'PASS' if ok else 'FAIL'} {name:16s} expect={sorted(expect)} got={sorted(codes)}")
        passed += 1 if ok else 0
    print(f"\nselftest {passed}/{len(CASES)} PASS")
    return 0 if passed == len(CASES) else 1


def main():
    ap = argparse.ArgumentParser(description="SVG 内部引用完整性巡检")
    ap.add_argument("--root", default=".", help="仓库根（默认当前目录）")
    ap.add_argument("--selftest", action="store_true", help="跑 12 例自测")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(args.root)


if __name__ == "__main__":
    sys.exit(main())
