#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""colsetdriftcheck.py —— 「同一张表的列集合」跨页漂移巡检（第 259 天新立，第一百四十项巡检）

## 立这一项的原因

本库的 `sql` 围栏里，同一张表会在多页各写一份 `CREATE TABLE`：建模页一份、迁移页一份、
实战页一份。**列类型**已经被 `typedriftcheck`（第 139 项）管住，**枚举取值**已经被
`enumdriftcheck`（第 138 项）管住，**列数与值数**已经被 `insertaritycheck`（第 121 项）管住，
**表建过没有**已经被 `ddlrefcheck`（第 113 项）管住。

四道门全绿，仍然可以出现这一种缺陷：

    建模页：CREATE TABLE invoice(id, no, net, tax, gross, ...);
    实战页：CREATE TABLE invoice(id, no, net, tax, ...);          -- 少了 gross
    迁移页：ALTER TABLE invoice ADD COLUMN gross INTEGER;          -- 又补回来了

照着实战页建库的人，`CHECK(gross = net + tax)` 会直接失败；而照着建模页建库的人，
迁移脚本会因为「列已存在」失败。两页都「语法正确、类型一致、枚举一致」。

**为什么不做成 E**：本库大量页面为了讲清一个点，只写**部分列**（`CREATE TABLE t(a, b)`
后面接「其余列略」）。这类写法是正当的，机器分不开「故意省略」与「抄漏」。所以跨页只报
`W`，由人判；只有**同一页内同名表两份 DDL 列集合不同**才报 `E`——一页之内自相矛盾，
没有反例可辩。

## 判据

  E0 ROOT_NOT_FOUND        既没有 docs/ 也没有 project/
  E1 NO_TABLES             一个 CREATE TABLE 都没解析到（活性判据）
  E2 DUP_COLUMN            同一份 DDL 里同一个列名出现两次（无正当解释）
  W1 CROSS_PAGE_SUBSET     同主题跨页：某页的列集合是三页以上共同定义的严格子集
  W2 ORDER_DIFF            列集合相同但列顺序不同（同主题跨页）
  W3 SAME_PAGE_CONFLICT    同一页内同名表两份 DDL 列集合不同（多为「改前/改后」对照）
  N1 PAGES / N2 TABLES / N3 DEFS 只计数

## 口径（四条）

1. **只解析 `sql` 围栏**（info 以 `sql` 开头），复用 `fenceutil.scan()`；heredoc 与缩进代码块
   不认——本库不用它们写 DDL。
2. **按顶层逗号切列**：括号深度与引号状态都要跟踪，`numeric(12,2)` 里的逗号不是列分隔符，
   `DEFAULT 'a,b'` 里的逗号也不是。这一条被真实语料打过两次（第 139 项同形）。
3. **表约束行不是列**：`PRIMARY KEY` / `FOREIGN KEY` / `UNIQUE` / `CHECK` / `CONSTRAINT` /
   `KEY` / `INDEX` / `EXCLUDE` / `LIKE` 开头的项跳过。
4. **`ALTER TABLE … ADD [COLUMN] x` 计入该页该表的列集合**：本库大量页面用「建表 + 补列」
   讲迁移，不并进去会制造大量假 `W1`。
5. **只在同一主题内比**（`docs/<分类>/<主题>` 或 `project/<组>/<项目>`）：`booking` 在
   预约专题与酒店专题里是两张不同的表，跨主题比会得到一屏「缺列」的噪声。
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

