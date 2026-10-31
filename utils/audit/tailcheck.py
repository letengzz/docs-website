#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tailcheck.py —— 「页面收尾结构」巡检（第 225 天新立，第 107 项巡检）

## 动机

`AGENTS.md` 第 5 节把「验证方式」和「参考资料」列为每页必备模块，但这两节都在页面**末尾**，
而末尾恰恰是最容易被顺手截断的地方：写到判据清单就收笔、复制模板时把尾节删掉、或者在
参考资料之后又追加了一节新内容（于是「参考资料」不再是最后一节，读者再也找不到权威链接）。

现有五十多项巡检各管一段，没有一项问这件事：

  * `emptysectioncheck`（第 103 项）  问「这一节是不是空的」；
  * `verifyevidencecheck`（第 99 项）  问「这条实测声明有没有可执行的验证」；
  * `sectionordercheck`              问序号小节（`## 五、`）的顺序；
  * `headingcheck` / `levelskipcheck`  问标题唯一性与层级。

也就是说：**一节都没有**和**一节是空的**是两件事，后者有人管，前者没人管。

## 判据

  E0 ROOT_NOT_FOUND   既无 docs/ 也无 project/
  E1 NO_PAGES         一页都没扫到（活性判据：拒绝在空集上判「全绿」）
  E2 VERIFY_AFTER_REF 「验证 / 自查 / 验收」小节出现在参考资料**之后**（顺序反了）
  W1 NO_REF           整页没有「参考资料」级小节
  W2 NO_VERIFY        整页没有「验证 / 自查 / 验收 / 自测」类小节
  W3 REF_EMPTY        参考资料小节下没有任何列表项、链接或反引号

## 口径（刻意保守）

  * 只扫 `docs/` 与 `project/` 下的 `*.md`；`DOCS_PLAN.md` / `AGENTS.md` 是台账与规则，不在范围内。
  * **只判 H2 与 H3**：H4 以下的小节名常是「验证一下这条 SQL」，不是页面级模块。
  * **页内不足 60 行不判**：`AGENTS.md` 已把 60 行以下定义为「未完成」，未完成页缺尾节是预期内的，
    重复报一遍只会淹没真问题。
  * **大类目录页（`docs/<分类>/index.md`）不判**：按规范它只放「分类名 + 子目录链接」，本就不该有验证节。
  * 代码围栏内不扫（示例里的 `## 参考资料` 是文本，不是结构）。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

MIN_LINES = 60
FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^##\s+(.*?)\s*$")
H3 = re.compile(r"^###\s+(.*?)\s*$")
REF_WORDS = ("参考资料", "参考文献", "延伸阅读")
VERIFY_WORDS = ("验证", "自查", "验收", "自测", "如何验证")
LISTY = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\[[^\]]+\]\(|>\s)")


def strip_fences(text: str) -> list[tuple[int, str]]:
    """返回 [(行号, 行内容)]，代码围栏内的行被替换为空行（保留行号对齐）。"""
    out, inside = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            out.append((i, ""))
            continue
        out.append((i, "" if inside else line))
    return out


def scan_page(path: str) -> tuple[list[tuple[str, str, str]], dict[str, int]]:
    """返回 (findings, counters)。findings 元素为 (severity, code, relpath, detail)。"""
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    lines = raw.splitlines()
    counters = {"pages": 0, "with_ref": 0, "with_verify": 0, "skipped": 0}
    if len(lines) < MIN_LINES:
        counters["skipped"] = 1
        return [], counters

    stripped = strip_fences(raw)
    heads: list[tuple[int, int, str]] = []  # (行号, 级别, 标题)
    for ln, line in stripped:
        m2, m3 = H2.match(line), H3.match(line)
        if m2:
            heads.append((ln, 2, m2.group(1)))
        elif m3:
            heads.append((ln, 3, m3.group(1)))
    if not heads:
        return [], counters

    ref_idx = None
    ver_idx = None
    for pos, (ln, lvl, title) in enumerate(heads):
        if ref_idx is None and any(w in title for w in REF_WORDS):
            ref_idx = pos
        if ver_idx is None and any(w in title for w in VERIFY_WORDS):
            ver_idx = pos

    counters["pages"] = 1
    counters["with_ref"] = 1 if ref_idx is not None else 0
    counters["with_verify"] = 1 if ver_idx is not None else 0

    findings: list[tuple[str, str, str, str]] = []
    if ref_idx is None:
        findings.append(("W", "NO_REF", path, "整页没有「参考资料」小节"))
        return findings, counters
    if ver_idx is None:
        findings.append(("W", "NO_VERIFY", path, "整页没有「验证 / 自查 / 验收」小节"))
    elif ver_idx > ref_idx:
        findings.append(("E", "VERIFY_AFTER_REF", path,
                         f"「{heads[ver_idx][2]}」出现在「{heads[ref_idx][2]}」之后"))

    # W3：参考资料小节内是否有实质内容（到下一个 H2/H3 或文末为止）
    start = heads[ref_idx][0]
    end = len(lines) + 1
    for ln, _lvl, _t in heads[ref_idx + 1:]:
        end = ln
        break
    body = [line for ln, line in stripped if start < ln < end]
    has_item = any(LISTY.match(line) for line in body) or any("`" in line for line in body)
    if not has_item:
        findings.append(("W", "REF_EMPTY", path, "参考资料小节下没有列表项、链接或反引号"))
    return findings, counters


