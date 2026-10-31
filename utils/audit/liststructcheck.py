#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""liststructcheck.py — 列表结构与渲染形态巡检 · 第 110 项

为什么立这一项
--------------
本库关于「一段话长得对不对」的门已经有六道：`headingcheck`（H1 唯一与层级）、
`levelskipcheck`（标题跳级）、`sectionnumcheck`（小节编号连续）、
`sectionordercheck`（末节顺序）、`emptysectioncheck`（空小节）、
`codegapcheck`（行内代码与中文间距）。**六道全绿，仍然可以写出一个渲染后就变形的列表**：

* 子项缩进用 4 个空格——Markdown 会把它当成「代码块」而不是「子列表」，
  页面上出现一块灰底等宽文字，读者以为那是示例。
* 同级标记在 `-` 与 `*` 之间来回换——渲染出来是两种不同的项目符号，
  看起来像两个不同的列表，实际上是一段。
* 有序列表写成 `1. 2. 4.`——中间那一条永远「消失」在读者眼里，
  因为编号是渲染器根据起始值重排的，人工写的 4 并不显示。
* 列表标记后面什么都没写（`- ` 结尾换行）——渲染出一个空的项目符号。

这四类都属于「**源文件看起来对、渲染出来不对**」，而构建不报错（Markdown 合法）、
链接全通、判据齐全。第 109 项（行内代码与中文间距）管的是「代码与文字的交界」，
这一项管的是「列表标记与缩进的交界」。

判据
----
E0 ROOT_NOT_FOUND       仓库根找不到
E1 NO_ITEMS             一个列表项都没扫到（活性判据）
E2 DEEP_INDENT          子项缩进 ≥ 父内容缩进 + 4，渲染成代码块（真缺陷）
E3 EMPTY_ITEM           列表标记后无内容，渲染成空项目符号（真缺陷）
W1 MARKER_MIX           同一层级混用 `-` / `*` / `+`（渲染出不同符号）
W2 NUM_GAP              有序列表编号跳号（渲染器会按起始值重排，人工写的号不显示）
W3 NUM_STYLE_MIX        同一层级混用 `1.` 与 `1)`（渲染风格不一致）
N1 ITEMS / N2 BLOCKS    只计数

口径（四条，写在前面，避免第二次运行时被关掉）
----------------------------------------------
1. **围栏内不扫**：示例代码里的 `- x` 是文本不是结构；围栏内的缩进也是有意义的。
2. **只判「同一列表块内的同级」**：块以「非空、非列表行」结束。跨块的编号重启
   （第二段又从 1 开始）是**正确写法**，不判。
3. **E2 用「父内容缩进 + 4」而不是「缩进是 4 的倍数」**：`- item` 的内容缩进是 2，
   子项写 3 个空格也能正确渲染（多缩进 1 无碍），写 6 个空格才会变代码块。
4. **W2 只在同一块内判连续**：`1.` 后面直接 `3.` 才是跳号；`1.` 后跟 `1.`（作者
   刻意全部写 1，GitHub 风格）不算跳号，也不推进期望值。

用法
----
    python3 utils/audit/liststructcheck.py            # 扫 docs/ 与 project/
    python3 utils/audit/liststructcheck.py --selftest # 跑内建夹具
    python3 utils/audit/liststructcheck.py --root docs

纪律：**只读、不改正文**。「这一段该用几个空格」是作者判断，本项只负责把
「哪一页、第几行、渲染成什么样」列出来。
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ROOTS = ("docs", "project")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
ITEM = re.compile(r"^(\s*)([-*+]|\d{1,3}([.)]))(?:\s+(.*))?$")
SETEXT = re.compile(r"^\s{0,3}(=+|-{3,})\s*$")


class Finding:
    __slots__ = ("code", "path", "line", "detail")

    def __init__(self, code, path, line, detail):
        self.code, self.path, self.line, self.detail = code, path, line, detail


def _indent(raw: str) -> int:
    return len(raw.expandtabs(2))


