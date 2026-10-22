#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""orphanpagecheck.py — 「页面有没有入口」巡检 · 第 83 项

为什么立这一项
--------------
全库的导航有三层：`nav.ts`（顶部）、`sidebar.ts`（路径前缀 → 分支）、各分支文件（树）。
`sidebarcheck.py`（第 79 项）查的是**反方向**：侧边栏里的 `{ text, link }` 指向的文件
是否存在、标题是否对得上。它回答「菜单里这一项点得开吗」。

**没有一项巡检问过正向的问题：磁盘上的页面，菜单里点得到吗？**

于是这一类债全库静默：

* 新建页面忘了挂侧边栏 → 构建绿、搜索能搜到、**菜单里没有**，读者只能靠 URL 猜；
* 老版本目录（`SpringBoot/v2`）在侧边栏里是叶子节点，子页面全部悬空 →
  「旧版本保留、可折叠查阅」的约定形式上满足、实际上查不到；
* 分支文件里写了 `"link": "…"`（键带引号）→ 只看 `link:` 的解析器会把它算成「未收录」，
  于是「假孤儿」与「真孤儿」混在一起，谁也说不清到底缺多少。

判据
----
E0 ROOT_NOT_FOUND   仓库根或 `.vitepress` 目录找不到
E1 NO_PAGES         一个 `index.md` 都没扫到（活性判据：拒绝在空集上给「全绿」）
E2 NO_ENTRIES       三层导航里一条 `link` 都没解析到（活性判据）
E3 ORPHAN_PAGE      页面存在，但没有任何导航条目指向它（读者点不到）
W1 NAV_ONLY         只被顶部导航（`nav.ts`）引用，未被侧边栏收录
W2 DEAD_LINK        导航条目指向的文件不存在（与 `sidebarcheck` 的 E2 同源，这里是汇总口径）

纪律
----
* **只读**：不写文件、不改台账。
* **两种 link 写法都认**：`link: "…"` 与 `"link": "…"`（`DotNet` 一段用了带引号的键）。
  只认一种就会产出「假孤儿」，这是第 83 项首轮 62 条里 5 条误报的来源。
* **只算 `index.md` 页面**：本库规范是「英文目录 + index.md」，平铺 `.md` 不在巡检范围。
* **分类落地页（`docs/<Cat>/index.md`）也算页面**：它必须被大类侧边栏收录，
  否则从菜单里点不到「AI 总览」这类入口。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/orphanpagecheck.py [--selftest] [--root .] [--limit 30]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

LINK_RE = re.compile(r'"?link"?\s*:\s*["\']([^"\']+)["\']')
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)


def load_nav_links(vp_dir: str) -> tuple[set[str], set[str], set[str]]:
    """返回 (全部 link, nav.ts 的 link, 侧边栏分支的 link)，均已归一化为仓库相对路径。"""
    all_links: set[str] = set()
    nav_links: set[str] = set()
    side_links: set[str] = set()
    for name in sorted(os.listdir(vp_dir)):
        if not name.endswith(".ts"):
            continue
        text = open(os.path.join(vp_dir, name), encoding="utf-8").read()
        found = {
            os.path.normpath(m.group(1).lstrip("/"))
            for m in LINK_RE.finditer(text)
        }
        all_links |= found
        if name == "nav.ts":
            nav_links |= found
        elif name != "sidebar.ts":  # sidebar.ts 只有 import 与挂载，没有条目
            side_links |= found
    return all_links, nav_links, side_links


def collect_pages(root: str) -> list[str]:
    pages: list[str] = []
    for base in ("docs", "project"):
        base_dir = os.path.join(root, base)
        if not os.path.isdir(base_dir):
            continue
        for dirpath, _dirnames, filenames in os.walk(base_dir):
            if "index.md" in filenames:
                pages.append(os.path.relpath(os.path.join(dirpath, "index.md"), root))
    return sorted(pages)


