#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ddlclaimcheck.py —— 「本页给出 N 张表 / N 个触发器」的自述计数与实物对账（第 144 项巡检）

背景
----
本仓的实战页习惯在标题与导语里报规模：「十张表、五个触发器与十九条断言」。读者据此判断
这一页能不能照着建库；一旦数字漂移，页面读起来完全正常、构建也不报错，只是照着做会少一张表。

既有巡检各管一段：
  - `countclaimcheck` 只看「全书 N 章」「共 N 页」这类**页面级**计数；
  - `judgesumcheck` 只看判据总览表的条数；
  - `ddlrefcheck` 只看 DDL 里的表名在正文里有没有被提到；
没有一项问「页面上写的对象数，和同一页 SQL 代码块里真的 CREATE 了几个，是不是一回事」。

判据（E 为错误、W 为提示）
--------------------------
  E0 ROOT_NOT_FOUND        给定的根目录不存在
  E2 TABLE_SHORT           「N 张表」的声称数 > 实际 `CREATE TABLE` 数（虚称，最危险）
  E3 TRIGGER_SHORT         「N 个触发器」的声称数 > 实际 `CREATE TRIGGER` 数
  E4 VIEW_SHORT            「N 个视图」的声称数 > 实际 `CREATE VIEW` 数
  E5 ASSERT_SHORT          「N 条断言」的声称数 > 断言表里的 `C*`/`N*` 行数
  W1 NO_CLAIM              有 DDL 代码块但没有任何计数声明（不强制，只提示）
  W2 OVER_CLAIM            实际数 > 声称数（少称，读者不会做错，但描述不准）
  W3 MULTI_CLAIM           同一页同一类声称出现多次且数字不同（取最大值为准，需人工确认）

口径说明（为什么这样取数）
--------------------------
1. **只认「N 张表 / N 个触发器 / N 个视图 / N 条断言」四种句式**。库内还有「N 张控制表」
   「N 章」「N 族 M 条」等表达，泛化会立刻产生大量误报；本巡检刻意保守。
2. **取同类声明的最大值**。实战页常写「9 张控制表 + 1 张源表」，逐句解析会把 9 当成总数；
   取最大值仍可能低估，所以「实际 > 声称」只判 W（少称），只有「声称 > 实际」才判 E（虚称）。
3. **断言只数表格行**：以「竖线 + 反引号 C1/N1」开头的表格行。正文里顺带提到的「三条断言」
   不参与计数——那类句子多半在讲别处的例子。
4. **大小写不敏感、允许 IF NOT EXISTS**：`CREATE TABLE IF NOT EXISTS foo` 计一个 `foo`；
   同一个名字在同一页出现两次（DDL 摘录 + 完整版）只算一个。
5. **只审有代码块的页**。整页没有任何围栏代码块，页内的「三张表」多半是别的语境
   （前端页里「三张表」是三个表格、「视图」是 UI 视图），直接跳过——这是被实测误报逼出来的
   第一次口径修正：首版把 60 多页前端内容判成错，逐页读下来**全是正当写法**。
   **代码块不限语言**：本仓大量实战页把建表语句写在 ```python 的脚本字符串里，只扫 ```sql
   会把「八张表都在页面上」的页面判成「只有三张」——这是第二次口径修正，也是本巡检
   最有价值的一课：**判据的语料假设错了，误报会像真缺陷一样理直气壮**。
6. **同类对象数为 0 时只判 W**。页面里出现「五个触发器」而 DDL 里一个 `CREATE TRIGGER` 都没有，
   也可能是「触发器在这一册、DDL 在上一册」；这种情况读数不足，不能判错。

用法
----
    python3 utils/audit/ddlclaimcheck.py --root .
    python3 utils/audit/ddlclaimcheck.py --selftest
