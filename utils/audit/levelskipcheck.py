#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""levelskipcheck.py —— 标题层级跳级巡检（第 85 项）。

为什么要有这一项
----------------
本仓与标题相关的门只有两道：

  * `headingcheck.py`   —— 一页有没有 H1、有没有多个 H1；
  * `sectionnumcheck.py` —— `## 一、` `## 二、` 这类**分节序号**是否连续。

两者都不看**层级**。于是下面这种结构能一路绿灯：

    # 页面标题
    ## 一、总览
    #### 关键细节        ← H2 直接跳到 H4，中间的 H3 不存在

它带来的不是渲染错误，而是三件更难发现的事：

1. **右侧 outline 断裂**：站点 `outline` 配置为 `[2, 6]`，H4 会出现在目录里，
   但它与 H2 之间没有任何从属关系——读者看到的是「和 H2 同级」的条目；
2. **锚点层级失真**：`#关键细节` 的 slug 与它的父级无关，页面内跳转能对上，
   但「这一段属于谁」这个信息在 HTML 里丢了；
3. **插入新内容时无处可放**：想给 H4 补一个「上一级」，只能把整段降级，
   而降级会改掉所有锚点——于是没人改，结构就永久歪着。

本项补的就是「**层级是否逐级递进**」这一个维度。

判据
----
E0 ROOT_NOT_FOUND     扫描根不存在
E1 NO_PAGES           一个 Markdown 都没扫到（活性：拒绝在空集上给全绿）
E2 LEVEL_SKIP         标题层级跳级（如 H2 → H4），跳过的层数 > 0
E3 MULTI_H1           H1 之后又出现 H1（`headingcheck` 已查，这里只做交叉验证）
W1 START_DEEP         页面第一个标题不是 H1 而是 H2/H3（缺页名）
W2 TOO_DEEP           出现 H5 / H6（outline 上限 6，但到 5 层通常说明该拆页）
W3 SETEXT             使用了 `===` / `---` 下划线式标题（与 ATX 混用会让 outline 错位）

刻意不查的
----------
* 代码围栏与其中的 `# 注释`（shell / python / yaml 的注释就是 `#`）；
* `:::` 容器内部的 `#`（本仓容器内不用标题语法，出现即为误写，由 `containercheck` 管）；
* frontmatter 的 `---`（只认行首且上一行是空行或文本行的下划线式标题，且长度 ≥ 3）。

用法
----
    python3 utils/audit/levelskipcheck.py [根目录 ...] [--quiet]
    python3 utils/audit/levelskipcheck.py --selftest

退出码：0 = 无 E 级；1 = 有 E 级；2 = 用法错误。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

ATX = re.compile(r"^(#{1,6})\s+\S")
SETEXT = re.compile(r"^(=+|-+)\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})([^`]*)$")


def parse(text: str):
    """返回 (headings, setext, h1_count)。headings = [(行号, 层级, 文字)]。"""
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                i = j + 1
                break

    heads: list[tuple[int, int, str]] = []
    setext: list[tuple[int, str]] = []
    in_fence = False
    marker = ""
    prev_text = ""
    prev_ln = 0
    for idx in range(i, len(lines)):
        line = lines[idx]
        ln = idx + 1
        fm = FENCE.match(line)
        if not in_fence:
            if fm:
                in_fence, marker, info = True, fm.group(1), fm.group(2)
                prev_text = ""
                continue
        else:
            # 只有「同字符、长度不短于开启标记」的整行才算闭合；
            # 4 反引号围栏里嵌 3 反引号的写法必须靠这一条才不误判
            if (fm and not fm.group(2).strip() and fm.group(1)[0] == marker[0]
                    and len(fm.group(1)) >= len(marker)):
                in_fence = False
            prev_text = ""
            continue
        m = ATX.match(line)
        if m:
            heads.append((ln, len(m.group(1)), line[m.end(1):].strip()))
            prev_text = ""
            continue
        if SETEXT.match(line) and len(line.strip()) >= 3 and prev_text:
            setext.append((ln, prev_text[:40]))
            prev_text = ""
            continue
        stripped = line.strip()
        # 段落行才算候选标题文字：排除列表、表格、引用、容器、缩进代码
        if stripped and not stripped.startswith(("#", "-", "*", "|", ">", ":", "    ")):
            prev_text, prev_ln = stripped, ln
        else:
            prev_text = ""
    return heads, setext


