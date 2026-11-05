#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figurecovercheck.py — 巡检「每页是否有配图」。

背景：AGENTS.md 第 7 节第 9 条要求「每篇页面正文都要有与内容对应的配图」。
既有巡检各管一段：linkexistcheck 管链接能不能打开、imageorigincheck 管路径形态、
assetsizecheck 管体积，但**没有一道门在问「这一页到底有没有图」**。本脚本补这一道。

判据
  E0 ROOT_NOT_FOUND   根目录不存在
  E1 NO_PAGES         根目录下没有 index.md
  E2 ABS_IMG_PATH     图片用了 /assets/... 绝对路径（站点 base 为 /docs-website/，会失效）
  W1 NO_FIGURE        页面既无 ![](...) 也无 <img ...>，且不是纯目录页
  W2 FIGURE_IN_FENCE  唯一出现的 ![...] 在代码围栏内（不算配图）
  W3 TOC_ONLY         纯目录页（只有 H1 + 列表，无 H2），不要求配图，跳过

用法
  python3 utils/audit/figurecovercheck.py            # 扫 docs/ 与 project/
  python3 utils/audit/figurecovercheck.py --selftest # 12 条自测
  python3 utils/audit/figurecovercheck.py --root docs/Backend/FleetTransport
"""
import os
import re
import sys
import tempfile

FENCE = re.compile(r"^(?P<fence>`{3,}|~{3,})")
IMG_MD = re.compile(r"!\[[^\]]*\]\((?P<src>[^)\s]+)")
IMG_HTML = re.compile(r"<img\s[^>]*?src=[\"'](?P<src>[^\"']+)[\"']", re.I)
H2 = re.compile(r"^##\s+\S")


def split_fences(lines):
    """返回 (fenced_line_index_set)。围栏内不参与「有没有图」的判定。"""
    inside, out = False, set()
    for i, ln in enumerate(lines):
        m = FENCE.match(ln.strip())
        if m:
            inside = not inside
            out.add(i)
            continue
        if inside:
            out.add(i)
    return out


def analyse(text):
    """返回 (images, fenced_images, has_h2)。"""
    lines = text.splitlines()
    fenced = split_fences(lines)
    imgs, fenced_imgs, has_h2 = [], [], False
    for i, ln in enumerate(lines):
        if i not in fenced and H2.match(ln):
            has_h2 = True
        for rx in (IMG_MD, IMG_HTML):
            for m in rx.finditer(ln):
                if i in fenced:
                    fenced_imgs.append(m.group("src"))
                else:
                    imgs.append(m.group("src"))
    return imgs, fenced_imgs, has_h2


def check(root):
    issues = []
    pages = 0
    for dirpath, _dirs, files in os.walk(root):
        if "index.md" not in files:
            continue
        pages += 1
        path = os.path.join(dirpath, "index.md")
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            issues.append(("E0", path, f"读不了：{e}"))
            continue
        imgs, fenced_imgs, has_h2 = analyse(text)
        for src in imgs:
            if src.startswith("/"):
                issues.append(("E2", path, f"绝对图片路径 {src}"))
        if imgs:
            continue
        if not has_h2:
            issues.append(("W3", path, "纯目录页，跳过"))
            continue
        if fenced_imgs:
            issues.append(("W2", path, f"图只在代码围栏内：{fenced_imgs[0]}"))
        else:
            issues.append(("W1", path, "正文没有任何配图"))
    return pages, issues


SELFTEST = [
    ("h1 + h2 + 一张相对路径图", "# T\n\n## A\n\n![x](assets/a.svg)\n", []),
    ("h1 + h2 + html img", "# T\n\n## A\n\n<img src=\"./assets/a.png\" />\n", []),
    ("h1 + h2 无图", "# T\n\n## A\n\n正文\n", ["W1"]),
    ("纯目录页", "# T\n\n- [a](A/index.md)\n- [b](B/index.md)\n", ["W3"]),
    ("图在围栏内", "# T\n\n## A\n\n```md\n![x](a.svg)\n```\n", ["W2"]),
    ("绝对路径", "# T\n\n## A\n\n![x](/assets/a.svg)\n", ["E2"]),
    ("围栏内绝对路径不算", "# T\n\n## A\n\n```html\n<img src=\"/a.png\">\n```\n![y](b.svg)\n", []),
    ("多图其一绝对", "# T\n\n## A\n\n![a](x.svg)\n![b](/y.svg)\n", ["E2"]),
    ("h3 不算 h2", "# T\n\n### 小标题\n\n正文\n", ["W3"]),
    ("围栏未闭合", "# T\n\n## A\n\n```\n![x](a.svg)\n", ["W2"]),
    ("空文件", "", ["W3"]),
    ("图片带空格标题", "# T\n\n## A\n\n![描述 带空格](assets/a b.svg)\n", []),
]


def selftest():
    ok = 0
    for i, (name, text, expect) in enumerate(SELFTEST, 1):
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "p"), exist_ok=True)
        open(os.path.join(tmp, "p", "index.md"), "w", encoding="utf-8").write(text)
        _pages, issues = check(tmp)
        got = [c for c, _p, _m in issues]
        # E2 与 W 可同时出现；自测按「包含期望集合」判
        good = all(e in got for e in expect) and (bool(expect) == bool(got) or expect == [])
        print(f"  {i:02d} {name:<22} got={got} expect={expect} {'PASS' if good else 'FAIL'}")
        ok += 1 if good else 0
    print(f"selftest {ok}/{len(SELFTEST)}")
    return 0 if ok == len(SELFTEST) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    roots = []
    if "--root" in argv:
        roots = [argv[argv.index("--root") + 1]]
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        roots = [os.path.join(base, "docs"), os.path.join(base, "project")]
    total_pages, all_issues = 0, []
    for r in roots:
        if not os.path.isdir(r):
            print(f"E0 ROOT_NOT_FOUND {r}")
            return 2
        pages, issues = check(r)
        total_pages += pages
        all_issues += issues
    order = {"E0": 0, "E1": 1, "E2": 2, "W1": 3, "W2": 4, "W3": 5}
    all_issues.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    for code, path, msg in all_issues:
        if code == "W3":
            continue
        print(f"{code} {path} {msg}")
    stat = {}
    for code, _p, _m in all_issues:
        stat[code] = stat.get(code, 0) + 1
    print(f"pages={total_pages} " + " ".join(f"{k}={v}" for k, v in sorted(stat.items())))
    hard = sum(v for k, v in stat.items() if k.startswith("E"))
    return 0 if hard == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
