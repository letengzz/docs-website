#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""保留字标识符巡检（SQL 代码块）。

立这一项的原因：本库有大量 `sql` 代码块，而「把保留字当列名」是一种
**写得出来、读得过去、跑起来才炸**的缺陷——典型如 `contract_modification.distinct`，
在 SQLite 里直接语法错误。文档里的 SQL 无法逐条执行，只能靠词法巡检兜住。

判据：
  E0 ROOT_NOT_FOUND   根目录不存在
  E1 NO_BLOCKS        一个 `sql` 代码块都没扫到（活性：拒绝在空样本上给全绿）
  E2 KEYWORD_IDENT    硬保留字被直接当作表名 / 列名（无引号，SQLite 直接语法错误）
  W1 PORTABILITY      软保留字被当作标识符：SQLite 能跑，MySQL / PostgreSQL 会报错
  W3 QUOTED_KEYWORD   保留字被反引号/双引号包裹：合法，但方言迁移时会出问题

用法：
  python3 utils/audit/reswordcheck.py [根目录 ...]
  python3 utils/audit/reswordcheck.py --selftest
"""
import argparse
import os
import re
import sys
import tempfile

DEFAULT_ROOTS = ["docs", "project"]

# 两级口径：HARD 是 SQLite 解析器真正不接受的保留字（无引号即语法错误）；
# SOFT 是 SQLite 里能当标识符用、但 MySQL / PostgreSQL 会报错的词（可移植性风险）。
HARD = {
    "add", "all", "alter", "and", "as", "autoincrement", "between", "case", "check", "collate",
    "commit", "constraint", "create", "default", "deferrable", "delete", "distinct", "drop",
    "else", "escape", "except", "exists", "foreign", "from", "group", "having", "in", "index",
    "insert", "intersect", "into", "is", "isnull", "join", "limit", "not", "notnull", "null",
    "on", "or", "order", "primary", "references", "select", "set", "table", "then", "to",
    "transaction", "union", "unique", "update", "using", "values", "when", "where",
}
SOFT = {
    "abort", "action", "after", "always", "analyze", "attach", "before", "begin", "by",
    "cascade", "cast", "column", "conflict", "cross", "current", "current_date", "current_time",
    "current_timestamp", "current_user", "database", "deferred", "desc", "detach", "do", "each",
    "end", "exclude", "exclusive", "explain", "fail", "filter", "first", "following", "for",
    "full", "generated", "glob", "groups", "if", "ignore", "immediate", "indexed", "initially",
    "inner", "instead", "key", "last", "left", "like", "match", "materialized", "natural", "no",
    "nothing", "nulls", "of", "offset", "others", "outer", "over", "partition", "plan", "pragma",
    "preceding", "query", "raise", "range", "recursive", "regexp", "reindex", "release", "rename",
    "replace", "restrict", "returning", "right", "rollback", "row", "rows", "savepoint", "temp",
    "temporary", "ties", "trigger", "unbounded", "view", "virtual", "window", "with", "without",
}
KEYWORDS = HARD | SOFT

TYPES = (r"text|integer|int|int2|int8|bigint|smallint|numeric|decimal|real|double precision|"
         r"float|varchar|varchar2|char|nvarchar|date|datetime|timestamp|timestamptz|time|"
         r"boolean|bool|json|jsonb|blob|bytea|uuid|serial|bigserial")

FENCE_RE = re.compile(r"^\s*```+\s*([A-Za-z0-9_+-]*)")
SQL_LANGS = {"sql", "sqlite", "postgres", "postgresql", "mysql", "tsql", "plsql"}

LINE_COMMENT = re.compile(r"--[^\n]*")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
STR_LIT = re.compile(r"'(?:''|[^'])*'")


def strip_noise(sql):
    """去掉注释与字符串字面量，避免把注释里的词当成代码。"""
    sql = BLOCK_COMMENT.sub(" ", sql)
    sql = LINE_COMMENT.sub(" ", sql)
    sql = STR_LIT.sub("''", sql)
    return sql


def iter_sql_blocks(text):
    """逐个产出 (起始行号, 代码内容)。"""
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if m and m.group(1).lower() in SQL_LANGS:
            lang = m.group(1).lower()
            start = i + 1
            buf = []
            i += 1
            while i < len(lines) and not FENCE_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            out.append((lang, start, "\n".join(buf)))
        else:
            i += 1
    return out


COL_DEF = re.compile(r"(?:\(\s*,?|,\s*|^\s*)\s*([A-Za-z_][A-Za-z_0-9]*)\s+(?:" + TYPES + r")\b",
                     re.I | re.M)
CREATE_TABLE = re.compile(r"create\s+(?:temp\s+|temporary\s+)?table\s+(?:if\s+not\s+exists\s+)?"
                          r"([A-Za-z_][A-Za-z_0-9]*)", re.I)
INSERT_COLS = re.compile(r"insert\s+(?:or\s+\w+\s+)?into\s+[\w.\[\]\"]+\s*\(([^()]*)\)", re.I)
AS_ALIAS = re.compile(r"\bas\s+([A-Za-z_][A-Za-z_0-9]*)\b", re.I)
QUOTED = re.compile(r"[`\"]([A-Za-z_][A-Za-z_0-9]*)[`\"]")


def scan_sql(sql):
    """返回 (e2 列表, w1 列表, w2 列表)，每项是 (词, 上下文行)。"""
    clean = strip_noise(sql)
    e2, w1, w2 = [], [], []

    for m in CREATE_TABLE.finditer(clean):
        word = m.group(1)
        if word.lower() in HARD:
            e2.append((word, m.group(0).strip()))
        elif word.lower() in SOFT:
            w1.append((word, m.group(0).strip()))

    # 只对 CREATE TABLE 段落做列名判定：从 create table 到其后的第一处行尾分号
    for m in re.finditer(r"create\s+(?:temp\s+|temporary\s+)?table\b.*?;", clean, re.I | re.S):
        seg = m.group(0)
        for cm in COL_DEF.finditer(seg):
            word = cm.group(1)
            if word.lower() in HARD:
                e2.append((word, cm.group(0).strip()[:40]))
            elif word.lower() in SOFT:
                w1.append((word, cm.group(0).strip()[:40]))

    for m in INSERT_COLS.finditer(clean):
        for item in m.group(1).split(","):
            name = item.strip().split()[0] if item.strip() else ""
            name = name.strip("`\"[]")
            if not name or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name):
                continue
            if name.lower() in HARD:
                e2.append((name, "INSERT 列清单"))
            elif name.lower() in SOFT:
                w1.append((name, "INSERT 列清单"))

    # `CREATE VIEW v AS SELECT ...` / `WITH x AS (...)` 不是别名，先排除语句起始词
    STMT_STARTERS = {"select", "with", "values", "table", "insert", "update", "delete"}
    for m in AS_ALIAS.finditer(clean):
        word = m.group(1)
        if word.lower() in KEYWORDS and word.lower() not in STMT_STARTERS:
            w2.append((word, "AS " + word))

    for m in QUOTED.finditer(sql):
        word = m.group(1)
        if word.lower() in KEYWORDS:
            w2.append((word, m.group(0)))

    return e2, w1, w2


def walk(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in {"node_modules", ".vitepress", "assets"}]
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def run(roots, quiet=False):
    if not all(os.path.isdir(r) for r in roots):
        print("E0 ROOT_NOT_FOUND  %s" % ", ".join(r for r in roots if not os.path.isdir(r)))
        return 2
    pages = blocks = 0
    e2 = w1 = w2 = 0
    rows = []
    for path in walk(roots):
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        found = iter_sql_blocks(text)
        if not found:
            continue
        pages += 1
        for _lang, start, sql in found:
            blocks += 1
            a, b, c = scan_sql(sql)
            for word, ctx in a:
                e2 += 1
                rows.append(("E2 KEYWORD_IDENT", path, start, "%s :: %s" % (word, ctx)))
            for word, ctx in b:
                w1 += 1
                rows.append(("W1 PORTABILITY", path, start, "%s :: %s" % (word, ctx)))
            for word, ctx in c:
                w2 += 1
                rows.append(("W3 QUOTED_KEYWORD", path, start, "%s :: %s" % (word, ctx)))

    if blocks == 0:
        print("E1 NO_BLOCKS  扫到 0 个 sql 代码块，拒绝给全绿")
        return 2
    if not quiet:
        for row in rows:
            print("%-18s %s:%d  %s" % row)
    print()
    print("pages=%d blocks=%d E=%d W1=%d W2=%d" % (pages, blocks, e2, w1, w2))
    return 1 if e2 else 0


# ---------------------------------------------------------------- selftest
CASES = [
    ("clean", "```sql\nCREATE TABLE t(id INTEGER PRIMARY KEY, name TEXT);\n```", (0, 0, 0)),
    ("distinct-col", "```sql\nCREATE TABLE t(distinct INTEGER);\n```", (1, 0, 0)),
    ("order-col", "```sql\nCREATE TABLE t(id INTEGER, order NUMERIC);\n```", (1, 0, 0)),
    ("table-hard", "```sql\nCREATE TABLE order(id INTEGER);\n```", (1, 0, 0)),
    ("table-soft", "```sql\nCREATE TABLE key(id INTEGER);\n```", (0, 1, 0)),
    ("insert-distinct", "```sql\nINSERT INTO t(id, distinct) VALUES(1,2);\n```", (1, 0, 0)),
    ("insert-clean", "```sql\nINSERT INTO t(id, is_distinct) VALUES(1,2);\n```", (0, 0, 0)),
    ("alias-key", "```sql\nSELECT a AS key FROM t;\n```", (0, 0, 1)),
    ("quoted", "```sql\nSELECT `order` FROM t;\n```", (0, 0, 1)),
    ("view-as-select", "```sql\nCREATE VIEW v AS SELECT 1;\n```", (0, 0, 0)),
    ("soft-col", "```sql\nCREATE TABLE t(action TEXT);\n```", (0, 1, 0)),
    ("comment-ignored", "```sql\n-- CREATE TABLE order(a INT);\nSELECT 1;\n```", (0, 0, 0)),
    ("string-ignored", "```sql\nINSERT INTO t(note) VALUES('CREATE TABLE key(x INT)');\n```", (0, 0, 0)),
    ("non-sql-fence", "```python\nCREATE TABLE order(a INT)\n```", (0, 0, 0)),
    ("type-word-ok", "```sql\nCREATE TABLE t(text TEXT, status TEXT);\n```", (0, 0, 0)),
    ("cte-ok", "```sql\nWITH x AS (SELECT 1) SELECT * FROM x;\n```", (0, 0, 0)),
    ("multi-col", "```sql\nCREATE TABLE t(\n  id INTEGER,\n  index TEXT\n);\n```", (1, 0, 0)),
]


def selftest():
    ok = 0
    total = len(CASES)
    tmp = tempfile.mkdtemp(prefix="resword-")
    for i, (name, body, want) in enumerate(CASES):
        d = os.path.join(tmp, "c%02d" % i)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.md"), "w", encoding="utf-8").write("# t\n\n" + body + "\n")
        pages = blocks = 0
        got = [0, 0, 0]
        for path in walk([d]):
            text = open(path, encoding="utf-8").read()
            for _l, _s, sql in iter_sql_blocks(text):
                blocks += 1
                a, b, c = scan_sql(sql)
                got[0] += len(a); got[1] += len(b); got[2] += len(c)
        good = tuple(got) == want
        ok += 1 if good else 0
        print("%-16s %s  期望 %s 实得 %s" % (name, "PASS" if good else "FAIL", want, tuple(got)))
    # 活性判据
    empty = os.path.join(tmp, "empty")
    os.makedirs(empty, exist_ok=True)
    open(os.path.join(empty, "index.md"), "w", encoding="utf-8").write("# 没有 sql 块\n\n普通文字。\n")
    n = sum(1 for _ in walk([empty]))
    alive = 0
    for path in walk([empty]):
        alive += len(iter_sql_blocks(open(path, encoding="utf-8").read()))
    good = (n == 1 and alive == 0)
    ok += 1 if good else 0
    print("%-16s %s  空样本应扫到 0 个块（E1 活性）" % ("no-blocks", "PASS" if good else "FAIL"))
    total += 1
    print("\nselftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SQL 代码块中的保留字标识符巡检")
    ap.add_argument("roots", nargs="*", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    sys.exit(run(args.roots or DEFAULT_ROOTS, args.quiet))