def walk(root: str) -> list[str]:
    paths = []
    for base in ("docs", "project"):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, _dirnames, filenames in os.walk(top):
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                full = os.path.join(dirpath, fn)
                # 大类目录页：docs/<分类>/index.md
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                if rel.count("/") == 2 and rel.endswith("/index.md"):
                    continue
                paths.append(full)
    return sorted(paths)


def report(root: str) -> int:
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND  仓库根既无 docs/ 也无 project/")
        return 2
    paths = walk(root)
    if not paths:
        print("E1 NO_PAGES  没有扫到任何 markdown 页面")
        return 2

    findings: list[tuple[str, str, str, str]] = []
    pages = with_ref = with_verify = skipped = 0
    for p in paths:
        f, c = scan_page(p)
        findings.extend(f)
        pages += c["pages"]
        with_ref += c["with_ref"]
        with_verify += c["with_verify"]
        skipped += c["skipped"]

    order = {"E": 0, "W": 1}
    findings.sort(key=lambda x: (order[x[0]], x[1], x[2]))
    for sev, code, path, detail in findings[:200]:
        print(f"{sev}{order[sev]} {code:18s} {os.path.relpath(path, root)} :: {detail}")
    e = sum(1 for f in findings if f[0] == "E")
    w = len(findings) - e
    print(f"pages={pages} skipped={skipped} with_ref={with_ref} with_verify={with_verify} E={e} W={w}")
    return 1 if e else 0


CASES = [
    ("ok-minimal",
     "# T\n" + "\n".join(f"正文第 {i} 行，凑足 60 行。" for i in range(56)) + "\n## 验证方式\n跑一下\n\n## 参考资料\n- [a](./b.md)\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("no-ref",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 验证方式\n跑一下\n",
     {"NO_REF": 1, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("no-verify",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 参考资料\n- x\n",
     {"NO_REF": 0, "NO_VERIFY": 1, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("verify-after-ref",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 参考资料\n- x\n\n## 验证方式\n跑\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 1}),
    ("ref-empty",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 验证方式\n跑\n\n## 参考资料\n\n（待补）\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 1, "VERIFY_AFTER_REF": 0}),
    ("ref-in-fence",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(54)) + "\n## 验证方式\n跑\n\n```md\n## 参考资料\n- x\n```\n",
     {"NO_REF": 1, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("h3-verify",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(56)) + "\n### 如何验证\n跑\n\n## 参考资料\n- x\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("h4-not-counted",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(56)) + "\n#### 验证一下这条 SQL\n跑\n\n## 参考资料\n- x\n",
     {"NO_REF": 0, "NO_VERIFY": 1, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("short-page-skipped",
     "# T\n## 验证方式\n跑\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("ref-backtick-only",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 验证方式\n跑\n\n## 参考资料\n`UBL 2.x`\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("ref-word-variant",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 验证方式\n跑\n\n## 延伸阅读\n- x\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
    ("verify-word-variant",
     "# T\n" + "\n".join(f"正文第 {i} 行。" for i in range(58)) + "\n## 验收清单\n- x\n\n## 参考资料\n- x\n",
     {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}),
]


def _run(td: str, body: str) -> dict[str, int]:
    p = os.path.join(td, "docs", "X", "index.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    findings, _c = scan_page(p)
    got = {"NO_REF": 0, "NO_VERIFY": 0, "REF_EMPTY": 0, "VERIFY_AFTER_REF": 0}
    for _sev, code, _p, _d in findings:
        got[code] = got.get(code, 0) + 1
    return got


def selftest() -> int:
    ok = total = 0
    for name, body, want in CASES:
        total += 1
        with tempfile.TemporaryDirectory() as td:
            got = _run(td, body)
            if got == want:
                ok += 1
            else:
                print(f"FAIL {name}: got={got} want={want}")
    # 活性判据：短页必须被跳过，而不是被当成「全绿」
    total += 1
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "docs", "X", "index.md")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write("# T\n")
        f2, c2 = scan_page(p)
        if c2["skipped"] == 1 and c2["pages"] == 0 and not f2:
            ok += 1
        else:
            print(f"FAIL activity: skipped={c2['skipped']} pages={c2['pages']} f={f2}")
    # 大类目录页排除：docs/A/index.md 不进扫描集合
    total += 1
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "docs", "A"), exist_ok=True)
        open(os.path.join(td, "docs", "A", "index.md"), "w", encoding="utf-8").write("# A\n- [x](X/index.md)\n")
        os.makedirs(os.path.join(td, "docs", "A", "X"), exist_ok=True)
        open(os.path.join(td, "docs", "A", "X", "index.md"), "w", encoding="utf-8").write("# X\n" * 70)
        paths = walk(td)
        if len(paths) == 1 and paths[0].endswith("A/X/index.md"):
            ok += 1
        else:
            print(f"FAIL category-root: {paths}")
    print(f"selftest {ok}/{total} {'PASS' if ok == total else 'FAIL'}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return report(a.root)


if __name__ == "__main__":
    sys.exit(main())
