#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""codegapcheck.py —— 行内代码与中文之间的间距巡检（第 109 项巡检，第 227 天新立）

## 动机（本仓「某个维度整体没人看」的第 N 次）

上一项巡检 `punctspacecheck`（第 108 项）专门管「中文标点与中英文间距」，但它的
docstring 第 1 条口径就把自己的一大块语料**主动剥掉**了：

> **先剥代码，再判标点。** 围栏代码块、行内代码、链接目标、裸 URL、HTML 标签
> 里的半角标点是正确写法，判了会立刻造出上万条噪声。

这个取舍是对的——不剥就是灾难。但它留下了一个**恰好被剥掉**的格子：

    「安装nvm后需要执行`nvm use xxx`进行安装」

半角标点没有、中英之间也没有（`执行` 与反引号之间就是没有空格），
`punctspacecheck` 看不见它，因为它先把 `` `nvm use xxx` `` 整段挖掉，
左右两个中文就变成了「执行」与「进行」，中间空无一物。

于是本库最常见的排版问题之一——**行内代码紧贴中文**——落在了两道门之间：
`headingcheck` 管结构、`linkexistcheck` 管链接、`punctspacecheck` 管标点，
**没有一道在看「代码与文字的交界」**。本项补这一段。

## 判据（E = 错误，W = 提示）

  E0 ROOT_NOT_FOUND     给定根目录不存在（活性判据）
  E1 NO_PAGES           一个 Markdown 都没扫到（活性判据，防「路径写错全绿」）
  E2 ODD_BACKTICK       单行内反引号总数为奇数（行内代码没闭合）
  W1 TIGHT_PRE_CJK      行内代码**前面**紧贴中文字符
  W2 TIGHT_NEXT_CJK     行内代码**后面**紧贴中文字符
  W3 TIGHT_LATIN        行内代码紧贴拉丁字母（`the `config`file` 这类）
  N1 SPANS              识别到的行内代码段数
  N2 CJK_PAGES          含中文的页面数（分母）

## 六条口径（每一条都是被真实语料逼出来的）

1. **E2 才是 E，其余全是 W。** 「代码与中文之间要不要空格」是**排版偏好**：
   本库两种写法都有，且都不影响渲染、不影响复制、不影响搜索。把它判成 E，
   这道门会在首轮就被关掉。而**反引号没闭合**是另一回事：它会让同一行后半段
   整段变成代码，`| 表格 | 单元格 |` 里的竖线也一起变色，是**渲染缺陷**。
2. **只认中文相邻，不认全角标点相邻。** 「执行 `ls`，然后」里反引号后面紧跟
   `，` 是**正确**写法（全角标点前不加空格），判了就是 100% 误报。
3. **W3 只认字母，不认数字。** 「第 `1` 页」与「第 `1`页」在中文里都通行，
   数字与代码之间的空格属风格；字母不同：`the `config`file` 一定少一个空格。
4. **一段代码只报一次。** 两侧都紧贴时，W1 与 W2 各记一条（它们是两个独立的
   修改点），但同侧的多次命中只记一次——否则一个 10 处的表格会刷出 20 条。
5. **围栏内一律不看。** 代码块里的反引号是代码，不是排版。
6. **E2 用「先剔成对、再看残留」判定，不用奇偶。** 直接数一行里反引号的奇偶，
   会把 `` ` ```markdown ` ``（代码里写着三个反引号）与 ```` ```` ```ts ```` ````
   （四个反引号包着三个）全判成未闭合——这两类在本库各有几十处，且都是
   **正确写法**。先 `SPAN.sub("")` 把成对段整段剔掉，残留才算没闭合。

## 为什么统计「分母」

本库 2,800 页里行内代码的密度差异极大：`AGENTS.md` 型页面几乎每两行一个，
叙事型页面整页没有。只报绝对数会让人误以为「问题很严重」，因此同时输出
`spans`（总段数）与 `cjk_pages`（含中文页数），比例才有意义。

用法：
    python3 codegapcheck.py                 # 默认扫 docs/ 与 project/
    python3 codegapcheck.py [根目录...]
    python3 codegapcheck.py --selftest
    python3 codegapcheck.py --verbose --summary
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

CJK_CHAR = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
LATIN = re.compile(r"[A-Za-z]")
FENCE = re.compile(r"^\s*(?:[-*+]\s+|\d{1,3}[.)]\s+)?(`{3,}|~{3,})")
SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
HTMLTAG = re.compile(r"</?[A-Za-z][^>]{0,200}>")
URL = re.compile(r"https?://[^\s`\"'<>()\[\]]+")


def strip_noise(line: str) -> str:
    """把不该判的东西换成等长空白，保持列位置不变。"""
    line = HTMLTAG.sub(lambda m: " " * len(m.group(0)), line)
    line = URL.sub(lambda m: " " * len(m.group(0)), line)
    return line


def scan_line(line: str):
    """返回 (spans, [warnings])，warnings 是 (kind, col, snippet)。"""
    warns = []
    spans = 0
    for m in SPAN.finditer(line):
        body = m.group(2)
        if "`" in body:
            continue
        spans += 1
        start, end = m.start(), m.end()
        prev = line[start - 1] if start > 0 else ""
        nxt = line[end] if end < len(line) else ""
        if prev and CJK_CHAR.match(prev):
            warns.append(("W1", start, line[max(0, start - 8):min(len(line), end + 4)]))
        if nxt and CJK_CHAR.match(nxt):
            warns.append(("W2", end, line[max(0, start - 4):min(len(line), end + 8)]))
        if prev and LATIN.match(prev):
            warns.append(("W3", start, line[max(0, start - 8):min(len(line), end + 4)]))
        if nxt and LATIN.match(nxt):
            warns.append(("W3", end, line[max(0, start - 4):min(len(line), end + 8)]))
    return spans, warns


