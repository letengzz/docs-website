#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svgsharecheck.py —— 「同一张图被几个页面引用」巡检（第 256 天新立，第 137 项巡检）

背景
----
第 255 天写充电桩专题时踩到一个「构建全绿、图却是错的」的缺陷：`Settlement` 页要画
「对账四形状」，直接从上一页复制了 `![对账四形状](../assets/ft-faq.svg)` 的引用，图
改了名字、内容没换——**页面渲染出的是一张排障决策树，配的却是一个对账表格的图注**。

既有的三项图片巡检各管一段，都不问这件事：

  - `figurecovercheck`（第 136 项）  这一页**有没有**图（页 → 图）；
  - `orphanassetcheck`（第 65 项）   这个文件**有没有人**引用（图 → 页）；
  - `imagebytescheck` / `assetsizecheck`  图的体积与字节重复（图 → 体积）。

「一张图被**几个**页面引用」两头都不沾。它恰好是上面那类缺陷的唯一特征：图存在、
被引用、页也有图，只有「**它本来属于另一页**」这件事没有任何门在看。

判据（E = 错误，必须修；W = 提示，登记长尾）
--------------------------------------------
  E0 ROOT_NOT_FOUND    给定的根目录既不存在也没有子目录
  E1 NO_PAGES          一个 index.md 都没扫到（活性判据，防「路径写错全绿」）
  E2 NO_SVG_REF        全库一条 SVG 引用都没扫到（活性判据，防解析器整体失效）
  W1 SHARED_FIGURE     同一张 SVG 被 2~3 个页面引用
  W2 CROSS_TOPIC       同一张 SVG 被**不同主题目录**的页面引用（几乎一定是配错）
  W3 SAME_PAGE_TWICE   同一张 SVG 在同一页被引用 ≥ 2 次（多半是复制粘贴）

为什么全部只报 W：一张图被两页共用**有时是合法的**（如「专题地图」在总览与目录页
各出现一次）。本项的价值不在于「拦住」，而在于把候选集从「全库 1,500+ 张图」缩到
「十几张需要人看一眼的图」——第 255 天那次，缩完只有 3 张。

口径
----
- 只统计 `*.svg`。PNG 由 `orphanassetcheck` / `imagebytescheck` 管，本项不重复。
- 围栏内的 `![](...)` 不算引用（那是示例代码），复用 `fenceutil.body_lines`。
- 只认相对路径；`http(s)://` 外链跳过（`imageorigincheck` 管那件事）。
- 主题目录 = 路径前三段，如 `docs/Backend/ChargingNetwork`。

用法
----
  python3 utils/audit/svgsharecheck.py [--root docs project] [--selftest]
  python3 utils/audit/svgsharecheck.py --root docs/Backend/ChargingNetwork

退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import body_lines  # noqa: E402

MD_IMG = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?[^)]*\)")
HTML_IMG = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.I)


def scan_refs(root_dirs, base):
    """返回 {page_rel: [svg_abs, ...]}，只保留 *.svg 的相对引用。"""
    refs = {}
    for root in root_dirs:
        for dirpath, _dirnames, filenames in os.walk(root):
            if "index.md" not in filenames:
                continue
            page = os.path.join(dirpath, "index.md")
            try:
                text = open(page, encoding="utf-8").read()
            except OSError:
                continue
            found = []
            for line in body_lines(text):
                cands = MD_IMG.findall(line) + HTML_IMG.findall(line)
                for raw in cands:
                    if raw.startswith(("http://", "https://", "//", "data:")):
                        continue
                    target = raw.split("#")[0].split("?")[0].strip()
                    if not target.lower().endswith(".svg"):
                        continue
                    abs_p = os.path.normpath(os.path.join(dirpath, target))
                    found.append(abs_p)
            if found:
                refs[os.path.relpath(os.path.join(dirpath), base)] = found
    return refs


def topic_of(page_rel):
    parts = page_rel.replace(os.sep, "/").split("/")
    return "/".join(parts[:3])


def analyze(refs, base):
    """纯函数：refs = {page_rel: [svg_abs,...]} → (findings, stats)。"""
    by_svg = {}
    for page, svgs in refs.items():
        seen = {}
        for p in svgs:
            seen[p] = seen.get(p, 0) + 1
        for p, cnt in seen.items():
            by_svg.setdefault(p, []).append((page, cnt))

    findings = []
    shared = cross = twice = 0
    for svg, users in sorted(by_svg.items()):
        rel = os.path.relpath(svg, base).replace(os.sep, "/")
        pages = sorted({u[0].replace(os.sep, "/") for u in users})
        topics = {topic_of(p) for p in pages}
        for page, cnt in users:
            if cnt >= 2:
                twice += 1
                findings.append(("W3", f"SAME_PAGE_TWICE {rel} :: {page} ×{cnt}"))
        if len(pages) >= 2:
            if len(topics) >= 2:
                cross += 1
                findings.append(("W2", f"CROSS_TOPIC {rel} :: {' | '.join(pages)}"))
            else:
                shared += 1
                findings.append(("W1", f"SHARED_FIGURE {rel} :: {' | '.join(pages)}"))

    stats = {
        "pages": len(refs),
        "svgs": len(by_svg),
        "refs": sum(len(v) for v in refs.values()),
        "shared": shared,
        "cross": cross,
        "twice": twice,
    }
    return findings, stats


