#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""judgecovercheck.py —— 判据族「声明 ⇄ 表」一致性巡检（第 62 项巡检）

背景
----
本仓每页开头有一段「判据族声明」，形如：

    本页判据族 `XTM-A` ~ `XTM-H`，共 8 条。定义表在第九节。

正文靠后的「判据族」一节给出定义表，每行一条。声明与表一旦对不上，**页面读起来
完全正常、构建也不报错**：读者按「8 条」去找会只找到 7 条，或者表里出现一条声明里
没有的 `-I`。

既有的三个巡检各管一段，都不问这件事：
  - `judgeidcheck`  只看**前缀是否撞号**（不同页面用了同一个前缀）；
  - `judgesumcheck` 只看**目录页总览表的条数**（"八族 64 条"）；
  - `countclaimcheck` 只看「全书 N 章 / 共 N 页」这类页数声明。
本巡检补的是**单页内部：声明 ↔ 表格** 这一段。

判据（E 为错误、W 为提示）
--------------------------
  E0 ROOT_NOT_FOUND        给定的根目录不存在
  E1 DECL_TABLE_MISSING    声明了族，但页内找不到任何 `PREFIX-X` 形式的条目行
  E2 COUNT_MISMATCH        声明「共 N 条」，去重后的条目数与 N 不符
  E3 SUFFIX_GAP            条目后缀不是从 A 起连续（缺号、跳号、乱序）
  E4 END_MISMATCH          声明写 `X-A ~ X-H`，但表内最后一条不是 H（或反之）
  E5 PREFIX_MISMATCH       同一声明里左右两个前缀不同（`AB-A ~ AC-H` 这类手误）
  W1 NO_DECL_MANY_IDS      页内出现 ≥4 条同前缀判据，但没有判据族声明
  W2 MULTI_DECL            同一页有多处判据族声明（历史叙述允许，需人工确认取值）

口径说明（为什么这样取数）
--------------------------
1. **两种行首写法都认**：`| `BR-A` |` 与 `| **`BR-A`** |`。本仓第 149 天那批页面用的是
   加粗写法，只认第一种会让 4 篇正常页面误报——这条是实测踩出来的。
2. **按去重后的后缀集合计数**，不按行数。同一页允许出现两张表（「声明表」+「判据定义表」，
   两表各 8 行），行数会是 16；重复条目本身由 `judgeidcheck` 的撞号检查覆盖。
3. **只扫 `index.md`**：判据族声明是「页面级」约定，散落在非入口文件里的判据不属于任何一页。
4. **声明取页内第一处**。若一页出现多处声明（W2），后面的多半是历史叙述或总览表述，
   人工确认第一处是现值即可。
5. **E3 只看后缀顺序，不看个数**：`A,B,D` 是缺号；`A,B,B,C` 去重后是 `A,B,C`，不算错
   （重复定义另有脚本管）。

用法
----
    python3 utils/audit/judgecovercheck.py [--root .] [--selftest] [--verbose]

