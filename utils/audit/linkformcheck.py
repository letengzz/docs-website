#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""linkformcheck.py —— Markdown 链接「语法形态」巡检（第 80 项）。

为什么要有这一项
----------------
本库关于链接已经有四道门：

  * `linkcheck`         —— 相对路径指向的文件存不存在；
  * `refcheck` / `refjudgecheck` —— 「参考资料」节与判据编号引用；
  * `anchorcheck`       —— `#fragment` 在目标页里能不能对上；
  * `imagecheck` / `orphanassetcheck` —— 图片是否被引用 / 是否存在。

它们有一个共同的**前提**：这个链接首先得是一个链接。而 Markdown 的链接语法极脆——
`[文本] (路径)` 多了一个空格、`[文本]（路径）` 用了全角括号、`[文本](路径`
少了一半括号——解析器会把它们当成**普通文字**，于是：

  1. 渲染出来的是一段带方括号的正文，读者点不动；
  2. 上面四道门**一条都不会报**——路径检查只遍历「被识别成链接」的节点，
     一段文字压根不进它的视野；
  3. 构建成功、链接检查全绿、配图检查全绿，唯独读者点不动。

这就是本项要补的盲区：**只看"长得像链接但不会被当成链接"的地方**，不重复检查
已经成立的链接指向哪里。

判据
----
E0 ROOT_NOT_FOUND     根目录不存在
E1 NO_PAGES           没扫到任何 Markdown（活性判据：拒绝在空集上给出全绿）
E2 SPACE_BEFORE_PAREN `](` 前面有空白（`[文本] (路径)`）：渲染成文字，点不动
E3 UNCLOSED_PAREN     `](` 之后本行没有右括号：整段退化成文字
E4 FULLWIDTH_PAREN    `]（路径）` 用全角括号包路径：中文输入法下最容易打出来的一种
E5 SPACE_IN_URL       链接目标里含空格：解析在第一个空格处截断，后半段变成正文
W1 EMPTY_TEXT         `[](...)` 空链接文本（屏幕阅读器读不出来是什么）
W2 NESTED_BRACKET     链接文本里又出现 `[`：嵌套方括号会让解析提前结束
W3 TRAILING_BRACKET   `](...)` 之后紧跟多余的 `]` / `》`（多打了半个括号）

刻意不查的（避免噪声）
----------------------
* 代码围栏与行内代码里的内容——那里本来就该是字面量；
* 图片 `![alt](src)`（`altqualitycheck` 管 alt，`imagecheck` 管路径）；
* HTML 注释；
* `[x]` 这类**任务清单**写法（后面不跟括号，或跟的是正文括号）。

用法
----
    python3 utils/audit/linkformcheck.py [根目录] [--quiet]
    python3 utils/audit/linkformcheck.py --selftest