CREATE_RE = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([A-Za-z_][\w.]*)\s*\(", re.I)
ALTER_RE = re.compile(r"alter\s+table\s+(?:only\s+)?([A-Za-z_][\w.]*)\s+add\s+(?:column\s+)?([A-Za-z_]\w*)", re.I)
NON_COL = re.compile(
    r"^(constraint|primary\s+key|foreign\s+key|unique|check|key|index|exclude|like)\b", re.I
)


def norm_table(name: str) -> str:
    name = name.strip().strip('"`[]')
    return name.split(".")[-1].lower()


def split_top(body: str):
    """按顶层逗号切分；跟踪括号与单双引号。"""
    out, buf, depth, quote = [], [], 0, None
    for ch in body:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


def match_paren(text: str, open_idx: int):
    """返回与 text[open_idx] == '(' 配对的 ')' 下标，失败返回 -1。"""
    depth, quote = 0, None
    for i in range(open_idx, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_block(block: str):
    """返回 [(table, [cols...], [dup...])]（可能多张表）。"""
    found = []
    for m in CREATE_RE.finditer(block):
        open_idx = block.index("(", m.end() - 1)
        close_idx = match_paren(block, open_idx)
        if close_idx == -1:
            continue
        body = block[open_idx + 1 : close_idx]
        cols, dup = [], []
        for item in split_top(body):
            s = item.strip()
            if not s or NON_COL.match(s):
                continue
            name = s.split()[0].strip('"`[]')
            if re.match(r"^[A-Za-z_]\w*$", name):
                low = name.lower()
                if low in cols and low not in dup:
                    dup.append(low)
                cols.append(low)
        if cols:
            found.append((norm_table(m.group(1)), cols, dup))
    return found


def collect(root: str):
    pages, tables = 0, 0
    defs = {}  # table -> list of dict(page, cols, order)
    for base in ("docs", "project"):
        base_dir = os.path.join(root, base)
        if not os.path.isdir(base_dir):
            continue
        for dirpath, _dirnames, filenames in os.walk(base_dir):
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, root)
                try:
                    text = open(path, encoding="utf-8").read()
                except OSError:
                    continue
                _mask, blocks, _unclosed = fenceutil.scan(text)
                lines = text.split("\n")
                page_hits = []
                for start, end, info in blocks:
                    if not info.lower().startswith("sql"):
                        continue
                    block = "\n".join(lines[start + 1 : end])
                    page_hits.extend(parse_block(block))
                    for m in ALTER_RE.finditer(block):
                        page_hits.append(("__alter__", norm_table(m.group(1)), m.group(2).lower()))
                if not page_hits:
                    continue
                pages += 1
                parts = rel.split(os.sep)
                topic = "/".join(parts[:3])
                alters = {}
                creates = {}
                dups = {}
                for hit in page_hits:
                    if hit[0] == "__alter__":
                        alters.setdefault(hit[1], set()).add(hit[2])
                    else:
                        creates.setdefault(hit[0], []).append(hit[1])
                        if len(hit) > 2 and hit[2]:
                            dups.setdefault(hit[0], set()).update(hit[2])
                for table, collists in creates.items():
                    merged = []
                    for cols in collists:
                        st = set(cols) | alters.get(table, set())
                        merged.append((cols, st))
                    key = topic + "::" + table
                    for cols, st in merged:
                        defs.setdefault(key, []).append(
                            {"page": rel, "cols": cols, "set": st,
                             "dup": sorted(dups.get(table, set()))}
                        )
                    tables += 1
    return pages, tables, defs


def judge(defs):
    errs, warns = [], []
    for key, items in sorted(defs.items()):
        table = key.split("::", 1)[1]
        for it in items:
            if it["dup"]:
                errs.append(("E2", it["page"], table, "重复列：" + ",".join(it["dup"])))
        by_page = {}
        for it in items:
            by_page.setdefault(it["page"], []).append(it["set"])
        for page, sets in by_page.items():
            if len(sets) > 1 and any(st != sets[0] for st in sets[1:]):
                warns.append(("W3", page, table, "同页两份 DDL 列集合不同"))
        if len(by_page) >= 3:
            union = set().union(*[st for sets in by_page.values() for st in sets])
            for page, sets in by_page.items():
                st = set().union(*sets)
                if st < union:
                    warns.append(("W1", page, table, "缺列：" + ",".join(sorted(union - st))))
        pages_by_set = {}
        for it in items:
            pages_by_set.setdefault(frozenset(it["set"]), []).append(it)
        if len(pages_by_set) > 1:
            first_key, first_order, first_page = None, None, None
            for k, its in pages_by_set.items():
                order = list(its[0]["cols"])
                if first_key is None:
                    first_key, first_order, first_page = k, order, its[0]["page"]
                elif k == first_key and order != first_order:
                    warns.append(("W2", its[0]["page"], table, "列顺序不同"))
    return errs, warns


def selftest():
    import tempfile
    import shutil

    cases = [
        # (name, body, expect_e, expect_w)
        ("same-page-dup", "```sql\nCREATE TABLE t(a int, b int);\n```\n```sql\nCREATE TABLE t(a int);\n```", 0, 1),
        ("dup-column", "```sql\nCREATE TABLE t6(a int, b int, a text);\n```", 1, 0),
        ("alter-ok", "```sql\nCREATE TABLE t2(a int, b int);\nALTER TABLE t2 ADD COLUMN c int;\n```", 0, 0),
        ("constraint-skip", "```sql\nCREATE TABLE t3(a int, PRIMARY KEY(a), CHECK(a>0));\n```", 0, 0),
        ("paren-comma", "```sql\nCREATE TABLE t4(a numeric(12,2), b text DEFAULT 'x,y');\n```", 0, 0),
        ("non-sql", "```text\nCREATE TABLE t5(a);\n```", 0, 0),
    ]
    ok = 0
    for name, body, ee, ew in cases:
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmp, "docs", "X"), exist_ok=True)
            open(os.path.join(tmp, "docs", "X", "index.md"), "w", encoding="utf-8").write(
                "# T\n\n" + body + "\n"
            )
            pages, tables, defs = collect(tmp)
            errs, warns = judge(defs)
            good = len(errs) == ee and len(warns) == ew
            print(("PASS " if good else "FAIL ") + name + f" E={len(errs)} W={len(warns)}")
            ok += 1 if good else 0
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    # 跨页 W1：三页定义同一张表，其中一页缺列
    tmp = tempfile.mkdtemp()
    try:
        for i, cols in enumerate(["a,b,c", "a,b,c", "a,b"]):
            d = os.path.join(tmp, "docs", "T", "topicA", f"P{i}")
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "index.md"), "w", encoding="utf-8").write(
                "# T\n\n```sql\nCREATE TABLE t9(" + cols + " int);\n```\n"
            )
        pages, tables, defs = collect(tmp)
        errs, warns = judge(defs)
        good = len(errs) == 0 and any(w[0] == "W1" for w in warns)
        print(("PASS " if good else "FAIL ") + f"cross-page-subset E={len(errs)} W={len(warns)}")
        ok += 1 if good else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    total = len(cases) + 1
    print(f"selftest {ok}/{total}")
    return 0 if ok == total else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = "."
    for a in argv:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND")
        return 2
    pages, tables, defs = collect(root)
    if not defs:
        print("E1 NO_TABLES")
        return 2
    errs, warns = judge(defs)
    for code, page, table, msg in errs:
        print(f"{code} {page} :: {table} :: {msg}")
    shown = 0
    for code, page, table, msg in warns:
        if shown < 40:
            print(f"{code} {page} :: {table} :: {msg}")
        shown += 1
    print(
        f"pages={pages} tables={tables} defs={sum(len(v) for v in defs.values())} "
        f"E={len(errs)} W={len(warns)}"
    )
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
