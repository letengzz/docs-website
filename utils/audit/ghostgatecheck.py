#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""ghostgatecheck.py — 「注释里提到的兄弟脚本」是否真的存在 · 第 96 项巡检

为什么立这一项
--------------
本库的巡检脚本互相引用（「交给 `linkexistcheck`」「复用 `fenceutil.scan()`」这类写法），
这是好事：它让读者知道「这个维度已经有一道门了」。**但引用的是历史名就不妙了**——
门在几年前被拆分、改名或删除，注释仍写着「已有 `refcheck` 管这件事」，
于是后来的维护者以为那道门还关着，**不再人工检查，也不再补**。

第 70 项 `auditmancheck` 管的是「`DOCS_PLAN.md` 台账里写的脚本是否存在」；
本项管的是**第三个位置**：`utils/` 下脚本自己的注释与 docstring。两者是同构问题、
不同来源——台账错了会被第 70 项抓住，注释错了此前没有任何一道门看得见。

本项立起来的当场读数（第 206 天，全库 `utils/**/*.py`）：22 处引用指向不存在的脚本，
其中 8 处是**真幽灵**（`refcheck` / `verifycheck` / `dupcheck` / `linkcheck` / `judgecheck`
/ `sectioncheck` / `judgecountcheck` / `judgerefcheck`），14 处是自测夹具里的假名
（`a.py` / `beta.py` / `ghost.py`）。这两类必须分开报，否则夹具假名会把真欠账埋掉。

判据
----
E0 ROOT_NOT_FOUND   仓库根找不到 `utils/`（活性）
E1 NO_REFS          一个 `.py` 引用都没解析到（活性判据：拒绝在空集上给「全绿」）
W1 PHANTOM_SCRIPT   注释里以「已有」语气提到、但 `utils/` 下不存在的脚本（**欠账**）
W2 HISTORICAL_REF   同一处已标注「历史名 / 已移除 / 已拆分」等字样（保留，不计欠账）
W3 FIXTURE_NAME     自测夹具里的假名（`a.py` / `beta.py` 这类，按形状识别，不计欠账）

口径（四条，都来自本库语料的打磨）
----------------------------------
1. **只扫 `utils/` 下的 Python 文件**。`docs/` 与 `project/` 里出现的文件名是**读者自己
   工程里的示例脚本**（`*_smoke.py` 这类），不是本仓的脚本；把它们算成幽灵引用会一次
   产出 265 个假缺陷。
2. **「存在」按文件名比对，不按路径**。本库脚本会被移动到别的目录（`utils/audit/` 之外），
   路径变了不影响「这道门还在」这件事；按路径比对会把移动误报成删除。
3. **历史标注看同一行**。本库的写法是「`refcheck`（历史名，已拆入 `linkexistcheck`）」，
   标注与引用在同一行；只有同一行出现标注词才降级为 `W2`，避免用「文档里提过历史」
   当全局豁免——那等于给整份文件开白名单。
4. **夹具假名按形状识别**：词干长度 ≤ 3、或词干在希腊字母表里（`alpha` / `beta` /
   `gamma` / `tau` / `omega`…）、或词干是 `xxx`/`stray`/`ghost`/`fixture`/`dummy`。
   这一类在自测里是**被测对象**，不是引用，所以只统计不报欠账。

纪律
----
* **只读**：不改任何文件，不改台账。
* **不自动改名**：把 `refcheck` 换成 `linkexistcheck` 是**语义判断**（两个脚本判的判据
  不同），必须人工确认；本项只负责列出来。
* 与第 70 项的关系：`auditmancheck` 管台账、本项管注释；两者都通过，才说明「门禁的名字
  与实物在全库一致」。

用法
----
    python3 utils/audit/ghostgatecheck.py [--root .] [--verbose] [--selftest]