退出码：0 = 无 E（W 不影响退出码）；1 = 存在 E；2 = 参数或根目录错误。
"""

import argparse
import os
import re
import string
import sys
import tempfile

DECL = re.compile(
    r"判据族[^。\n]{0,60}?"
    r"`([A-Z][A-Z0-9]{0,7})-([A-Z])`\s*[~～\-—]{1,2}\s*`([A-Z][A-Z0-9]{0,7})-([A-Z])`"
    r"([^。\n]{0,40})"
)

ROW = r"^\|\s*(?:\*\*)?\s*`{pre}-([A-Z])`\s*(?:\*\*)?\s*\|"

ID_ANY = re.compile(r"`([A-Z][A-Z0-9]{0,7})-([A-Z])`")

# 任何形式的「区间表达」：`AB-A` ~ `AB-H`。即使没用「判据族」三个字，也算已声明。
RANGE = re.compile(
    r"`([A-Z][A-Z0-9]{0,7})-([A-Z])`\s*[~～\-—]{1,2}\s*`([A-Z][A-Z0-9]{0,7})-([A-Z])`"
)

SKIP_DIRS = {".git", "node_modules", ".vitepress", "dist", "assets", ".workbuddy", "cache"}


def iter_pages(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if "index.md" in filenames:
            yield os.path.join(dirpath, "index.md")


def check_file(path):
    """返回 (errors, warnings)，每项是 (code, message)。"""
    errs, warns = [], []
    with open(path, encoding="utf-8") as f:
        s = f.read()

    decls = list(DECL.finditer(s))
    if not decls:
        # W1：既没有声明、也没有任何「区间表达」，却堆了 ≥4 条同前缀判据
        ranged = {r.group(1) for r in RANGE.finditer(s) if r.group(1) == r.group(3)}
        ranged |= {r.group(3) for r in RANGE.finditer(s) if r.group(1) == r.group(3)}
        seen = {}
        for m in ID_ANY.finditer(s):
            seen.setdefault(m.group(1), []).append(m.group(2))
        hot = {k: v for k, v in seen.items() if len(set(v)) >= 4 and k not in ranged}
        if hot:
            for pre, sfx in hot.items():
                warns.append((
                    "W1",
                    f"页内出现 {len(set(sfx))} 条 `{pre}-*` 判据但没有判据族声明（漏声明？）",
                ))
        return errs, warns

    m = decls[0]
    pre_l, first, pre_r, last, tail = m.groups()
    cn = re.search(r"共\s*(\d+)\s*条", tail)
    n = cn.group(1) if cn else None

    if len(decls) > 1:
        warns.append(("W2", f"页内共有 {len(decls)} 处判据族声明，取第一处（第 "
                            f"{s[:m.start()].count(chr(10)) + 1} 行）"))

    if pre_l != pre_r:
        errs.append(("E5", f"声明两侧前缀不同：`{pre_l}-{first}` ~ `{pre_r}-{last}`"))
        return errs, warns

    pre = pre_l
    body = s[m.end():] if not n else s[m.end():]
    hits = re.findall(ROW.format(pre=re.escape(pre)), body, re.M)
    seq = list(dict.fromkeys(hits))

    if not seq:
        errs.append(("E1", f"声明了 `{pre}-*` 族，但页内找不到 `| `{pre}-X` |` 形式的条目行"))
        return errs, warns

    if n is not None and len(seq) != int(n):
        errs.append(("E2", f"声明「共 {n} 条」，表内去重后 {len(seq)} 条：{''.join(seq)}"))

    expect = string.ascii_uppercase[: len(seq)]
    if "".join(seq) != expect:
        errs.append(("E3", f"后缀不连续：期望 {''.join(expect)}，实际 {''.join(seq)}"))

    if seq[-1] != last:
        errs.append(("E4", f"声明收在 `{pre}-{last}`，表内最后一条是 `{pre}-{seq[-1]}`"))
    if first != "A":
        errs.append(("E4", f"声明从 `{pre}-{first}` 起，判据族必须从 A 起"))

    return errs, warns


def run(root, verbose=False):
    if not os.path.isdir(root):
        print("[E0] ROOT_NOT_FOUND: " + root)
        return 2

    pages = 0
    per_code = {}
    e_cnt = w_cnt = 0
    bad_pages = 0

    for p in sorted(iter_pages(root)):
        pages += 1
        errs, warns = check_file(p)
        rel = os.path.relpath(p, root)
        if errs:
            bad_pages += 1
        for code, msg in errs:
            e_cnt += 1
            per_code.setdefault(code, []).append((rel, msg))
        for code, msg in warns:
            w_cnt += 1
            per_code.setdefault(code, []).append((rel, msg))

    # E 逐条列出；W 只列前 5 例（提示类，逐页刷屏会把 E 淹掉）
    for code in sorted(per_code):
        items = per_code[code]
        limit = len(items) if code.startswith("E") else (len(items) if verbose else 5)
        for rel, msg in items[:limit]:
            print(f"[{code}] {rel}: {msg}")
        if limit < len(items):
            print(f"[{code}] …另有 {len(items) - limit} 条同类提示（--verbose 全列）")

    print(f"\n扫描 {pages} 个 index.md；E={e_cnt}（涉及 {bad_pages} 页）W={w_cnt}")
    return 0 if e_cnt == 0 else 1


def selftest():
    """最小复现：七类判据各造一个用例，一条正常页作为对照。"""
    cases = [
        # (文件名, 内容, 期望命中的 code 集合)
        ("ok.md", """# T

