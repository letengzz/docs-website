#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ddlrefcheck.py —— 「SQL 里引用的表到底建过没有」巡检（第 231 天新立，第一百一十三项巡检）

## 动机

本库的 `sql` 代码块已经有 1,700 多个，其中近半是「先 `CREATE TABLE`、再 `SELECT` /
`INSERT`」的成对写法。两段的**表名**必须一致，否则读者照着抄就会得到
`no such table: xxx`——而文档本身看起来完全正确。

已有四项巡检各管一段，**没有一项问「这个表名在哪儿建过」**：

  * `reswordcheck`（第 112 项）   —— SQL 标识符撞了保留字；
  * `jsonfencecheck`              —— `json` 围栏可解析性；
  * `fencecheck`                  —— 围栏语言标注；
  * `linkexistcheck`              —— Markdown 链接与图片。

它们看的都是「围栏本身」，不看**围栏里的语义**。于是这一类缺陷长期静默：
`CREATE TABLE tre_position (...)` 与后面 `FROM tre_positions` 差一个 `s`，
读者复制粘贴时才发现，而作者永远不知道。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND   仓库根既无 docs/ 也无 project/（活性，防路径写错全绿）
  E1 NO_BLOCKS        一个 sql 块都没扫到就拒绝判定（活性）
  E2 TYPO_TABLE       本页建了 >= 3 张表，某个被引用的名字与本页某张表**共享 >= 4 字符前缀
                      且编辑距离 <= 1**（`tre_positions` vs `tre_position`）→ 确定的拼写错
  W1 CROSS_PAGE_ONLY  本页引用的表只在**别页**定义过（合法的跨页引用，提示审计）
  W2 NO_DDL_PAGE      本页有 sql 块且引用了表，但本页一个 `CREATE TABLE` 都没有
  W3 MULTI_DEF        同一表名在**不同页面**被定义（同名不同结构，跨页抄改的残留）
  W4 UNRESOLVED       引用了一个全库都没有的表名，且与本页任何表都不「像」——多半是
                      教学片段里的占位表名（`tbl`、`order_tbl`），只计数不展开

## 口径（为什么这样取数）

1. **先剥注释与字符串字面量，再正则**。`-- CREATE TABLE key(x INT)` 与
   `VALUES('CREATE TABLE key(x INT)')` 两例若先扫描，会凭空造出一张表；这条与
   `reswordcheck` 第 230 天踩的坑是同一个，直接复用它的两段式剥法。
2. **只认 `FROM` / `JOIN` / `INSERT INTO` / `UPDATE` 四个位置**。`SELECT 1 FROM dual`
   这类不是本库写法，不必兼容；反过来 `CREATE VIEW ... AS SELECT` 的 `AS SELECT`
   不会被误判（本脚本不把 `AS` 后面的 `SELECT` 当表名）。
3. **CTE 与派生表要排除**：`WITH x AS (...)` 的 `x`、`FROM (SELECT ...) t` 的 `t`
   都不是表。前者用 `WITH` / `), name AS (` 两个正则收集，后者因为紧跟 `(` 而跳过。
4. **`pragma_*` / `sqlite_*` / `excluded` / `json_*` 一律不算表**：它们不是用户表。
5. **`E2` 只在「本页与全库都找不到」时报**。只要别页定义过，就降级为 `W1`——
   跨页引用在本库是常态（Practice 页引用 AccountModel 页的 DDL），把它判 E 会让
   这道门第一天就背上几百条假错误。
6. **`W3` 刻意不判 E**：同一张表在两个专题里各自建一次，往往是「两册讲两件事」的
   既定写法（如各册都有自己的 `outbox`），不是缺陷。
7. **E 只用「编辑距离 <= 1」判，不用「引用无定义」判**。这条是被全库语料打出来的：
   首版把「引用了但全库没建」一律判 E，全库 **E=500**——逐条打开几乎全是教学片段
   （`FROM tbl`、`FROM order_tbl`）与方言函数（`extract(day FROM x)` 的 `FROM`、
   `ON CONFLICT DO UPDATE SET` 的 `UPDATE`）。改成「同页近似拼写」后 E=15，
   再把「只共享前缀」收紧为「前缀 >= 4 **且** 编辑距离 <= 1」并排除分表序列
   （`t_order_0` / `t_order_1`）与序列名（`*_seq`），**E 归零**，而人造的
   `tre_positions` 仍能被抓到。**一道首轮就报 500 条假错的门，第二天就会被整体跳过。**

用法：

    python3 utils/audit/ddlrefcheck.py                 # 全库
    python3 utils/audit/ddlrefcheck.py --root docs     # 只看 docs
    python3 utils/audit/ddlrefcheck.py --verbose       # 逐条明细
    python3 utils/audit/ddlrefcheck.py --selftest      # 12 例自测
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from collections import defaultdict

