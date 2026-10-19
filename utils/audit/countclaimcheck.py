#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""countclaimcheck.py —— 自述计数巡检（第 61 项巡检）

背景
----
本仓大量页面用「全书 N 章」「本专题共 N 页」这类**自述计数**给读者一个规模预期。
这些数字一旦漂移，页面读起来完全正常、构建也不报错，但读者按「10 页」去找会发现只有 9 页。
既有的巡检各管一段：
  - `chapterlistcheck` 只看目录页有没有把章节列全（顺序与条目数）；
  - `judgesumcheck` 只看判据总览表的条数；
  - `headingcheck` 只看 H1 与侧边栏标题；
没有一项问「页面上写的数字，和磁盘上的目录数是不是一回事」。

判据（E 为错误、W 为提示）
--------------------------
  E0 ROOT_NOT_FOUND        给定的根目录不存在
  E1 CHAPTER_CLAIM_MISMATCH 项目目录页「全书 N 章」与 chapter 子目录数不符
  E2 PAGE_CLAIM_MISMATCH    专题目录页「共 N 页/章」与子目录数不符
  E3 STALE_CURRENT         同一页出现多处「当前全书 N 章」且数字互不相同（旧值没删）
  W1 NO_CLAIM              有子目录但没有计数声明（不强制，只提示）
  W2 MULTI_CLAIM           同一页有多处计数声明（历史叙述允许，需人工确认最后一处是现值）

口径说明（为什么这样取数）
--------------------------
1. **只认「全书 N 章」与「共 N 页/章」两种句式**。库内存在「本章 8 页分工」「N 族 M 条判据」
   等大量近似表达，泛化会立刻产生成百上千条误报；本巡检刻意保守。
2. **chapter 子目录** = 直接子目录里排除 `assets`，且该子目录下有 `index.md`。
3. 项目目录页取**最后一处**声明为现值（历史进展段允许出现旧值），但若同时存在多处
   「当前全书」，视为旧值未清理（E3），因为「当前」只能有一个。

用法
----
    python3 utils/audit/countclaimcheck.py [--root .] [--selftest]

