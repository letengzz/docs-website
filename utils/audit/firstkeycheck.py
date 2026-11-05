#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""firstkeycheck.py —— 「表格首列是不是唯一键」巡检（第 258 天新立，第 140 项巡检）

背景
----
库内几乎每张表都是「首列当键」：`| 天 | 步骤 | 章节 |`、`| 编号 | 判据 | 怎么验 |`、
`| 表 | 主键 | 一行代表 |`。读者扫表时先看首列，**首列重复就意味着有一行是废的**——
要么漏改了一行（复制上一行只改了后半段），要么同一件事被登记了两次。

既有的表格巡检各管一段，都不问这件事：

  - `tablecheck`（第 73 项）        表格**结构**（表头 / 分隔行 / 列数）
  - `tablesumcheck`（第 115 项）    合计行**加得对不对**
  - `missingsymcheck`（第 138 项）  同一列**缺值符号**是否混用
  - `cellgapcheck`（第 128 项）     空单元格
  - `unitmixcheck`（第 104 项）     同一列**量纲**是否混用

「这一列的值有没有重复」没有任何门在看。而它恰好是「整行复制后只改了一半」这类
缺陷的唯一可自动识别的痕迹——第 258 天写报关专题的对照表时，就有两行的「维度」
都是「汇率从哪取」，肉眼看表格完全正常。

判据（E = 错误，必须修；W = 提示，登记长尾）
--------------------------------------------
  E0 ROOT_NOT_FOUND   给定的根目录不存在
  E1 NO_TABLES        一张表都没扫到（活性判据，防路径写错全绿）
  E2 NO_ROWS          扫到了表头但没有任何数据行参与判定（解析器整体失效）
  W1 KEY_DUP          首列属于「编号族」（编号/序号/判据/错误码/表名/脚本/字段…）且取值重复
  W2 OTHER_DUP        首列不属于编号族但取值重复（可能是合法的分组表）
  W3 ROW_DUP          同一张表里两行**完全相同**（整行复制未改，一定是废行）

口径
----
- 缺值符号（`—` `-` `N/A` `无` 空）**不参与**重复判定：一列里 8 个 `—` 不是「重复的键」，
  而是「这一列没填」。与 `missingsymcheck` 的符号类表保持一致。
- 重复按**表**聚合：同一张表里同一个值出现 N 次只报 1 条（报首个重复值），否则一张
  20 行的表能刷出 10 条。同一张表里多个不同的值重复，也只报首条并带上「共 N 处」。
- 首列表头命中编号族才报 `W1`；其余报 `W2`。分开的原因是处置方式不同：`W1` 一定是错，
  `W2` 常常是合法的分组表（如「渠道」列在多行里出现两次，因为一个渠道有两档费率）。
- 围栏内的表格不算（那是示例代码），复用 `fenceutil.body_lines`。
- 表头含「运算符 / 符号 / 标记」这类列不参与判定（内容本身就是符号）。

为什么 E 只有三条活性判据：首列重复**没有一条能 100% 断定是错的**（见 `W2` 的反例），
硬升 `E` 只会逼着人去写逐条豁免。本项的价值是把候选集从「全库一万多张表」缩到
「几十张需要人看一眼的表」——第 258 天实测 13,878 张表里只有 20 张需要看。

用法
----
  python3 utils/audit/firstkeycheck.py [--root docs project] [--selftest]
  python3 utils/audit/firstkeycheck.py --root docs/Backend/CustomsTrade

退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402

# 首列命中这些词 = 「编号族」，重复一定是错
# 口径第二轮收敛：首版把「参数 / 字段 / 版本 / 表 / 项」也算编号族，实测 7 条 W1 里
# 6 条是**合法分组表**（一张表列一个表的多个字段、一个版本的多个特性），于是收窄到
# 「一件事只可能有一行」的那几个表头——编号、序号、判据、错误码、断言、天、步骤、命令。
KEY_COL = (
    "编号", "序号", "序", "#", "ID", "id", "判据", "错误码", "断言",
    "检查项", "天", "步骤", "条号", "命令", "键",
)
# 首列内容就是符号本身的列，不参与
SYMBOL_COL = ("运算符", "操作符", "符号", "标记", "通配符")
MISSING = {"—", "–", "-", "--", "---", "－", "N/A", "n/a", "NA", "N.A.", "无", "暂无", "没有", "/", "／", ""}

