#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enumdriftcheck.py —— 「同一列允许哪些值」跨页漂移巡检（第 256 天新立，第一百三十八项巡检）

## 动机

本库的 `sql` 围栏里，状态列几乎都以 `CHECK (col IN ('A','B',...))` 的形式给出取值集合。
同一个列（`enrollment.state`、`attempt.state`、`shipment.status`）会在**同一主题的多页**出现：
建模页给一份、迁移页给一份、实战页再抄一份。抄改的残留在文档里**完全静默**——
页面读起来通顺、`pnpm docs:build` 全绿、链接全通，只有照着最后一份 DDL 建库的人才会发现
「库里允许 `CANCELLED`，业务代码却在写 `已取消`」。

既有巡检各管一段，**没有一项在比「同一个列允许哪些值」**：

  * `ddlrefcheck`（第 113 项）—— 「SQL 里引用的表建过没有」，跨页同名表只在**整块 DDL 文本**上判（W3），
    列级取值集合不在它的口径里；
  * `insertaritycheck`    —— `INSERT` 的列数与 `CREATE TABLE` 对不对得上；
  * `ddlrefcheck` 的 E2   —— 表名拼错（共享 >= 4 字符前缀）；
  * `unitmixcheck`        —— 量纲混用；
  * `judgecountcheck` 等  —— 全是「条数」类断言，不看取值。

于是「同一列两套取值」这一类缺陷长期只有人工评审在守。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND      仓库根既无 docs/ 也无 project/（活性，防路径写错全绿）
  E1 NO_VALUES           一个 `CHECK (x IN (...))` 都没解析到就拒绝判定（活性）
  E2 CHECK_CONFLICT      **同一页**内同一个 `表.列` 出现两套互不相容的 `CHECK` 集合
                         —— 无反例可辩（一页之内自相矛盾），一定是改了一半
  W1 WHERE_OUT_OF_CHECK  同一页里某个「页内唯一的列名」在 `WHERE col IN (...)` 中出现了
                         `CHECK` 不允许的值 —— 写了个库里不可能存在的状态
  W2 CROSS_PAGE_DRIFT    **跨页**同一 `表.列` 的集合互不相容（各有对方没有的值）
  W3 SUBSET_DRIFT        跨页或同页，一套是另一套的严格子集（多半是「最小可运行版」）

## 为什么跨页差异只报 `W`

同一条纪律已经在本仓的其他门禁上反复验证过（`assetdupcheck` 的跨目录重复、
`imagecoverweight` 的体积阈值、`h2dupcheck` 的重复锚点）：**会误报的门禁很快会被整体跳过**。
跨页取值不同有两类完全正当的成因——实战页只保留本例用到的名字、章节各自演进——
机器分不开这两类与「抄改残留」。而**同页两套互不相容**没有任何正当解释，所以它是唯一的 `E`。

`E2` 的粒度刻意定在**同一主题目录**内：跨主题同名表（各专题各建一份 `orders`）是合法的，
放到全库级立刻变成误报源。跨主题的差异只进报告，不阻断。

## 口径

  * 只解析 `sql` 围栏（` ```sql `），其余语言围栏里的 `CHECK` 不算；
  * `CREATE TABLE` 的列定义按**括号配平**切块，块内的 `check (col in (...))` 才收；
  * 表名与列名统一小写，去掉反引号与双引号；
  * `W1` 只对「该页 CHECK 声明过的列名里**只出现一次**的那个」做比对，
    出现两次以上的（如多张表都有 `state`）一律跳过并计入 `skipped`
    —— 宁可漏报，不可误报（本仓纪律：会误报的门禁很快会被整体跳过）。
"""
import os
import re
import sys
import tempfile

SKIP_DIRS = {"node_modules", ".git", ".vitepress", "dist", "assets", "public", "utils"}

CHECK_RE = re.compile(
    r"check\s*\(\s*[`\"\[]?(\w+)[`\"\]]?\s+in\s*\(([^)]*)\)\s*\)", re.I)
CREATE_RE = re.compile(
    r"create\s+table\s+(?:if\s+not\s+exists\s+)?[`\"]?([\w.]+)[`\"]?\s*\(", re.I)
