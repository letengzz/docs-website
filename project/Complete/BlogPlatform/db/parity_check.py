#!/usr/bin/env python3
"""全栈博客平台：MySQL 与 PostgreSQL 双方言 DDL 的结构一致性门禁（零第三方依赖）。

用法：
    python db/parity_check.py            # 校验 db/mysql 与 db/postgres 全部脚本
    python db/parity_check.py --verbose  # 输出每张表的比对明细
退出码：0 一致；1 不一致或解析失败。

与基座模板 db/parity_check.py 同源，差异两处：
1. 归一化表补充 MEDIUMTEXT/TEXT → text（博客正文列）；
2. 全文检索索引按「名称对齐、列形态豁免」处理——MySQL 的
   FULLTEXT ... WITH PARSER ngram 与 PG 的 GIN + to_tsvector 索引列
   形态天然不同，只要求索引在两侧同名存在（SEARCH_INDEXES 注册表）。
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# 方言类型归一化：两侧最终必须落到同一个逻辑类型
NORMALIZE = {
    "BIGINT": "bigint",
    "INT": "integer",
    "INTEGER": "integer",
    "TINYINT": "smallint",
    "SMALLINT": "smallint",
    "MEDIUMTEXT": "text",
    "TEXT": "text",
    "DATETIME": "timestamp",
    "TIMESTAMP": "timestamp",
}

# 全文检索索引：MySQL FULLTEXT(ngram) 与 PG GIN(to_tsvector) 列形态不同，
# 只要求两侧同名存在，列清单不参与比对。
SEARCH_INDEXES = {"ft_posts_search"}


@dataclass
class Column:
    name: str
    raw_type: str
    nullable: bool = True

    @property
    def norm_type(self) -> str:
        t = re.sub(r"\s+", " ", self.raw_type.upper().strip())
        if t in NORMALIZE:
            return NORMALIZE[t]
        m = re.match(r"^(VARCHAR|CHAR)\((\d+)\)$", t)
        if m:
            return f"varchar({m.group(2)})"
        m = re.match(r"^(DATETIME|TIMESTAMP)(\(\d+\))?$", t)
        if m:
            return "timestamp"
        return t


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    primary_key: list[str] = field(default_factory=list)
    uniques: list[tuple[str, list[str]]] = field(default_factory=list)
    indexes: list[tuple[str, list[str]]] = field(default_factory=list)
    search_indexes: list[str] = field(default_factory=list)
    has_comment: bool = False


def strip_comments(sql: str) -> tuple[str, list[str]]:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    strings: list[str] = []

    def _stash(m: re.Match) -> str:
        strings.append(m.group(0))
        return f"\x00{len(strings) - 1}\x00"

    sql = re.sub(r"'(?:[^']|'')*'", _stash, sql)
    return sql, strings


def parse_ddl(path: Path) -> dict[str, Table]:
    raw = path.read_text(encoding="utf-8")
    sql, _ = strip_comments(raw)
    tables: dict[str, Table] = {}

    for m in re.finditer(r"CREATE\s+TABLE\s+(\w+)\s*\(", sql, flags=re.S | re.I):
        name = m.group(1).lower()
        depth, i = 1, m.end()
        while i < len(sql) and depth:
            if sql[i] == "(":
                depth += 1
            elif sql[i] == ")":
                depth -= 1
            i += 1
        if depth:
            raise ValueError(f"{path.name}: 表 {name} 括号不配平")
        body = sql[m.end(): i - 1]
        tail = sql[i: i + 2000]
        tbl = Table(name=name)
        tbl.has_comment = bool(re.search(r"COMMENT", tail, re.I))

        for item in _split_top(body):
            head = item.strip().split(None, 1)
            if not head:
                continue
            kw = head[0].upper()
            if kw in ("PRIMARY", "UNIQUE", "CONSTRAINT", "KEY", "INDEX", "FULLTEXT"):
                _parse_constraint(item, tbl)
            else:
                _parse_column(item, tbl)
        tables[name] = tbl

    # 表外 CREATE INDEX：普通索引进 indexes，GIN 索引进 search_indexes
    for m in re.finditer(
        r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)\s+ON\s+(\w+)\s*(?:USING\s+\w+\s*)?\((.*?)\)\s*;",
        sql, flags=re.S | re.I,
    ):
        idx_name, tbl_name, cols = m.group(1), m.group(2).lower(), m.group(3)
        if tbl_name not in tables:
            continue
        if idx_name.lower() in SEARCH_INDEXES or "to_tsvector" in cols.lower():
            tables[tbl_name].search_indexes.append(idx_name.lower())
        else:
            tables[tbl_name].indexes.append((idx_name.lower(), _cols(cols)))
    return tables


def _split_top(body: str) -> list[str]:
    depth, cur, out = 0, [], []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


def _cols(s: str) -> list[str]:
    return [c.strip().strip("'\"").lower() for c in s.split(",") if c.strip()]


def _parse_column(item: str, tbl: Table) -> None:
    toks = item.strip().split()
    if len(toks) < 2:
        return
    cname, ctype = toks[0].strip("`\"").lower(), toks[1]
    if "(" in ctype and ")" not in ctype:
        rest = item.strip().split(None, 1)[1]
        ctype = rest[: rest.index(")") + 1]
    tbl.columns.append(Column(name=cname, raw_type=ctype,
                              nullable="NOT NULL" not in item.upper()))


def _parse_constraint(item: str, tbl: Table) -> None:
    up = item.upper()
    m = re.search(r"PRIMARY\s+KEY\s*\((.*?)\)", item, re.I | re.S)
    if m:
        tbl.primary_key = _cols(m.group(1))
        return
    if re.search(r"\bUNIQUE\b", up):
        m2 = re.search(r"UNIQUE\s+(?:KEY|INDEX)\s+(\w+)\s*\((.*?)\)", item, re.I | re.S)
        if m2:
            tbl.uniques.append((m2.group(1).lower(), _cols(m2.group(2))))
        else:
            m3 = re.search(r"CONSTRAINT\s+(\w+)\s+UNIQUE\s*\((.*?)\)", item, re.I | re.S)
            if m3:
                tbl.uniques.append((m3.group(1).lower(), _cols(m3.group(2))))
        return
    if re.search(r"\bFULLTEXT\b", up):
        m4 = re.search(r"FULLTEXT\s+(?:KEY|INDEX)\s+(\w+)", item, re.I | re.S)
        if m4:
            tbl.search_indexes.append(m4.group(1).lower())
        return
    m = re.search(r"\b(?:KEY|INDEX)\s+(\w+)\s*\((.*?)\)", item, re.I | re.S)
    if m:
        tbl.indexes.append((m.group(1).lower(), _cols(m.group(2))))


def compare(mysql: dict[str, Table], postgres: dict[str, Table]) -> list[str]:
    problems: list[str] = []
    for side, a, b in (("MySQL", mysql, postgres), ("PostgreSQL", postgres, mysql)):
        for name in a:
            if name not in b:
                problems.append(f"[{side}] 表 {name} 在对方言中缺失")
    for name in sorted(set(mysql) & set(postgres)):
        ta, tb = mysql[name], postgres[name]
        ca = {c.name: c for c in ta.columns}
        cb = {c.name: c for c in tb.columns}
        for c in ca:
            if c not in cb:
                problems.append(f"[{name}] 列 {c} 在 PostgreSQL 版缺失")
        for c in cb:
            if c not in ca:
                problems.append(f"[{name}] 列 {c} 在 MySQL 版缺失")
        for c in sorted(set(ca) & set(cb)):
            if ca[c].norm_type != cb[c].norm_type:
                problems.append(
                    f"[{name}] 列 {c} 类型不一致：MySQL {ca[c].raw_type} "
                    f"({ca[c].norm_type}) vs PostgreSQL {cb[c].raw_type} ({cb[c].norm_type})")
            if ca[c].nullable != cb[c].nullable:
                problems.append(f"[{name}] 列 {c} 可空性不一致")
        if sorted(ta.primary_key) != sorted(tb.primary_key):
            problems.append(f"[{name}] 主键不一致：{ta.primary_key} vs {tb.primary_key}")
        ua = sorted(ta.uniques, key=lambda x: x[0])
        ub = sorted(tb.uniques, key=lambda x: x[0])
        if [u[1] for u in ua] != [u[1] for u in ub]:
            problems.append(f"[{name}] 唯一约束不一致：{ua} vs {ub}")
        ia = sorted(ta.indexes, key=lambda x: x[0])
        ib = sorted(tb.indexes, key=lambda x: x[0])
        if [i[1] for i in ia] != [i[1] for i in ib]:
            problems.append(f"[{name}] 普通索引不一致：{ia} vs {ib}")
        sa, sb = sorted(ta.search_indexes), sorted(tb.search_indexes)
        if sa != sb:
            problems.append(f"[{name}] 全文检索索引不一致：{sa} vs {sb}")
        if not (ta.has_comment and tb.has_comment):
            problems.append(f"[{name}] 双方都必须有表注释（COMMENT / COMMENT ON）")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent),
                    help="包含 mysql/ 与 postgres/ 子目录的根（默认：脚本所在目录）")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    mysql_sql = sorted((root / "mysql").glob("*.sql"))
    pg_sql = sorted((root / "postgres").glob("*.sql"))
    if not mysql_sql or not pg_sql:
        print("FAIL: 未找到双方言 SQL 脚本（mysql/ 与 postgres/）")
        return 1

    tables: dict[str, dict[str, Table]] = {}
    problems: list[str] = []
    try:
        for label, files in (("MySQL", mysql_sql), ("PostgreSQL", pg_sql)):
            merged: dict[str, Table] = {}
            for f in files:
                merged |= parse_ddl(f)
            tables[label] = merged
    except ValueError as e:
        print("FAIL:", e)
        return 1
    problems += compare(tables["MySQL"], tables["PostgreSQL"])

    names_a = {p.name for p in mysql_sql}
    names_b = {p.name for p in pg_sql}
    if names_a != names_b:
        problems.append(f"脚本清单不一致：MySQL {sorted(names_a)} vs PostgreSQL {sorted(names_b)}")

    if args.verbose:
        for tname, t in sorted(tables["MySQL"].items()):
            print(f"表 {tname}: {len(t.columns)} 列, 主键 {t.primary_key}, "
                  f"唯一 {[(u[0], u[1]) for u in t.uniques]}, "
                  f"索引 {[(i[0], i[1]) for i in t.indexes]}, 全文 {t.search_indexes}")
    if problems:
        for p in problems:
            print("FAIL:", p)
        return 1
    n = len(tables["MySQL"])
    cols = sum(len(t.columns) for t in tables["MySQL"].values())
    print(f"OK: {n} 张表 / {cols} 列 双方言结构一致（类型已归一化比对，全文索引按名称对齐）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
