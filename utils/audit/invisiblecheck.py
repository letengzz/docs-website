#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""invisiblecheck.py —— 不可见字符巡检（第 124 项巡检）。

背景
----
本库已有 120 多项巡检，分别管「看得见的错」：围栏没闭合（`fencecheck`）、
全角标点在代码里（`fwcodecheck`）、中文与英文之间没空格（`codegapcheck`）、
表格列数不齐（`tablecheck`）。但没有一项管**看不见的字符**：

  - 从网页或聊天窗口粘进来的零宽空格（U+200B），让 `git diff` 显示「无变化」，
    而 `grep` 永远搜不到那个词；
  - 复制命令时带上不换行空格（U+00A0），终端把它当成普通空格，shell 直接
    `command not found`；
  - 全角空格（U+3000）混进代码围栏，Python 报 `IndentationError`，报错行号
    指向一个「看起来完全正常」的空行；
  - 文件带 BOM（U+FEFF），`#!/usr/bin/env bash` 前多三个字节，脚本执行报
    `bad interpreter`；
  - 软连字符（U+00AD）与方向控制符（U+202A~U+202E）会让等宽字体下的文本
    看起来正常、复制出来却是另一串东西。

这些字符的共同点是：**渲染出来看不见，复制出来要命**。本项只做一件事——
把它们找出来，并按「在代码里」与「在正文里」分级。

判据（E 为错误、W 为提示）
--------------------------
E0 ROOT_NOT_FOUND      仓库根既无 docs/ 也无 project/
E1 NO_PAGES            一个 Markdown 都没扫到（活性判据，防路径写错全绿）
E2 BOM                 文件以 U+FEFF 开头（BOM；会让 shebang 与首行标题失效）
E3 ZW_IN_FENCE         围栏代码内出现零宽字符（U+200B/200C/200D/2060/FEFF）
W1 NBSP                正文出现不换行空格 U+00A0（复制即多一个「假空格」）
W2 IDEO_INDENT         围栏代码**行首**出现全角空格 U+3000（缩进看起来对、跑起来报错）
W6 IDEO_INLINE         围栏代码行内出现全角空格（多半是刻意排版，需人工确认）
W3 BIDI                出现方向控制符（U+202A~U+202E / U+2066~U+2069）
W4 SOFT_HYPHEN         出现软连字符 U+00AD
W5 ZW_IN_PROSE         正文出现零宽字符（多半是粘贴残留，不影响执行但影响检索）

**为什么只有前四条是 E**：E2/E3 会直接让命令跑不通或让文件头失效，是「复制即
报错」级别；W1~W5 的后果是「搜不到、看着别扭」，需要人判断是刻意还是残留。
把 W 也判成 E，会在首轮就把几百条粘贴残留变成红项，最后大家学会忽略这道门。

口径
----
* **只扫 `docs/` 与 `project/`**：`DOCS_PLAN.md` 的台账长行里有大量刻意写下的
  示例字符，扫进来只会制造噪声。
* **围栏识别允许缩进与标题**：本库常写 ````` ```python [a.py] ``` ``，也常在列表
  项里缩进 4~6 格开围栏；只认行首三反引号会把围栏内的内容当正文。
* **BOM 只在文件第 0 字节判**：正文中间出现的 U+FEFF 归 W5（那是粘贴残留）。
* **同一行同一类只报一次**：一个零宽字符被复制十遍，报十次没有意义。

用法
----
    python3 utils/audit/invisiblecheck.py              # 默认根：仓库根
    python3 utils/audit/invisiblecheck.py --verbose    # 连 W 一起列
    python3 utils/audit/invisiblecheck.py --selftest    # 判据自测
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

BOM = "\ufeff"
ZW = {"\u200b": "ZWSP", "\u200c": "ZWNJ", "\u200d": "ZWJ", "\u2060": "WJ", "\ufeff": "BOM"}
NBSP = "\u00a0"
IDEO = "\u3000"
SOFT = "\u00ad"
BIDI = [chr(c) for c in range(0x202A, 0x202F)] + [chr(c) for c in range(0x2066, 0x206A)]

FENCE_OPEN = re.compile(r"^\s{0,8}(?:[-*+]\s+|\d{1,3}[.)]\s+)?(`{3,}|~{3,})")
ROOTS = ("docs", "project")


def iter_pages(root: str):
    for base in ROOTS:
        p = os.path.join(root, base)
        if not os.path.isdir(p):
            continue
        for dirpath, _dirs, files in os.walk(p):
            for f in sorted(files):
                if f.endswith(".md"):
                    yield os.path.join(dirpath, f)


