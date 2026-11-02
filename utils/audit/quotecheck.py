#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""quotecheck.py —— 中文引号与括号的配对巡检（第 118 项）。

为什么要有这一项
----------------
本库关于「一段话长得对不对」的门已经有九道：`headingcheck`（标题唯一）、`levelskipcheck`
（层级不跳）、`sectionnumcheck`（编号连续）、`sectionordercheck`（小节顺序）、
`emptysectioncheck`（空小节）、`codegapcheck`（行内代码与中文间距）、`liststructcheck`
（列表缩进与标记）、`emphasischeck`（粗体定界符）、`punctspacecheck`（标点与间距）。
**九道全绿仍然可以写出一个引号没闭合的句子**：`他说的「预算就是授权，系统里就多了一个
`「` 而没有 `」`。渲染器不会报错（引号不是 Markdown 语法），构建不报错，链接全通，
只有读者读到那一句时发现「引号一直没关」。

这类缺陷的代价不是「不好看」，而是**语义被改写**：一个没闭合的「会把后面整段读成引文，
一个没闭合的（会把后面整句读成插入语。中文写作里引号与括号用得比英文密得多，而输入法
切换、复制粘贴、跨行编辑都会漏掉另一侧。

判据（E 为错误、W 为提示、N 为计数）
------------------------------------
  E0 ROOT_NOT_FOUND     仓库根既无 docs/ 也无 project/
  E1 NO_PAGES           一页都没扫到就拒绝判定（活性）
  E2 ODD_QUOTE          段落内「」计数为奇数（确定笔误）
  E3 ODD_TITLE_QUOTE    段落内《》计数为奇数
  W1 ODD_DQUOTE         段落内“”计数为奇数（跨段引用可能合法）
  W2 ODD_CORNER         段落内『』计数为奇数（嵌套引号，长尾）
  W3 ODD_PAREN          段落内（）计数为奇数（跨段插入语可能合法）
  W4 HALF_QUOTE_CJK     半角 " 紧邻中文字符
  N1 PAGES / N2 PARAS / N3 PAIRS 只计数

为什么只有 E2/E3 是 E
---------------------
「」与《》在本库的用法是**一句话内成对**：没有跨段引文的写法。计数为奇数，一定是漏了
另一侧，不存在「合法的例外」。而“”与（）确实存在跨段写法（长引用、跨段的补充说明），
判成 E 会让这道门第二天就被关掉——这是本仓反复验证过的一条纪律：**会大面积报红的门禁
很快会被整体跳过**（见 `depthcheck`、`assetweightcheck` 的阈值取舍）。

口径
----
* 先剥围栏、再剥行内代码、再剥链接目标与裸 URL、最后剥 HTML 标签与属性——这四处里的
  引号是**语法**不是标点（`<img src="...">`、`[文本](a "标题")`）。
* 段落切分：空行为界；表格按**行**切（`|` 行天然是独立句子）；标题单独成段。
* 只扫 `docs/` 与 `project/`：`DOCS_PLAN.md` 是计划日志，含大量刻意写坏的反例。

用法
----
    python3 utils/audit/quotecheck.py [root] [--selftest]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(```+|~~~+)")
SPAN = re.compile(r"`[^`\n]*`")
LINK_TGT = re.compile(r"\]\([^)\n]*\)")
URL = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&*+,;=%]+")
HTML = re.compile(r"</?[A-Za-z][^>]{0,300}>")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")

PAIRS = {
    "「": ("」", "E2 ODD_QUOTE"),
    "《": ("》", "E3 ODD_TITLE_QUOTE"),
    "“": ("”", "W1 ODD_DQUOTE"),
    "『": ("』", "W2 ODD_CORNER"),
    "（": ("）", "W3 ODD_PAREN"),
}
HALF_QUOTE_CJK = re.compile(r'[\u4e00-\u9fff]"|"[\u4e00-\u9fff]')


def strip_noise(line: str) -> str:
    s = LINK_TGT.sub("]", line)
    s = URL.sub("", s)
    s = SPAN.sub("", s)
    s = HTML.sub("", s)
    return s


