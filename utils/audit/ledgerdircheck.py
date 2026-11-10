#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""ledgerdircheck.py —— 「台账声称建成的目录，磁盘上到底有没有」（第 143 项巡检）

## 动机：台账是本库唯一的进度真相，而它从来自证

`DOCS_PLAN.md` 的轮换表是 300 多行、每行一句「✅（新建 `docs/...`）」。这句话同时
承担三种职能：进度记录、范围声明、给下一次运行的输入。它一旦写错，后面所有判断
都会跟着错——而它**没有任何一道门在看**。

既有巡检都在看「实物」：`linkexistcheck` 管正文链接、`sidebarcheck` 管配置链接、
`indexcovercheck` 管目录页清单、`judgeidcheck` 管判据编号。**没有一项把台账与磁盘
对起来。** 于是可以出现这样的状态：轮换表标 ✅、写满 800 字的实测读数、侧边栏挂着
「页面待补」，而 `docs/Backend/ThatTopic` 在磁盘与全部 git 历史里都不存在。

这不是假想。本项首次运行时全库命中 **2 条**，两条都是「台账先写、实物后做」，其中
一条连侧边栏占位都没有（`LoanServicing`），另一条有占位（`AMLCompliance`）。它们的
共同点是**构建全绿**：没有页面就没有链接，没有链接就没有断链。

## 判据

  E0 ROOT_NOT_FOUND      仓库根或 DOCS_PLAN.md 找不到
  E1 NO_ROWS             一行轮换表都没解析到（正则失效时拒绝判绿）
  E2 CLAIM_MISSING       台账里以反引号声明的路径在磁盘上不存在
  E3 CLAIM_MISSING_DONE  同上，且该行标了 ✅（「已完成」与「不存在」直接矛盾）
  （标「待补 / 待写」的行按计划处理，不参与 E2/E3：待建路径本来就不该存在）
  W1 CASE_MISMATCH       只在大小写上不匹配（macOS 大小写不敏感，构建会假绿）
  N1 ROWS / N2 CLAIMS / N3 OK

## 口径（两轮，全部被真实语料打回）

1. **只认反引号里的路径**。首版把正文里所有 `docs/xxx` 形态的字符串都算成声明，
   一次报出 17 条，逐条打开全是**跨专题引用**（「留在 `RiskDecision`」）与**举例**
   （`docs/A/...`）。声明必须长成 `` `docs/Backend/Xxx` `` 这样、以反引号定界。
2. **只认 `docs/` 与 `project/` 开头**。台账里还有 `../docs/...`、`/docs/...` 与
   `*.md` 形态，它们不是「目录声明」。
3. **`W1` 必须按父目录逐字符比对**：`os.path.exists` 在 macOS 上大小写不敏感，
   `docs/Backend/graphrelation` 会返回真，而站点构建在 Linux 上会 404。

## 被否决的判据（如实记录）

`W2 NO_CLAIM_IN_DONE`：标 ✅ 但没写反引号路径的行。全库 **83 条**，全是早期「已沉淀至
`project/...`」或纯文字行——它们是**写法差异**，不是缺陷，实现后会长期刷屏，故删除。

