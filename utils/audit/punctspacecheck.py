#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""punctspacecheck.py —— 中文标点与中英文间距巡检（第 226 天新立，第 108 项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

本库关于「一句话怎么写」的门已经有七道，**全部围绕结构与语义**：

  * `headingcheck` / `levelskipcheck` / `sectionnumcheck` / `sectionordercheck`
    —— 标题唯一性、层级、编号、末节；
  * `leadparagraphcheck` / `emptysectioncheck` / `placeholdercheck`
    —— 导语、空小节、占位词；
  * `nearthdupcheck` / `paradupcheck` —— 句子与段落的重复。

七道全绿的页面，可以写出「使用PostgreSQL,然后执行 migrate」这种句子：
**半角逗号夹在中文里、中英文之间没有空格**。构建不报错（Markdown 合法）、
链接全通、判据齐全、单测全绿——它只是**读起来不像中文技术文档**。

这类缺陷的代价不是「不好看」，而是**搜索与朗读**：
「PostgreSQL」与「使用」黏在一起，编辑器双击选不中、语音合成会连读成一个词；
半角逗号会让部分排版引擎按西文规则断行，中文句子里出现奇怪的断点。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND     给定根目录不存在（活性判据）
  E1 NO_PAGES           一个 Markdown 都没扫到（活性判据，防「路径写错全绿」）
  E2 NO_TEXT            剥掉代码与链接后没有一个可比字符（活性判据）
  W1 HALF_PUNCT_CJK     半角 , . ; : ? ! 紧邻中文字符（中文句子里用西文标点）
  W2 NO_SPACE_LATIN     中文字符紧邻拉丁字母，两侧无空格
  W3 SPACE_AFTER_FW     全角标点后紧跟一个空格（「， 然后」）
  N1 CJK_CHARS          可比中文字符数
  N2 MIX_RUNS           中英混排边界数（= W1 + W2 的候选总量，用于看比例）

## 五条口径（每一条都是被真实语料逼出来的）

1. **先剥代码，再判标点。** 围栏代码块、行内代码、链接目标、裸 URL、HTML 标签
   里的半角标点是**正确写法**，判了会立刻造出上万条噪声。本库 2,800 页里
   行内代码极多（`W1`、`ORDER BY`），不剥就是一场灾难。
2. **W1 只看「紧邻中文」的半角标点。** `1,000`、`3.13.12`、`index.md` 里的标点
   两侧都不是中文字符，天然不触发；`，` 与半角 `,` 混用才是要报的那一类。
3. **W2 只认拉丁字母，不认数字。** 「12 个月」与「12个月」在本库都有，
   数字与中文之间的空格是**风格**不是**规则**（中英混排规范里数字常不空格），
   判了会造出数千条「可能是故意的」提示。字母不同：`PostgreSQL数据库` 一定少一个空格。
4. **不判「全角括号里包西文」与「中文引号方向」**：前者是排版偏好，后者在
   源码里无法稳定区分，判了只会让这道门在第二次运行时被关掉。
5. **W3 单独成档，不并入 W1**：全角标点后多一个空格在不同编辑器里表现不同
   （有的会被吞掉），属「看见就改、不改也能读」的长尾。

用法：
    python3 punctspacecheck.py [根目录...]
    python3 punctspacecheck.py --selftest
    python3 punctspacecheck.py --verbose --summary
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