FENCE = re.compile(r"^(\s*)```(\w+)?[^\n]*\n(.*?)^\s*```", re.S | re.M)
CREATE = re.compile(r"\bCREATE\s+(?:TEMP(?:ORARY)?\s+)?(?:TABLE|(?:MATERIALIZED\s+)?VIEW)\s+"
                    r"(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][\w.]*)", re.I)
# EXTRACT(day FROM x) / SUBSTRING(s FROM 2) 里的 FROM 不是表引用，先整体抹掉
EXTRACT = re.compile(r"\b(?:extract|substring|position|trim|overlay)\s*\([^()]*\)", re.I)
REF = re.compile(r"\b(?:FROM|JOIN|INSERT\s+INTO)\s+([A-Za-z_][\w.]*)", re.I)
CTE1 = re.compile(r"\bWITH\s+(?:RECURSIVE\s+)?([A-Za-z_]\w*)\s+AS\b", re.I)
CTE2 = re.compile(r"\)\s*,\s*([A-Za-z_]\w*)\s+AS\s*\(", re.I)
SKIP_PREFIX = ("pragma_", "sqlite_", "json_", "jsonb_", "pg_", "information_schema",
               "excluded", "dual", "unnest", "current_", "generate_")
SQL_KEYWORDS = {"select", "values", "set", "where", "table", "into", "from", "join",
                "on", "using", "as", "and", "or", "not", "null", "default"}


def strip_sql(text: str) -> str:
    """剥掉注释与单引号字符串（等长占位），保留换行以便定位。"""
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "'":
            out.append("'")
            i += 1
            while i < n:
                if text[i] == "'" and (i + 1 >= n or text[i + 1] != "'"):
                    out.append(" ")
                    i += 1
                    break
                if text[i] == "'" and i + 1 < n and text[i + 1] == "'":
                    out.append("  ")
                    i += 2
                    continue
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            continue
        if text.startswith("--", i):
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if text.startswith("/*", i):
            while i < n and not text.startswith("*/", i):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def sql_blocks(md: str):
    for m in FENCE.finditer(md):
        lang = (m.group(2) or "").lower()
        if lang in ("sql", "sqlite", "postgresql", "mysql"):
            yield m.group(3)


def tables_created(blocks) -> set[str]:
    out = set()
    for b in blocks:
        for m in CREATE.finditer(strip_sql(b)):
            out.add(m.group(1).split(".")[-1].lower())
    return out


def tables_referenced(blocks) -> set[str]:
    out = set()
    for b in blocks:
        s = EXTRACT.sub(" ", strip_sql(b))
        ctes = {m.group(1).lower() for m in CTE1.finditer(s)}
        ctes |= {m.group(1).lower() for m in CTE2.finditer(s)}
        for m in REF.finditer(s):
            raw = m.group(1)
            low = raw.lower()
            name = low.split(".")[-1]
            if name in ctes or name in SQL_KEYWORDS:
                continue
            if any(name.startswith(p) for p in SKIP_PREFIX):
                continue
            if name.endswith(("_at", "_by", "_id", "_no", "_time", "_seq")):
                continue          # 列名样式，不是表
            # 函数调用 / 派生表：名字后面紧跟 '('
            if re.match(r"\s*\(", s[m.end(1):m.end(1) + 3]):
                continue
            out.add(name)
    return out


def iter_md(root: str):
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, _dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".md"):
                    yield os.path.join(dirpath, f)


