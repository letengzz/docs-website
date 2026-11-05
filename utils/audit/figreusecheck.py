#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十项巡检：同一页里同一张配图被反复引用（图复用）
立这一项的原因：本库的配图巡检管了三件事——figurecovercheck 管「有没有图」、
svgsharecheck 管「一张图跨了几页」、assetdupcheck 管「同目录同内容存了几份」。
没有一项管「同一页里同一张图出现好几次」。而这类缺陷在页面上看起来只是
「排版重复」，构建全绿、链接全通、覆盖率达标，四道门一起放行。

判据：
  E0 ROOT_NOT_FOUND          活性前置：仓库根不存在
  E1 NO_PAGES                活性：扫到 0 个 Markdown
  E2 REPEAT_3PLUS            同一页内同一张图被引用 >= 3 次（无歧义冗余）
  W1 REPEAT_TWICE            同一页内同一张图被引用恰好 2 次（可能是前后对比，只报告）
  W2 SAME_STEM_DIFF_EXT      同一页引用了同名的 .svg 与 .png（多半是想用一份却写了两份）

退出码只认 E 级。
"""
import argparse
import os
import re
import sys
import tempfile
from collections import defaultdict

FENCE_RE = re.compile(r"^\s*(```|~~~)")
IMG_MD = re.compile(r"!\[[^\]]*\]\(\s*([^)\s]+)")
IMG_HTML = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.I)
CODE_SPAN = re.compile(r"`[^`\n]*`")


def strip_code(src):
    """先剥围栏、再剥行内代码；两者都等长空格占位以保留行号。"""
    out = []
    in_fence = False
    for line in src.split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(" " * len(line))
            continue
        if in_fence:
            out.append(" " * len(line))
        else:
            out.append(CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def collect(src):
    """返回 [(target, line_no)]，跳过外链与站点绝对路径。"""
    body = strip_code(src)
    refs = []
    for i, line in enumerate(body.split("\n"), 1):
        for m in IMG_MD.finditer(line):
            refs.append((m.group(1).strip(), i))
        for m in IMG_HTML.finditer(line):
            refs.append((m.group(1).strip(), i))
    keep = []
    for t, ln in refs:
        low = t.lower()
        if low.startswith(("http://", "https://", "//", "data:")) or t.startswith("/"):
            continue
        keep.append((t.split("#")[0].split("?")[0], ln))
    return keep


def normalise(page_path, target):
    base = os.path.dirname(page_path)
    p = os.path.normpath(os.path.join(base, target))
    return p.replace("\\", "/").lower()


def scan_page(page_path):
    src = open(page_path, encoding="utf-8", errors="ignore").read()
    refs = collect(src)
    counter = defaultdict(list)
    for t, ln in refs:
        counter[normalise(page_path, t)].append((t, ln))
    return counter


def iter_pages(root):
    for base in ("docs", "project"):
        for dp, dn, fn in os.walk(os.path.join(root, base)):
            dn[:] = [d for d in dn if d not in ("node_modules", "assets", ".vitepress", ".git")]
            for f in fn:
                if f.endswith(".md"):
                    yield os.path.join(dp, f)


def check(root):
    errs, warns, counts = [], [], {"pages": 0, "refs": 0, "groups": 0}
    if not os.path.isdir(root):
        return [("E0", "ROOT_NOT_FOUND", root, 0)], [], counts
    for page in iter_pages(root):
        counts["pages"] += 1
        counter = scan_page(page)
        rel = os.path.relpath(page, root).replace("\\", "/")
        for key, hits in counter.items():
            counts["refs"] += len(hits)
            if len(hits) < 2:
                continue
            counts["groups"] += 1
            lines = [ln for _, ln in hits]
            if len(hits) >= 3:
                errs.append(("E2", "REPEAT_3PLUS", rel, lines[0], f"{hits[0][0]} × {len(hits)}"))
            else:
                warns.append(("W1", "REPEAT_TWICE", rel, lines[0], f"{hits[0][0]} × 2"))
        stems = defaultdict(set)
        for key in counter:
            stem, ext = os.path.splitext(key)
            if ext in (".svg", ".png"):
                stems[stem].add(ext)
        for stem, exts in stems.items():
            if len(exts) == 2:
                warns.append(("W2", "SAME_STEM_DIFF_EXT", rel, 0, os.path.basename(stem)))
    if counts["pages"] == 0:
        errs.append(("E1", "NO_PAGES", root, 0))
    return errs, warns, counts


# ------------------------------ selftest ------------------------------
CASES = [
    ("case-01-repeat3", {"a.md": "![x](assets/x.svg)\n\n![y](assets/x.svg)\n\n![z](assets/x.svg)\n"}, "E2", True),
    ("case-02-repeat2", {"a.md": "![x](assets/x.svg)\n\n![y](assets/x.svg)\n"}, "W1", False),
    ("case-03-single", {"a.md": "![x](assets/x.svg)\n"}, None, False),
    ("case-04-in-fence", {"a.md": "```md\n![x](assets/x.svg)\n![x](assets/x.svg)\n![x](assets/x.svg)\n```\n"}, None, False),
    ("case-05-in-span", {"a.md": "写法是 `![x](assets/x.svg)` 重复三遍 `![x](assets/x.svg)` `![x](assets/x.svg)`\n"}, None, False),
    ("case-06-external", {"a.md": '<img src="https://e.com/a.png">\n<img src="https://e.com/a.png">\n<img src="https://e.com/a.png">\n'}, None, False),
    ("case-07-absolute", {"a.md": '<img src="/assets/a.png">\n<img src="/assets/a.png">\n<img src="/assets/a.png">\n'}, None, False),
    ("case-08-diff", {"a.md": "![a](assets/a.svg)\n![b](assets/b.svg)\n"}, None, False),
    ("case-09-stem", {"a.md": "![a](assets/logo.svg)\n![a](assets/logo.png)\n"}, "W2", False),
    ("case-10-cross", {"a.md": "![a](assets/a.svg)\n", "b.md": "![a](assets/a.svg)\n", "c.md": "![a](assets/a.svg)\n"}, None, False),
    ("case-11-html3", {"a.md": '<img src="./assets/x.svg">\n<img src="./assets/x.svg">\n<img src="./assets/x.svg">\n'}, "E2", True),
    ("case-12-anchor-diff", {"a.md": "![a](assets/x.svg#p1)\n![b](assets/x.svg#p2)\n"}, "W1", False),
]


def selftest():
    tmp = os.path.join(tempfile.gettempdir(), "figreuse-selftest")
    os.makedirs(tmp, exist_ok=True)
    passed = 0
    for idx, (name, files, code, is_err) in enumerate(CASES, 1):
        d = os.path.join(tmp, name)
        os.makedirs(os.path.join(d, "docs", "Sub"), exist_ok=True)
        for fn, body in files.items():
            with open(os.path.join(d, "docs", "Sub", fn), "w", encoding="utf-8") as f:
                f.write(body)
        errs, warns, _ = check(d)
        got = set(c for c, _, _, *_ in errs) | set(c for c, _, _, *_ in warns)
        want = set() if code is None else {code}
        ok = got == want
        passed += 1 if ok else 0
        print(("PASS " if ok else "FAIL ") + f"{idx:02d} {name} want={sorted(want)} got={sorted(got)}")
    print(f"selftest {passed}/{len(CASES)}")
    return 0 if passed == len(CASES) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    errs, warns, counts = check(os.path.abspath(a.root))
    for c, code, path, line, detail in errs:
        print(f"{c} {code} {path}:{line} {detail}")
    if a.list:
        for c, code, path, line, detail in warns:
            print(f"{c} {code} {path}:{line} {detail}")
    print(f"pages={counts['pages']} refs={counts['refs']} groups={counts['groups']} "
          f"E={len(errs)} W={len(warns)}")
    print("RESULT", "OK" if not errs else "FAIL", "EXIT=" + ("0" if not errs else "1"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
