#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""indexcovercheck.py — 「目录页有没有列全子页」巡检 · 第 89 项

为什么立这一项
--------------
本库关于「页面能不能被点开」的门已经有四道，但**没有一道问过目录页**：

* `sidebarcheck`（第 79 项）：侧边栏里的 `link` 指向的文件在不在 → 管菜单；
* `orphanpagecheck`（第 83 项）：磁盘上的页面在侧边栏里有没有入口 → 管菜单反方向；
* `linkexistcheck`（第 86 项）：正文里的相对链接目标在不在 → 管正文；
* `linkformcheck`：链接的语法形态 → 管写法。

于是这一类债一直静默：**主题目录的 `index.md` 是读者进入该主题的第一屏**（`AGENTS.md`
第 6 节写的就是「目录页 = `# 主题名` + 子页链接列表」），但新增子页后忘了补目录页时，
侧边栏里有它、正文链接也通、构建也绿——**只有从目录页点不到**。它比孤儿页更隐蔽：
孤儿页至少能从侧边栏发现，而「目录页漏一行」看起来只是一屏少了条链接。

判据
----
E0 ROOT_NOT_FOUND   仓库根找不到（或既没有 docs/ 也没有 project/）
E1 NO_PAGES         一个 `index.md` 都没扫到（活性判据：拒绝在空集上给「全绿」）
E2 MISSING_SUBPAGE  目录页已列出部分子页（≥1），但漏了其余子页
E3 DEAD_SUBLINK     目录页链接到「本目录下某个子目录的 index.md」，但该文件不存在
W1 NO_LIST          有子页但一个都没链（可能是正文页，不判 E）

怎么判「目录页」
--------------
本库有两类 `index.md`：**目录页**（只放链接列表）与**承载正文的章节页**（第 6 节明确允许）。
机械判定用「已列出 ≥1 个子页」这条：既然它已经在列子页，它就是目录页，漏掉的就该报 E2；
一个子页都没列的，只报 W1——因为无法区分「它是正文页」还是「它忘了列」。

纪律
----
* **只读**：不写文件、不改台账、不自动补链接（补链接会改变文章结构，交人工）。
* **跳过围栏与行内代码**：围栏解析复用 `fenceutil.scan()`（第 88 项的共享底座），
  本项不自己写第五份围栏正则。
* **只认相对链接**：以 `http` / `mailto` / `#` 开头的跳过；`X/index.md`、`./X/index.md`、
  `X/`、`X` 四种写法都算链接到子目录 X。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/indexcovercheck.py              # 全库
    python3 utils/audit/indexcovercheck.py --root . --limit 50
    python3 utils/audit/indexcovercheck.py --selftest