退出码：0 = 无 E（W 不影响退出码）；1 = 存在 E；2 = 参数或根目录错误。
"""

import argparse
import os
import re
import sys
import tempfile

CHAPTER_CLAIM = re.compile(r"全书\s*\*{0,2}\s*(\d+)\s*章")
CURRENT_CLAIM = re.compile(r"当前全书\s*\*{0,2}\s*(\d+)\s*章")
PAGE_CLAIM = re.compile(r"共\s*\*{0,2}\s*(\d+)\s*(页|章)")


def child_chapters(path):
    """直接子目录中，排除 assets 且含 index.md 的目录数。"""
    out = []
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        if not os.path.isdir(full) or name == "assets":
            continue
        if os.path.isfile(os.path.join(full, "index.md")):
            out.append(name)
    return out


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def check_project_index(path):
    """项目目录页：全书 N 章 vs 章节目录数。"""
    errs, warns = [], []
    text = read(path)
    chapters = child_chapters(os.path.dirname(path))

    all_claims = [(m.start(), int(m.group(1))) for m in CHAPTER_CLAIM.finditer(text)]
    cur_claims = [(m.start(), int(m.group(1))) for m in CURRENT_CLAIM.finditer(text)]

    if not all_claims:
        if chapters:
            warns.append(("W1", "NO_CLAIM", f"{path}: 有 {len(chapters)} 章但无「全书 N 章」声明"))
        return errs, warns

    # 现值 = 最后一处声明
    claimed = all_claims[-1][1]
    if claimed != len(chapters):
        errs.append((
            "E1", "CHAPTER_CLAIM_MISMATCH",
            f"{path}: 声明全书 {claimed} 章，实际 {len(chapters)} 个章节目录",
        ))

    if len(cur_claims) > 1 and len({v for _, v in cur_claims}) > 1:
        vals = sorted({v for _, v in cur_claims})
        errs.append((
            "E3", "STALE_CURRENT",
            f"{path}: 出现多处「当前全书」，数值互不相同 {vals}（旧值未清理）",
        ))

    if len(all_claims) > 1:
        warns.append(("W2", "MULTI_CLAIM", f"{path}: {len(all_claims)} 处计数声明（取最后一处为现值）"))
    return errs, warns


def check_topic_index(path):
    """专题目录页：共 N 页/章 vs 子页目录数。"""
    errs, warns = [], []
    text = read(path)
    children = child_chapters(os.path.dirname(path))
    claims = [(m.start(), int(m.group(1))) for m in PAGE_CLAIM.finditer(text)]
    if not claims:
        if children:
            warns.append(("W1", "NO_CLAIM", f"{path}: 有 {len(children)} 个子页但无「共 N 页」声明"))
        return errs, warns

    claimed = claims[-1][1]
    if claimed != len(children):
        errs.append((
            "E2", "PAGE_CLAIM_MISMATCH",
            f"{path}: 声明共 {claimed} 页，实际 {len(children)} 个子页目录",
        ))
    if len(claims) > 1:
        warns.append(("W2", "MULTI_CLAIM", f"{path}: {len(claims)} 处「共 N 页」声明"))
    return errs, warns


def walk(root):
    errs, warns, pages = [], [], 0
    for base in ("docs", "project"):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            errs.append(("E0", "ROOT_NOT_FOUND", f"{top} 不存在"))
            continue
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in (".vitepress", "node_modules")]
            if "index.md" not in filenames:
                continue
            pages += 1
            path = os.path.join(dirpath, "index.md")
            rel = os.path.relpath(path, root)
            # 只把 project/{Base,Complete}/<项目>/index.md 当项目目录页；
            # 分类页（project/Complete/index.md）属于目录页，按专题口径检查或跳过。
            parts = rel.split(os.sep)
            is_project = (len(parts) == 4 and parts[0] == "project"
                          and parts[1] in ("Base", "Complete"))
            e, w = (check_project_index if is_project else check_topic_index)(path)
            errs.extend(e)
            warns.extend(w)
    return pages, errs, warns


def selftest():
    """最小复现：五类判据各造一个用例。"""
    cases = []

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs"))
        proj = os.path.join(tmp, "project", "Complete", "Demo")
        os.makedirs(os.path.join(proj, "A"))
        os.makedirs(os.path.join(proj, "assets"))
        for d in ("A",):
            open(os.path.join(proj, d, "index.md"), "w").close()
        open(os.path.join(proj, "index.md"), "w", encoding="utf-8").write("全书 3 章\n")
        pages, errs, _ = walk(tmp)
        cases.append(("E1 章数不符", any(code == "E1" for code, _, _ in errs)))

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs"))
        proj = os.path.join(tmp, "project", "Complete", "Demo")
        os.makedirs(os.path.join(proj, "A"))
        open(os.path.join(proj, "A", "index.md"), "w").close()
        open(os.path.join(proj, "index.md"), "w", encoding="utf-8").write("**当前全书 1 章**\n")
        _, errs, _ = walk(tmp)
        cases.append(("E1 章数相符不报错", not errs))

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs"))
        proj = os.path.join(tmp, "project", "Complete", "Demo")
        os.makedirs(os.path.join(proj, "A"))
        open(os.path.join(proj, "A", "index.md"), "w").close()
        open(os.path.join(proj, "index.md"), "w", encoding="utf-8").write(
            "当前全书 1 章。后来当前全书 2 章。\n"
        )
        _, errs, _ = walk(tmp)
        cases.append(("E3 多处当前值冲突", any(code == "E3" for code, _, _ in errs)))

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "project"))
        top = os.path.join(tmp, "docs", "Demo")
        os.makedirs(os.path.join(top, "P1"))
        open(os.path.join(top, "P1", "index.md"), "w").close()
        open(os.path.join(top, "index.md"), "w", encoding="utf-8").write("本专题共 2 页。\n")
        _, errs, _ = walk(tmp)
        cases.append(("E2 页数与目录数不符", any(code == "E2" for code, _, _ in errs)))

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "project"))
        top = os.path.join(tmp, "docs", "Demo")
        os.makedirs(os.path.join(top, "P1"))
        open(os.path.join(top, "P1", "index.md"), "w").close()
        open(os.path.join(top, "index.md"), "w", encoding="utf-8").write("本专题目录，逐页阅读。\n")
        _, errs, warns = walk(tmp)
        cases.append(("W1 有子页无声明", any(code == "W1" for code, _, _ in warns)))

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
