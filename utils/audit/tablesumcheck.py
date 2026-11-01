#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tablesumcheck.py —— 「表格的合计行到底加得对不对」巡检（第 233 天新立，第一百一十五项巡检）

## 动机

本库有两千多张 Markdown 表格，其中大量是「分项 + 合计」的形态：金额、工时、条数、占比。
`tablecheck` 只管**列数对不对齐**，`unitmixcheck` 只管**量纲有没有混**，`countclaimcheck`
只管**正文里的数字有没有出处**——**没有一项把一列数字真的加起来**。

于是这类缺陷可以长期存在：合计行比上面几项多 1,200 元、少 8 小时、百分数加起来 113%。
它有几个共同特征，决定了它必须由脚本抓：

  * **人眼几乎发现不了**：一列十几行数字，没人会当场心算；
  * **不影响渲染**：页面看起来完全正常；
  * **有传染性**：合计错了，下游所有引用这个合计的结论都错，而且错得很像真的；
  * **作者有动机写合计**：写合计恰恰说明他在意这个数，所以错的那一处最容易被引用。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND   仓库根既无 docs/ 也无 project/（活性，防路径写错全绿）
  E1 NO_TABLES        一张表都没扫到就拒绝判定（活性）
  E2 TOTAL_MISMATCH   合计行的某个数值列与上方分项之和不一致，且差额超出舍入容差
  W1 TOTAL_NO_NUMERIC 有合计行，但该行没有任何**可比较**的数值列（合计写成了文字 / 破折号）

## 口径（为什么这样取数）

1. **只认「行首单元格是合计词」的行**：`合计` / `总计` / `小计` / `总额` / `总合计`，
   允许带全角冒号与括号说明（`合计（元）`）。只认行首是关键——正文里「合计」二字
   出现得极多，认全表会把说明文字当合计行。
2. **合计行必须出现在分项之后**。出现在表头的（分组表头）不参与比较，直接跳过：
   本库确有「| 合计 | 分项 A | 分项 B |」这种跨列表头。
3. **容差 = 0.51 × 分项条数 + 0.5，另加 0.05% × |合计| 的相对项**。这一条不是拍的：
   每个分项按显示精度取整的最大误差是 0.5，`n` 个分项最坏累计 `0.5n`，合计自身再
   取整一次加 0.5 —— 所以「两行整数、差 1」在数学上**不能判错**（它完全可能是
   `100.5 + 249.5` 显示成 `100 + 250`）。相对项是为了放过「万元为单位、分项保留整数」
   这类大数表。**这条容差被真实语料打了两轮**：首版 0.01 绝对容差全库 E=31，
   27 条是 `138.7 + 24.3 = 163 vs 163.0` 的纯舍入差；第二版改成 0.6% 相对容差后，
   又出现「两行分项、差 1 元」被放过——那本来就不该报。
4. **一个数字列都不「加」的表直接跳过**：`| 项 | 说明 |`、`| 判据 | 怎么验 |` 这类表
   没有合计行，本来就没什么可判。
5. **只判「同行同列」**：合计行第 3 格对上方第 3 格之和。不做「跨列合并」推断——
   合并单元格在 GFM 里不存在，靠猜只会造出假错。
6. **含 `%` 的列整列跳过**。这是首轮真实语料打出来的第二条：`RiskDecision/Scorecard`
   的「坏率」列四行是 6% / 12% / 26% / 56%，合计行是 **25%**——它不是和（100%），
   而是按箱样本量加权平均（1,000 / 4,000）。比率列的「合计」天然不等于和，
   判它等于制造假错。
7. **一格里有多个数字的，整列放弃**。`4min10s`、`2h15min`、`1,000 / 3,000` 都不是
   可加量。首版把它们拼成 `410`、`215`、`10003000`，于是
   `Ops/BackupDR/DisasterRecovery` 的演练记录表报出「分项和 577 vs 合计 4,240」——
   一个纯粹由解析器造出来的错误。
8. **`—` / `-` / `N/A` / 空白一律当「无值」**，不让它把整列变成不可比较：本库很多
   合计行只在金额列有数，工时列写 `—`，这不是缺陷。
9. **不做百分比列的「应等于 100」判定**。试过，噪声太大：`占比 + 覆盖率`、「多币种
   分项」、「按口径拆的同一笔钱」都会合法地不等于 100，而它们的写法与真正的错法
   长得一模一样——**一条会大面积误报的门禁，第二天就会被整体跳过**（本仓反复验证）。