"""

import argparse
import os
import re
import sys
import tempfile
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402  第 88 项的共享围栏解析

LINK_RE = re.compile(r"\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
SKIP_DIRS = {".git", ".vitepress", "node_modules", ".workbuddy", "assets", "public"}
ROOTS = ("docs", "project")


def body_text(text):
    """去掉围栏与行内代码后的正文（行内代码里的链接是示例，不算入口）。"""
    mask, _, _ = scan(text)
    out = []
    for i, line in enumerate(text.split("\n")):
        if i in mask:
            continue
        out.append(INLINE_CODE_RE.sub("", line))
    return "\n".join(out)


def links_of(page):
    """返回该页所有相对链接的原始目标（已 unquote，去掉锚点）。page 为绝对路径。"""
    res = []
    with open(page, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    for m in LINK_RE.finditer(body_text(text)):
        raw = m.group(1).strip()
        if raw.startswith(("http://", "https://", "mailto:", "#", "/")):
            continue
        raw = urllib.parse.unquote(raw.split("#")[0].split("?")[0])
        if raw:
            res.append(raw)
    return res


def resolve(page_dir, target):
    """把相对链接解析成绝对路径（不要求存在）。"""
    return os.path.normpath(os.path.join(page_dir, target))


def collect(root):
    """返回 (pages, topics)：pages 是全部 index.md；topics 是 [(目录, 子目录列表, 页面路径)]。"""
    pages, topics = [], []
    for base in ROOTS:
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            if "index.md" not in filenames:
                continue
            page = os.path.join(dirpath, "index.md")
            pages.append(page)
            kids = sorted(
                d for d in dirnames
                if os.path.isfile(os.path.join(dirpath, d, "index.md"))
            )
            if kids:
                topics.append((dirpath, kids, page))
    return pages, topics


def run(root, limit=40, quiet=False):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND: %s" % root)
        return 1
    if not any(os.path.isdir(os.path.join(root, b)) for b in ROOTS):
        print("E0 ROOT_NOT_FOUND: 既没有 docs/ 也没有 project/")
        return 1
    pages, topics = collect(root)
    if not pages:
        print("E1 NO_PAGES: 一个 index.md 都没扫到")
        return 1

    e2, e3, w1 = [], [], []
    for d, kids, page in topics:
        targets = links_of(page)
        resolved = [resolve(d, t) for t in targets]
        covered = set()
        for kid in kids:
            want = os.path.normpath(os.path.join(d, kid, "index.md"))
            want_dir = os.path.normpath(os.path.join(d, kid))
            if want in resolved or want_dir in resolved:
                covered.add(kid)
        missing = [k for k in kids if k not in covered]
        if missing and covered:
            e2.append((page, missing))
        elif missing and not covered:
            w1.append((page, len(missing)))
        # E3：链接指向「本目录下某个子目录的 index.md」但文件不存在
        for t, r in zip(targets, resolved):
            if not t.endswith("index.md"):
                continue
            parent = os.path.dirname(r)
            if os.path.dirname(parent) != os.path.normpath(d):
                continue
            if os.path.isfile(r):
                continue
            e3.append((page, t))

    if not quiet:
        shown = 0
        for page, miss in e2:
            for m in miss:
                print("E2 MISSING_SUBPAGE: %s 漏了子页 %s/" % (os.path.relpath(page, root), m))
                shown += 1
                if shown >= limit:
                    break
            if shown >= limit:
                print("...（只显示前 %d 条）" % limit)
                break
        for page, t in e3[:limit]:
            print("E3 DEAD_SUBLINK: %s → %s" % (os.path.relpath(page, root), t))
        for page, n in w1[:limit]:
            print("W1 NO_LIST: %s 有 %d 个子页，一个都没链" % (os.path.relpath(page, root), n))
    print("pages=%d topics=%d E2=%d E3=%d W1=%d" % (len(pages), len(topics), len(e2), len(e3), len(w1)))
    return 0 if not (e2 or e3) else 1


def _make(root, files):
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)


def selftest():
    cases = []

    # ① 目录页列全 → 全绿
    d = tempfile.mkdtemp()
    _make(d, {
        "docs/A/index.md": "# A\n\n- [子一](S1/index.md)\n- [子二](S2/index.md)\n",
        "docs/A/S1/index.md": "# S1\n",
        "docs/A/S2/index.md": "# S2\n",
    })
    cases.append(("列全", d, 0))

    # ② 漏一个子页 → E2
    d = tempfile.mkdtemp()
    _make(d, {
        "docs/A/index.md": "# A\n\n- [子一](S1/index.md)\n",
        "docs/A/S1/index.md": "# S1\n",
        "docs/A/S2/index.md": "# S2\n",
    })
    cases.append(("漏子页", d, 1))

    # ③ 一个都没列 → 只报 W1
    d = tempfile.mkdtemp()
    _make(d, {
        "docs/A/index.md": "# A\n\n这是正文，没有列表。\n",
        "docs/A/S1/index.md": "# S1\n",
    })
    cases.append(("只报W1", d, 0))

    # ④ 目录页链到不存在的子目录 → E3
    d = tempfile.mkdtemp()
    _make(d, {
        "docs/A/index.md": "# A\n\n- [子一](S1/index.md)\n- [幽灵](Ghost/index.md)\n",
        "docs/A/S1/index.md": "# S1\n",
    })
    cases.append(("死链", d, 1))

    # ⑤ 链接写在围栏里不算 → W1（不是 E2）
    d = tempfile.mkdtemp()
    _make(d, {
        "docs/A/index.md": "# A\n\n```text\n- [子一](S1/index.md)\n```\n",
        "docs/A/S1/index.md": "# S1\n",
    })
    cases.append(("围栏内链接", d, 0))

    # ⑥ 目录形式 `S1/` 也算链接到子页
    d = tempfile.mkdtemp()
    _make(d, {
        "docs/A/index.md": "# A\n\n- [子一](S1/)\n",
        "docs/A/S1/index.md": "# S1\n",
    })
    cases.append(("目录写法", d, 0))

    # ⑦ 空仓库 → E1
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs"))
    cases.append(("空仓库", d, 1))

    passed = 0
    for name, root, expect in cases:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = run(root, limit=5)
        out = buf.getvalue()
        if name in ("漏子页", "死链", "空仓库"):
            ok = rc == 1 and ("E2=" in out or "E3=" in out or "E1" in out)
        else:
            ok = rc == 0 and "E2=0" in out and "E3=0" in out
        print("%s  %s → %s" % ("PASS" if ok else "FAIL", name, out.strip().splitlines()[-1]))
        passed += 1 if ok else 0
    print("selftest %d/%d" % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(args.root, args.limit)


if __name__ == "__main__":
    sys.exit(main())