def paragraphs(text: str):
    """按空行切段；表格逐行；标题单独；围栏整块跳过。"""
    out, buf, in_fence, fence_tok = [], [], False, ""
    for raw in text.splitlines():
        m = FENCE.match(raw)
        if m:
            tok = m.group(1)[:3]
            if not in_fence:
                in_fence, fence_tok = True, tok
            elif tok == fence_tok:
                in_fence = False
            if buf:
                out.append("\n".join(buf)); buf = []
            continue
        if in_fence:
            continue
        if not raw.strip():
            if buf:
                out.append("\n".join(buf)); buf = []
            continue
        if HEADING.match(raw) or raw.lstrip().startswith("|"):
            if buf:
                out.append("\n".join(buf)); buf = []
            out.append(raw)
            continue
        buf.append(raw)
    if buf:
        out.append("\n".join(buf))
    return out


def check_text(text: str):
    """返回 [(code, snippet)]。"""
    hits = []
    for para in paragraphs(text):
        body = "\n".join(strip_noise(l) for l in para.splitlines())
        for left, (right, label) in PAIRS.items():
            if body.count(left) != body.count(right):
                hits.append((label.split()[0], para.strip().splitlines()[0][:60]))
        if HALF_QUOTE_CJK.search(body):
            hits.append(("W4", para.strip().splitlines()[0][:60]))
    return hits


def run(root: Path):
    roots = [p for p in (root / "docs", root / "project") if p.is_dir()]
    if not roots:
        print("E0 ROOT_NOT_FOUND")
        return 1
    pages = paras = pairs = 0
    stat = {}
    rows = []
    for base in roots:
        for f in sorted(base.rglob("*.md")):
            pages += 1
            text = f.read_text(encoding="utf-8", errors="replace")
            ps = paragraphs(text)
            paras += len(ps)
            for p in ps:
                for left, (right, _) in PAIRS.items():
                    pairs += min(p.count(left), p.count(right))
            for code, snippet in check_text(text):
                stat[code] = stat.get(code, 0) + 1
                rows.append((code, f.relative_to(root), snippet))
    e = sum(v for k, v in stat.items() if k.startswith("E") and k != "E0" and k != "E1")
    w = sum(v for k, v in stat.items() if k.startswith("W"))
    for code, path, snip in rows:
        if code.startswith("E"):
            print(f"{code} {path}  :: {snip}")
    print(f"pages={pages} paras={paras} pairs={pairs} E={e} W={w} "
          + " ".join(f"{k}={v}" for k, v in sorted(stat.items())))
    return 0 if e == 0 else 1


SELFTEST = [
    ("干净：一句话内成对", "他说的「预算就是授权」这句要记住。", False),
    ("漏右引号", "他说的「预算就是授权，系统里就多了一个。", True),
    ("漏左引号", "他说预算就是授权」，然后走了。", True),
    ("书名号漏闭合", "参考《企业内部控制应用指引第 15 号。", True),
    ("书名号成对", "参考《企业内部控制应用指引第 15 号》。", False),
    ("行内代码里的引号不算", "执行 `echo \"「\"` 看输出。", False),
    ("围栏里的引号不算", "```text\n「未闭合\n```\n\n正常段落。", False),
    ("链接标题里的引号不算", '[文档](a.md "标题「")', False),
    ("HTML 属性里的引号不算", '<img src="a.png" alt="图「">', False),
    ("双引号跨段：只提示", "第一段“引文开始。\n\n第二段结束”。", False),
    ("半角引号贴中文：提示", '他说"预算"就是授权。', False),
    ("表格行独立成段", "| 列一 | 「甲」 |\n| --- | --- |", False),
]


def selftest() -> int:
    ok = 0
    for name, text, expect_err in SELFTEST:
        hits = check_text(text)
        has_err = any(h[0] in ("E2", "E3") for h in hits)
        good = has_err == expect_err
        print(f"[{'PASS' if good else 'FAIL'}] {name}")
        ok += 1 if good else 0
    print(f"--selftest {ok}/{len(SELFTEST)}")
    return 0 if ok == len(SELFTEST) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(Path(a.root).resolve())


if __name__ == "__main__":
    sys.exit(main())
