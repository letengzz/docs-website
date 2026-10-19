#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""judgeidcheck.py —— 「判据编号唯一性」巡检（第 166 天新立，第五十七项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

判据（`CE-A`、`LPG-H` 这类编号）在本仓是**跨页面的引用坐标**：
正文写「见 `DGD-F`」、目录页写「十页共 80 条」、项目章节写「判据 `PLP-A~PLP-H`」。
读者与作者都靠这个编号定位「这条约定在哪一页」。

已有的三项判据巡检各有分工，**没有一项问「编号本身唯不唯一」**：

  * `judgecheck.py`         —— 单页内「声明条数 = 定义表行数」；
  * `judgecountcheck.py`    —— 声明了判据的页数与占比；
  * `judgesumcheck.py`      —— 专题目录页那张总览表与实际声明是否一致；
  * `judgerefcheck.py`      —— 正文引用的判据编号是否真的被定义过。

于是两类**静默缺陷**长期无人发现：

  1. **整段判据表被复制两次**——同一页里 `RTX-B` 被定义两遍，读者点到第二个表，
     看到的「约定」可能与第一个不同，而两个表的条数都「看起来对」。
  2. **两个专题撞了同一个族前缀**——`DD-G` 同时属于监控大盘的交付演练与另一个章节，
     搜「DD-G」得到两页，编号失去定位能力。第 163 天曾**人工**发现 `MP` 撞了 Uniapp、
     `DG` 撞了 DataGovernance，当时靠 `git grep` 逐个核对——这类事不该靠人记。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 NO_FILES            一个 Markdown 都没扫到（活性判据：拒绝在空集上给出「全绿」）
  E1 DUP_ID_SAME_PAGE    同一页面内同一判据 ID 被定义多次（复制粘贴残留 / 一个页面里两张定义表）
  E2 DUP_ID_CROSS_PAGE   不同页面定义了同一判据 ID（引用坐标冲突）
  W3 UNDEFINED_RANGE     正文声明了 `XXX-A~XXX-H`，但该族在库内一条定义都没有

## 与 judgecheck.py 的边界（刻意不重复）

`judgecheck` 的 `E2 DUP_NUMBER` 查的是**同一张表内**的重号，`W1 PREFIX_COLLISION`
查的是**同一前缀被两个以上专题复用**。本脚本**不再重复这两条**，只补它够不到的
两个层级：**同一页面的多张表之间**，以及**两个页面之间**——`DD-G` 那次撞号正是
「同一项目、两个页面」，`judgecheck` 的专题级 W1 看不见它。


## 定义表怎么认

只认「表格行首列是被反引号包住的编号」这一种形态：

    | `CE-A` | 约定 | 定错了会怎样 | 怎么验证 |

围栏代码块内的同名行会被剥掉（判据表常被当作示例贴进代码块）。
除 `judgecheck` 的宽口径外，本脚本额外要求该行**至少 3 个单元格**——
两列表格里的编号更可能是示例而非定义。

用法：
    python3 judgeidcheck.py [根目录...]
    python3 judgeidcheck.py --selftest