"""

import argparse
import os
import re
import sys
import tempfile

PY_REF = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*\.py)\b")

# 历史标注词：同一行出现即降级为 W2
HISTORY_MARKERS = (
    "历史", "已移除", "已拆分", "已拆入", "已合并", "已废弃", "已改名", "改名为", "旧名", "旧版",
)

# 自测夹具里的假名（形状识别）
GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
    "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
}
FIXTURE_STEMS = {"xxx", "stray", "ghost", "fixture", "dummy", "sample", "fake"}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".vitepress", "dist", ".workbuddy"}

# 本文件自身的自测夹具里写着大量「假的脚本名」，扫自己会产出几十条假缺陷。
# 口径：自测字符串不是引用。
SELF_NAME = os.path.basename(__file__)


def collect_existing(root):
    """收集 utils/ 下所有 .py 的文件名（按文件名比对，不按路径）。"""
    names = set()
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "utils")):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                names.add(fn)
    return names


def is_fixture(name):
    stem = name[:-3].lower()
    if stem in GREEK or stem in FIXTURE_STEMS:
        return True
    return len(stem) <= 3


def scan_file(path, existing):
    """返回 [(level, name, lineno, line)]。level ∈ {W1, W2, W3}"""
    out = []
    me = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except (OSError, UnicodeDecodeError):
        return out
    for i, line in enumerate(lines, 1):
        for m in PY_REF.finditer(line):
            name = m.group(1)
            if name == me or name in existing:
                continue
            if is_fixture(name):
                out.append(("W3", name, i, line.strip()))
            elif any(k in line for k in HISTORY_MARKERS):
                out.append(("W2", name, i, line.strip()))
            else:
                out.append(("W1", name, i, line.strip()))
    return out


def check(root, verbose=False):
    utils = os.path.join(root, "utils")
    if not os.path.isdir(utils):
        return None
    existing = collect_existing(root)
    result = {"W1": 0, "W2": 0, "W3": 0}
    issues = []
    files = 0
    refs = 0
    for dirpath, dirnames, filenames in os.walk(utils):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".py") or fn == SELF_NAME:
                continue
            files += 1
            for level, name, lineno, line in scan_file(os.path.join(dirpath, fn), existing):
                result[level] += 1
                refs += 1
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                if verbose or level == "W1":
                    issues.append((level, rel, lineno, name, line[:110]))
    return result, issues, files, refs


def build(files):
    """自测夹具：在临时目录里造 utils/ 结构。files 形如 {'utils/audit/x.py': '内容'}"""
    root = tempfile.mkdtemp(prefix="ghostgate-")
    for rel, content in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    return root


def selftest():
    cases = []

    # 1. 引用了真实存在的脚本：不报
    r = build({"utils/audit/a_check.py": '"""见 `b_check.py`。"""\n',
               "utils/audit/b_check.py": '"""b。"""\n'})
    res, issues, _, refs = check(r)
    cases.append(("存在即不报", res["W1"] == 0 and refs == 0))

    # 2. 引用不存在的脚本：W1
    r = build({"utils/audit/a_check.py": '"""交给 `refcheck.py` 管。"""\n'})
    res, _, _, _ = check(r)
    cases.append(("幽灵引用 W1", res["W1"] == 1))

    # 3. 同一行有历史标注：降级 W2
    r = build({"utils/audit/a_check.py": '"""`refcheck.py`（历史名，已拆入 linkexistcheck）。"""\n'})
    res, _, _, _ = check(r)
    cases.append(("历史标注 W2", res["W2"] == 1 and res["W1"] == 0))

    # 4. 夹具假名（单字母）：W3
    r = build({"utils/audit/a_check.py": "# 夹具：a.py 只有一行\n"})
    res, _, _, _ = check(r)
    cases.append(("夹具单字母 W3", res["W3"] == 1 and res["W1"] == 0))

    # 5. 夹具假名（希腊字母）：W3
    r = build({"utils/audit/a_check.py": "# 自测夹具 beta.py\n"})
    res, _, _, _ = check(r)
    cases.append(("夹具希腊字母 W3", res["W3"] == 1))

    # 6. 自引用不报
    r = build({"utils/audit/ghostgatecheck.py": '"""见 `nope_check.py`。"""\n'})
    res, _, _, refs = check(r)
    cases.append(("跳过本文件自身", refs == 0))

    # 7. 移动目录后仍算存在（按文件名比对）
    r = build({"utils/audit/a_check.py": '"""见 `moved.py`。"""\n',
               "utils/other/moved.py": '"""moved。"""\n'})
    res, _, _, refs = check(r)
    cases.append(("移动后仍存在", refs == 0))

    # 8. 缺 utils/ → None（由 main 报 E0）
    r = tempfile.mkdtemp(prefix="ghostgate-")
    cases.append(("缺 utils 返回 None", check(r) is None))

    # 9. 全库无引用 → refs=0（由 main 报 E1）
    r = build({"utils/audit/a_check.py": "# 没有提到任何脚本\n"})
    res, _, _, refs = check(r)
    cases.append(("无引用 refs=0", refs == 0 and res["W1"] == 0))

    # 10. 一行多个引用分别计数
    r = build({"utils/audit/a_check.py": "# x_check.py 与 y_check.py 都不存在\n"})
    res, _, _, _ = check(r)
    cases.append(("一行两引用", res["W1"] == 2))

    # 11. 非 .py 文件不扫
    r = build({"utils/audit/notes.md": "见 `ghostcheck.py`\n"})
    res, _, files, refs = check(r)
    cases.append(("非 py 不扫", refs == 0 and files == 0))

    # 12. 下划线短名不被当成夹具（长度 4，不在表内）
    r = build({"utils/audit/a_check.py": "# 见 `zzzz.py`\n"})
    res, _, _, _ = check(r)
    cases.append(("4 字母不算夹具", res["W1"] == 1 and res["W3"] == 0))

    ok = 0
    for name, passed in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok += 1 if passed else 0
    print(f"selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description="注释里提到的兄弟脚本是否存在（第 96 项）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true", help="把 W2/W3 也逐条打印")
    ap.add_argument("--summary", action="store_true", help="只打印汇总行")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    got = check(root, verbose=args.verbose)
    if got is None:
        print("E0 ROOT_NOT_FOUND（找不到 utils/）")
        return 2
    res, issues, files, refs = got
    if not args.summary:
        for level, rel, lineno, name, line in issues:
            print(f"{level}\t{rel}:{lineno}\t{name}\t{line}")
    e1 = 1 if refs == 0 else 0
    if e1 and not args.summary:
        print("E1 NO_REFS（一个 .py 引用都没解析到，路径或口径可能写错了）")
    print(
        "ghostgatecheck: files={} refs={} E={} W1={} W2={} W3={}".format(
            files, refs, e1, res["W1"], res["W2"], res["W3"]
        )
    )
    return 0 if (e1 == 0 and res["W1"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
