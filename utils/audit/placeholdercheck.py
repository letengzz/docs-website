#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""placeholdercheck.py — 「占位与半成品」巡检 · 第 94 项

为什么立这一项
--------------
`AGENTS.md` 第 5 节把「禁止空壳页」写成硬要求：每篇必须有概念、示例、清单、
易错点、验证方式、参考资料。但**「写了一半」和「写完了」在文件层面长得一样**：
两者的行数、标题层级、表格数量都可能是合规的。

已有的门都拦不住它：

* `headingcheck`（第 84 项）     —— 管标题层级与数量；
* `leadparagraphcheck`（第 90 项）—— 管「H1 下方有没有定位段」；
* `judgecovercheck`（第 91 项）   —— 管「有没有判据表」；
* `sectionordercheck`（第 89 项） —— 管「末节是不是参考资料」；
* `countclaimcheck`              —— 管「十页 / 80 条」这类数字声明是否自洽。

于是出现一种很具体的页面：**结构齐全、数字自洽、参考资料也贴了，但正文里留着
一句「待补充」**。它不会让构建失败，只会让读者在第 3 屏撞上一堵墙，然后关页。

判据
----
E0 ROOT_NOT_FOUND   仓库根找不到（既没有 docs/ 也没有 project/）
E1 NO_PAGES         一个 .md 都没扫到（活性判据：拒绝在空集上给「全绿」）
W1 MARKER_PROSE     正文（围栏与行内代码之外）出现占位词：TODO / FIXME / TBD / 待补充 / 待核实 …
W2 MARKER_HEAVY     单页正文出现 ≥ 3 处占位词（多半是整节没写，不是一处疏忽）
W3 MARKER_TITLE     标题（H1~H6）里出现占位词（目录与侧边栏都会跟着显示，影响面更大）

口径（四条，全部来自真实语料）
------------------------------
1. **围栏里的 TODO 不算**：`docs/Tools/Efficiency/ShellProductivity` 有 7 处
   `TODO`，全部在 shell 示例（`# TODO: 换成你的路径`）里——那是**示例内容**，
   不是欠账。所以先按 `fenceutil.scan()` 把围栏整段剔掉再匹配。
2. **行内代码里的占位词也不算**：正文常写「把 `TODO` 换成你的任务名」，这是在
   *解释* 占位词，不是在留债。匹配前先把反引号内的内容替换成等长空格。
3. **只用大写英文标记，且必须是「独立记号」**：`todo` / `fixme` 小写形式在正常
   英文句子里会误报（如 "a to-do list"）；`XXX` 在 `id=XXX` 这种「错误信息里的
   占位 id」也会误报，所以它前后必须不是字母数字或 `=` `:` `/` `-`。中文词只收
   「待补充 / 待核实 / 待完善」这类明确的未完成语。**「待确认」「待定」不收**：
   它们在本库里大量作为「状态列取值」和正常行文出现（「原因待确认后再补一条」），
   收进来会一次性造出 10 条误报，把真欠账埋掉。
4. **引号里的占位词是「在讨论占位词」，不算欠账**：本库大量页面把「待确认」
   当反例写（「不许写成『待确认』」），把 `TODO` 当示例讲。所以匹配前先把
   `「…」`、`“…”`、`"…"` 里的内容抹成空格——**这不是放宽门槛，而是修正对象**：
   本项要抓的是「作者自己留下的未完成标记」，不是「文章里提到过这个词」。

纪律
----
* **只读**：不写文件、不自动删标记、不自动补段落。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/placeholdercheck.py
    python3 utils/audit/placeholdercheck.py --root . --limit 40
    python3 utils/audit/placeholdercheck.py --selftest
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402

SKIP_DIRS = {".git", ".vitepress", "node_modules", ".workbuddy", "assets", "public"}
ROOTS = ("docs", "project")

HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)$")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
QUOTED_RE = re.compile(r"「[^」\n]*」|“[^”\n]*”|\"[^\"\n]*\"")

MARKERS = [
    ("TODO", re.compile(r"\bTODO\b")),
    ("FIXME", re.compile(r"\bFIXME\b")),
    ("TBD", re.compile(r"\bTBD\b")),
    ("XXX", re.compile(r"(?<![\w=:/.-])XXX(?![\w=:/.-])")),
    ("待补充", re.compile(r"待补充")),
    ("待核实", re.compile(r"待核实")),
    ("待完善", re.compile(r"待完善")),
]