def selftest():
    """12 条纯函数自测：不碰磁盘，只喂 refs 字典。"""
    # 主题目录 = 路径前三段，因此 fixture 一律用「docs/X/Theme/...」这样的真实深度
    T1, T2 = "docs/Backend/ThemeA", "docs/Backend/ThemeB"
    cases = [
        ("单页单图无告警", {f"{T1}/index.md": ["/b/x.svg"]}, []),
        ("同主题两页同图 → W1", {f"{T1}/index.md": ["/b/x.svg"], f"{T1}/Sub/index.md": ["/b/x.svg"]}, ["W1"]),
        ("跨主题同图 → W2", {f"{T1}/index.md": ["/b/x.svg"], f"{T2}/index.md": ["/b/x.svg"]}, ["W2"]),
        ("同页两次 → W3", {f"{T1}/index.md": ["/b/x.svg", "/b/x.svg"]}, ["W3"]),
        ("多个不同图无告警", {f"{T1}/index.md": ["/b/x.svg", "/b/y.svg"]}, []),
        ("同页两次 + 他页一次 → W3+W1", {f"{T1}/index.md": ["/b/x.svg", "/b/x.svg"],
                                          f"{T1}/Sub/index.md": ["/b/x.svg"]}, ["W3", "W1"]),
        ("三个同主题页共用 → W1", {f"{T1}/a/index.md": ["/b/x.svg"], f"{T1}/b/index.md": ["/b/x.svg"],
                                   f"{T1}/c/index.md": ["/b/x.svg"]}, ["W1"]),
        ("三页跨两主题 → W2", {f"{T1}/index.md": ["/b/x.svg"], f"{T1}/Sub/index.md": ["/b/x.svg"],
                               f"{T2}/Sub/index.md": ["/b/x.svg"]}, ["W2"]),
        ("空输入无告警", {}, []),
        ("三个不同图三页 —— 无", {f"{T1}/a/index.md": ["/b/1.svg"], f"{T1}/b/index.md": ["/b/2.svg"],
                                  f"{T2}/c/index.md": ["/b/3.svg"]}, []),
        ("同页三图其中之一重复 → W3", {f"{T1}/index.md": ["/b/1.svg", "/b/2.svg", "/b/2.svg"]}, ["W3"]),
        ("两页各自两图且不交叉 → 无", {f"{T1}/a/index.md": ["/b/1.svg", "/b/2.svg"],
                                       f"{T2}/b/index.md": ["/b/3.svg", "/b/4.svg"]}, []),
    ]
    ok = 0
    for name, refs, want in cases:
        got, _ = analyze(refs, "/")
        codes = sorted({c for c, _ in got})
        if codes == sorted(want):
            ok += 1
        else:
            print(f"  FAIL {name}: want {want} got {codes}")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()

    roots, i = ["docs", "project"], 1
    while i < len(argv):
        if argv[i] == "--root":
            roots, i = [], i + 1
            while i < len(argv) and not argv[i].startswith("--"):
                roots.append(argv[i])
                i += 1
        else:
            i += 1

    missing = [r for r in roots if not os.path.isdir(r)]
    if missing:
        print(f"E0 ROOT_NOT_FOUND {' '.join(missing)}")
        return 1

    base = os.getcwd()
    refs = scan_refs(roots, base)
    if not refs:
        print("E1 NO_PAGES 没有扫到任何含图片引用的 index.md")
        return 1
    total_refs = sum(len(v) for v in refs.values())
    if total_refs == 0:
        print("E2 NO_SVG_REF 一条 SVG 相对引用都没扫到")
        return 1

    findings, st = analyze(refs, base)
    for code, msg in findings:
        print(f"{code} {msg}")

    e_cnt = sum(1 for c, _ in findings if c.startswith("E"))
    w_cnt = len(findings) - e_cnt
    print(f"\npages={st['pages']} svg_refs={st['refs']} distinct_svg={st['svgs']}")
    print(f"合计 {len(findings)} 条：E={e_cnt} W={w_cnt} "
          f"(W1={st['shared']} W2={st['cross']} W3={st['twice']})")
    print("RESULT", "OK" if e_cnt == 0 else "FAIL")
    return 0 if e_cnt == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
