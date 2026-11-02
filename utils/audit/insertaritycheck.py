#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""insertaritycheck.py —— SQL 围栏里 INSERT 的列数与值个数是否一致（第 121 项巡检）。

背景
----
本库的 `sql` 围栏已有 1,700 多个，其中大量是「先 CREATE TABLE、再 INSERT 示例行」的成对写法。
读者照着抄时，最容易踩的错不是语法，而是**列数与值个数不等**：

    INSERT INTO claim (claim_id, claim_no, status) VALUES (1, 'C-1');

SQLite 直接报 `table claim has 3 columns but 2 values were supplied`。这类缺陷在文档里
完全看不出来——高亮正常、表格对齐正常、构建也不报错，只有读者动手那一刻才炸，而且
大概率以为是自己抄漏了。

既有巡检各管一段，都不问这件事：

  - `ddlrefcheck`（第 113 项）  引用的表建过没有
  - `reswordcheck`（第 112 项） 标识符是不是保留字
  - `fwcodecheck`（第 117 项）  语法区有没有全角标点
  - `jsonfencecheck`（第 97 项） json 能不能解析
  - `langmatchcheck`            标着 sql 的块里是不是 sql

「列数 vs 值数」落在它们之间：表名存在、没有保留字、没有全角标点、确实是 SQL——四条全绿。

判据（E 为错误、W 为提示）
--------------------------
E0 ROOT_NOT_FOUND      仓库根既无 docs/ 也无 project/
E1 NO_BLOCKS           一个 sql 围栏都没扫到就拒绝判定（活性）
E2 ARITY_MISMATCH      显式列名个数 / 无列名时的建表列数 ≠ VALUES 元组元素个数
E3 MULTIROW_MISMATCH   VALUES 有多行时，某一行与第一行的元素个数不同
W1 UNKNOWN_TABLE       同页找不到该表的 CREATE TABLE（跨页引用或教学片段，只计数）
W2 UNKNOWN_COLUMN      显式列名不在同页建表语句里（可能被 ALTER 加列，只提示）
W3 NO_COLUMNS          无列名的 INSERT 且同页无建表语句，无法判定（只计数）

设计取舍
--------
* **只判同页**：跨页引用（Practice 页引用 AccountModel 页的 DDL）是合法写法，判 E 会
  大面积误报。全库 `ddlrefcheck` 实测跨页引用 398 处，这个量级足以让这道门第一天就被关掉。
* **先剥注释与字符串，再数逗号**：`('a,b', 2)` 与 `-- INSERT INTO t VALUES (1)` 都能
  凭空造出错判，而这两类在本库都真实存在。
* **括号深度要数**：`(1, coalesce(a, b), 3)` 的内层逗号不是元组分隔符。
* **多行 VALUES 逐行判**：`VALUES (1,2),(3,4,5)` 只有第二行错，报 E3 并给出第几行。
* **约束行不算列**：`PRIMARY KEY (a, b)` 里的逗号不是列分隔符，按首词白名单剔除。

用法
----
    python3 utils/audit/insertaritycheck.py                # 默认根：仓库根
    python3 utils/audit/insertaritycheck.py --verbose      # 连 W 一起列
    python3 utils/audit/insertaritycheck.py --selftest     # 判据自测

退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

FENCE_OPEN = re.compile(r"^\s*```\s*sql\s*$", re.I)
FENCE_ANY = re.compile(r"^\s*```")
CREATE = re.compile(r"CREATE\s+(?:TEMP(?:ORARY)?\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][\w]*)", re.I)
INSERT = re.compile(r"INSERT\s+(?:OR\s+\w+\s+)?INTO\s+([A-Za-z_][\w]*)\s*", re.I)
CONSTRAINT_WORDS = ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "CONSTRAINT", "KEY", "EXCLUDE")


def strip_sql(s: str) -> str:
    """剥掉 -- 行注释、/* */ 块注释与 '...' 字符串字面量（等长占位，保留位置）。"""
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "'":
            j = i + 1
            while j < n:
                if s[j] == "'" and j + 1 < n and s[j + 1] == "'":
                    j += 2
                    continue
                if s[j] == "'":
                    break
                j += 1
            out.append("''")
            i = j + 1
        elif c == "-" and i + 1 < n and s[i + 1] == "-":
            j = s.find("\n", i)
            i = n if j == -1 else j
        elif c == "/" and i + 1 < n and s[i + 1] == "*":
            j = s.find("*/", i + 2)
            i = n if j == -1 else j + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def split_top(s: str, sep: str = ",") -> list[str]:
    """按顶层分隔符切分（忽略括号内的分隔符）。"""
    parts, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            depth -= 1
            cur.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip() != ""]