## 已知边界

  * 表格里的公式（`=SUM(...)`）不解析，按「无值」处理；
  * 分项本身跨行合并（`↑` 表示同上）不推断，按「无值」处理；
  * 只扫 `.md`，不扫 `.vitepress/` 下的 TS。

用法：

    python3 utils/audit/tablesumcheck.py              # 全库
    python3 utils/audit/tablesumcheck.py --verbose    # 展开每条明细
    python3 utils/audit/tablesumcheck.py --selftest   # 判据自测
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Optional, Tuple

TOTAL_WORDS = ("合计", "总计", "小计", "总额", "总合计", "合 计")
NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
CLEAN_RE = re.compile(r"[`*_￥¥$,\s]|元|万元|亿元|小时|分钟|人时|条|台|件|次|天|%|h|min|s\b")


def clean(cell: str) -> Optional[float]:
    """把一个单元格变成数字；变成不了就返回 None。"""
    s = cell.strip()
    if not s:
        return None
    if s in ("—", "-", "–", "－", "/", "N/A", "n/a", "无", "—"):
        return None
    s = s.replace("<br/>", " ").replace("<br>", " ")
    # 一格多个数字（`4min10s`、`2h15min`、`1,000 / 3,000`）不是可加量，直接放弃
    if len(re.findall(r"\d+(?:\.\d+)?", s)) > 1:
        return None
    s = CLEAN_RE.sub("", s)
    if not s:
        return None
    return float(s) if NUM_RE.match(s) else None


def split_row(line: str) -> List[str]:
    """按未转义的竖线切单元格。"""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells, buf, esc = [], [], False
    for ch in line:
        if esc:
            buf.append(ch)
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    cells.append("".join(buf).strip())
    return cells


def is_sep(line: str) -> bool:
    s = line.strip()
    if "-" not in s:
        return False
    return bool(re.match(r"^\|?[\s:\-|]+\|?$", s))


def is_total_row(cells: List[str]) -> bool:
    if not cells:
        return False
    head = cells[0].strip().lstrip("*").strip()
    head = re.sub(r"[（(].*?[)）]", "", head).strip()
    for w in TOTAL_WORDS:
        if head.startswith(w):
            return True
    return False


def iter_tables(text: str):
    """产出 (start_line, header_cells, rows[list[list[str]]])。"""
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n - 1:
        line = lines[i]
        if line.strip().startswith("|") and is_sep(lines[i + 1]):
            header = split_row(line)
            rows, j = [], i + 2
            while j < n and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            yield i + 1, header, rows
            i = j
        else:
            i += 1


def check_table(header: List[str], rows: List[List[str]]) -> Tuple[List[Tuple[int, str, float, float]], bool]:
    """返回 ([(列号, 列名, 分项和, 合计值)], 是否有合计行)。"""
    total_idx = [k for k, r in enumerate(rows) if is_total_row(r)]
    if not total_idx:
        return [], False
    ti = total_idx[-1]                       # 只认最后一条合计行
    prow = [k for k in range(ti) if not is_total_row(rows[k])]
    if len(prow) < 2:
        return [], True
    total_row = rows[ti]
    width = max(len(total_row), max((len(rows[k]) for k in prow), default=0))
    bad = []
    for c in range(1, min(width, len(total_row))):
        if "%" in total_row[c] or any(c < len(rows[k]) and "%" in rows[k][c] for k in prow):
            continue                          # 比率列的「合计」是加权平均，不是求和
        tv = clean(total_row[c])
        if tv is None:
            continue
        vals = [clean(rows[k][c]) for k in prow if c < len(rows[k])]
        nums = [v for v in vals if v is not None]
        if len(nums) < 2 or len(nums) < len(vals):
            continue                          # 该列不是纯数字列，不判
        s = sum(nums)
        tol = max(0.51 * len(nums) + 0.5, 0.0005 * abs(tv))
        if abs(s - tv) > tol:
            name = header[c] if c < len(header) else f"第{c+1}列"
            bad.append((c, name, s, tv))
    return bad, True