"""

import argparse
import os
import re
import sys

NUM = r"([一二三四五六七八九十两]+|\d+)"
TABLE_CLAIM = re.compile(NUM + r"\s*张表")
TRIGGER_CLAIM = re.compile(NUM + r"\s*个触发器")
VIEW_CLAIM = re.compile(NUM + r"\s*个视图")
ASSERT_CLAIM = re.compile(NUM + r"\s*条断言")

_CN = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
       "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def to_int(tok):
    """把「十」「十九」「二十五」「3」都转成整数；无法解析返回 None。"""
    if tok.isdigit():
        return int(tok)
    if "十" not in tok:
        return _CN.get(tok) if len(tok) == 1 else None
    head, _, tail = tok.partition("十")
    tens = _CN.get(head, 1) if head else 1
    ones = _CN.get(tail, 0) if tail else 0
    return tens * 10 + ones

CREATE_TABLE = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z_][\w.]*)", re.I)
CREATE_TRIGGER = re.compile(r"create\s+trigger\s+(?:if\s+not\s+exists\s+)?([a-zA-Z_][\w.]*)", re.I)
CREATE_VIEW = re.compile(r"create\s+(?:or\s+replace\s+)?view\s+([a-zA-Z_][\w.]*)", re.I)
ASSERT_ROW = re.compile(r"^\|\s*`([CN]\d+)`\s*\|")

ANY_FENCE = re.compile(r"^(```+|~~~+)\s*[\w+-]*")


def split_blocks(text):
    """返回 (全部代码块列表, 去掉代码块后的正文)。

    DDL 不只出现在 ```sql 块里：本仓大量实战页把建表语句写在 ```python 的脚本字符串中，
    只扫 sql 块会把「八张表都在页面上」的页面判成「只有三张」。这是实测误报逼出来的第二个口径修正。
    """
    lines = text.splitlines()
    blocks, prose, cur, inside, fence = [], [], None, False, None
    for line in lines:
        st = line.strip()
        m = ANY_FENCE.match(st)
        if not inside and m:
            inside, fence, cur = True, m.group(1)[0] * 3, []
            continue
        if inside and st.startswith(fence):
            inside = False
            blocks.append("\n".join(cur))
            continue
        if inside:
            cur.append(line)
        else:
            prose.append(line)
    if inside:
        blocks.append("\n".join(cur))
    return blocks, "\n".join(prose)


SELF_REF = ("本页", "本册", "这一页", "本专题", "实战")


def head_scope(text, limit=900):
    """只取「H1 + 导语」里**指向本页自己**的那些行。

    计数声明有两种：描述系统（「本项目十二张表」）与描述本页（「实战：十张表」）。
    只有后者才该与页内 DDL 对账；前者是规模描述，页内本来就只放摘录。
    判定方式：行内出现「本页/本册/这一页/本专题」，或首次出现的 H1 以「实战」开头。
    """
    head = text[:limit].splitlines()
    keep, h1_seen = [], False
    for line in head:
        if line.startswith("# ") and not h1_seen:
            h1_seen = True
            if line.lstrip("# ").startswith("实战"):
                keep.append(line)
            continue
        if any(k in line for k in SELF_REF):
            keep.append(line)
    return "\n".join(keep)


def claims_in(text, pattern, label):
    vals = [v for m in pattern.finditer(text) if (v := to_int(m.group(1))) is not None]
    if not vals:
        return None, []
    return max(vals), vals


def check_page(path, text):
    errs, warns = [], []
    blocks, prose = split_blocks(text)
    if not blocks:
        return errs, warns          # 口径 5：整页没有代码块，跳过
    ddl = "\n".join(blocks)

    tables = {m.group(1).lower() for m in CREATE_TABLE.finditer(ddl)}
    triggers = {m.group(1).lower() for m in CREATE_TRIGGER.finditer(ddl)}
    views = {m.group(1).lower() for m in CREATE_VIEW.finditer(ddl)}
    asserts = {m.group(1) for line in prose.splitlines() if (m := ASSERT_ROW.match(line))}

    specs = [
        ("E2", "TABLE_SHORT", tables, TABLE_CLAIM, "张表"),
        ("E3", "TRIGGER_SHORT", triggers, TRIGGER_CLAIM, "个触发器"),
        ("E4", "VIEW_SHORT", views, VIEW_CLAIM, "个视图"),
        ("E5", "ASSERT_SHORT", asserts, ASSERT_CLAIM, "条断言"),
    ]

    has_code = bool(blocks)
    any_claim = False
    scope = head_scope(prose)
    for code, kind, actual, pattern, unit in specs:
        claim, all_vals = claims_in(scope, pattern, unit)
        if claim is None:
            continue
        any_claim = True
        if len(set(all_vals)) > 1:
            warns.append(("W3", "MULTI_CLAIM",
                          f"{path}: 「{unit}」出现 {len(all_vals)} 次且数字不同 {sorted(set(all_vals))}（取 {claim}）"))
        if len(actual) == 0:
            warns.append(("W1", "NO_DDL_FOR_CLAIM",
                          f"{path}: 声称 {claim} {unit}，但页内 DDL 里对应对象为 0（读数不足，不判错）"))
            continue
        if claim > len(actual):
            errs.append((code, kind, f"{path}: 声称 {claim} {unit}，实际 {len(actual)} 个"))
        elif claim < len(actual):
            warns.append(("W2", "OVER_CLAIM", f"{path}: 声称 {claim} {unit}，实际 {len(actual)} 个"))

    if has_code and not any_claim:
        got = [f"{len(tables)} 表"] if tables else []
        got += [f"{len(triggers)} 触发器"] if triggers else []
        got += [f"{len(views)} 视图"] if views else []
        if got:
            warns.append(("W1", "NO_CLAIM", f"{path}: 有 DDL（{' / '.join(got)}）但无计数声明"))
    return errs, warns


def walk(root):
    pages = 0
    errs, warns = [], []
    for base in ("docs", "project"):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, _, files in os.walk(top):
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root)
                try:
                    text = open(path, encoding="utf-8").read()
                except OSError:
                    continue
                pages += 1
                e, w = check_page(rel, text)
                errs += e
                warns += w
    return pages, errs, warns


def selftest():
    import tempfile
    cases = []

    def run(files):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, body in files.items():
                p = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w", encoding="utf-8").write(body)
            return walk(tmp)

    ok_body = """# 实战：两张表与一条断言