退出码：0 = 无 E 级；1 = 有 E 级；2 = 用法错误。
"""

import os
import re
import sys

PAGE_EXT = (".md",)

FENCE = re.compile(r"^(\s*)(```+|~~~+)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# E2：`]` 与 `(` 之间夹了空白，且括号里看起来是个路径/域名（避免把「见附录 [A] (第 3 章)」这类正文误判）
E2 = re.compile(r"\]\s+\((?=[^)\n]*(?:/|\.md|\.png|\.jpg|\.svg|\.pdf|https?:|www\.))")
# E3：`](` 出现但到行尾都没有 `)`
E3 = re.compile(r"\]\([^)\n]*$")
# E4：全角括号包着一个路径
E4 = re.compile(r"\]（(?=(?:\.{0,2}/|https?://|[A-Za-z0-9_-]+/[A-Za-z0-9_-]))")
# E5：目标里含空白
E5 = re.compile(r"\]\(([^)\n]*)\)")
# W1：空文本（前面不是 `!`，排除图片）
W1 = re.compile(r"(?<!!)\[\]\(")
# W2：链接文本里再出现 `[`
W2 = re.compile(r"\[[^\]\n]*\[")
# W3：`](...)` 之后紧跟字母数字或中文（多为「多写了半个括号」或漏了空格）
W3 = re.compile(r"\]\([^)\n]*\)[\]\u300b]")


def strip_noise(text):
    """去掉围栏代码块、行内代码、HTML 注释，保留行号（用空行占位）。"""
    out = []
    in_fence = False
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(line)
    body = "\n".join(out)
    body = HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), body)
    body = INLINE_CODE.sub("", body)
    return body.splitlines()


def iter_pages(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".vitepress", "dist", ".workbuddy")]
        for fn in sorted(filenames):
            if fn.endswith(PAGE_EXT):
                yield os.path.join(dirpath, fn)


def check_file(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    findings = []
    for i, line in enumerate(strip_noise(text), 1):
        # 表格单元格里的 `|` 转义不影响这里的判定，先统一去掉反斜杠转义
        probe = line.replace("\\|", "|")
        for code, rx in (("E2", E2), ("E3", E3), ("E4", E4), ("W1", W1), ("W2", W2), ("W3", W3)):
            if rx.search(probe) and (code != "W2" or "](" in probe):
                findings.append((code, i, line.strip()[:120]))
        for m in E5.finditer(probe):
            if " " in m.group(1).strip():
                findings.append(("E5", i, line.strip()[:120]))
    return findings


def run(root=".", quiet=False):
    if not os.path.isdir(root):
        print(f"E0 ROOT_NOT_FOUND  {root}")
        return 1
    pages = 0
    stats = {}
    errs = 0
    for path in iter_pages(root):
        pages += 1
        for code, ln, snippet in check_file(path):
            stats[code] = stats.get(code, 0) + 1
            if code.startswith("E"):
                errs += 1
            if not quiet or code.startswith("E"):
                print(f"{code}  {path}:{ln}  {snippet}")
    if pages == 0:
        print("E1 NO_PAGES  没有扫到任何 Markdown")
        return 1
    print(f"\npages={pages} " + " ".join(f"{k}={v}" for k, v in sorted(stats.items())) + f" E={errs}")
    return 1 if errs else 0


FIXTURES = {
    "good.md": """# good

[正常链接](foo/index.md) 与 [带锚点](bar/index.md#节) 都对。
行内代码 `[文本] (路径)` 不算，代码块里的也不算：

```markdown
[文本] (路径)
[文本（全角）]（路径.md）
```
""",
    "space.md": "# bad\n\n见 [连接池] (ConnectionPool/index.md) 那一页。\n",
    "unclosed.md": "# bad\n\n见 [未闭合](ConnectionPool/index.md 那一页。\n",
    "fullwidth.md": "# bad\n\n见 [全角]（ConnectionPool/index.md）。\n",
    "space_in_url.md": "# bad\n\n[a](my file.md)\n",
    "empty.md": "# bad\n\n[](ConnectionPool/index.md)\n",
    "nested.md": "# bad\n\n[[嵌套]](ConnectionPool/index.md)\n",
    "trailing.md": "# bad\n\n[a](b.md)]\n",
    "task.md": "# ok\n\n- [x] 已完成\n- [ ] 待办\n",
}


def selftest():
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        for name, content in FIXTURES.items():
            open(os.path.join(d, name), "w", encoding="utf-8").write(content)
        found = {}
        for name in FIXTURES:
            for code, ln, snip in check_file(os.path.join(d, name)):
                found.setdefault(name, set()).add(code)

    cases = [
        ("good.md", set()),
        ("space.md", {"E2"}),
        ("unclosed.md", {"E3"}),
        ("fullwidth.md", {"E4"}),
        ("space_in_url.md", {"E5"}),
        ("empty.md", {"W1"}),
        ("nested.md", {"W2"}),
        ("trailing.md", {"W3"}),
        ("task.md", set()),
    ]
    ok = 0
    for name, expect in cases:
        got = found.get(name, set())
        if got == expect:
            ok += 1
        else:
            print(f"  FAIL {name}: expect={sorted(expect)} got={sorted(got)}")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    quiet = "--quiet" in argv
    rest = [a for a in argv if not a.startswith("--")]
    if len(rest) > 1:
        print("usage: linkformcheck.py [root] [--quiet] | --selftest")
        return 2
    return run(rest[0] if rest else ".", quiet)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