def scan(root: str, verbose: bool = False) -> int:
    if not (os.path.isdir(os.path.join(root, "docs")) or os.path.isdir(os.path.join(root, "project"))):
        print(f"E0 ROOT_NOT_FOUND: {os.path.abspath(root)}")
        return 2
    files, tables, e2, w1 = 0, 0, [], []
    for base in ("docs", "project"):
        for dirpath, _dirs, names in os.walk(os.path.join(root, base)):
            for nm in names:
                if not nm.endswith(".md"):
                    continue
                p = os.path.join(dirpath, nm)
                files += 1
                try:
                    text = open(p, encoding="utf-8").read()
                except (OSError, UnicodeDecodeError):
                    continue
                for ln, header, rows in iter_tables(text):
                    tables += 1
                    bad, has_total = check_table(header, rows)
                    rel = os.path.relpath(p, root)
                    if has_total and not bad:
                        numeric_cols = sum(
                            1 for c in range(1, len(header))
                            if sum(1 for r in rows if clean(r[c]) is not None if c < len(r)) >= 2)
                        if numeric_cols == 0:
                            w1.append((rel, ln))
                    for c, name, s, tv in bad:
                        e2.append((rel, ln, c + 1, name, s, tv))
    for rel, ln, col, name, s, tv in e2:
        print(f"E2 TOTAL_MISMATCH  {rel}:{ln}  列{col}「{name}」 分项和={s:g} 合计={tv:g} 差={s-tv:+g}")
    if verbose:
        for rel, ln in w1:
            print(f"W1 TOTAL_NO_NUMERIC  {rel}:{ln}  合计行没有可比较的数值列")
    if tables == 0:
        print("E1 NO_TABLES: 一张表都没扫到")
        return 2
    print(f"files={files} tables={tables} E={len(e2)} W1={len(w1)}")
    return 0 if not e2 else 1


CASES = [
    ("合计正确", ["| 项 | 金额 |", "| --- | --- |", "| A | 100 |", "| B | 250 |", "| 合计 | 350 |"], False),
    ("合计差 3（超出舍入）", ["| 项 | 金额 |", "| --- | --- |", "| A | 100 |", "| B | 250 |", "| 合计 | 353 |"], True),
    ("合计差 1（舍入无法排除）", ["| 项 | 金额 |", "| --- | --- |", "| A | 100 |", "| B | 250 |", "| 合计 | 351 |"], False),
    ("舍入差 0.4 放过", ["| 项 | 金额 |", "| --- | --- |", "| A | 138.7 |", "| B | 24.3 |", "| 合计 | 163 |"], False),
    ("千分位与单位", ["| 项 | 金额 |", "| --- | --- |", "| A | 1,200 元 |", "| B | 800 元 |", "| 合计 | 2,000 元 |"], False),
    ("百分比列", ["| 项 | 占比 |", "| --- | --- |", "| A | 30% |", "| B | 45% |", "| 合计 | 75% |"], False),
    ("合计行有破折号列跳过", ["| 项 | 金额 | 工时 |", "| --- | --- | --- |", "| A | 100 | 2 |", "| B | 250 | 3 |", "| 合计 | 350 | — |"], False),
    ("无合计行不判", ["| 项 | 金额 |", "| --- | --- |", "| A | 100 |", "| B | 250 |"], False),
    ("两列一列错", ["| 项 | 金额 | 工时 |", "| --- | --- | --- |", "| A | 100 | 2 |", "| B | 250 | 3 |", "| 合计 | 350 | 9 |"], True),
    ("合计行在表头不判", ["| 合计 | 分项A | 分项B |", "| --- | --- | --- |", "| 100 | 60 | 40 |"], False),
    ("分项含非数字整列跳过", ["| 项 | 金额 |", "| --- | --- |", "| A | 见附注 |", "| B | 250 |", "| 合计 | 250 |"], False),
    ("比率列合计为加权平均不判", ["| 项 | 坏率 |", "| --- | --- |", "| A | 6% |", "| B | 56% |", "| 合计 | 25% |"], False),
    ("时长多数字整列跳过", ["| 阶段 | 实际 |", "| --- | --- |", "| A | 4min10s |", "| B | 22min |", "| 合计 | 4,240 |"], False),
]


def selftest() -> int:
    ok = 0
    for idx, (desc, lines, want) in enumerate(CASES, 1):
        text = "\n".join(lines)
        got = False
        for _ln, header, rows in iter_tables(text):
            bad, _has = check_table(header, rows)
            got = bool(bad)
        mark = "PASS" if got == want else "FAIL"
        if got == want:
            ok += 1
        print(f"{mark} {idx:>2}. {desc}: got={got} want={want}")
    print(f"selftest {ok}/{len(CASES)}")
    return 0 if ok == len(CASES) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="表格合计行守恒 🔍 巡检")
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return scan(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