def check_text(text: str, path: str = "<text>", findings: list | None = None) -> list:
    """返回 (findings, n_items, n_blocks)。"""
    findings = findings if findings is not None else []
    stack: list[dict] = []
    in_fence = False
    items = blocks = 0

    def close():
        nonlocal blocks
        if stack:
            blocks += 1
            stack.clear()

    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.strip():
            continue                      # 空行不结束列表块（松散列表合法）
        if SETEXT.match(line) and not stack:
            continue

        m = ITEM.match(line)
        if not m:
            if line.lstrip().startswith((">", "|")):
                close()                   # 引用与表格不属于列表块
            else:
                close()                   # 任何正文行都结束列表块
            continue

        indent = _indent(m.group(1))
        marker = m.group(2)
        content = (m.group(4) or "").strip()
        ordered = marker[0].isdigit()
        style = marker[-1] if ordered else marker

        if not content:
            findings.append(Finding("E3", path, lineno,
                                    f"标记后无内容：{line.strip()[:40]}"))

        while stack and indent < stack[-1]["indent"]:
            stack.pop()

        if stack:
            parent = stack[-1]
            content_indent = parent["indent"] + len(parent["marker"]) + 1
            if indent - content_indent >= 4:
                findings.append(Finding(
                    "E2", path, lineno,
                    f"缩进 {indent} 超出父内容缩进 {content_indent} 4 格以上，将渲染成代码块"))

        if stack and indent == stack[-1]["indent"]:
            sib = stack[-1]
            if not ordered and not sib["ordered"] and sib["style"] != style:
                findings.append(Finding("W1", path, lineno,
                                        f"同级标记混用 {sib['style']!r} 与 {style!r}"))
            if ordered != sib["ordered"]:
                # 标记类型切换 = 新的子列表，不参与同级比较
                sib.update({"ordered": ordered, "style": style,
                            "num": int(re.sub(r"\D", "", marker)) if ordered else 0})
                items += 1
                continue
            if ordered and sib["ordered"]:
                num = int(re.sub(r"\D", "", marker))
                if sib["style"] != style:
                    findings.append(Finding("W3", path, lineno,
                                            f"同级编号风格混用 {sib['style']!r} 与 {style!r}"))
                if not (sib["num"] == num == 1) and num != sib["num"] + 1:
                    findings.append(Finding("W2", path, lineno,
                                            f"编号跳号：{sib['num']} → {num}"))
                sib["num"] = num
            sib["style"] = style
        else:
            if not stack:
                blocks += 1
            stack.append({"indent": indent, "marker": marker, "ordered": ordered,
                          "style": style,
                          "num": int(re.sub(r"\D", "", marker)) if ordered else 0})
        items += 1

    close()
    return findings, items, blocks


def iter_pages(roots):
    for root in roots:
        base = Path(root)
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            yield p


def run(roots) -> int:
    findings: list = []
    pages = items = blocks = 0
    for p in iter_pages(roots):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"E2 READ_FAIL {p}: {exc}")
            continue
        pages += 1
        f, i, b = check_text(text, str(p))
        findings += f
        items += i
        blocks += b

    if pages == 0:
        print("E1 NO_ITEMS  一个页面都没扫到（活性判据）")
        return 2
    if items == 0:
        print(f"E1 NO_ITEMS  pages={pages} 但一个列表项都没扫到（活性判据）")
        return 2

    order = {"E2": 0, "E3": 1, "W1": 2, "W2": 3, "W3": 4}
    findings.sort(key=lambda x: (order.get(x.code, 9), x.path, x.line))
    for f in findings:
        print(f"{f.code} {_name(f.code):14s} {f.path}:{f.line}  {f.detail}")

    counts = {k: sum(1 for f in findings if f.code == k) for k in order}
    e = counts["E2"] + counts["E3"]
    w = sum(counts[k] for k in ("W1", "W2", "W3"))
    print(f"\npages={pages} blocks={blocks} items={items} "
          f"E={e} (E2={counts['E2']} E3={counts['E3']}) "
          f"W={w} (W1={counts['W1']} W2={counts['W2']} W3={counts['W3']})")
    return 1 if e else 0


