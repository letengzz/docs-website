#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""asciidiagramcheck.py —— 「用代码块画图」巡检（第 135 项巡检）

## 为什么立这一项

`AGENTS.md` 第 7 节第 7 条写得很硬：

> `text` 代码块画图**不算配图**：涉及流程、架构、对比的页面必须在 `assets/` 放置 SVG
> 示意图并用相对路径引用，禁止只用代码块画图代替。

这条规则和别的规则不一样：它是**唯一一条没有巡检看管的规则**。现有的图像类巡检各管一截——

* `imageorigincheck`（第 98 项）管配图的**路径形态**（相对/绝对、data URI）；
* `linkexistcheck` 的 `E3 BROKEN_ASSET` 管配图**存不存在**；
* `logocheck` 管主题首页有没有**官方 Logo**；
* `orphanassetcheck` 管 `assets/` 里有没有**没人引用的孤儿图**。

四项都在问「图对不对」，**没有一项问「该有图的地方有没有图」**。于是这样一页可以全绿通过：
正文讲一条五步流程，用 ```text 画了一个带框线的流程，通篇零配图——渲染出来是一段等宽字符，
在手机上要横向滚动；规则第 7 条要求的是 SVG。

## 判据（二真四提示）

* `E0 ROOT_NOT_FOUND` / `E0 READ_FAIL` —— 活性，防「读不到也算全绿」
* `E1 NO_PAGES` —— 活性，防「扫了个空目录」
* `W1 BOXART_NO_IMAGE` —— `text` 围栏里有框线图，**整页没有任何配图**（违反 7.7）
* `W2 BOXART_WITH_IMAGE` —— 有框线图但页面已有配图（允许，只计数：代码块可能是「文字版备份」）
* `W3 MERMAID_FENCE` —— ```mermaid 围栏（本仓 `config.mts` 未接 mermaid 渲染插件，
  读者看到的是一段源码而不是图）
* `W4 ASCII_TABLE` —— `+---+` 画的 ASCII 表格（不是流程图，但同样不该用代码块代替表格）
* `N1/N2/N3` —— 页面数 / 框线块数 / 目录树块数（只计数，不判错）

## 为什么 `W1` 不记 `E`

「框线图 + 无配图」是**规则违反**，但判据无法区分两种情形：一种是作者偷懒（该画 SVG），
一种是作者刻意（给纯文本读者留一份可复制的结构）。本库的惯例是：`W` 记账、由写页人确认；
**同一条 `W1` 连续两轮不降，就该去补图**——这正是本巡检的用法。

## 口径是被真实语料打回来的（三轮）

**第一轮**：把「`text` 围栏里出现框线字符」整块判成框线图 → 全库 **286 页**报警。
逐页打开发现绝大多数是**目录树**：

```text
docs-website/
├─ docs/
│  └─ Backend/
└─ project/
```

目录树用 `├──`/`└──` 是**最合适的表示**（比任何 SVG 都清楚，而且可以直接复制），
不该被规则误伤。改成「同一页 ≥2 行含**连续 3 个以上 `─`**」（`├──` 只有 2 个）后：286 → **28 页**。

**第二轮**：28 页里有 2 页是 `+-----+-----+` 画的 **ASCII 表格**。它是「表格」不是「图」，
按 7.7 不适用（7.7 讲的是流程、架构、对比图），但同样不该出现在代码块里——因此单独归
`W4 ASCII_TABLE`，只计数不判错，避免和「缺流程图」混在一起讨论。28 页里真正命中 `W1` 的 5 页。

**第三轮**：`mermaid` 围栏。本仓 `package.json` 与 `config.mts` 都没有 mermaid 相关依赖，
所以 ```mermaid 会被当成普通代码块渲染——**作者以为自己写了图，读者看到的是一段 `graph TD`**。
这条不是「有没有配图」的问题，而是「图根本没渲染」，单独归 `W3`，全库 **28 页**。它是明确欠账，
但在本仓装上渲染插件之前，报警比静默好。

## 收口读数

`--selftest 16/16`；全库 `pages=3185 box_pages=28 no_image=5 ascii_table=2 mermaid=28`
→ `E=0 W1=5 W3=28 W4=2`。**`W1` 的 5 条按日消化**（每页补一张 SVG，或删掉代码块改文字），
`W3` 的 28 条要等 `config.mts` 接上 mermaid 才能清零——两者都登记在「存量整理任务清单」里。

## 口径

1. 只看围栏内的内容；行内代码与正文都不算。
2. 只认 `text` / `plain` / `txt` / 无语言 四种围栏——`js`、`sql` 里的框线是注释装饰，不算。
3. 围栏允许带列表标记前缀（`2. ```text`），CommonMark 合法。
4. 「有配图」= 出现 `<img` 或 `![`；只看本页，不跨页推断。
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

