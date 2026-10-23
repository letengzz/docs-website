#!/usr/bin/env python3
r"""fenceutil.py — 围栏（代码块）解析的唯一实现 · 第 88 项巡检的共享底座

为什么要有这个文件
------------------
本库有四道巡检需要「知道哪几行在围栏里」：`fencecheck`（围栏自身）、`tickscheck`
（行内代码）、`langmatchcheck`（语言标注）、`levelskipcheck`（标题跳级）。四家各
写了一份正则，历史上**连续三次**在同一个地方栽跟头：

1. 第 85 项：简单 `^\s*(```|~~~)` 切换，在「四反引号围栏嵌三反引号」时提前闭合
   （`docs/Others/TechWriting/Examples` 一次误报 8 条 MULTI_H1）。
2. 第 86 项：行内代码不是安全区，反引号游程算错，`W2_NOEXT` 长期挂 1 条。
3. 第 87 项：`^\s{0,3}` 判围栏，把列表项内部**缩进 4 空格**的合法围栏当正文，
   一次误报 16 条（`Frontend/Frame/Vue/Vue3/Router`）。

结论：围栏解析只该有一份实现。本模块是那一份。

口径（三条，全部被真实语料打出来过）
------------------------------------
- **开围栏**：`^\s*` 之后允许列表标记（`- ` / `* ` / `+ ` / `1. `），再是 ≥3 个
  同字符反引号或波浪号。缩进不限——列表项内部的 4 空格围栏是 CommonMark 合法的。
- **闭围栏**：同字符、长度 **不短于** 开围栏、且**不带 info string**。这条专治
  「四反引号里嵌三反引号」：内层的 ``` 长度不足，不算闭合。
- **未闭合**：一路吞到文末，并被单独标出（交给 `tickscheck` 的 `E3` 判）。

不做的事：不解析缩进式代码块（4 空格 + 非围栏），不解析 HTML 块。本库不用它们。
"""

import re

OPEN_RE = re.compile(r"^(?P<indent>\s*)(?:[-*+]\s+|\d+\.\s+)?(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def is_open(line: str):
    """是开围栏则返回 (char, length, info)；否则 None。"""
    m = OPEN_RE.match(line)
    if not m:
        return None
    fence = m.group("fence")
    return fence[0], len(fence), (m.group("info") or "").strip()


def scan(text: str):
    """扫一段文本。

    返回 `(mask, blocks, unclosed)`：
    - `mask`：**围栏行与围栏内所有行**的行号集合（0 基，含首尾围栏行）
    - `blocks`：`[(start, end, info)]`，start/end 为首尾围栏行号
    - `unclosed`：未闭合块的起始行号（无则 None）
    """
    lines = text.split("\n")
    mask, blocks, unclosed = set(), [], None
    i, n = 0, len(lines)
    while i < n:
        op = is_open(lines[i])
        if not op:
            i += 1
            continue
        char, ln, info = op
        j = i + 1
        while j < n:
            cl = is_open(lines[j])
            if cl and cl[0] == char and cl[1] >= ln and not cl[2]:
                break
            j += 1
        if j >= n:
            unclosed = i
            mask.update(range(i, n))
            blocks.append((i, n - 1, info))
            break
        mask.update(range(i, j + 1))
        blocks.append((i, j, info))
        i = j + 1
    return mask, blocks, unclosed


def body_lines(text: str):
    """返回「不在围栏里」的行（保留原行号顺序），供链接/标题类巡检使用。"""
    mask, _, _ = scan(text)
    return [ln for idx, ln in enumerate(text.split("\n")) if idx not in mask]


def fence_count(text: str) -> int:
    _, blocks, _ = scan(text)
    return len(blocks)


if __name__ == "__main__":
    # 自检：三种历史翻车形态
    cases = {
        "四反引号嵌三反引号": "````markdown\n```js\nx\n```\n````\n",
        "列表项内缩进 4 空格": "1. 步骤\n\n    ```shell\n    echo hi\n    ```\n",
        "带 info string": "```text [文件路径]\nbody\n```\n",
    }
    for name, txt in cases.items():
        mask, blocks, unclosed = scan(txt)
        print(f"{name}: blocks={len(blocks)} lines_in_fence={len(mask)} unclosed={unclosed}")