CJK = (
    "\u4e00-\u9fff"          # 基本区
    "\u3400-\u4dbf"          # 扩展 A
    "\u3000-\u303f"          # 中文标点（不含在「中文字符」判定里，见下）
)
CJK_CHAR = re.compile(f"[{CJK}]")
CJK_ONLY = re.compile(f"[\\u4e00-\\u9fff\\u3400-\\u4dbf]")
LATIN = re.compile(r"[A-Za-z]")
HALF_PUNCT = ",.;:?!"
FW_PUNCT = "，。；：？！、）】》」』”’…"

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`+[^`]*`+")
HTML_TAG = re.compile(r"<[^>]{1,200}>")
MD_LINK_TARGET = re.compile(r"\]\([^)]*\)")
BARE_URL = re.compile(r"https?://[^\s)>\]]+")


def strip_code(text: str) -> str:
    """剥掉围栏代码块、行内代码、链接目标、裸 URL、HTML 标签，保留行结构。"""
    out = []
    fence = None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence is None and m:
            fence = m.group(2)[0] * 3
            out.append("")
            continue
        if fence is not None:
            if line.strip().startswith(fence):
                fence = None
            out.append("")
            continue
        out.append(line)
    s = "\n".join(out)
    s = INLINE_CODE.sub(" CODE ", s)
    s = MD_LINK_TARGET.sub("] ", s)
    s = BARE_URL.sub(" URL ", s)
    s = HTML_TAG.sub(" ", s)
    return s


def scan(text: str):
    """返回 (w1, w2, w3, cjk, mix)。text 需已 strip。"""
    w1 = w2 = w3 = 0
    cjk = 0
    details = []
    n = len(text)
    for i, ch in enumerate(text):
        if CJK_ONLY.match(ch):
            cjk += 1
            prev = text[i - 1] if i > 0 else ""
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt and nxt in HALF_PUNCT:
                # 「中文,」——半角标点紧跟中文
                w1 += 1
                details.append(("W1", text[max(0, i - 12):i + 12]))
            if prev and prev in HALF_PUNCT and prev != ".":
                # 「,中文」（句点豁免：`3.13.12中文` 里的点常是版本号残留，交给 W1 的另一侧判）
                w1 += 1
                details.append(("W1", text[max(0, i - 12):i + 12]))
            if nxt and LATIN.match(nxt):
                w2 += 1
                details.append(("W2", text[max(0, i - 12):i + 12]))
            if prev and LATIN.match(prev):
                w2 += 1
                details.append(("W2", text[max(0, i - 12):i + 12]))
        elif ch in FW_PUNCT:
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt == " " and i + 2 < n and CJK_ONLY.match(text[i + 2] or ""):
                w3 += 1
                details.append(("W3", text[max(0, i - 12):i + 12]))
    return w1, w2, w3, cjk, w1 + w2, details


def iter_pages(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in {".vitepress", "node_modules", ".git", "public"}]
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def run(roots, verbose=False, summary=False):
    pages = 0
    total = {"W1": 0, "W2": 0, "W3": 0}
    cjk_total = 0
    mix_total = 0
    hits = []
    for path in iter_pages(roots):
        pages += 1
        try:
            raw = open(path, encoding="utf-8").read()
        except OSError:
            continue
        body = strip_code(raw)
        w1, w2, w3, cjk, mix, details = scan(body)
        cjk_total += cjk
        mix_total += mix
        total["W1"] += w1
        total["W2"] += w2
        total["W3"] += w3
        if w1 or w2 or w3:
            hits.append((path, w1, w2, w3, details[:3]))
    if pages == 0:
        print("E1 NO_PAGES  一个 Markdown 都没扫到")
        return 1
    if cjk_total == 0:
        print("E2 NO_TEXT   剥掉代码后没有一个可比字符")
        return 1
    for path, w1, w2, w3, details in hits if verbose else []:
        for kind, ctx in details:
            print(f"{kind} {path}: …{ctx.strip()}…")
    if summary:
        for path, w1, w2, w3, _ in sorted(hits, key=lambda x: -(x[1] + x[2] + x[3]))[:20]:
            print(f"  {w1:4d} {w2:4d} {w3:4d}  {path}")
    print(f"pages={pages} cjk={cjk_total} mix={mix_total} "
          f"W1_HALF_PUNCT={total['W1']} W2_NO_SPACE_LATIN={total['W2']} W3_SPACE_AFTER_FW={total['W3']}")
    return 0


def selftest():
    cases = [
        ("干净页", "使用 PostgreSQL 数据库，然后执行迁移。", 0, 0, 0),
        ("半角逗号", "使用 PostgreSQL,然后执行迁移。", 1, 0, 0),
        ("半角句号", "执行完毕.然后核对结果。", 1, 0, 0),
        ("缺空格", "使用PostgreSQL数据库。", 0, 2, 0),
        ("右侧缺空格", "配置好之后运行migrate命令。", 0, 2, 0),
        ("全角后空格", "先备份， 然后迁移。", 0, 0, 1),
        ("数字与中文不报", "共 12 个月，分 3 期。", 0, 0, 0),
        ("围栏内不报", "```sql\nSELECT a,b FROM t;\n```\n正文正常。", 0, 0, 0),
        ("行内代码不报", "字段 `a,b` 与 `x=1;y=2` 都是示例。", 0, 0, 0),
        ("URL 不报", "访问 https://example.com/a,b?x=1 查看。", 0, 0, 0),
        ("链接目标不报", "见 [文档](../a,b/index.md) 一节。", 0, 0, 0),
        ("英文句子里不报", "The quick brown fox, jumps over.", 0, 0, 0),
        ("HTML 属性不报", '<img src="./a,b.png" style="zoom:75%;" /> 图片。', 0, 0, 0),
        ("版本号不报", "Python 3.13.12 与 SQLite 3.50.4。", 0, 0, 0),
        ("中文引号不报", "他说「这样不行」，然后走了。", 0, 0, 0),
    ]
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        for name, body, e1, e2, e3 in cases:
            p = os.path.join(td, "case.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(body + "\n")
            w1, w2, w3, _, _, _ = scan(strip_code(body + "\n"))
            good = (w1 == e1 and w2 == e2 and w3 == e3)
            print(("PASS" if good else "FAIL"), name, f"got W1={w1} W2={w2} W3={w3} want {e1}/{e2}/{e3}")
            ok += 1 if good else 0
        print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=[])
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    roots = a.roots or ([a.root] if a.root else ["."])
    if not all(os.path.isdir(r) for r in roots):
        print("E0 ROOT_NOT_FOUND", roots)
        return 1
    return run(roots, a.verbose, a.summary)


if __name__ == "__main__":
    sys.exit(main())