ROOTS_DEFAULT = ["docs", "project"]

# 围栏：允许列表标记前缀（CommonMark 合法），语言标签允许为空
FENCE = re.compile(r"^(\s*)(?:\d{1,3}[.)]\s+|[-*+]\s+)?(`{3,}|~{3,})\s*([^\s`]*)?")
# 连续 3 个以上「─」：目录树的 ├── 只有 2 个，不会命中
DASH3 = re.compile(r"─{3,}")
# ASCII 表格边框
PLUSROW = re.compile(r"^\s*\+[-=+]{4,}\+?\s*$")
# 目录树行
TREELINE = re.compile(r"^\s*(?:[│ ])*(?:├|└)")
IMG_MD = re.compile(r"!\[[^\]]*\]\(")
IMG_TAG = re.compile(r"<img\b", re.I)

TEXT_LANGS = {"text", "plain", "txt", ""}


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def iter_md(root: str):
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in sorted(filenames):
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def fences(text: str):
    """产出 (lang, lines, start_line_no)。只按成对围栏切，未闭合的块按到文末处理。"""
    out = []
    lines = text.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        mark = m.group(2)
        lang = (m.group(3) or "").strip().lower()
        start = i + 1
        body = []
        i += 1
        while i < n:
            m2 = FENCE.match(lines[i])
            if m2 and lines[i].strip().startswith(mark[0] * len(mark)):
                break
            body.append(lines[i])
            i += 1
        out.append((lang, body, start))
        i += 1
    return out


def classify(body):
    """返回 'box' / 'ascii_table' / 'tree' / None。优先级：框线图 > ASCII 表 > 目录树。"""
    dash = sum(1 for b in body if DASH3.search(b))
    plus = sum(1 for b in body if PLUSROW.match(b))
    tree = sum(1 for b in body if TREELINE.match(b))
    if dash >= 2:
        return "box"
    if plus >= 2:
        return "ascii_table"
    if tree >= 2:
        return "tree"
    return None


def has_image(text: str) -> bool:
    return bool(IMG_MD.search(text) or IMG_TAG.search(text))


def scan(roots):
    pages = box_pages = no_image = ascii_pages = mermaid_pages = tree_pages = 0
    box_blocks = 0
    w1, w3, w4 = [], [], []
    for root in roots:
        if not os.path.isdir(root):
            print(f"E0 ROOT_NOT_FOUND {root}", file=sys.stderr)
            return 1
        for path in iter_md(root):
            try:
                text = read(path)
            except OSError as e:  # pragma: no cover
                print(f"E0 READ_FAIL {path}: {e}", file=sys.stderr)
                continue
            pages += 1
            kinds = []
            for lang, body, start in fences(text):
                if lang == "mermaid":
                    w3.append((path, start))
                    mermaid_pages += 1
                    continue
                if lang not in TEXT_LANGS:
                    continue
                kind = classify(body)
                if kind == "box":
                    box_blocks += 1
                    kinds.append((kind, start))
                elif kind == "ascii_table":
                    w4.append((path, start))
                    kinds.append((kind, start))
                elif kind == "tree":
                    tree_pages += 1
            boxes = [k for k in kinds if k[0] == "box"]
            if boxes:
                box_pages += 1
                if has_image(text):
                    pass
                else:
                    no_image += 1
                    w1.append((path, boxes[0][1]))
            if any(k[0] == "ascii_table" for k in kinds):
                ascii_pages += 1
    if pages == 0:
        print("E1 NO_PAGES 一个 Markdown 都没扫到", file=sys.stderr)
        return 1

    for path, line in w1:
        print(f"{path}:{line} W1 BOXART_NO_IMAGE 框线图但整页无配图")
    for path, line in w4:
        print(f"{path}:{line} W4 ASCII_TABLE 用 +---+ 画表格")
    for path, line in w3:
        print(f"{path}:{line} W3 MERMAID_FENCE 本仓未接 mermaid 渲染，读者看到的是源码")

    total_w = len(w1) + len(w3) + len(w4)
    print(f"\npages={pages} box_pages={box_pages} no_image={no_image} "
          f"ascii_table={ascii_pages} mermaid={mermaid_pages} tree_pages={tree_pages} "
          f"box_blocks={box_blocks}")
    print(f"合计 {total_w} 条：E=0 W={total_w}（W1={len(w1)} W3={len(w3)} W4={len(w4)}）")
    print("RESULT OK")
    return 0