`W3 ORPHAN_DIR`：磁盘上有目录、台账里没有对应行。首版跑出 **31 条**，全部是
`assets/`、并行会话当日新增、以及只改了子页没动轮换表的正常情况。**「台账漏记」
与「目录多余」是两件事，混在一起只会刷屏**，故不实现。
"""
import argparse
import os
import re
import sys
import tempfile

ROW_RE = re.compile(r"^\|\s*(\d{1,3})\s*\|\s*([^|]*)\|(.*)$")
CLAIM_RE = re.compile(r"`((?:docs|project)/[A-Za-z0-9_./\-]+)`")
DONE_MARK = "✅"


def _exists_exact(root, rel):
    """逐级按磁盘真实名字比对，识别大小写漂移。"""
    cur = root
    for part in rel.strip("/").split("/"):
        try:
            names = os.listdir(cur)
        except OSError:
            return "missing"
        if part in names:
            cur = os.path.join(cur, part)
        elif part.lower() in {n.lower() for n in names}:
            return "case"
        else:
            return "missing"
    return "ok"


def check(root, list_all=False):
    plan = os.path.join(root, "DOCS_PLAN.md")
    errs, warns, counts = [], [], {"rows": 0, "claims": 0, "ok": 0}
    if not os.path.isdir(root):
        return [("E", "E0", "DOCS_PLAN.md", 0, "root not found")], warns, counts
    if not os.path.isfile(plan):
        return [("E", "E0", "DOCS_PLAN.md", 0, "plan not found")], warns, counts

    with open(plan, encoding="utf-8") as f:
        lines = f.readlines()

    for no, line in enumerate(lines, 1):
        m = ROW_RE.match(line.rstrip("\n"))
        if not m:
            continue
        body = line
        counts["rows"] += 1
        # 显式标「待补 / 待写」的行是计划，不是声明：路径写在反引号里也只是待建目标
        if "待补" in body or "待写" in body:
            continue
        claims = sorted(set(CLAIM_RE.findall(body)))
        if not claims:
            continue
        done = DONE_MARK in body
        for c in claims:
            rel = c.rstrip("/")
            if rel.endswith(".md"):
                continue
            counts["claims"] += 1
            st = _exists_exact(root, rel)
            if st == "ok":
                counts["ok"] += 1
            elif st == "case":
                warns.append(("W", "W1", "DOCS_PLAN.md", no, f"case mismatch: {rel}"))
            else:
                code = "E3" if done else "E2"
                errs.append(("E", code, "DOCS_PLAN.md", no,
                             f"{'done but missing' if done else 'claimed missing'}: {rel}"))
    if counts["rows"] == 0:
        errs.append(("E", "E1", "DOCS_PLAN.md", 0, "no rotation rows parsed"))
    return errs, warns, counts


CASES = [
    ("done_row_ok", "| 1 | Backend | 主题 ✅（新建 `docs/Backend/A`） | 章节 |\n", set()),
    ("done_row_missing", "| 2 | Backend | 主题 ✅（新建 `docs/Backend/Ghost`） | 章节 |\n", {"E3"}),
    ("pending_row_missing", "| 3 | Backend | 主题 ⬜（`docs/Backend/Later`） | 章节 |\n", {"E2"}),
    ("inline_ref_not_claim", "| 4 | Backend | 主题（留在 `RiskDecision`） | 章节 |\n", set()),
    ("no_backtick_no_claim", "| 5 | Backend | 主题（新建 docs/Backend/X） | 章节 |\n", set()),
    ("pending_marker_exempt", "| 6 | Backend | 主题 ⚠️ **待补**（原标「已完成」，新建 `docs/Backend/Ghost`） | 章节 |\n", set()),
]


def selftest():
    tmp = os.path.join(tempfile.gettempdir(), "ledgerdir-selftest")
    passed = 0
    for idx, (name, row, want) in enumerate(CASES, 1):
        d = os.path.join(tmp, name)
        os.makedirs(os.path.join(d, "docs", "Backend", "A"), exist_ok=True)
        with open(os.path.join(d, "DOCS_PLAN.md"), "w", encoding="utf-8") as f:
            f.write("# plan\n\n| 天 | 分类 | 主题 | 章节 |\n| --- | --- | --- | --- |\n" + row)
        errs, warns, _ = check(d)
        got = {code for _, code, *_ in errs}
        ok = got == want
        passed += 1 if ok else 0
        print(("PASS " if ok else "FAIL ") + f"{idx:02d} {name} want={sorted(want)} got={sorted(got)}")
    print(f"selftest {passed}/{len(CASES)}")
    return 0 if passed == len(CASES) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    errs, warns, counts = check(os.path.abspath(a.root))
    for c, code, path, line, detail in errs:
        print(f"{c} {code} {path}:{line} {detail}")
    if a.list:
        for c, code, path, line, detail in warns:
            print(f"{c} {code} {path}:{line} {detail}")
    print(f"rows={counts['rows']} claims={counts['claims']} ok={counts['ok']} "
          f"E={len(errs)} W={len(warns)}")
    print("RESULT", "OK" if not errs else "FAIL", "EXIT=" + ("0" if not errs else "1"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
