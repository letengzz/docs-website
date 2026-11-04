#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""nullguardcheck.py —— 「时态列的比较漏了 NULL 兜底」巡检（第 250 天新立，第一百三十二项巡检）

## 动机

本库大量页面用**区间**表达「当时有效」：`student_status.to_date`、`employment.end_date`、
`policy.valid_to`、`slot.expired_at`。它们的共同形态是：

| 语义 | 存法 |
| --- | --- |
| 已经结束 | 有结束日期 |
| **仍然有效** | 结束日期是 `NULL` |

于是「在某个时点 T 有效」这一句，唯一正确的写法是三段：

```sql
WHERE start_date <= :t
  AND (to_date IS NULL OR to_date > :t)   -- ← 少了这一对括号就只剩两段
```

而 SQL 的三值逻辑会把漏掉的那一段变成**静默的丢失**：`to_date > :t` 对 `NULL` 求值得到
`UNKNOWN`，`WHERE` 只保留 `TRUE`——**所有「当前仍然有效」的行被整批排除**。不报错、不警告，
只是结果集少了一批。这类缺陷的读数往往「看起来还挺正常」：

- 学籍表里「在籍」的人全都不见了，只留下退学、毕业的人（本专题第 250 天实测：2,936 人里
  只剩 64 人）；
- 任职表里「在职」的人全都不见了，只剩离职的；
- 保单表里「未到期」的全都不见了，只剩已失效的。

更麻烦的是它**与被查的数据高度负相关**：越是「当前有效」的记录越容易消失，而这恰恰是
报表最想看的那些人。文档里的 SQL 会被读者原样抄走，所以这一段必须在文档阶段就挡住。

## 判据

| ID | 级别 | 含义 |
| --- | --- | --- |
| `E0` | 致命 | 根目录不存在 |
| `E1` | 致命 | 扫描范围内没有任何 markdown（活性判据，防「扫了个空目录也算全绿」） |
| `W1` | 警告 | 时态列做**上界**比较（`>` / `>=`）时缺 NULL 兜底——「当前有效」的行会被整批丢掉 |
| `W2` | 警告 | 时态列做**下界**比较（`<` / `<=`）时缺 NULL 兜底——语义上通常无害（`NULL` 代表「还没结束」），但写法不一致，记账 |

为什么 `W1` 不升到 `E`：本库有相当一批页面是**故意**把错写法贴出来做反例的（「这样写会
丢掉在籍的人」），机检无法区分「示范」与「照抄」。所以按 `W` 记账，由人工在写页时确认；
但**同一条 `W1` 若连续两页复现，就该去改那两页的正文**——这正是本巡检的用法。

## 兜底的三种合法写法（任一即可）

```sql
-- ① IS NULL 显式兜底
AND (to_date IS NULL OR to_date > :t)
-- ② 哨兵日期（本库不推荐，但认）
AND COALESCE(to_date, '9999-12-31') > :t
-- ③ IFNULL / NVL 同义
AND IFNULL(to_date, '9999-12-31') > :t
```

三种都在同一行里出现即可，本巡检按**行**判定，不做跨行数据流分析（跨行会把
`CASE WHEN ... END` 里的换行误判）。

## 用法

```shell
python3 utils/audit/nullguardcheck.py --selftest   # 10 条自检
python3 utils/audit/nullguardcheck.py              # 全库
python3 utils/audit/nullguardcheck.py docs/Backend # 只看一个子树
```

退出码：`0` 全绿、`1` 有 E 级、`2` 自检失败。
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402

DEFAULT_ROOTS = ["docs", "project"]
SKIP_DIRS = {".vitepress", "node_modules", ".git", "assets", "public"}

# 时态列：以 _to / _end / _until / _expiry 结尾，或几个固定名
# 注意 `_at` 后缀**不收**：created_at / updated_at 是瞬时点，本来就不该做 NULL 兜底，
# 收进来会让全库每个时间戳比较都报警（真实语料里这类比较有上万处）。
_NAME = (r"(?:[A-Za-z_][A-Za-z0-9_]*(?:_to|_end|_until|_expiry|_expired)"
         r"|to_date|end_date|dt_end|valid_to|valid_until|expired_at)")
TEMPORAL_RE = re.compile(r"(?<![\w.])" + _NAME + r"(?![\w(])", re.I)
TEMPORAL_FULL = re.compile(r"^" + _NAME + r"$", re.I)

CMP_RE = re.compile(r"(?P<col>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<op>>=|>|<=|<)\s*(?P<rhs>[^\s,;)]+)")

GUARD_FUNCS = ("coalesce(", "ifnull(", "nvl(", "nvl2(", "isnull(")


def _in_guard(code, start, end):
    """比较表达式是否落在 coalesce(...)/ifnull(...) 的括号内。"""
    low = code.lower()
    best = -1
    for fn in GUARD_FUNCS:
        p = low.rfind(fn, 0, start)
        if p > best:
            best = p
    if best < 0:
        return False
    depth = 0
    for ch in code[best:end]:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                # 括号在比较符之前就闭合了 → 不属于该函数
                return low.find(")", best) > end
    return depth > 0