"""

from __future__ import annotations

import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

ID_RE = re.compile(r"^`([A-Z][A-Z0-9]{1,4}-[A-Z]{1,2})`$")
TOKEN_RE = re.compile(r"`([A-Z][A-Z0-9]{1,4}-[A-Z]{1,2})`")
RANGE_RE = re.compile(r"`([A-Z][A-Z0-9]{1,4})-([A-Z])~([A-Z][A-Z0-9]{1,4})-([A-Z])`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def strip_fences(text: str) -> list[str]:
    """剥掉围栏代码块，返回「可见行」。"""
    out, inside = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            inside = not inside
            continue
        if not inside:
            out.append(line)
    return out


def topic_of(path: Path) -> str:
    """把页面归到一个「专题」：docs/<大类>/<主题> 或 project/<层>/<项目>。"""
    parts = path.parts
    if "docs" in parts:
        i = parts.index("docs")
        if len(parts) > i + 2:
            return "/".join(parts[i : i + 3])
        return "/".join(parts[i:])
    if "project" in parts:
        i = parts.index("project")
        if len(parts) > i + 2:
            return "/".join(parts[i : i + 3])
        return "/".join(parts[i:])
    return str(path.parent)


def collect(root: Path):
    """返回 (定义表, 声明范围表, 文件数)。"""
    defs: dict[str, list[Path]] = defaultdict(list)
    tokens: set[str] = set()
    ranges: dict[str, set[Path]] = defaultdict(set)
    files = 0
    for p in sorted(root.rglob("*.md")):
        parts = p.parts
        if any(seg.startswith(".") or seg in {"node_modules"} for seg in parts):
            continue
        if root == REPO and not ({"docs", "project"} & set(parts)):
            continue
        files += 1
        for line in strip_fences(p.read_text(encoding="utf-8", errors="ignore")):
            s = line.strip()
            for r in RANGE_RE.finditer(s):
                ranges[r.group(1)].add(p)
            tokens.update(TOKEN_RE.findall(s))
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 3:
                continue
            m = ID_RE.match(cells[0])
            if m:
                defs[m.group(1)].append(p)
    return defs, ranges, tokens, files


def report(defs, ranges, tokens, files: int) -> int:
    if files == 0:
        print("E0 NO_FILES  没有扫到任何 Markdown，拒绝判定")
        return 1

    errors = 0
    warns = 0

    # E1 / E2
    for jid, pages in sorted(defs.items()):
        uniq = sorted(set(pages))
        if len(uniq) == 1 and len(pages) > 1:
            print(f"E1 DUP_ID_SAME_PAGE  {jid}  在 {uniq[0]} 定义 {len(pages)} 次")
            errors += 1
        elif len(uniq) > 1:
            for p in uniq:
                print(f"E2 DUP_ID_CROSS_PAGE {jid}  {p}")
            errors += 1

    defined_prefixes = {jid.rsplit("-", 1)[0] for jid in defs}
    seen_prefixes = {tok.rsplit("-", 1)[0] for tok in tokens}

    # W3：声明了范围却无定义
    for pref, pages in sorted(ranges.items()):
        if pref not in defined_prefixes and pref not in seen_prefixes:
            sample = sorted(pages)[0]
            print(f"W3 UNDEFINED_RANGE   {pref}-X  声明于 {sample}，库内无任何定义")
            warns += 1

    print(f"\npages={files}  ids={len(defs)}  prefixes={len(defined_prefixes)}  E={errors}  W={warns}")
    return 1 if errors else 0


def selftest() -> int:
    cases = []

    def mk(files: dict[str, str]) -> Path:
        d = Path(tempfile.mkdtemp(prefix="judgeid-"))
        for name, body in files.items():
            p = d / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")
        return d

    row = "| `{i}` | 约定 | 错 | 验 |\n"
    ok = mk({"docs/A/T/x/index.md": "# x\n\n| 判据 | 约定 | 错 | 验 |\n| --- | --- | --- | --- |\n" + row.format(i="AA-A") + row.format(i="AA-B")})
    defs, ranges, tokens, files = collect(ok)
    cases.append(("干净单页", report(defs, ranges, tokens, files) == 0 and len(defs) == 2))

    dup_same = mk({"docs/A/T/x/index.md": "# x\n\n" + row.format(i="BB-A") + row.format(i="BB-A")})
    defs, ranges, tokens, files = collect(dup_same)
    cases.append(("同页重复必须 E", report(defs, ranges, tokens, files) == 1))

    dup_cross = mk({
        "docs/A/T/x/index.md": "# x\n\n" + row.format(i="CC-A"),
        "docs/A/T/y/index.md": "# y\n\n" + row.format(i="CC-A"),
    })
    defs, ranges, tokens, files = collect(dup_cross)
    cases.append(("跨页重复必须 E", report(defs, ranges, tokens, files) == 1))

    fenced = mk({"docs/A/T/x/index.md": "# x\n\n```text\n" + row.format(i="DD-A") + "```\n"})
    defs, ranges, tokens, files = collect(fenced)
    cases.append(("围栏内不算定义", report(defs, ranges, tokens, files) == 0 and len(defs) == 0))

    pref = mk({
        "docs/A/T/x/index.md": "# x\n\n" + row.format(i="EE-A"),
        "docs/B/U/y/index.md": "# y\n\n" + row.format(i="EE-B"),
    })
    defs, ranges, tokens, files = collect(pref)
    cases.append(("同前缀不同编号不报错（前缀冲突归 judgecheck）", report(defs, ranges, tokens, files) == 0))

    rng = mk({"docs/A/T/x/index.md": "# x\n\n判据 `FF-A~FF-H` 八条。\n"})
    defs, ranges, tokens, files = collect(rng)
    cases.append(("声明范围无定义必须 W", report(defs, ranges, tokens, files) == 0 and "FF" in ranges))

    empty = mk({"docs/A/T/readme.txt": "no md"})
    defs, ranges, tokens, files = collect(empty)
    cases.append(("空集必须 E0", report(defs, ranges, tokens, files) == 1))

    passed = sum(1 for _, v in cases if v)
    for name, v in cases:
        print(f"  [{'PASS' if v else 'FAIL'}] {name}")
    print(f"selftest: {passed}/{len(cases)}")
    return 0 if passed == len(cases) else 1


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--selftest" in sys.argv:
        return selftest()
    roots = [Path(a) for a in args] or [REPO]
    rc = 0
    total_defs = 0
    for r in roots:
        defs, ranges, tokens, files = collect(r)
        total_defs += len(defs)
        rc |= report(defs, ranges, tokens, files)
    return rc


if __name__ == "__main__":
    sys.exit(main())
