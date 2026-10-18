#!/usr/bin/env python3
"""judgesumcheck.py —— 专题目录页「判据总览表」与各页「本页判据族」声明的一致性巡检。

为什么需要它：
  judgecheck 校验单页内「声明 = 定义表条数」，但它不看**专题目录页那张总览表**。
  于是目录页写「本专题十页共 80 条」，而十页实际各声明 8 条却只有九页——总数对不上，
  读者按目录页的 80 去核对，永远核不出来。这一类缺陷在构建时完全静默。

判据：
  E0 ROOT_NOT_FOUND        扫描根不存在
  E1 NO_TOPICS             活性：一个专题都没找到，拒绝判定（防「扫错目录全绿」）
  E2 DECLARED_NOT_LISTED   某页声明了判据族，但目录页总览表里没有这一族
  E3 COUNT_MISMATCH        目录页该族「条数」≠ 该族所在页面的声明条数
  E4 LISTED_NOT_DECLARED   目录页列了这一族，但专题下没有任何页面声明它
  W1 NO_COUNT              目录页表格行里取不到「条数」（列序可能不对）

用法：
  python3 utils/audit/judgesumcheck.py [--root docs project] [--selftest]
退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

DECL = re.compile(r"本页判据族[^`]*`([A-Z][A-Z0-9]*)-A`[^`]*~[^`]*`\1-H`[^，,]*[，,]?\s*共\s*(\d+)\s*条")
FAM = re.compile(r"`([A-Z][A-Z0-9]*)-A`\s*~\s*`([A-Z][A-Z0-9]*)-H`")
BARE = re.compile(r"^`([A-Z][A-Z0-9]{1,8})`$")
PURE = re.compile(r"^\*{0,2}(\d{1,3})\s*条?\*{0,2}$")


def read(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def scan(root: str):
    """返回 {专题目录: {"rows": {family: count}, "decls": {family: (count, relpath)}}}"""
    topics: dict[str, dict] = {}
    for dirpath, _dirs, files in os.walk(root):
        if "index.md" not in files:
            continue
        idx = os.path.join(dirpath, "index.md")
        text = read(idx)
        rows: dict[str, tuple[int, str]] = {}
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            m = FAM.search(" | ".join(cells))
            fam = ""
            if m and m.group(1) == m.group(2):
                fam = m.group(1)
            else:
                for c in cells:
                    bm = BARE.match(c)
                    if bm:
                        fam = bm.group(1)
                        break
            if not fam:
                continue
            # 列序不固定（库内存在四种写法），因此按「内容」找条数：最后一个纯数字单元格
            cnt = -1
            for c in reversed(cells):
                pm = PURE.match(c)
                if pm:
                    cnt = int(pm.group(1))
                    break
            rows[fam] = (cnt, cells[0])
        if not rows:
            continue
        subs = [x for x in sorted(os.listdir(dirpath))
                if os.path.isdir(os.path.join(dirpath, x)) and x != "assets"
                and os.path.isfile(os.path.join(dirpath, x, "index.md"))]
        if len(subs) < 1:
            continue        # 没有子页面 = 这是一个叶子页，不是专题目录
        decls: dict[str, tuple[int, str]] = {}
        legacy: set[str] = set()
        any_fam: set[str] = set()   # 只统计子页面，不统计目录页自身（否则会把「列了但没声明」洗掉）
        for sub in subs:
            page = os.path.join(dirpath, sub, "index.md")
            if not (os.path.isdir(os.path.join(dirpath, sub)) and os.path.isfile(page)):
                continue
            if sub == "assets":
                continue
            body = read(page)
            any_fam |= set(re.findall(r"`([A-Z][A-Z0-9]*)-[A-H]`", body))
            found = DECL.findall(body)
            for fam, cnt in found:
                decls[fam] = (int(cnt), f"{sub}/index.md")
            if not found:
                for fam in FAM.findall(body):
                    if fam[0] == fam[1]:
                        legacy.add(fam[0])
        topics[dirpath] = {"rows": rows, "decls": decls, "legacy": legacy,
                           "any_fam": any_fam, "index": idx}
    return topics


def check(topics):
    errs, warns = [], []
    for d, t in sorted(topics.items()):
        rows, decls = t["rows"], t["decls"]
        for fam, (cnt, label) in rows.items():
            if cnt < 0:
                warns.append(("W1", t["index"], f"{fam} 行取不到条数（列序应为 页面|族|约定|条数）"))
                continue
            if fam not in decls:
                if fam in t.get("legacy", set()) or fam in t.get("any_fam", set()):
                    warns.append(("W2", t["index"],
                                  f"`{fam}` 只有旧格式判据表、没有「本页判据族」声明行（无法参与求和核对）"))
                else:
                    errs.append(("E4", t["index"], f"`{fam}` 列在总览表（{label}）但专题下无页面声明它"))
            elif decls[fam][0] != cnt:
                errs.append(("E3", t["index"], f"`{fam}` 表里 {cnt} 条，{decls[fam][1]} 声明 {decls[fam][0]} 条"))
        for fam, (cnt, rel) in decls.items():
            if fam not in rows:
                errs.append(("E2", os.path.join(d, rel), f"声明 `{fam}`（{cnt} 条）但目录页总览表没有这一族"))
    return errs, warns


def selftest() -> int:
    cases = 0
    ok = 0

    def mk(tmp, idx_rows, pages):
        os.makedirs(tmp, exist_ok=True)
        with open(os.path.join(tmp, "index.md"), "w", encoding="utf-8") as f:
            f.write("# 示例专题\n\n| 页面 | 判据族 | 覆盖的约定 | 条数 |\n| --- | --- | --- | --- |\n")
            for r in idx_rows:
                f.write(r + "\n")
        for name, body in pages.items():
            os.makedirs(os.path.join(tmp, name), exist_ok=True)
            with open(os.path.join(tmp, name, "index.md"), "w", encoding="utf-8") as f:
                f.write(body)

    decl = "本页判据族 `{f}-A` ~ `{f}-H`，共 {n} 条。定义表在第九节。\n"
    row = "| {p} | `{f}-A` ~ `{f}-H` | 约定 | {n} |"

    # 1 一致：无 E
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, [row.format(p="总览", f="AAA", n=8), row.format(p="实战", f="BBB", n=8)],
           {"Overview": decl.format(f="AAA", n=8), "Practice": decl.format(f="BBB", n=8)})
        e, w = check(scan(tmp))
        cases += 1; ok += (len(e) == 0)

    # 2 条数不符 → E3
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, [row.format(p="总览", f="AAA", n=8)],
           {"Overview": decl.format(f="AAA", n=7)})
        e, _ = check(scan(tmp))
        cases += 1; ok += any(x[0] == "E3" for x in e)

    # 3 列了但没人声明 → E4
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, [row.format(p="总览", f="AAA", n=8), row.format(p="实战", f="CCC", n=8)],
           {"Overview": decl.format(f="AAA", n=8)})
        e, _ = check(scan(tmp))
        cases += 1; ok += any(x[0] == "E4" for x in e)

    # 4 声明了但没列 → E2
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, [row.format(p="总览", f="AAA", n=8)],
           {"Overview": decl.format(f="AAA", n=8), "Extra": decl.format(f="DDD", n=8)})
        e, _ = check(scan(tmp))
        cases += 1; ok += any(x[0] == "E2" for x in e)

    # 5 活性：空目录不判定（topics 为空）
    with tempfile.TemporaryDirectory() as tmp:
        e, w = check(scan(tmp))
        cases += 1; ok += (len(e) == 0)

    print(f"selftest {ok}/{cases} PASS")
    return 0 if ok == cases else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="*", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    roots = [r for r in a.root if os.path.isdir(r)]
    if not roots:
        print("E0 ROOT_NOT_FOUND", a.root)
        return 1
    topics = {}
    for r in roots:
        topics.update(scan(r))
    if not topics:
        print("E1 NO_TOPICS（活性失败：一个专题都没找到，拒绝判定）")
        return 1
    errs, warns = check(topics)
    for code, path, msg in errs + warns:
        print(f"{code} {path}: {msg}")
    print(f"topics={len(topics)} E={len(errs)} W={len(warns)}")
    if warns and all(w[0] == "W1" for w in warns):
        print("  （W1 全部为「行里找不到纯数字条数」——多半是列序里用了「8 条」以外的写法）")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