NAMES = {"E2": "DEEP_INDENT", "E3": "EMPTY_ITEM", "W1": "MARKER_MIX",
         "W2": "NUM_GAP", "W3": "NUM_STYLE_MIX"}


def _name(code: str) -> str:
    return NAMES.get(code, code)


# ---------------- selftest ----------------
CASES = [
    # (说明, 文本, 期望的判据集合)
    ("干净页（无序 + 有序 + 松散列表）",
     "- a\n- b\n  - b1\n  - b2\n\n1. x\n2. y\n3. z\n", set()),
    ("子项缩进 6 格（父内容缩进 2）⇒ 代码块",
     "- a\n      - b\n", {"E2"}),
    ("子项缩进 3 格 ⇒ 合法，不判",
     "- a\n   - b\n", set()),
    ("同级标记混用",
     "- a\n* b\n", {"W1"}),
    ("有序编号跳号",
     "1. a\n3. b\n", {"W2"}),
    ("有序编号全部写 1（GitHub 风格）⇒ 不判",
     "1. a\n1. b\n", set()),
    ("编号风格混用",
     "1. a\n2) b\n", {"W3"}),
    ("空项目",
     "- a\n-\n", {"E3"}),
    ("围栏内不扫",
     "```text\n- a\n      - b\n```\n", set()),
    ("缩进 5 格的围栏也算围栏（列表内常见写法）",
     "     ```java\n     * x\n     ```\n", set()),
    ("跨块编号重启 ⇒ 不判",
     "1. a\n2. b\n\n正文段落\n\n1. c\n", set()),
    ("引用块里的列表不参与",
     "> - a\n> * b\n", set()),
    ("表格行结束列表块",
     "1. a\n\n| h |\n| - |\n| v |\n\n1. b\n", set()),
    ("有序表子项缩进 4（父内容缩进 3）⇒ 合法，不判",
     "1. a\n    1. b\n", set()),
    ("有序表子项缩进 7（父内容缩进 3）⇒ 代码块",
     "1. a\n       1. b\n", {"E2"}),
    ("制表符按 2 空格展开",
     "- a\n\t- b\n", set()),
]


def selftest() -> int:
    ok = 0
    for i, (desc, text, expect) in enumerate(CASES, 1):
        findings, _, _ = check_text(text, f"case{i}.md")
        got = {f.code for f in findings}
        if got == expect:
            ok += 1
        else:
            print(f"FAIL {i} {desc}: 期望 {sorted(expect)}，实际 {sorted(got)}")

    # 目录聚合 + 空目录活性
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "docs"
        d.mkdir()
        (d / "a.md").write_text("- a\n* b\n", encoding="utf-8")
        findings, items, _ = check_text((d / "a.md").read_text(encoding="utf-8"), "docs/a.md")
        if items == 2 and any(f.code == "W1" for f in findings):
            ok += 1
        else:
            print("FAIL 目录聚合：期望 2 项且报 W1")
        empty = Path(td) / "empty"
        empty.mkdir()
        if list(iter_pages([str(empty)])) == []:
            ok += 1
        else:
            print("FAIL 空目录活性：期望空列表")

    total = len(CASES) + 2
    print(f"selftest {ok}/{total} {'PASS' if ok == total else 'FAIL'}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="列表结构与渲染形态巡检")
    ap.add_argument("--root", action="append", help="扫描根目录，可重复；默认 docs 与 project")
    ap.add_argument("--selftest", action="store_true", help="跑内建夹具")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    roots = tuple(args.root) if args.root else ROOTS
    if not any(Path(r).is_dir() for r in roots):
        print(f"E0 ROOT_NOT_FOUND  扫描根都不存在：{roots}")
        return 2
    return run(roots)


if __name__ == "__main__":
    sys.exit(main())