本页判据族 `AB-A` ~ `AB-H`，共 8 条。定义表在第八节。

| 编号 | 判据 |
| --- | --- |
""" + "".join(f"| `AB-{c}` | x |\n" for c in string.ascii_uppercase[:8]), set()),
        # 加粗写法必须认（第 149 天那批页面）
        ("bold.md", """# T

## 八、判据族声明（`CD-A` ~ `CD-H`）

| 编号 | 判据 |
| --- | --- |
""" + "".join(f"| **`CD-{c}`** | x |\n" for c in string.ascii_uppercase[:8]), set()),
        # E1：声明了但没有表
        ("e1.md", "本页判据族 `EF-A` ~ `EF-H`，共 8 条。\n\n这里没有表。\n", {"E1"}),
        # E2：声明 8 条，表里 7 条
        ("e2.md", "本页判据族 `GH-A` ~ `GH-H`，共 8 条。\n\n| 编号 |\n| --- |\n"
         + "".join(f"| `GH-{c}` |\n" for c in string.ascii_uppercase[:7]), {"E2", "E4"}),
        # E3：缺号（A,B,D）
        ("e3.md", "本页判据族 `IJ-A` ~ `IJ-D`，共 3 条。\n\n| 编号 |\n| --- |\n"
         "| `IJ-A` |\n| `IJ-B` |\n| `IJ-D` |\n", {"E3"}),
        # E4：声明 H，表停 G
        ("e4.md", "本页判据族 `KL-A` ~ `KL-H`，共 7 条。\n\n| 编号 |\n| --- |\n"
         + "".join(f"| `KL-{c}` |\n" for c in string.ascii_uppercase[:7]), {"E4"}),
        # E5：左右前缀不同
        ("e5.md", "本页判据族 `MN-A` ~ `MO-H`，共 8 条。\n\n| 编号 |\n| --- |\n| `MN-A` |\n",
         {"E5"}),
        # W1：没有声明但堆了 4 条
        ("w1.md", "| 编号 |\n| --- |\n" + "".join(f"| `OP-{c}` |\n" for c in "ABCD"), set()),
        # W2：两处声明
        ("w2.md", "本页判据族 `QR-A` ~ `QR-H`，共 8 条。\n\n后文又说 判据族 `QR-A` ~ `QR-H` 共 8 条。\n\n"
         "| 编号 |\n| --- |\n" + "".join(f"| `QR-{c}` |\n" for c in string.ascii_uppercase[:8]), set()),
    ]

    ok = 0
    with tempfile.TemporaryDirectory() as d:
        for name, content, expect in cases:
            sub = os.path.join(d, name.replace(".md", ""))
            os.makedirs(sub, exist_ok=True)
            with open(os.path.join(sub, "index.md"), "w", encoding="utf-8") as f:
                f.write(content)
            errs, warns = check_file(os.path.join(sub, "index.md"))
            got = {c for c, _ in errs}
            want_w = {"W1"} if name == "w1.md" else ({"W2"} if name == "w2.md" else set())
            got_w = {c for c, _ in warns}
            good = got == expect and got_w == want_w
            ok += good
            print(f"  {'PASS' if good else 'FAIL'} {name}: E={sorted(got)} "
                  f"W={sorted(got_w)} 期望 E={sorted(expect)} W={sorted(want_w)}")

    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description="判据族「声明 ⇄ 表」一致性巡检")
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    return run(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
