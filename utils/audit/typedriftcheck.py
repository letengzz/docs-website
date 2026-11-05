#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""typedriftcheck.py —— 「同一列是什么类型」跨页漂移巡检（第 257 天新立，第一百三十九项巡检）

## 动机

第 138 项 `enumdriftcheck` 管住了「同一列允许哪些**值**」，但同一个 `CREATE TABLE` 里的
**列类型**仍然是自由发挥的：同一张 `order` 表的 `total_amount`，建模页写 `numeric(12,2)`、
迁移页写 `numeric(10,2)`、实战页写 `decimal(12,2)`。三种写法在 SQL 里都能跑，于是
「照着最后一份 DDL 建库」的人会得到一个精度不同的库——而金额列少两位，是**上线三个月后
对账时才炸**的那类缺陷。

既有巡检各管一段，**没有一项在读列类型**：

  * `ddlrefcheck`（第 113 项）—— 「SQL 里引用的表建过没有」，比的是表名与整块 DDL 文本；
  * `insertaritycheck` —— `INSERT` 的列数与 `CREATE TABLE` 对不对得上；
  * `enumdriftcheck`（第 138 项）—— 列的**取值集合**；
  * `unitmixcheck` —— 量纲（元 / 分）混用，但它读的是正文散文，不读 DDL 类型；
  * `tablesumcheck` / `judgesumcheck` —— 全在数「条数」。

「同一列两套类型」这一维度因此长期只有人工评审在守。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND      仓库根既无 docs/ 也无 project/（活性，防路径写错全绿）
  E1 NO_COLUMNS          一个 `CREATE TABLE` 列定义都没解析到就拒绝判定（活性）
  E2 TYPE_CONFLICT       **同一页**内同一个 `表.列` 出现两种**归一后仍不同**的类型
                         —— 一页之内自相矛盾，一定是改了一半，无反例可辩
  W1 CROSS_PAGE_DRIFT    **跨页**同一 `表.列` 的类型归一后仍不同
  W2 EQUIV_SPELLING      归一**前**不同、归一**后**相同（`decimal` / `numeric`、
                         `timestamp` / `timestamp without time zone`）
                         —— 不是缺陷，是「库内有两种写法」的线索

## 为什么跨页差异只报 `W`

与第 138 项同一条纪律（也是本仓其他门禁反复验证过的）：**会误报的门禁很快会被整体跳过**。
跨页类型不同有两类完全正当的成因——① 实战页为了让例子可跑，把 `numeric` 换成 `real`；
② 大版本目录各自演进（`MySQL57` 用 `datetime`、`MySQL84` 用 `timestamp`）。
机器分不开这两类与「抄改残留」。而**同一页两套互不相容**没有任何正当解释，所以它是唯一的 E。

`E2` 的粒度定在**同一主题目录**内（路径前三段）：跨主题同名表（各专题各建一份 `orders`）
是合法的，放到全库级立刻变成误报源。

## 口径

  * 只解析 `sql` 围栏；`text` / `markdown` 围栏里的 DDL 示例不算；
  * `CREATE TABLE` 的列定义按**括号配平**切块，块内再按**顶层逗号**切列
    （`numeric(12,2)` 里的逗号不是列分隔符——这是首版最容易写错的地方）；
  * 表约束行（`primary key (…)` / `unique (…)` / `foreign key …` / `check (…)` /
    `constraint …`）不是列，跳过；
  * 列名与表名统一小写、去掉反引号与双引号；
  * 类型只取「类型部分」，截断在 `not null` / `default` / `primary` / `unique` /
    `references` / `check` / `generated` / `collate` 这些关键字之前；
  * 类型归一：去空格、别名映射（`int` → `integer`、`decimal` → `numeric`、
    `varchar` → `character varying`、`int8` → `bigint`、`bool` → `boolean`、
    `float8` → `double precision`、`timestamptz` 与 `timestamp with time zone` 统一）、
    精度参数内的空格去掉（`numeric(12, 2)` → `numeric(12,2)`）；
  * `alter table … add [column] col type` 也收——它对同一张表是同一份契约的一部分。

## 用法

  python typedriftcheck.py                  # 扫默认仓库根
  python typedriftcheck.py D:/docs-website  # 指定扫描根
  python typedriftcheck.py --selftest       # 夹具自测（12 条，断言「失败项集合恰好等于期望」）