SEP = re.compile(r"^\|?[\s:|-]+\|[\s:|-]*$")


def split_cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def scan_tables(path):
    """返回 [[(行号, 原始行), ...], ...]，围栏内的表格已剔除（行号为文件真实行号）。"""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    mask, _blocks, _unclosed = scan(text)
    lines = [(i, ln) for i, ln in enumerate(text.split("\n"), 1) if (i - 1) not in mask]
    tables, cur = [], []
    for i, ln in lines:
        if ln.strip().startswith("|") and ln.count("|") >= 2:
            cur.append((i, ln))
        else:
            if len(cur) >= 2:
                tables.append(cur)
            cur = []
    if len(cur) >= 2:
        tables.append(cur)
    return tables


def is_key_col(name):
    n = name.strip()
    return any(k == n or k in n for k in KEY_COL)


def analyze(root_dirs, base):
    findings, st = [], dict(pages=0, tables=0, rows=0, keydup=0, otherdup=0, rowdup=0)
    for root in root_dirs:
        for dirpath, _dirs, files in os.walk(os.path.join(base, root)):
            for fn in sorted(files):
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, base)
                st["pages"] += 1
                for rows in scan_tables(p):
                    hdr_i, hdr_line = rows[0]
                    if len(rows) < 3:
                        continue
                    if not SEP.match(rows[1][1].strip().replace(" ", "")):
                        continue
                    st["tables"] += 1
                    header = split_cells(hdr_line)
                    col0 = header[0] if header else ""
                    body = [(i, split_cells(ln)) for i, ln in rows[2:]]
                    body = [(i, c) for i, c in body if c and c[0].strip() not in MISSING]
                    if not body:
                        continue
                    st["rows"] += len(body)
                    if any(k in col0 for k in SYMBOL_COL):
                        continue

                    # 整行重复
                    seen_row, row_dup = {}, []
                    for i, cells in body:
                        key = "|".join(x.strip() for x in cells)
                        if key in seen_row:
                            row_dup.append((seen_row[key], i))
                        else:
                            seen_row[key] = i
                    if row_dup:
                        st["rowdup"] += 1
                        a, b = row_dup[0]
                        findings.append(("W3", f"{rel}:{hdr_i} 表首列「{col0}」第 {b} 行与第 {a} 行完全相同"
                                               f"（共 {len(row_dup)} 处）"))
                        continue

                    # 首列重复
                    seen, dups = {}, []
                    for i, cells in body:
                        v = cells[0].strip()
                        if v in seen:
                            dups.append((v, seen[v], i))
                        else:
                            seen[v] = i
                    if not dups:
                        continue
                    if is_key_col(col0):
                        st["keydup"] += 1
                        v, a, b = dups[0]
                        findings.append(("W1", f"{rel}:{hdr_i} 表首列「{col0}」是编号族但取值重复："
                                               f"「{v}」出现在第 {a}/{b} 行（共 {len(dups)} 处）"))
                    else:
                        st["otherdup"] += 1
                        v, a, b = dups[0]
                        findings.append(("W2", f"{rel}:{hdr_i} 表首列「{col0}」取值重复："
                                               f"「{v}」出现在第 {a}/{b} 行（共 {len(dups)} 处）"))
    return findings, st


