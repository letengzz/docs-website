#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tablecheck.py —— Markdown 表格结构巡检（第 73 项）。

判据
----
E0 ROOT_NOT_FOUND   根目录不存在
E1 NO_PAGES         没扫到任何 Markdown（活性判据）
E2 COLUMN_MISMATCH  数据行单元格数 ≠ 表头单元格数（渲染会缺列 / 串列）
E3 BAD_DELIMITER    分隔行单元格数 ≠ 表头单元格数
E4 TABLE_MASKED     表头前少空行，表格不会被渲染成表格
W1 HEADER_ONLY      只有表头与分隔行，没有数据行
W2 EMPTY_HEADER     表头存在空单元格

用法
----
    python3 utils/audit/tablecheck.py [根目录]
    python3 utils/audit/tablecheck.py --selftest

退出码：0 = 无 E 级；1 = 有 E 级；2 = 用法错误。
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

SKIP_DIRS = {"node_modules", ".git", ".vitepress", "dist", ".workbuddy"}
# markdown-it 的表格分隔符口径：可选冒号 + 至少一个短横线
DELIM_RE = re.compile(r"^:?-+:?$")
FENCE_RE = re.compile(r"^\s{0,8}(`{3,}|~{3,})")
# 这些行本身就是「块边界」，表格紧跟其后仍会被正常解析
BLOCK_BOUNDARY_RE = re.compile(r"^\s*(#{1,6}\s|:::+\s*|>|[-*+]\s|\d+[.)]\s|<[a-zA-Z/!])")


def split_row(line: str) -> list[str]:
    """按未转义的竖线切分单元格。

    刻意**不**识别行内代码：markdown-it 的表格切分只认反斜杠转义，不认反引号，
    所以 `` `a|b` `` 里的竖线在渲染时确实会切开单元格——这正是要抓的缺陷。
    """
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, buf, i = [], [], 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            buf.append(s[i:i + 2])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def is_delim_row(line: str) -> bool:
    if "-" not in line:
        return False
    cells = [c for c in split_row(line)]
    if len(cells) < 2:
        return False
    return all(DELIM_RE.match(c.replace(" ", "")) for c in cells)


def scan_file(path: str):
    """返回 [(级别, 判据, 行号, 说明)]。"""
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except UnicodeDecodeError:
        return [("E", "E0", 0, "不是 UTF-8 编码")]

    fence = None
    i = 0
    while i < len(lines):
        line = lines[i]
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            i += 1
            continue
        if fence is not None:
            i += 1
            continue

        if "|" in line and i + 1 < len(lines) and is_delim_row(lines[i + 1]):
            header = split_row(line)
            delim = split_row(lines[i + 1])
            if len(delim) != len(header):
                out.append(("E", "E3", i + 1,
                            f"分隔行 {len(delim)} 列 ≠ 表头 {len(header)} 列"))
            empty_idx = [k for k, c in enumerate(header) if c == ""]
            if len(empty_idx) == 1 and empty_idx[0] == 0 and len(header) > 2:
                empty_idx = []          # 对比表常见的空对角单元格，不算缺陷
            for idx in empty_idx:
                out.append(("W", "W2", i + 1, f"第 {idx + 1} 列表头为空"))
            prev = lines[i - 1] if i > 0 else ""
            if prev.strip() != "" and "|" not in prev \
                    and not FENCE_RE.match(prev) and not BLOCK_BOUNDARY_RE.match(prev):
                out.append(("E", "E4", i + 1, "表头前缺少空行，表格不会渲染"))
            j = i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip() != "":
                if FENCE_RE.match(lines[j]):
                    break
                cells = split_row(lines[j])
                if len(cells) != len(header):
                    out.append(("E", "E2", j + 1,
                                f"数据行 {len(cells)} 列 ≠ 表头 {len(header)} 列"))
                j += 1
            if j == i + 2:
                out.append(("W", "W1", i + 1, "只有表头与分隔行，没有数据行"))
            i = j
            continue
        i += 1
    return out


def iter_md(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def run(root: str) -> int:
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND", root)
        return 1
    pages = list(iter_md(root))
    if not pages:
        print("E1 NO_PAGES", root)
        return 1
    e = w = 0
    for p in pages:
        for level, judge, ln, msg in scan_file(p):
            print(f"{level} {judge} {os.path.relpath(p, root)}:{ln} {msg}")
            if level == "E":
                e += 1
            else:
                w += 1
    print(f"pages={len(pages)} E={e} W={w}")
    return 0 if e == 0 else 1


GOOD = (
    "# t\n\n"
    "| 列 A | 列 B |\n| --- | --- |\n| 1 | 2 |\n\n"
    "| 带 \\| 转义 | `a\\|b` |\n| --- | --- |\n| x | y |\n"
)

BAD = (
    "# t\n\n"
    "| A | B | C |\n| --- | --- |\n| 1 | 2 | 3 |\n\n"      # E3
    "| A | B |\n| --- | --- |\n| 1 | 2 | 3 |\n\n"            # E2
    "段落紧贴表格\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\n"   # E4
    "| A |  |\n| --- | --- |\n| 1 | 2 |\n\n"                 # W2
    "| A | B |\n| --- | --- |\n\n"                           # W1
    "```md\n| A | B |\n| --- | --- |\n| 1 |\n```\n"          # 代码块内不报
)


def selftest() -> int:
    with tempfile.TemporaryDirectory() as d:
        g, b = os.path.join(d, "good.md"), os.path.join(d, "bad.md")
        open(g, "w", encoding="utf-8").write(GOOD)
        open(b, "w", encoding="utf-8").write(BAD)
        good, bad = scan_file(g), scan_file(b)
    ok = True
    if good:
        ok = False
        print("FAIL: good.md 应为 0 条，实际", good)
    got = {j for _, j, _, _ in bad}
    want = {"E2", "E3", "E4", "W1", "W2"}
    if not want.issubset(got):
        ok = False
        print("FAIL: bad.md 缺判据", want - got)
    if sum(1 for _, j, _, _ in bad if j == "E2") != 1:
        ok = False
        print("FAIL: E2 应恰好 1 条（代码块内的表格不应计入），实际",
              [x for x in bad if x[1] == "E2"])
    print("selftest", "PASS" if ok else "FAIL", f"(good=0 bad={len(bad)})")
    return 0 if ok else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(selftest())
    if len(args) > 1:
        print("usage: tablecheck.py [root] | --selftest")
        sys.exit(2)
    sys.exit(run(args[0] if args else "."))