def match_paren(s: str, start: int) -> int:
    """返回与 s[start]=='(' 匹配的右括号下标，找不到返回 -1。"""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_tables(sql: str) -> dict[str, list[str]]:
    """同页建表：表名 -> 列名列表（顺序）。"""
    tables: dict[str, list[str]] = {}
    for m in CREATE.finditer(sql):
        name = m.group(1).strip().lower()
        p = sql.find("(", m.end())
        if p == -1:
            continue
        q = match_paren(sql, p)
        if q == -1:
            continue
        body = sql[p + 1:q]
        like = re.match(r"\s*LIKE\s+([A-Za-z_][\w]*)", body, re.I)
        if like:
            src = like.group(1).lower()
            if src in tables:
                tables[name] = list(tables[src])
            continue
        cols = []
        for item in split_top(body):
            head = item.split()[0].upper() if item.split() else ""
            if head in CONSTRAINT_WORDS:
                continue
            col = re.match(r"([A-Za-z_][\w]*)", item)
            if col:
                cols.append(col.group(1).lower())
        if cols:
            tables[name] = cols
    return tables


def parse_inserts(sql: str):
    """产出 (表名, 显式列名列表或 None, [每行的元素个数], 行号偏移)。"""
    for m in INSERT.finditer(sql):
        name = m.group(1).lower()
        pos = m.end()
        cols = None
        if pos < len(sql) and sql[pos] == "(":
            q = match_paren(sql, pos)
            if q == -1:
                continue
            cols = [c.strip().strip('"').lower() for c in split_top(sql[pos + 1:q])]
            pos = q + 1
        vm = re.match(r"\s*VALUES\s*", sql[pos:], re.I)
        if not vm:
            continue
        pos += vm.end()
        rows = []
        while pos < len(sql) and sql[pos] == "(":
            q = match_paren(sql, pos)
            if q == -1:
                break
            rows.append(len(split_top(sql[pos + 1:q])))
            pos = q + 1
            while pos < len(sql) and sql[pos] in " \t\r\n,":
                pos += 1
        if rows:
            raw = sql[m.start():pos]
            if "..." in raw or "\u2026" in raw:
                continue          # 教学片段：略去列或值，不判
            yield name, cols, rows, sql[:m.start()].count("\n") + 1


def scan_file(path: str):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    # 抽取 sql 围栏（保留围栏内相对行号）
    blocks, cur, inside = [], None, False
    for i, ln in enumerate(lines, 1):
        if not inside and FENCE_OPEN.match(ln):
            inside, cur = True, [i, []]
            continue
        if inside and FENCE_ANY.match(ln):
            inside = False
            blocks.append(cur)
            cur = None
            continue
        if inside and cur is not None:
            cur[1].append(ln)
    if inside and cur is not None:
        blocks.append(cur)

    sql = strip_sql("\n".join("\n".join(b[1]) for b in blocks))
    tables = parse_tables(sql)
    findings = []
    for start, body in blocks:
        text = strip_sql("\n".join(body))
        for name, cols, rows, off in parse_inserts(text):
            line = start + off
            if name not in tables:
                findings.append(("W1", line, f"UNKNOWN_TABLE {name}"))
                continue
            tbl_cols = tables[name]
            if cols is None:
                if len(rows) > 1 and any(r != len(tbl_cols) for r in rows):
                    findings.append(("E3", line, f"MULTIROW_MISMATCH {name} 建表 {len(tbl_cols)} 列 / 各行 {rows}"))
                elif rows[0] != len(tbl_cols):
                    findings.append(("E2", line, f"ARITY_MISMATCH {name} 建表 {len(tbl_cols)} 列 / 值 {rows[0]} 个"))
            else:
                if len(cols) != rows[0]:
                    findings.append(("E2", line, f"ARITY_MISMATCH {name} 列 {len(cols)} 个 / 值 {rows[0]} 个"))
                elif len(rows) > 1 and any(r != len(cols) for r in rows):
                    findings.append(("E3", line, f"MULTIROW_MISMATCH {name} 列 {len(cols)} 个 / 各行 {rows}"))
                for c in cols:
                    if c and c not in tbl_cols:
                        findings.append(("W2", line, f"UNKNOWN_COLUMN {name}.{c}"))
    return blocks, findings