IN_RE_TMPL = r"[`\"\[]?{col}[`\"\]]?\s+in\s*\(([^)]*)\)"
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`]*)")
VAL_SPLIT = re.compile(r"\s*,\s*")


def body_sql_blocks(lines):
    """返回 [(start_line_no, [text,...])]，只保留 sql 围栏内的行。"""
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


def norm_vals(raw):
    vals = []
    for part in VAL_SPLIT.split(raw.strip()):
        v = part.strip().strip("'\"`").strip()
        if v:
            vals.append(v.lower())
    return frozenset(vals)


def parse_check_sets(text_lines):
    """从一个 sql 块里抽出 [(表格内相对行号, table, col, frozenset)]。"""
    joined = "\n".join(text_lines)
    found = []
    for m in CREATE_RE.finditer(joined):
        table = m.group(1).lower()
        # 从 CREATE 的 '(' 开始做括号配平，找到表定义结束位置
        i = m.end() - 1
        depth = 0
        end = len(joined)
        while i < len(joined):
            ch = joined[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        block = joined[m.end():end]
        base_line = joined[:m.end()].count("\n")
        for cm in CHECK_RE.finditer(block):
            col = cm.group(1).lower()
            vals = norm_vals(cm.group(2))
            if not vals:
                continue
            rel = base_line + block[:cm.start()].count("\n")
            found.append((rel, table, col, vals))
    return found


def topic_of(rel):
    parts = rel.replace("\\", "/").split("/")
    return "/".join(parts[:3])


def scan(root):
    checks, wheres, files = [], {}, 0
    for base in ("docs", "project"):
        bpath = os.path.join(root, base)
        if not os.path.isdir(bpath):
            continue
        for dirpath, dirnames, filenames in os.walk(bpath):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fn in filenames:
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
                    for rel_line, table, col, vals in parse_check_sets(blk):
                        checks.append({
                            "rel": rel, "topic": topic_of(rel),
                            "line": start + rel_line, "table": table,
                            "col": col, "vals": vals,
                        })
                    wheres.setdefault(rel, []).append((start, "\n".join(blk)))
    return checks, wheres, files


def check(root):
    errs, warns = [], []
    if not (os.path.isdir(os.path.join(root, "docs")) or
            os.path.isdir(os.path.join(root, "project"))):
        return [("E0", "ROOT_NOT_FOUND", root, 0)], [], 0, 0, 0
    checks, wheres, files = scan(root)
    if not checks:
        return [("E1", "NO_VALUES", "", 0)], [], files, 0, 0

    # E2 / W2：按 (topic, table, col) 归组
    groups = {}
    for c in checks:
        groups.setdefault((c["topic"], c["table"], c["col"]), []).append(c)
    for (topic, table, col), items in sorted(groups.items()):
        pages = {c["rel"] for c in items}
        sets = {c["vals"] for c in items}
        if len(sets) < 2:
            continue
        biggest = max(sets, key=len)
        subset_only = all(s <= biggest for s in sets)
        detail = " / ".join(
            f"{c['rel']}:{c['line']} = {{{','.join(sorted(c['vals']))}}}" for c in items[:4])
        if subset_only:
            # 严格子集：多半是「教学/最小可运行版」，照抄会得到一个状态更少的库 → 只提示
            warns.append(("W3", "SUBSET_DRIFT", f"{topic} · {table}.{col}", 0, detail))
        elif len(pages) >= 2:
            # 跨页互不相容：可能是刻意的（各自演进 / 实战页只保留本例用到的名字），
            # 与 assetdupcheck 的跨目录重复同一条纪律——跨页差异只报告，交给人判断
            warns.append(("W2", "CROSS_PAGE_DRIFT", f"{topic} · {table}.{col}", 0, detail))
        else:
            # 同一页内两套取值互不相容：无反例可辩，一定是改了一半
            one = items[0]["rel"]
            errs.append(("E2", "CHECK_CONFLICT", f"{one} · {table}.{col}", 0, detail))

    # W1：页内唯一的列名，WHERE 里出现了 CHECK 不允许的值
    skipped = 0
    for rel, blocks in wheres.items():
        page_checks = [c for c in checks if c["rel"] == rel]
        bycol = {}
        for c in page_checks:
            bycol.setdefault(c["col"], []).append(c)
        for col, items in bycol.items():
            if len(items) > 1:
                skipped += 1
                continue
            allowed = items[0]["vals"]
            rx = re.compile(IN_RE_TMPL.format(col=re.escape(col)), re.I)
            for start, txt in blocks:
                for m in rx.finditer(txt):
                    got = norm_vals(m.group(1))
                    if not got or got <= allowed:
                        continue
                    bad = sorted(got - allowed)
                    line = start + txt[:m.start()].count("\n")
                    warns.append(("W1", "WHERE_OUT_OF_CHECK", rel,
                                  line, f"{col} 出现 CHECK 之外的值 {{{','.join(bad)}}}"))
    return errs, warns, files, len(checks), skipped


# ---------------- selftest ----------------

FIX = {
    "Backend/topic-a/Overview": """# A

```sql
create table enrollment (
  enrollment_id text primary key,
  state text not null check (state in ('ACTIVE','COMPLETED','CANCELLED'))
);
```
""",
    "Backend/topic-a/Legacy": """# A2

同一主题的另一页写了另一套状态名（互不相容 → E2）。

```sql
create table enrollment (
  enrollment_id text primary key,
  state text not null check (state in ('ACTIVE','WITHDRAWN'))
);
```
""",
    "Backend/topic-b/Overview": """# B

跨主题同名表、取值完全不同 —— 合法，不该报 E2。

```sql
create table enrollment (
  state text check (state in ('报名','在读'))
);
```
""",
    "Backend/topic-c/Bad": """# C

```sql
create table attempt (
  attempt_id text primary key,
  state text check (state in ('OPEN','SUBMITTED','SCORED'))
);
select * from attempt where state in ('OPEN','LOST');
```
""",
    "Backend/topic-d/Drift": """# D

反例与正例同页，状态集合改了一半。

```sql
create table cert (
  status text check (status in ('ISSUED','REVOKED'))
);
```

```sql
create table cert (
  status text check (status in ('ISSUED','VOID'))
);
```
""",
    "Backend/topic-e/Notes": """# E

正文里提到 check (state in ('X')) 但不在围栏内，不该被收。

```python
# check (state in ('NOT_SQL'))
```
""",
    "Backend/topic-f/Overview": """# G

```sql
create table payment (
  pay_id text primary key,
  status text check (status in ('PENDING','PAID','REFUNDED'))
);
```
""",
    "Backend/topic-f/Trim": """# G2

最小可运行版，状态是上一页的子集（→ W3，不阻断）。

```sql
create table payment (
  pay_id text primary key,
  status text check (status in ('PENDING','PAID'))
);
```
""",
}


def write_fixtures(root):
    for rel, body in FIX.items():
        d = os.path.join(root, "docs", *rel.split("/"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


def selftest():
    import hashlib
    sig = hashlib.sha1("\n".join(sorted(FIX)).encode()).hexdigest()[:8]
    root = os.path.join(tempfile.gettempdir(), "enumdrift-selftest", sig)
    os.makedirs(root, exist_ok=True)
    write_fixtures(root)
    errs, warns, files, n, skipped = check(root)
    got = {(e[0], e[1]) for e in errs} | {(w[0], w[1]) for w in warns}
    expect = {("E2", "CHECK_CONFLICT"), ("W1", "WHERE_OUT_OF_CHECK"),
              ("W2", "CROSS_PAGE_DRIFT"), ("W3", "SUBSET_DRIFT")}
    ok = got == expect
    print(f"files={files} check_sets={n} skipped={skipped}")
    for e in errs:
        print("ERR ", e[0], e[1], e[2], "|", e[4] if len(e) > 4 else "")
    for w in warns:
        print("WARN", w[0], w[1], w[2], w[3], "|", w[4])
    # 反向探针：topic-b 是跨主题同名表，不应被判 E2
    cross = [w for w in warns if w[2].startswith("topic-b")]
    if cross:
        ok = False
        print("FAIL topic-b 跨主题不该报警")
    print("SELFTEST", "PASS" if ok else "FAIL", f"{1 if ok else 0}/1")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = "."
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
        elif not a.startswith("-") and os.path.isdir(a):
            root = a
    errs, warns, files, n, skipped = check(root)
    for e in errs:
        print(f"{e[0]} {e[1]} :: {e[2]} | {e[4] if len(e) > 4 else ''}")
    for w in warns:
        print(f"{w[0]} {w[1]} :: {w[2]}:{w[3]} | {w[4]}")
    print(f"pages={files} check_sets={n} skipped_ambiguous_cols={skipped}")
    print(f"合计 {len(errs) + len(warns)} 条：E={len(errs)} W={len(warns)}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