SELFTEST_FILES = {
    "w1_keydup/index.md": """# 判据重复

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| LNM-A | 组卷冻结 | 重算 0 份变化 |
| LNM-B | 冻结版本 | 0 份变化 |
| LNM-A | 组卷冻结（重复登记） | 换个说法 |
""",
    "w2_otherdup/index.md": """# 分组表

| 渠道 | 档位 | 费率 |
| --- | --- | --- |
| 门店 | A | 3% |
| 门店 | B | 5% |
| 线上 | A | 2% |
""",
    "w3_rowdup/index.md": """# 整行重复

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| X1 | 甲 | 看 1 |
| X2 | 乙 | 看 2 |
| X2 | 乙 | 看 2 |
""",
    "symbol/index.md": """# 缺值不参与

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| — | 甲 | 看 1 |
| — | 乙 | 看 2 |
| X3 | 丙 | 看 3 |
""",
    "clean/index.md": """# 干净

| 天 | 步骤 | 章节 |
| --- | --- | --- |
| 257 | 第 2 步 | 进度 |
| 258 | 第 3 步 | 交卷 |
""",
    "fenced/index.md": """# 围栏内不算

```markdown
| 编号 | 判据 |
| --- | --- |
| A1 | 甲 |
| A1 | 甲 |
```
""",
    "symcol/index.md": """# 符号列

| 运算符 | 含义 |
| --- | --- |
| + | 加 |
| + | 加 |
""",
}


def selftest():
    tmp = tempfile.mkdtemp(prefix="firstkey_")
    for rel, content in SELFTEST_FILES.items():
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    old = os.getcwd()
    os.chdir(tmp)
    try:
        cases = []

        def run(root="."):
            return analyze([root], os.getcwd())[0]

        def has(rel, code, frag=""):
            return any(c == code and rel in m and frag in m for c, m in run())

        cases.append(("W1 编号族首列重复", has("w1_keydup", "W1", "LNM-A")))
        cases.append(("W1 同表只报一条", sum(1 for c, m in run() if "w1_keydup" in m) == 1))
        cases.append(("W2 非编号族重复只提示", has("w2_otherdup", "W2", "门店")))
        cases.append(("W2 不升级为 E", not any(c.startswith("E") and "w2_otherdup" in m for c, m in run())))
        cases.append(("W3 整行完全相同", has("w3_rowdup", "W3", "第 7 行")))
        cases.append(("W3 优先于 W1", not any("w3_rowdup" in m and c == "W1" for c, m in run())))
        cases.append(("缺值符号不参与重复判定", not any("symbol/" in m for _c, m in run())))
        cases.append(("clean 无 W", not any("clean/" in m for _c, m in run())))
        cases.append(("围栏内不报", not any("fenced/" in m for _c, m in run())))
        cases.append(("符号列不参与", not any("symcol/" in m for _c, m in run())))
        st = analyze(["."], os.getcwd())[1]
        cases.append(("统计字段齐全", all(k in st for k in
                                          ("pages", "tables", "rows", "keydup", "otherdup", "rowdup"))))
        cases.append(("行号取文件真实行号", any("w1_keydup/index.md:3" in m for _c, m in run())))
    finally:
        os.chdir(old)

    bad = 0
    for name, okv in cases:
        print(("PASS " if okv else "FAIL ") + name)
        if not okv:
            bad += 1
    print(f"\nselftest {len(cases)-bad}/{len(cases)}")
    return 0 if bad == 0 else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    roots, i = ["docs", "project"], 1
    while i < len(argv):
        if argv[i] == "--root":
            roots, i = [], i + 1
            while i < len(argv) and not argv[i].startswith("--"):
                roots.append(argv[i])
                i += 1
        else:
            i += 1

    missing = [r for r in roots if not os.path.isdir(r)]
    if missing:
        print(f"E0 ROOT_NOT_FOUND {' '.join(missing)}")
        return 1

    findings, st = analyze(roots, os.getcwd())
    if st["tables"] == 0:
        print("E1 NO_TABLES 一张表都没扫到（路径写错？）")
        return 1
    if st["rows"] == 0:
        print("E2 NO_ROWS 扫到了表头但没有任何数据行参与判定（解析器失效？）")
        return 1

    order = {"W1": 0, "W2": 1, "W3": 2}
    findings.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    for code, msg in findings:
        print(f"{code} {msg}")

    e_cnt = sum(1 for c, _ in findings if c.startswith("E"))
    w_cnt = len(findings) - e_cnt
    print(f"\npages={st['pages']} tables={st['tables']} rows={st['rows']}")
    print(f"合计 {len(findings)} 条：E={e_cnt} W={w_cnt} "
          f"(W1={st['keydup']} W2={st['otherdup']} W3={st['rowdup']})")
    print("RESULT", "OK" if e_cnt == 0 else "FAIL")
    return 0 if e_cnt == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