```sql
CREATE TABLE a (id INTEGER);
CREATE TABLE IF NOT EXISTS b (id INTEGER);
```

| 编号 | 断言 |
| --- | --- |
| `C1` | 成立 |
"""
    _, e, w = run({"docs/X/ok/index.md": ok_body})
    cases.append(("一致时无 E", len(e) == 0))

    short = ok_body.replace("CREATE TABLE IF NOT EXISTS b (id INTEGER);", "")
    _, e, _ = run({"docs/X/short/index.md": short.replace("两张表", "三张表").replace("一条断言", "三条断言")})
    cases.append(("虚称表数判 E2", any(c == "E2" for c, _, _ in e)))
    cases.append(("虚称断言判 E5", any(c == "E5" for c, _, _ in e)))

    no_sql = "# 实战：两张表\n\n本页不给 DDL。\n"
    _, e, _ = run({"docs/X/nosql/index.md": no_sql})
    cases.append(("无 sql 块整页跳过", len(e) == 0))

    trig = """# 实战：一个触发器

```sql
CREATE TRIGGER t1 BEFORE INSERT ON a BEGIN SELECT 1; END;
CREATE TRIGGER t2 BEFORE INSERT ON a BEGIN SELECT 1; END;
```
"""
    _, _, w = run({"docs/X/trig/index.md": trig})
    cases.append(("少称判 W2", any(c == "W2" for c, _, _ in w)))

    multi = """# 实战：三张表

```sql
CREATE TABLE a (id INTEGER);
```
另外本页早先写过 五张表。
"""
    _, _, w = run({"docs/X/multi/index.md": multi})
    cases.append(("多处不同判 W3", any(c == "W3" for c, _, _ in w)))

    noclaim = """# 实战

```sql
CREATE TABLE a (id INTEGER);
CREATE VIEW v AS SELECT 1;
```
"""
    _, _, w = run({"docs/X/noclaim/index.md": noclaim})
    cases.append(("有 DDL 无声称判 W1", any(c == "W1" for c, _, _ in w)))

    ok = 0
    for name, passed in cases:
        print(("PASS  " if passed else "FAIL  ") + name)
        ok += 1 if passed else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"E0 ROOT_NOT_FOUND {root}")
        return 2

    pages, errs, warns = walk(root)
    for code, kind, msg in errs:
        print(f"{code} {kind} {msg}")
    print(f"pages={pages} E={len(errs)} W={len(warns)}")
    for code, kind, msg in warns[:40]:
        print(f"  {code} {kind} {msg}")
    if len(warns) > 40:
        print(f"  ... 其余 {len(warns) - 40} 条 W 略")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