def scan_text(text: str):
    """返回 [(code, lineno, detail)]；code 为判据名。"""
    hits = []
    if text.startswith(BOM):
        hits.append(("E2_BOM", 0, "文件以 U+FEFF 开头"))

    in_fence = False
    fence_mark = ""
    for i, line in enumerate(text.splitlines(), start=1):
        m = FENCE_OPEN.match(line)
        if m:
            mark = m.group(1)
            if not in_fence:
                in_fence, fence_mark = True, mark[0]
                continue
            if mark[0] == fence_mark:
                in_fence = False
                continue
        body = line[1:] if (i == 1 and line.startswith(BOM)) else line
        if in_fence:
            zw = [n for ch, n in ZW.items() if ch in body]
            if zw:
                hits.append(("E3_ZW_IN_FENCE", i, "/".join(sorted(set(zw)))))
            if re.match(r"^\u3000+", body):
                hits.append(("W2_IDEO_INDENT", i, f"行首 ×{len(re.match(r'^\u3000+', body).group(0))}"))
            elif IDEO in body:
                hits.append(("W6_IDEO_INLINE", i, f"行内 ×{body.count(IDEO)}"))
        else:
            if NBSP in body:
                hits.append(("W1_NBSP", i, f"×{body.count(NBSP)}"))
            zw = [n for ch, n in ZW.items() if ch in body]
            if zw:
                hits.append(("W5_ZW_IN_PROSE", i, "/".join(sorted(set(zw)))))
        if any(ch in body for ch in BIDI):
            hits.append(("W3_BIDI", i, "方向控制符"))
        if SOFT in body:
            hits.append(("W4_SOFT_HYPHEN", i, "U+00AD"))
    return hits


def run(root: str, verbose: bool) -> int:
    if not any(os.path.isdir(os.path.join(root, r)) for r in ROOTS):
        print(f"E0 ROOT_NOT_FOUND: {root}")
        return 2
    pages = list(iter_pages(root))
    if not pages:
        print("E1 NO_PAGES: 未扫到任何 Markdown")
        return 2

    counts = {}
    rows = []
    for p in pages:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError as ex:
            print(f"W0 READ_ERROR {p}: {ex}")
            continue
        for code, line, detail in scan_text(text):
            counts[code] = counts.get(code, 0) + 1
            rows.append((code, os.path.relpath(p, root), line, detail))

    errors = [r for r in rows if r[0].startswith("E")]
    warns = [r for r in rows if r[0].startswith("W")]
    for code, path, line, detail in sorted(errors):
        print(f"{code} {path}:{line} {detail}")
    if verbose:
        for code, path, line, detail in sorted(warns):
            print(f"{code} {path}:{line} {detail}")

    print(
        f"pages={len(pages)} E={len(errors)} W={len(warns)} "
        + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    )
    return 1 if errors else 0


def selftest() -> int:
    cases = []

    def make(content: str, name: str = "a.md"):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "docs"), exist_ok=True)
        with open(os.path.join(d, "docs", name), "w", encoding="utf-8", newline="") as f:
            f.write(content)
        return d

    # 1 BOM
    cases.append(("E2_BOM", make(BOM + "# 标题\n")))
    # 2 围栏内零宽
    cases.append(("E3_ZW_IN_FENCE", make("```shell\ngit\u200b status\n```\n")))
    # 3 围栏内行首全角空格（真会 IndentationError）
    cases.append(("W2_IDEO_INDENT", make("```python\ndef f():\n\u3000\u3000pass\n```\n")))
    # 3b 围栏内行内全角空格（刻意排版）
    cases.append(("W6_IDEO_INLINE", make("```markdown\n- 版本：1.0\u3000镜像：x\n```\n")))
    # 4 正文 NBSP
    cases.append(("W1_NBSP", make("价格\u00a0100 元。\n")))
    # 5 方向控制符
    cases.append(("W3_BIDI", make("正常\u202e文本\n")))
    # 6 软连字符
    cases.append(("W4_SOFT_HYPHEN", make("soft\u00adhyphen\n")))
    # 7 正文零宽
    cases.append(("W5_ZW_IN_PROSE", make("粘贴\u200b残留\n")))
    # 8 反例：围栏外的全角空格不按 E3 报（是正文缩进）
    cases.append(("NONE", make("正文\u3000正文\n")))
    # 9 反例：代码块里的中文正常，不该报
    cases.append(("NONE", make("```sql\n-- 注释\nselect 1;\n```\n")))
    # 10 反例：列表项内的围栏也要识别
    cases.append(("E3_ZW_IN_FENCE", make("- 步骤：\n\n  ```shell\n  echo\u200b 1\n  ```\n")))
    # 11 反例：行内代码里的零宽归 W5 而非 E3
    cases.append(("W5_ZW_IN_PROSE", make("命令 `echo\u200b 1` 即可。\n")))
    # 12 反例：波浪线围栏同样识别
    cases.append(("E3_ZW_IN_FENCE", make("~~~text\na\u200bb\n~~~\n")))
    # 13 反例：正常文件零命中
    cases.append(("NONE", make("# 标题\n\n正文。\n\n```shell\necho 1\n```\n")))
    # 14 反例：BOM 出现在正文中间不算 E2
    cases.append(("W5_ZW_IN_PROSE", make("# 标题\n\n中间\ufeffBOM\n")))
    # 15 围栏未闭合时，后续正文按围栏处理（零宽归 E3）
    cases.append(("E3_ZW_IN_FENCE", make("```shell\necho 1\n\n正文\u200b\n")))

    fails = 0
    for i, (expect, d) in enumerate(cases, start=1):
        rows = []
        for p in iter_pages(d):
            rows += scan_text(open(p, encoding="utf-8", errors="replace").read())
        codes = {r[0] for r in rows}
        if expect == "NONE":
            ok = not rows
        else:
            ok = expect in codes
        if not ok:
            fails += 1
            print(f"  case {i}: expect {expect}, got {sorted(codes) or 'NONE'}")
        else:
            print(f"  case {i}: PASS ({expect})")
    print(f"selftest {len(cases) - fails}/{len(cases)}")
    return 0 if fails == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(os.path.abspath(a.root), a.verbose)


if __name__ == "__main__":
    sys.exit(main())