def scan(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    hs, setext = parse(text)

    e2, e3, w1, w2, w3 = [], [], [], [], []

    if hs:
        first_ln, first_lv, first_tx = hs[0]
        if first_lv != 1:
            w1.append((first_ln, f"首个标题是 H{first_lv}：{first_tx}"))
        prev_lv = first_lv
        seen_h1 = first_lv == 1
        for ln, lv, tx in hs[1:]:
            if lv == 1:
                if seen_h1:
                    e3.append((ln, f"第二个 H1：{tx}"))
                seen_h1 = True
            elif lv - prev_lv > 1:
                e2.append((ln, f"H{prev_lv} → H{lv}，跳过 H{prev_lv + 1}：{tx}"))
            if lv >= 5:
                w2.append((ln, f"H{lv}：{tx}"))
            prev_lv = lv

    for ln, tx in setext:
        w3.append((ln, f"下划线式标题：{tx}"))

    return {"e2": e2, "e3": e3, "w1": w1, "w2": w2, "w3": w3, "heads": len(hs)}


def run(roots: list[str], quiet: bool) -> int:
    pages = 0
    errors = 0
    warns = 0
    for root in roots:
        if not os.path.isdir(root):
            print(f"E0 ROOT_NOT_FOUND {root}")
            return 1
        for dp, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "assets", ".vitepress", ".workbuddy")]
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                pages += 1
                p = os.path.join(dp, fn)
                r = scan(p)
                for tag, key, code in (("E2", "e2", "LEVEL_SKIP"), ("E3", "e3", "MULTI_H1")):
                    for ln, msg in r[key]:
                        errors += 1
                        print(f"{tag} {code} {p}:{ln}  {msg}")
                for tag, key, code in (("W1", "w1", "START_DEEP"), ("W2", "w2", "TOO_DEEP"), ("W3", "w3", "SETEXT")):
                    for ln, msg in r[key]:
                        warns += 1
                        if not quiet:
                            print(f"{tag} {code} {p}:{ln}  {msg}")
    if pages == 0:
        print("E1 NO_PAGES 没有扫到任何 Markdown（拒绝在空集上判定）")
        return 1
    print(f"pages={pages} E={errors} W={warns}")
    return 0 if errors == 0 else 1


SELFTEST_CASES = [
    ("# A\n\n## B\n\n### C\n", 0, 0),
    ("# A\n\n#### D\n", 1, 0),
    ("# A\n\n## B\n\n#### D\n", 1, 0),
    ("# A\n\n## B\n\n```sh\n# 注释\n#### 不是标题\n```\n", 0, 0),
    ("# A\n\n## B\n\n## C\n", 0, 0),
    ("## B\n\n# A\n", 0, 1),
    ("# A\n\n# B\n", 1, 0),
    ("# A\n\n## B\n\n##### E\n", 1, 1),
    ("# A\n\n标题\n===\n\n## B\n", 0, 1),
    ("---\ntitle: x\n---\n\n# A\n\n## B\n", 0, 0),
]


def selftest() -> int:
    ok = 0
    for i, (src, want_e, want_w) in enumerate(SELFTEST_CASES, 1):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(src)
            r = scan(p)
            e = len(r["e2"]) + len(r["e3"])
            w = len(r["w1"]) + len(r["w2"]) + len(r["w3"])
            if len(r["e3"]) > 0 and want_e == 0:
                pass
            good = (e, w) == (want_e, want_w)
            if not good:
                print(f"FAIL case {i}: want E={want_e} W={want_w}, got E={e} W={w}")
                print(repr(src))
            else:
                ok += 1
    print(f"selftest {ok}/{len(SELFTEST_CASES)}")
    return 0 if ok == len(SELFTEST_CASES) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=["docs", "project"])
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(a.roots or ["docs", "project"], a.quiet)


if __name__ == "__main__":
    sys.exit(main())