def iter_md(roots):
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".vitepress", "node_modules", "assets")]
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def run(roots, verbose=False) -> int:
    if not any(os.path.isdir(r) for r in roots):
        print("E0 ROOT_NOT_FOUND  仓库根既无 docs/ 也无 project/")
        return 1
    pages = blocks_n = inserts = 0
    stat = {"E2": 0, "E3": 0, "W1": 0, "W2": 0}
    details = []
    for path in iter_md(roots):
        blocks, findings = scan_file(path)
        if not blocks:
            continue
        pages += 1
        blocks_n += len(blocks)
        for code, line, msg in findings:
            if code in ("E2", "E3"):
                stat[code] += 1
                details.append((code, path, line, msg))
            else:
                stat[code] += 1
                if verbose:
                    details.append((code, path, line, msg))
    if blocks_n == 0:
        print("E1 NO_BLOCKS  一个 sql 围栏都没扫到，拒绝判定")
        return 1
    e = stat["E2"] + stat["E3"]
    for code, path, line, msg in details:
        if code.startswith("E") or verbose:
            print(f"{code} {path}:{line} {msg}")
    print(f"pages={pages} blocks={blocks_n} E2={stat['E2']} E3={stat['E3']} "
          f"W1={stat['W1']} W2={stat['W2']} E={e}")
    return 0 if e == 0 else 1


SELFTEST = [
    ("显式列名 3 个 / 值 2 个 -> E2", """```sql
CREATE TABLE t (a INT, b INT, c INT);
INSERT INTO t (a, b, c) VALUES (1, 2);
```""", 1),
    ("显式列名 2 个 / 值 2 个 -> 通过", """```sql
CREATE TABLE t (a INT, b INT, c INT);
INSERT INTO t (a, b) VALUES (1, 2);
```""", 0),
    ("无列名 / 建表 3 列 / 值 3 个 -> 通过", """```sql
CREATE TABLE t (a INT, b INT, c INT);
INSERT INTO t VALUES (1, 2, 3);
```""", 0),
    ("无列名 / 建表 3 列 / 值 2 个 -> E2", """```sql
CREATE TABLE t (a INT, b INT, c INT);
INSERT INTO t VALUES (1, 2);
```""", 1),
    ("多行值都对 -> 通过", """```sql
CREATE TABLE t (a INT, b INT);
INSERT INTO t VALUES (1, 2), (3, 4);
```""", 0),
    ("多行中第二行少一个 -> E3", """```sql
CREATE TABLE t (a INT, b INT);
INSERT INTO t VALUES (1, 2), (3);
```""", 1),
    ("函数调用内的逗号不算分隔 -> 通过", """```sql
CREATE TABLE t (a INT, b INT, c INT);
INSERT INTO t VALUES (1, coalesce(2, 3), 4);
```""", 0),
    ("字符串里的逗号不算分隔 -> 通过", """```sql
CREATE TABLE t (a TEXT, b INT);
INSERT INTO t VALUES ('x,y', 2);
```""", 0),
    ("跨页引用（本页无建表）-> 不判 E", """```sql
INSERT INTO other (a, b) VALUES (1);
```""", 0),
    ("约束行不算列 -> 通过", """```sql
CREATE TABLE t (a INT, b INT, PRIMARY KEY (a, b));
INSERT INTO t VALUES (1, 2);
```""", 0),
    ("注释里的 INSERT 不算 -> 通过", """```sql
CREATE TABLE t (a INT, b INT);
-- INSERT INTO t (a, b, c) VALUES (1);
INSERT INTO t VALUES (1, 2);
```""", 0),
    ("带 ON CONFLICT 仍判列数 -> E2", """```sql
CREATE TABLE t (a INT, b INT);
INSERT INTO t (a, b, c) VALUES (1, 2) ON CONFLICT DO NOTHING;
```""", 1),
    ("INSERT OR REPLACE 前缀仍判列数 -> E2", """```sql
CREATE TABLE t (a INT, b INT);
INSERT OR REPLACE INTO t (a, b) VALUES (1);
```""", 1),
    ("LIKE 继承列数 -> 通过", """```sql
CREATE TABLE a (x INT, y INT);
CREATE TABLE b (LIKE a INCLUDING ALL);
INSERT INTO b VALUES (1, 2);
```""", 0),
    ("教学片段（... 省略）-> 不判", """```sql
CREATE TABLE t (a INT, b INT);
INSERT INTO t (..., b, ...) VALUES (...);
```""", 0),
    ("四列五值 -> E2", """```sql
CREATE TABLE t (a INT, b INT, c INT, d INT);
INSERT INTO t (a, b, c, d) VALUES (1, 2, 3, 4, 5);
```""", 1),
]


def selftest() -> int:
    ok = 0
    for name, text, want in SELFTEST:
        d = tempfile.mkdtemp()
        p = os.path.join(d, "a.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        _, findings = scan_file(p)
        got = 1 if any(c in ("E2", "E3") for c, _, _ in findings) else 0
        flag = "ok" if got == want else "FAIL"
        if got == want:
            ok += 1
        print(f"[{flag}] {name} -> got={got} want={want}")
    print(f"selftest {ok}/{len(SELFTEST)}")
    return 0 if ok == len(SELFTEST) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="INSERT 列数与值个数一致性巡检")
    ap.add_argument("--root", nargs="*", default=["docs", "project"])
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(a.root, a.verbose)


if __name__ == "__main__":
    sys.exit(main())