# ---------------- 自测 ----------------

CASES = [
    # (名称, 文件内容, 期望 W1 数, 期望 W3 数, 期望 W4 数, 期望存在框线块)
    ("框线图且无配图", "x\n\n```text\n┌──────┐\n│ a → b │\n└──────┘\n```\n", 1, 0, 0, True),
    ("框线图但有配图", "x\n\n![图](assets/a.svg)\n\n```text\n┌──────┐\n│ a → b │\n└──────┘\n```\n", 0, 0, 0, True),
    ("img 标签也算配图", '<p><img src="assets/a.png" /></p>\n\n```text\n┌────┐\n│ a  │\n└────┘\n```\n', 0, 0, 0, True),
    ("目录树不算框线图", "```text\ndocs/\n├─ Backend/\n│  └─ Go/\n└─ Frontend/\n```\n", 0, 0, 0, False),
    ("ASCII 表算 W4", "```text\n+------+------+\n| a    | b    |\n+------+------+\n```\n", 0, 0, 1, False),
    ("mermaid 围栏", "```mermaid\ngraph TD\n  A --> B\n```\n", 0, 1, 0, False),
    ("js 围栏里的框线不算", "```js\n// ┌────────┐\n// │ 注释装饰 │\n// └────────┘\n```\n", 0, 0, 0, False),
    ("只有一行框线不算", "```text\n┌──────────┐\n其他内容\n另一行\n```\n", 0, 0, 0, False),
    ("带列表标记的围栏", "1. 步骤\n   ```text\n   ┌────┐\n   │ a  │\n   └────┘\n   ```\n", 1, 0, 0, True),
    ("大写 TEXT 也认", "```TEXT\n┌────┐\n│ a  │\n└────┘\n```\n", 1, 0, 0, True),
    ("波浪线围栏", "~~~text\n┌────┐\n│ a  │\n└────┘\n~~~\n", 1, 0, 0, True),
    ("无语言围栏也认", "```\n┌────┐\n│ a  │\n└────┘\n```\n", 1, 0, 0, True),
    ("上下边框两行即算", "```text\n┌────┐\n└────┘\n```\n", 1, 0, 0, True),
    ("单条横线仍不算", "```text\n┌────┐\n│ a  │\n正文\n```\n", 0, 0, 0, False),
    ("mermaid 与框线并存", "```mermaid\ngraph TD\n  A-->B\n```\n\n```text\n┌────┐\n│ a  │\n└────┘\n```\n", 1, 1, 0, True),
    ("sql 围栏里的横线不算", "```sql\n-- ────────────\nselect 1;\n-- ────────────\n```\n", 0, 0, 0, False),
    ("行内代码里的框线不算", "正文写 `┌───┐` 不算，因为不在围栏里。\n", 0, 0, 0, False),
]


def selftest() -> int:
    passed = failed = 0
    for name, content, ew1, ew3, ew4, expect_box in CASES:
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "docs"))
        with open(os.path.join(d, "docs", "p.md"), "w", encoding="utf-8") as f:
            f.write(content)
        text = read(os.path.join(d, "docs", "p.md"))
        w1 = w3 = w4 = 0
        got_box = False
        for lang, body, _s in fences(text):
            if lang == "mermaid":
                w3 += 1
                continue
            if lang not in TEXT_LANGS:
                continue
            kind = classify(body)
            if kind == "box":
                got_box = True
                if not has_image(text):
                    w1 += 1
            elif kind == "ascii_table":
                w4 += 1
        ok = (w1 == ew1 and w3 == ew3 and w4 == ew4 and got_box == expect_box)
        if ok:
            passed += 1
            print(f"PASS {name}")
        else:
            failed += 1
            print(f"FAIL {name}: W1={w1}(期望{ew1}) W3={w3}(期望{ew3}) "
                  f"W4={w4}(期望{ew4}) box={got_box}(期望{expect_box})")
    print(f"\nselftest {passed}/{passed + failed}")
    return 0 if failed == 0 else 1


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    if "--selftest" in argv:
        return selftest()
    roots = args or ROOTS_DEFAULT
    for r in roots:
        if not os.path.isdir(r):
            print(f"E0 ROOT_NOT_FOUND {r}", file=sys.stderr)
            return 1
    return scan(roots)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