HEAVY_THRESHOLD = 3


def _blank(pat, line: str) -> str:
    """把匹配到的片段替换成等长空格，保持列号不变。"""
    return pat.sub(lambda m: " " * len(m.group(0)), line)


def analyze(text: str):
    """返回 (prose_hits, title_hits, samples)。

    prose_hits: 正文（非围栏、非行内代码）中的占位词条数
    title_hits: 标题行里的占位词条数
    samples:    [(行号, 词, 行摘要)]
    """
    mask, _blocks, _unclosed = scan(text)
    prose_hits, title_hits = 0, 0
    samples = []
    for i, raw in enumerate(text.split("\n")):
        if i in mask:
            continue
        line = _blank(INLINE_CODE_RE, raw)
        line = _blank(QUOTED_RE, line)
        is_title = bool(HEAD_RE.match(line))
        for name, pat in MARKERS:
            for _ in pat.finditer(line):
                if is_title:
                    title_hits += 1
                else:
                    prose_hits += 1
                if len(samples) < 5:
                    samples.append((i + 1, name, raw.strip()[:70]))
    return prose_hits, title_hits, samples


def _iter_pages(root: str):
    for base in ROOTS:
        start = os.path.join(root, base)
        if not os.path.isdir(start):
            continue
        for dirpath, dirnames, filenames in os.walk(start):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def run(root: str, limit: int, quiet: bool) -> int:
    if not any(os.path.isdir(os.path.join(root, b)) for b in ROOTS):
        print("E0 ROOT_NOT_FOUND %s" % root)
        return 1
    pages = 0
    w1, w2, w3 = 0, 0, 0
    rows = []
    for path in _iter_pages(root):
        pages += 1
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        prose, title, samples = analyze(text)
        rel = os.path.relpath(path, root)
        if title:
            w3 += 1
            rows.append(("W3", rel, "标题含占位词 %d 处" % title))
        if prose >= HEAVY_THRESHOLD:
            w2 += 1
            rows.append(("W2", rel, "正文占位词 %d 处（整节未写？）" % prose))
        elif prose:
            w1 += 1
            rows.append(("W1", rel, "正文占位词 %d 处：%s" % (prose, samples[0][1])))
    if pages == 0:
        print("E1 NO_PAGES %s" % root)
        return 1
    if not quiet:
        for code, rel, msg in rows[:limit]:
            print("%s %-52s %s" % (code, rel, msg))
        if len(rows) > limit:
            print("... 其余 %d 条省略" % (len(rows) - limit))
    print("pages=%d W1=%d W2=%d W3=%d" % (pages, w1, w2, w3))
    return 0


def _make(root: str, files: dict) -> None:
    for rel, content in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)


def selftest() -> int:
    cases = []

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n正文写完了，没有标记。\n"})
    cases.append(("干净页面", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n这一节 TODO\n"})
    cases.append(("正文一个 TODO", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n```shell\n# TODO: 换成你的路径\n```\n"})
    cases.append(("围栏里的 TODO 不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n把 `TODO` 换成任务名即可。\n"})
    cases.append(("行内代码里的 TODO 不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、待补充\n\n正文。\n"})
    cases.append(("标题含待补充", d, (0, 1)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\nTODO 一\n\nFIXME 二\n\n待完善 三\n"})
    cases.append(("三处占位（heavy）", d, (3, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n这个 todo 小写不算。\n"})
    cases.append(("小写 todo 不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"project/Complete/P/index.md": "# 项目\n\n待核实：并发数。\n"})
    cases.append(("project 目录也扫", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n不许写成「待补充」，要给解除条件。\n"})
    cases.append(("引号里的待补充不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n报错：Result type not match for select id=XXX\n"})
    cases.append(("id=XXX 不算占位标记", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n剩下的口径 TODO\n"})
    cases.append(("行尾独立 TODO 仍报", d, (1, 0)))

    ok = 0
    for name, d, want in cases:
        page = list(_iter_pages(d))[0]
        with open(page, encoding="utf-8") as f:
            prose, title, _ = analyze(f.read())
        got = (prose, title)
        flag = "PASS" if got == want else "FAIL(got=%s want=%s)" % (got, want)
        if got == want:
            ok += 1
        print("  %-24s %s" % (name, flag))
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(os.path.abspath(args.root), args.limit, args.quiet)


if __name__ == "__main__":
    sys.exit(main())