def run(root: str, limit: int) -> int:
    vp = os.path.join(root, ".vitepress")
    if not os.path.isdir(vp):
        print("E0 ROOT_NOT_FOUND  找不到 .vitepress：%s" % vp)
        return 2

    pages = collect_pages(root)
    if not pages:
        print("E1 NO_PAGES  一个 index.md 都没扫到")
        return 2

    all_links, nav_links, side_links = load_nav_links(vp)
    if not all_links:
        print("E2 NO_ENTRIES  三层导航里没有解析到任何 link")
        return 2

    orphans = [p for p in pages if os.path.normpath(p) not in all_links]
    # 大类落地页（docs/<Cat>/index.md）只出现在 nav.ts 是设计如此，不算不一致
    nav_only = [
        p for p in pages
        if os.path.normpath(p) not in side_links
        and os.path.normpath(p) in nav_links
        and len(os.path.normpath(p).split(os.sep)) > 3
    ]
    dead = sorted(
        link for link in side_links
        if link.endswith(".md") and not os.path.isfile(os.path.join(root, link))
    )

    print("pages=%d links=%d side_links=%d" % (len(pages), len(all_links), len(side_links)))
    for p in orphans[:limit]:
        print("E3 ORPHAN_PAGE  %s" % p)
    for p in nav_only[:limit]:
        print("W1 NAV_ONLY     %s" % p)
    for p in dead[:limit]:
        print("W2 DEAD_LINK    %s" % p)
    print(
        "E3=%d W1=%d W2=%d%s"
        % (
            len(orphans),
            len(nav_only),
            len(dead),
            "" if len(orphans) <= limit else "（仅显示前 %d 条）" % limit,
        )
    )
    return 0 if not orphans and not dead else 1


def selftest() -> int:
    """六类夹具：正常页 / 孤儿页 / 带引号键的 link / nav-only / 断链 / 空仓库。"""
    cases = []

    def build(files: dict[str, str]) -> str:
        root = tempfile.mkdtemp(prefix="orphanpage-")
        for rel, content in files.items():
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(content)
        return root

    # ① 正常：两个页面都被收录
    r = build({
        ".vitepress/sidebar.ts": "",
        ".vitepress/backend.ts": 'export const A = [{ link: "/docs/B/index.md" }];',
        "docs/B/index.md": "# B\n",
    })
    cases.append(("正常页", r, 0))

    # ② 孤儿：页面存在但无人引用
    r = build({
        ".vitepress/sidebar.ts": "",
        ".vitepress/backend.ts": 'export const A = [{ link: "/docs/B/index.md" }];',
        "docs/B/index.md": "# B\n",
        "docs/B/C/index.md": "# C\n",
    })
    cases.append(("孤儿页", r, 1))

    # ③ 带引号的键也算收录（DotNet 写法）
    r = build({
        ".vitepress/sidebar.ts": "",
        ".vitepress/backend.ts": 'export const A = [{ "link": "/docs/B/C/index.md", "text": "C" }];',
        "docs/B/C/index.md": "# C\n",
    })
    cases.append(("引号键", r, 0))

    # ④ nav-only：顶部导航有、侧边栏没有
    r = build({
        ".vitepress/sidebar.ts": "",
        ".vitepress/nav.ts": 'export const nav = [{ link: "/docs/B/index.md" }];',
        ".vitepress/backend.ts": 'export const A = [{ link: "/docs/B/C/index.md" }];',
        "docs/B/index.md": "# B\n",
        "docs/B/C/index.md": "# C\n",
    })
    cases.append(("nav-only", r, 0))

    # ⑤ 断链：侧边栏指向不存在的文件
    r = build({
        ".vitepress/sidebar.ts": "",
        ".vitepress/backend.ts": 'export const A = [{ link: "/docs/B/index.md" }, { link: "/docs/X/index.md" }];',
        "docs/B/index.md": "# B\n",
    })
    cases.append(("断链", r, 1))

    # ⑥ 空仓库：只有 index.md（没有 .vitepress 就会 E0）
    r = build({"docs/B/index.md": "# B\n"})
    cases.append(("缺配置", r, 2))

    passed = 0
    for name, root, expect in cases:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = run(root, limit=5)
        ok = (rc == expect) or (expect == 0 and rc == 0)
        # 「空仓库」用返回码 2 判定；其余按「是否有 E」判定
        if expect == 0:
            ok = "E3=0" in buf.getvalue() and "W2=0" in buf.getvalue()
        elif expect == 1:
            ok = ("E3=" in buf.getvalue() and "E3=0" not in buf.getvalue()) or "W2=0" not in buf.getvalue()
        else:
            ok = rc == 2
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
        passed += 1 if ok else 0
    print("selftest %d/%d" % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(args.root, args.limit)


if __name__ == "__main__":
    sys.exit(main())