def check_text(text, path="<selftest>"):
    lines = text.split("\n")
    _, blocks, _ = scan(text)
    findings = []
    stat = {"guarded": 0, "temporal": 0}
    for start, end, info in blocks:
        if not (info or "").lower().startswith("sql"):
            continue
        for ln in range(start + 1, end):
            line = lines[ln]
            code = line.split("--")[0]
            if not code.strip():
                continue
            if not TEMPORAL_RE.search(code):
                continue
            low = code.lower()
            # CHECK (end_date > start_date) 是列内值域约束，不查行；不参与 NULL 兜底判定
            is_check = re.search(r"\bCHECK\s*\(", code, re.I) is not None
            for m in CMP_RE.finditer(code):
                col, op = m.group("col"), m.group("op")
                if not TEMPORAL_FULL.match(col):
                    continue
                stat["temporal"] += 1
                if is_check:
                    stat["guarded"] += 1
                    continue
                if "is null" in low or _in_guard(code, m.start(), m.end()):
                    stat["guarded"] += 1
                    continue
                if op in (">", ">="):
                    findings.append(("W1", ln + 1,
                                     "`%s %s` 缺 NULL 兜底：当前有效的行会被整批排除（应写 `%s IS NULL OR %s %s ...`）"
                                     % (col, op, col, col, op)))
                else:
                    findings.append(("W2", ln + 1,
                                     "`%s %s` 未处理 NULL（语义通常无害，但与别处写法不一致）" % (col, op)))
    return findings, stat


def iter_md(roots):
    for root in roots:
        if not os.path.isdir(root):
            yield None, root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn), root


def run(roots, quiet=False):
    total = {"W1": 0, "W2": 0}
    files = 0
    stat = {"guarded": 0, "temporal": 0}
    for path, root in iter_md(roots):
        if path is None:
            print("E0 ROOT_NOT_FOUND  %s" % root)
            total["E0"] = total.get("E0", 0) + 1
            continue
        files += 1
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as exc:
            print("E0 READ_FAIL  %s  %s" % (path, exc))
            total["E0"] = total.get("E0", 0) + 1
            continue
        findings, st = check_text(text)
        stat["guarded"] += st["guarded"]
        stat["temporal"] += st["temporal"]
        for code, ln, msg in findings:
            total[code] = total.get(code, 0) + 1
            if not quiet:
                print("%-3s %s:%d  %s" % (code, path, ln, msg))
        if not findings:
            continue
    if files == 0:
        print("E1 NO_FILES  扫描范围内没有任何 markdown")
        return 1
    warns = total.get("W1", 0) + total.get("W2", 0)
    errs = total.get("E0", 0)
    print("\nfiles=%d temporal_cmp=%d guarded=%d" % (files, stat["temporal"], stat["guarded"]))
    print("W1=%d W2=%d" % (total.get("W1", 0), total.get("W2", 0)))
    print("合计 %d 条：E=%d W=%d" % (errs + warns, errs, warns))
    print("RESULT " + ("OK" if errs == 0 else "FAIL"))
    return 0 if errs == 0 else 1


SELFTEST = [
    ("上界裸比较（丢在籍）", """
```sql
SELECT * FROM student_status WHERE to_date > '2024-01-01';
```
""", ["W1"]),
    ("上界带 IS NULL 兜底", """
```sql
SELECT * FROM student_status
 WHERE start_date <= '2024-01-01'
   AND (to_date IS NULL OR to_date > '2024-01-01');
```
""", []),
    ("上界用 COALESCE 哨兵", """
```sql
SELECT * FROM student_status WHERE COALESCE(to_date, '9999-12-31') > '2024-01-01';
```
""", []),
    ("上界用 IFNULL", """
```sql
SELECT * FROM employment WHERE IFNULL(end_date, '9999-12-31') >= '2024-01-01';
```
""", []),
    ("下界裸比较只记账", """
```sql
SELECT * FROM policy WHERE valid_to < '2024-01-01';
```
""", ["W2"]),
    ("非时态列不参与", """
```sql
SELECT * FROM student WHERE age > 18 AND name > 'M';
```
""", []),
    ("注释里不算", """
```sql
-- WHERE to_date > '2024-01-01' 这是反例
SELECT 1;
```
""", []),
    ("非 sql 围栏不参与", """
```python
to_date > "2024-01-01"
```
""", []),
    ("多行语句逐行判定", """
```sql
SELECT *
  FROM student_status
 WHERE to_date > '2024-01-01'
   AND start_date <= '2024-01-01';
```
""", ["W1"]),
    ("函数调用不是列", """
```sql
SELECT TO_DATE(x) FROM t WHERE end_date <= '2024-01-01';
```
""", ["W2"]),
]


def selftest():
    ok = 0
    for name, text, expect in SELFTEST:
        findings, _ = check_text(text)
        got = sorted({c for c, _, _ in findings})
        good = got == sorted(set(expect))
        ok += 1 if good else 0
        print("%-24s %s  got=%s expect=%s" % (name, "PASS" if good else "FAIL", got, sorted(set(expect))))
    print("\nselftest %d/%d" % (ok, len(SELFTEST)))
    return 0 if ok == len(SELFTEST) else 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="时态列 NULL 兜底巡检")
    ap.add_argument("roots", nargs="*", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    sys.exit(run(args.roots or DEFAULT_ROOTS, args.quiet))