"""
import os
import re
import sys
import tempfile

DEFAULT_ROOT = r"D:\docs-website"
SKIP_DIRS = {"node_modules", ".git", ".vitepress", "dist", "assets", "public", "utils"}

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`]*)")
CREATE_RE = re.compile(
    r"create\s+table\s+(?:if\s+not\s+exists\s+)?[`\"]?([\w.]+)[`\"]?\s*\(", re.I)
ALTER_RE = re.compile(
    r"alter\s+table\s+(?:if\s+exists\s+)?[`\"]?([\w.]+)[`\"]?\s+add\s+(?:column\s+)?"
    r"[`\"]?(\w+)[`\"]?\s+([^\n;]+)", re.I)

CONSTRAINT_PREFIX = ("primary key", "unique", "foreign key", "check", "constraint",
                     "exclude", "like", "index", "key ")
# `alter table … add <这些词>` 加的不是列（ClickHouse 的 ADD INDEX、PG 的 ADD CONSTRAINT 都在此列）
NON_COLUMN_ADD = {
    "add", "column", "constraint", "index", "primary", "foreign", "unique", "check",
    "partition", "projection", "skip", "setting", "settings", "materialize", "key",
    "default", "modify", "drop", "rename", "alter", "comment", "owner", "enable", "disable",
}
TYPE_STOP = ("not null", "null,", "null)", " default", " primary", " unique",
             " references", " check", " generated", " collate", " identity")

ALIAS = {
    "int": "integer", "int4": "integer", "serial4": "integer",
    "int8": "bigint", "int2": "smallint",
    "decimal": "numeric", "float8": "double precision", "float4": "real",
    "bool": "boolean",
    "varchar": "character varying", "nvarchar": "character varying",
    "char": "character", "bpchar": "character",
    "timestamptz": "timestamp with time zone",
    "timestamp without time zone": "timestamp",
    "timestamp with time zone": "timestamptz",
}


def strip_type(raw):
    """从列定义的后半截里取出「类型部分」。"""
    t = " " + raw.strip().lower() + " "
    t = re.sub(r"\s+", " ", t)
    cut = len(t)
    for kw in TYPE_STOP:
        i = t.find(kw)
        if i != -1:
            cut = min(cut, i)
    t = t[:cut].strip()
    t = t.replace("( ", "(").replace(" )", ")")
    t = re.sub(r"\s*,\s*", ",", t)
    return t


def norm_type(t):
    """归一化：别名映射（含带精度的类型）+ 去多余空格。返回归一后的字符串。"""
    if not t:
        return ""
    tt = re.sub(r"\s+", " ", t.strip().lower())
    m = re.match(r"^([a-z][a-z ]*?)\s*(\((.*)\))?$", tt)
    if m:
        base = m.group(1).strip()
        args = m.group(3)
        base = ALIAS.get(base, base)
        return f"{base}({args})" if args else base
    return ALIAS.get(tt, tt)


def split_top_level(body):
    """按顶层逗号切块（括号内的逗号不算）。"""
    out, depth, cur = [], 0, []
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
    if "".join(cur).strip():
        out.append("".join(cur))
    return out


def matching_paren(text, start):
    """从 text[start] == '(' 开始找配对的 ')'，返回索引（找不到返回 len-1）。"""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def body_sql_blocks(lines):
    """返回 [(起始行号, 行列表)]，只保留 sql 围栏。"""
    out, cur, lang, start = [], None, None, 0
    for i, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if m:
            if cur is None:
                cur, lang, start = [], m.group(2).lower(), i + 1
            else:
                if lang == "sql" and cur:
                    out.append((start, cur))
                cur, lang = None, None
            continue
        if cur is not None:
            cur.append(line)
    if cur is not None and lang == "sql" and cur:
        out.append((start, cur))
    return out


def parse_columns(sql_lines):
    """从一个 sql 块里抽出 [(相对行号, 表名, 列名, 类型原文)]。"""
    joined = "\n".join(sql_lines)
    found = []

    for m in CREATE_RE.finditer(joined):
        table = m.group(1).lower()
        open_idx = joined.index("(", m.end() - 1)
        close_idx = matching_paren(joined, open_idx)
        body = joined[open_idx + 1:close_idx]
        base_line = joined[:open_idx].count("\n")
        offset = 0
        for part in split_top_level(body):
            line_no = base_line + body[:offset].count("\n") if offset else base_line
            offset += len(part) + 1
            seg = part.strip()
            if not seg:
                continue
            low = seg.lower()
            if any(low.startswith(p) for p in CONSTRAINT_PREFIX):
                continue
            mm = re.match(r'[`"\[]?(\w+)[`"\]]?\s+(.+)$', seg, re.S)
            if not mm:
                continue
            col = mm.group(1).lower()
            typ = strip_type(mm.group(2))
            if not typ:
                continue
            found.append((line_no, table, col, typ))

    for m in ALTER_RE.finditer(joined):
        table = m.group(1).lower()
        col = m.group(2).lower()
        rest = split_top_level(m.group(3))
        typ = strip_type(rest[0]) if rest else ""
        if typ and col not in NON_COLUMN_ADD:
            line_no = joined[:m.start()].count("\n")
            found.append((line_no, table, col, typ))
    return found


def topic_of(rel):
    return "/".join(rel.replace("\\", "/").split("/")[:3])


def scan(root):
    cols, files = [], 0
    if not (os.path.isdir(os.path.join(root, "docs")) or
            os.path.isdir(os.path.join(root, "project"))):
        return None, 0
    for base in ("docs", "project"):
        bpath = os.path.join(root, base)
        if not os.path.isdir(bpath):
            continue
        for dirpath, dirnames, filenames in os.walk(bpath):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fn in sorted(filenames):
                if not fn.endswith(".md"):
                    continue
                files += 1
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace("\\", "/")
                try:
                    with open(full, encoding="utf-8", errors="replace") as f:
                        lines = f.read().splitlines()
                except OSError:
                    continue
                for start, blk in body_sql_blocks(lines):
                    for rel_line, table, col, typ in parse_columns(blk):
                        cols.append({
                            "rel": rel, "topic": topic_of(rel), "line": start + rel_line,
                            "table": table, "col": col, "type": typ,
                            "norm": norm_type(typ),
                        })
    return cols, files


def check(root):
    """返回 (errs, warns, files, ncols)。errs/warns 元素为 (code, name, where, line, detail)。"""
    cols, files = scan(root)
    if cols is None:
        return [("E0", "ROOT_NOT_FOUND", root, 0, "")], [], 0, 0
    if not cols:
        return [("E1", "NO_COLUMNS", "", 0, f"files={files}")], [], files, 0

    errs, warns = [], []
    groups = {}
    for c in cols:
        groups.setdefault((c["topic"], c["table"], c["col"]), []).append(c)

    for (topic, table, col), items in sorted(groups.items()):
        pages = {c["rel"] for c in items}
        norms = {c["norm"] for c in items}
        raws = {c["type"] for c in items}

        def detail(cs):
            return " / ".join(f"{c['rel']}:{c['line']} = {c['type']}" for c in cs[:4])

        if len(norms) > 1 and len(pages) == 1:
            one = sorted(pages)[0]
            errs.append(("E2", "TYPE_CONFLICT", f"{one} · {table}.{col}", 0, detail(items)))
        elif len(norms) > 1:
            warns.append(("W1", "CROSS_PAGE_DRIFT", f"{topic} · {table}.{col}", 0, detail(items)))
        elif len(raws) > 1:
            warns.append(("W2", "EQUIV_SPELLING", f"{topic} · {table}.{col}", 0, detail(items)))
    return errs, warns, files, len(cols)


# ------------------------------------------------------------------ 自测

CASES = [
    # (目录名, {相对路径: 内容}, 期望失败集合)
    ("c01_clean", {"a.md": "```sql\ncreate table t (id integer primary key, name text not null);\n```\n"}, set()),
    ("c02_same_page_conflict",
     {"a.md": "```sql\ncreate table t (amount numeric(12,2));\ncreate table u (id int);\n"
              "alter table t add amount decimal(10,2);\n```\n"}, {"E2"}),
    ("c03_cross_page",
     {"a.md": "```sql\ncreate table t (amount numeric(12,2));\n```\n",
      "b.md": "```sql\ncreate table t (amount numeric(10,2));\n```\n"}, {"W1"}),
    ("c04_equiv_spelling",
     {"a.md": "```sql\ncreate table t (amount numeric(12,2));\n```\n",
      "b.md": "```sql\ncreate table t (amount decimal(12, 2));\n```\n"}, {"W2"}),
    ("c05_diff_tables",
     {"a.md": "```sql\ncreate table t (amount numeric(12,2));\n"
              "create table u (amount integer);\n```\n"}, set()),
    ("c06_cross_topic",
     {"docs/Backend/Ta/a.md": "```sql\ncreate table t (amount numeric(12,2));\n```\n",
      "docs/Backend/Tb/b.md": "```sql\ncreate table t (amount bigint);\n```\n"}, set()),
    ("c07_non_sql_fence",
     {"a.md": "```text\ncreate table t (amount numeric(12,2));\n```\n"}, {"E1"}),
    ("c08_table_constraint",
     {"a.md": "```sql\ncreate table t (\n  id integer,\n  primary key (id)\n);\n```\n"}, set()),
    # 精度参数里的空格差：归一后相同 → 不许报（反向探针，防「空格差异」被当成类型冲突）
    ("c09_space_in_precision",
     {"a.md": "```sql\ncreate table t (amount numeric(12, 2), x int);\n"
              "alter table t add column amount numeric(12,2);\n```\n"}, set()),
    ("c10_varchar_vs_text",
     {"a.md": "```sql\ncreate table t (note text);\n```\n",
      "b.md": "```sql\ncreate table t (note varchar(200));\n```\n"}, {"W1"}),
    ("c11_empty", {"a.md": "# 空页\n\n没有 SQL。\n"}, {"E1"}),
    ("c12_alter_conflict",
     {"a.md": "```sql\ncreate table t (pct integer);\nalter table t add pct smallint;\n```\n"},
     {"E2"}),
    # 反向探针：`alter … add constraint` 加的不是列（首轮全库实测的假阳性来源之一）
    ("c13_add_constraint",
     {"a.md": "```sql\ncreate table card (id bigint, j jsonb);\n"
              "alter table card add constraint card_desc_shape check (j is null or j ? 'type');\n"
              "alter table card add constraint card_desc_size check (j is null or octet_length(j::text) <= 131072);\n"
              "```\n"}, set()),
    # 反向探针：ClickHouse 的 `ALTER TABLE … ADD INDEX` 也不是列（首轮另一处假阳性）
    ("c14_clickhouse_add_index",
     {"a.md": "```sql\nALTER TABLE events ADD INDEX idx_evt event_type TYPE set(100) GRANULARITY 4;\n"
              "ALTER TABLE events ADD INDEX idx_ip props['ip'] TYPE bloom_filter GRANULARITY 4;\n"
              "```\n"}, {"E1"}),
]


def selftest():
    root = os.environ.get("TYPEDRIFT_SANDBOX") or os.path.join(
        tempfile.gettempdir(), "typedrift_sandbox")
    os.makedirs(root, exist_ok=True)
    passed = 0
    for name, files, expect in CASES:
        case_dir = os.path.join(root, name)
        os.makedirs(case_dir, exist_ok=True)
        for rel, text in files.items():
            # 相对路径不带 docs/ 或 project/ 前缀时，补成 docs/Backend/<用例>/，
            # 让「主题目录 = 路径前三段」的口径与真实语料一致
            rel_path = rel if rel.split("/")[0] in ("docs", "project") \
                else f"docs/Backend/{name}/{rel}"
            full = os.path.join(case_dir, *rel_path.split("/"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        errs, warns, files_n, ncols = check(case_dir)
        got = {e[0] for e in errs} | {w[0] for w in warns}
        ok = got == expect
        passed += 1 if ok else 0
        if not ok:
            print(f"FAIL {name}: 期望 {sorted(expect)} 实得 {sorted(got)}")
    total = len(CASES)
    print(f"--selftest {passed}/{total} {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = DEFAULT_ROOT
    for a in argv[1:]:
        if not a.startswith("-"):
            root = a
    errs, warns, files, ncols = check(root)
    for code, name, where, line, detail in errs:
        print(f"{code} {name:<18} {where}  {detail}")
    for code, name, where, line, detail in warns:
        print(f"{code} {name:<18} {where}  {detail}")
    e = len(errs)
    w = len(warns)
    print(f"\npages={files} columns={ncols} 合计 {e + w} 条：E={e} "
          f"W={w} (W1={sum(1 for x in warns if x[0] == 'W1')} "
          f"W2={sum(1 for x in warns if x[0] == 'W2')})")
    print(f"EXIT={1 if e else 0}")
    return 1 if e else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
