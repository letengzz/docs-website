#!/usr/bin/env python3
"""blockgapcheck.py —— Markdown 块级元素之间「缺空行」的巡检（第一百二十三项）。

为什么需要它：
  本库已有 tablecheck（表格列数）、liststructcheck（列表结构）、containercheck（容器配对）、
  fencecheck（围栏闭合）四道门，但它们都只看**一个块内部**是否成立，
  没有一道看**两个块之间**是否被空行隔开。

  而 CommonMark 里，表格行紧跟一行正文（中间没有空行）时，表格会被降级成段落文本：
  页面上出现的是一串带竖线的文字，不是表格。围栏结束标记后面紧跟正文也有同类问题——
  闭合标记会被当成内容的一部分。这两类缺陷在构建时完全静默，GitHub 与 VitePress 的
  渲染差异还会让作者本地看着正常。

判据：
  E0 ROOT_NOT_FOUND      扫描根不存在
  E1 NO_PAGES            活性：一页都没扫到，拒绝判定
  E2 TABLE_SWALLOW       表格最后一行后面紧跟普通正文（该行会被吞成表格的一个单元格）
  W1 CONTAINER_TIGHT     容器结束 `:::` 后紧跟非空行（渲染正常，但会与下文粘连）
  W2 FENCE_TIGHT         围栏开始标记前无空行（可能是列表内合法写法，故只提示）
  W3 FENCE_CLOSE_TEXT    围栏结束标记后紧跟正文（实测渲染正常，仅作形态提示）

  注意：E3 在口径收敛时被**降级为 W3**。首版按 CommonMark 常识判定「围栏后必须空行」，
  但用本仓真实的 `createMarkdownRenderer()` 实测，```js … ``` 后紧跟正文会正常渲染成
  `<pre>` + `<p>`，并非缺陷。而「表格后紧跟正文」实测会把正文渲染成
  `<td>正文</td><td></td>` —— 这才是真会静默吞内容的一类。

用法：
  python3 utils/audit/blockgapcheck.py [--root docs project] [--selftest]
退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

FENCE = re.compile(r"^(\s*)(```+|~~~+)")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
CONTAINER_CLOSE = re.compile(r"^\s*:::\s*$")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")


def iter_md(root: str):
    for dirpath, _dirs, files in os.walk(root):
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def scan_file(path: str):
    """返回 [(code, lineno, detail)]"""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    out = []
    in_fence = False
    fence_mark = ""
    # 跳过 frontmatter
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, min(len(lines), 40)):
            if lines[i].strip() == "---":
                start = i + 1
                break

    for i in range(start, len(lines)):
        line = lines[i]
        m = FENCE.match(line)
        if m:
            mark = m.group(2)[0]
            if not in_fence:
                # 围栏开始：前一行紧邻非空（且不是列表项/缩进）→ W2
                if i > start:
                    prev = lines[i - 1]
                    if prev.strip() and not prev.lstrip().startswith(("-", "*", "+")) \
                            and not re.match(r"^\s*\d{1,3}[.)]\s", prev) \
                            and not prev.strip().startswith("|") \
                            and not HEADING.match(prev):
                        out.append(("W2", i + 1, "围栏开始前缺空行"))
                in_fence = True
                fence_mark = mark
                continue
            elif mark == fence_mark:
                in_fence = False
                # 围栏结束：下一行紧邻非空 → E3
                if i + 1 < len(lines) and lines[i + 1].strip():
                    out.append(("W3", i + 1, f"围栏结束后紧跟: {lines[i + 1][:40]}"))
                continue

        if in_fence:
            continue

        # 表格行之后紧跟「普通正文」→ E2（标题/列表/引用/容器/围栏都能正常中断表格）
        if TABLE_ROW.match(line):
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            t = nxt.strip()
            interrupts = (not t) or TABLE_ROW.match(nxt) or HEADING.match(nxt) \
                or t.startswith(("-", "*", "+", ">", ":::", "```", "~~~", "<", "|")) \
                or re.match(r"^\d{1,3}[.)]\s", t)
            if t and not interrupts:
                out.append(("E2", i + 2, f"表格后紧跟正文: {t[:40]}"))

        # 容器结束之后紧跟非空 → W1
        if CONTAINER_CLOSE.match(line) and i + 1 < len(lines):
            nxt = lines[i + 1]
            if nxt.strip() and not CONTAINER_CLOSE.match(nxt):
                out.append(("W1", i + 2, f"容器结束后紧跟: {nxt.strip()[:40]}"))

    return out


SELFTEST = [
    ("表格后紧跟正文", "| a | b |\n| --- | --- |\n| 1 | 2 |\n正文\n", {"E2"}),
    ("表格后空行再正文", "| a | b |\n| --- | --- |\n| 1 | 2 |\n\n正文\n", set()),
    ("表格结束于文件尾", "| a | b |\n| --- | --- |\n| 1 | 2 |\n", set()),
    ("表格后紧跟标题", "| a | b |\n| --- | --- |\n| 1 | 2 |\n## 标题\n", set()),
    ("表格后紧跟引用", "| a | b |\n| --- | --- |\n| 1 | 2 |\n> 注\n", set()),
    ("表格后紧跟围栏", "| a | b |\n| --- | --- |\n| 1 | 2 |\n```js\na\n```\n\n尾\n", set()),
    ("围栏后紧跟正文", "```js\nlet a = 1;\n```\n正文\n", {"W3"}),
    ("围栏后空行", "```js\nlet a = 1;\n```\n\n正文\n", set()),
    ("围栏内出现表格行", "```md\n| a | b |\n文本\n```\n\n尾\n", set()),
    ("容器结束后紧跟正文", "::: tip\n提示\n:::\n正文\n", {"W1"}),
    ("容器后空行", "::: tip\n提示\n:::\n\n正文\n", set()),
    ("围栏前缺空行", "正文\n```js\nlet a = 1;\n```\n\n尾\n", {"W2"}),
    ("列表内围栏前无空行", "- 项\n  ```js\n  a\n  ```\n\n尾\n", set()),
    ("表格后紧跟列表", "| a | b |\n| --- | --- |\n| 1 | 2 |\n- 项\n", set()),
    ("行内管道不算表格", "文本 | 文本\n\n尾\n", set()),
    ("嵌套表格行内换行", "| a | b |\n| --- | --- |\n| 1<br/>2 | 3 |\n\n尾\n", set()),
]


def selftest() -> int:
    bad = 0
    for name, body, expect in SELFTEST:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.md")
            open(p, "w", encoding="utf-8").write(body)
            got = {c for c, _, _ in scan_file(p)}
        ok = got == expect
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got={sorted(got)} expect={sorted(expect)}")
        bad += 0 if ok else 1
    print(f"\nselftest {len(SELFTEST) - bad}/{len(SELFTEST)}")
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="+", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    for r in args.root:
        if not os.path.isdir(r):
            print(f"E0 ROOT_NOT_FOUND {r}")
            return 1
    pages = 0
    stat = {"E2": 0, "W1": 0, "W2": 0, "W3": 0}
    for root in args.root:
        for p in iter_md(root):
            pages += 1
            for code, ln, detail in scan_file(p):
                stat[code] += 1
                print(f"{code} {p}:{ln} {detail}")
    if pages == 0:
        print("E1 NO_PAGES")
        return 1
    e = stat["E2"]
    print(f"\npages={pages} E2={stat['E2']} W1={stat['W1']} W2={stat['W2']} W3={stat['W3']} E={e}")
    return 0 if e == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