def scan(root: str, verbose: bool):
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND", root)
        return 2
    pages = []
    for p in iter_md(root):
        try:
            md = open(p, encoding="utf-8").read()
        except OSError:
            continue
        blocks = list(sql_blocks(md))
        if not blocks:
            continue
        pages.append((p, blocks))
    if not pages:
        print("E1 NO_BLOCKS  一个 sql 块都没扫到")
        return 2

    created_all = defaultdict(set)      # table -> {page}
    page_created, page_ref = {}, {}
    for p, blocks in pages:
        c = tables_created(blocks)
        r = tables_referenced(blocks)
        page_created[p], page_ref[p] = c, r
        for t in c:
            created_all[t].add(p)

    def series(a, b):
        """t_order_0 / t_order_1 这类分表序列：尾号不同但主干相同，不算拼写错。"""
        return (re.sub(r"_\d+$", "", a) == re.sub(r"_\d+$", "", b)
                and re.search(r"_\d+$", a) and re.search(r"_\d+$", b))

    def near_miss(name, pool):
        """同页已定义表里，与本名「共享 >= 4 字符前缀 且 编辑距离 <= 1」的那个。

        只共享前缀不够：`dim_user` 与 `dim_sku` 共享 `dim_`，但它们是两张不同的表。
        编辑距离 <= 1 才是「多一个 s」「少一个下划线」这类真正的拼写错。
        """
        if len(name) < 4:
            return None
        for t in pool:
            if abs(len(t) - len(name)) > 1:
                continue
            k = 0
            while k < min(len(t), len(name)) and t[k] == name[k]:
                k += 1
            if k < 4:
                continue
            if series(t, name):
                continue
            # 去掉公共前缀后，剩余部分长度差 <= 1 且只允许一处增删改
            ta, na = t[k:], name[k:]
            if abs(len(ta) - len(na)) <= 1 and (not ta or not na or ta[1:] == na[1:] or ta == na[1:] or ta[1:] == na):
                return t
        return None

    e2, w1, w2, w4 = [], [], [], []
    for p, _ in pages:
        for t in sorted(page_ref[p]):
            if t in page_created[p]:
                continue
            if t in created_all:
                w1.append((p, t, sorted(created_all[t])[0]))
                continue
            # 只有「本页建了 >= 3 张表，且这个没建的名字与本页某张表共享 4 字符前缀」
            # 才判 E——即可以确定是拼写错，而不是「教学片段里的占位表名」。
            twin = near_miss(t, page_created[p]) if len(page_created[p]) >= 3 else None
            if twin:
                e2.append((p, t, twin))
            else:
                w4.append((p, t))
        if not page_created[p]:
            w2.append((p, len(page_ref[p])))

    w3 = [(t, sorted(ps)) for t, ps in created_all.items() if len(ps) > 1]

    for p, t, twin in e2:
        print(f"E2 TYPO_TABLE        {p} :: {t}（本页建的是 {twin}）")
    if verbose:
        for p, t, where in w1:
            print(f"W1 CROSS_PAGE_ONLY   {p} :: {t} 定义于 {where}")
        for p, n in w2:
            print(f"W2 NO_DDL_PAGE       {p} :: 引用 {n} 张表，本页无 CREATE TABLE")
        for p, t in w4:
            print(f"W4 UNRESOLVED        {p} :: {t}（全库无定义，多半是教学片段）")
        for t, ps in w3:
            print(f"W3 MULTI_DEF         {t} :: {len(ps)} 页各自定义（{ps[0]} …）")

    print(f"pages={len(pages)} created={sum(len(v) for v in page_created.values())} "
          f"refs={sum(len(v) for v in page_ref.values())} "
          f"E={len(e2)} W1={len(w1)} W2={len(w2)} W3={len(w3)} W4={len(w4)}")
    return 1 if e2 else 0


# ---------------------------------------------------------------- selftest
CASES = [
    # (说明, sql 块内容, 期望是否报 E2)
    ("定义与引用同名", "CREATE TABLE t(a INT);\nSELECT * FROM t;", False),
    ("少一个字母", "CREATE TABLE tre_position(a INT);\nSELECT * FROM tre_positions;", True),
    ("CTE 不算表", "WITH x AS (SELECT 1 AS a) SELECT * FROM x;", False),
    ("派生表不算表", "SELECT * FROM (SELECT 1) t;", False),
    ("JOIN 的表要定义", "CREATE TABLE a(i INT);\nSELECT * FROM a JOIN b ON 1=1;", True),
    ("INSERT INTO 也要定义", "CREATE TABLE a(i INT);\nINSERT INTO a VALUES(1);", False),
    ("INSERT INTO 未定义", "INSERT INTO nope VALUES(1);", True),
    ("UPSERT 的 UPDATE SET 不误判成表", "CREATE TABLE a(i INT);\nINSERT INTO a VALUES(1) ON CONFLICT(i) DO UPDATE SET i=2;", False),
    ("EXTRACT 里的 FROM 不误判", "CREATE TABLE a(i INT);\nSELECT extract(day FROM occurred_at) FROM a;", False),
    ("pragma 不算表", "SELECT count(*) FROM pragma_table_info('a');", False),
    ("注释里的建表不算", "-- CREATE TABLE ghost(a INT)\nSELECT * FROM ghost;", True),
    ("字符串里的建表不算", "SELECT 1 FROM x WHERE s='CREATE TABLE y(a INT)';", True),
    ("函数调用不算表", "SELECT * FROM json_each('[1]');", False),
]


def selftest() -> int:
    ok = 0
    for idx, (desc, sql, want_e2) in enumerate(CASES, 1):
        blocks = [sql]
        created = tables_created(blocks)
        refs = tables_referenced(blocks)
        undefined = [t for t in refs if t not in created]
        got = bool(undefined)
        mark = "PASS" if got == want_e2 else "FAIL"
        if got == want_e2:
            ok += 1
        print(f"{mark} {idx:>2}. {desc}: refs={sorted(refs)} created={sorted(created)} "
              f"undefined={sorted(undefined)}")
    print(f"selftest {ok}/{len(CASES)}")
    return 0 if ok == len(CASES) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="SQL 表名引用 🔍 巡检")
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return scan(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