def iter_pages(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in
                           {".git", "node_modules", ".vitepress", "dist", "assets", "public", ".workbuddy"}]
            for name in sorted(filenames):
                if name.endswith(".md"):
                    yield os.path.join(dirpath, name)


def audit_text(text: str):
    """对一份 Markdown 文本跑判据，返回 dict（供 --selftest 与主流程共用）。"""
    res = {"spans": 0, "E2": 0, "W1": 0, "W2": 0, "W3": 0, "details": []}
    in_fence = False
    for lineno, raw in enumerate(text.splitlines(), 1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = strip_noise(raw)
        # 先剔掉所有成对的行内代码，剩下的反引号就是没闭合的
        if "`" in SPAN.sub("", line):
            res["E2"] += 1
            res["details"].append((lineno, "E2", 0, raw[:80]))
            continue
        spans, warns = scan_line(line)
        res["spans"] += spans
        for kind, col, snippet in warns:
            res[kind] += 1
            res["details"].append((lineno, kind, col, snippet))
    return res


def run(roots, verbose=False, summary=False):
    for root in roots:
        if not os.path.isdir(root):
            print(f"E0 ROOT_NOT_FOUND {root}")
            return 2
    pages = list(iter_pages(roots))
    if not pages:
        print("E1 NO_PAGES")
        return 2

    totals = {"spans": 0, "E2": 0, "W1": 0, "W2": 0, "W3": 0}
    cjk_pages = 0
    per_page = []
    for path in pages:
        try:
            text = open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        res = audit_text(text)
        if CJK_CHAR.search(text):
            cjk_pages += 1
        for k in totals:
            totals[k] += res[k]
        hit = res["E2"] + res["W1"] + res["W2"] + res["W3"]
        if hit:
            per_page.append((path, res))

    for path, res in sorted(per_page, key=lambda x: -(x[1]["E2"] * 10 + x[1]["W1"] + x[1]["W2"])):
        print(f"{path}: E2={res['E2']} W1={res['W1']} W2={res['W2']} W3={res['W3']}")
        if verbose:
            for lineno, kind, col, snippet in res["details"][:5]:
                print(f"    {kind} L{lineno}: {snippet.strip()}")

    print(f"pages={len(pages)} cjk_pages={cjk_pages} spans={totals['spans']} "
          f"E={totals['E2']} W1={totals['W1']} W2={totals['W2']} W3={totals['W3']}")
    if summary and totals["spans"]:
        w = totals["W1"] + totals["W2"] + totals["W3"]
        print(f"density: {w}/{totals['spans']} = {w / totals['spans'] * 100:.2f}% 段有问题")
    return 0 if totals["E2"] == 0 else 1


CASES = [
    # (说明, 文本, 期望)
    ("紧贴中文前置", "执行`ls` 看看\n", {"W1": 1, "W2": 0}),
    ("紧贴中文后置", "执行 `ls`看看\n", {"W1": 0, "W2": 1}),
    ("两侧都空", "执行 `ls` 看看\n", {}),
    ("全角标点相邻不算", "执行 `ls`，然后\n", {}),
    ("反引号紧跟括号不算", "（`ls`）\n", {}),
    ("拉丁字母紧贴", "the `config`file\n", {"W3": 1}),
    ("数字紧贴不算", "第`1`页\n", {"W1": 1}),
    ("围栏内不判", "```\n执行`ls`看看\n```\n", {}),
    ("单行反引号奇数", "这里有 `没闭合\n", {"E2": 1}),
    ("双反引号成对", "`` code `tick` `` 后面\n", {}),
    ("HTML 标签豁免", "<br/>执行 `ls` 看看\n", {}),
    ("URL 豁免", "见 https://a.b/c 然后 `ls` 结束\n", {}),
    ("表格里也判", "| 行 | 执行`ls` 看 |\n", {"W1": 1}),
    ("空文本", "", {}),
]


def selftest():
    ok = 0
    for msg, text, expect in CASES:
        res = audit_text(text)
        good = all(res[k] == v for k, v in expect.items()) and \
            (("E2" in expect) or res["E2"] == 0)
        if good:
            ok += 1
        else:
            print(f"FAIL {msg}: got E2={res['E2']} W1={res['W1']} W2={res['W2']} W3={res['W3']}, want {expect}")
    # 目录级：临时目录里放两个文件，验证聚合与 E1
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as f:
            f.write("执行`ls` 看看\n")
        with open(os.path.join(tmp, "b.md"), "w", encoding="utf-8") as f:
            f.write("正常 `ls` 文本\n")
        pages = list(iter_pages([tmp]))
        agg = {"W1": 0}
        for p in pages:
            agg["W1"] += audit_text(open(p, encoding="utf-8").read())["W1"]
        if len(pages) == 2 and agg["W1"] == 1:
            ok += 1
        else:
            print(f"FAIL dir aggregation: pages={len(pages)} W1={agg['W1']}")
    empty = tempfile.mkdtemp()
    if not list(iter_pages([empty])):
        ok += 1
    else:
        print("FAIL empty dir should yield no pages")
    total = len(CASES) + 2
    print(f"selftest {ok}/{total}")
    return 0 if ok == total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    roots = args.roots or [r for r in ("docs", "project") if os.path.isdir(r)]
    sys.exit(run(roots or ["."], args.verbose, args.summary))


if __name__ == "__main__":
    main()
