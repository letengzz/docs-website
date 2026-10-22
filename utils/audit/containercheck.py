#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""containercheck.py — 提示容器 `:::` 的开闭配对巡检 · 第 82 项

为什么立这一项
--------------
`AGENTS.md` 第 4 节把 `::: tip / warning / danger / info / details` 定为本库的提示容器，
`config.mts` 还把标题文案改成了中文（提示 / 说明 / 注意 / 信息 / 详细信息）。这些容器是
**块级语法**：一个没闭合的 `::: tip` 会把后面所有内容一起吞进容器里。

此前 81 项巡检没有一项读过容器的开闭：

* `tickscheck` 管反引号游程与围栏闭合，**只管代码围栏**；
* `headingcheck` 管标题层级；
* `tablecheck` 管表格列数；
* `sectionordercheck` 管「参考资料是否在文末」——它只能看见**标题行**，
  而被容器吞掉的标题在渲染后依然是个标题，所以它也不会报。

于是「容器少写一行 `:::`」这类硬缺陷，构建照样成功、页面照样能开，只是
**后面的判据表与参考资料被塞进了一个灰底框里**，读者看不出、作者看不见。

判据
----
E0 ROOT_NOT_FOUND    仓库根既无 docs/ 也无 project/
E1 NO_CONTAINERS     一个容器都没扫到（活性判据，防「路径写错全绿」）
E2 UNCLOSED          开容器后直到文件结束都没有闭合
E3 STRAY_CLOSE       出现 `:::` 但栈里没有可闭合的容器
E4 UNKNOWN_TYPE      容器类型不在白名单（拼错、或用了别的站的语法）
E5 CLOSE_TOO_SHORT   闭合行的冒号数少于开启行（`:::: tip` 用 `:::` 收）
W1 EMPTY_CONTAINER   容器内没有任何非空内容
W2 TITLE_TOO_LONG    容器标题超过 40 字符（渲染后挤压正文）
W3 TYPE_CASE         类型首字母大写（`::: Tip`，全库统一小写）

纪律
----
* **只读**：不写文件、不改台账。
* **跳过代码围栏**：`:::` 出现在 ``` / ~~~ 块里是示例，不是容器（本库有大量这种示例）。
* **嵌套按冒号数判**：VitePress 允许外层用 4 个以上冒号包住内层的 3 个冒号，
  所以「嵌套」本身不是错误，**冒号数不匹配**才是。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/containercheck.py [--selftest] [--root .]
"""

import argparse
import os
import re
import sys
import tempfile

EXT = (".md",)
SKIP_DIRS = {".git", "node_modules", ".vitepress", "dist", ".workbuddy", "__pycache__"}

TYPES = {
    "tip", "warning", "danger", "info", "details",
    "code-group", "code-group-item", "v-pre", "raw", "note", "important", "caution",
}

OPEN_RE = re.compile(r"^(\s*)(:{3,})\s*(.*)$")
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def iter_pages(root):
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(EXT):
                    yield os.path.join(dirpath, fn)


def scan_file(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    findings = []
    stack = []           # [(lineno, colons, type)]
    in_fence = False
    fence_char = ""
    fence_len = 0
    saw_container = False

    for i, line in enumerate(lines, 1):
        fm = FENCE_RE.match(line)
        if fm:
            ch, run = fm.group(2)[0], len(fm.group(2))
            if not in_fence:
                in_fence, fence_char, fence_len = True, ch, run
                continue
            if ch == fence_char and run >= fence_len:
                in_fence = False
                continue
            continue
        if in_fence:
            continue

        m = OPEN_RE.match(line)
        if not m:
            continue
        colons = len(m.group(2))
        rest = m.group(3).strip()

        if not rest:
            # 闭合：找最近的、冒号数不大于当前的开启行
            if not stack:
                findings.append(("E", "STRAY_CLOSE", i, "多余的 `:::` 闭合"))
                continue
            if stack[-1][1] > colons:
                findings.append(("E", "CLOSE_TOO_SHORT", i,
                                 f"开启用了 {stack[-1][1]} 个冒号，闭合只有 {colons} 个"))
            stack.pop()
            continue

        # 开启
        saw_container = True
        ctype = rest.split()[0].lower()
        title = rest[len(rest.split()[0]):].strip()
        if ctype not in TYPES:
            findings.append(("E", "UNKNOWN_TYPE", i, f"未知容器类型 {ctype!r}"))
        if rest.split()[0][:1].isupper():
            findings.append(("W", "TYPE_CASE", i, f"类型应小写：{rest.split()[0]!r}"))
        if len(title) > 40:
            findings.append(("W", "TITLE_TOO_LONG", i, f"标题 {len(title)} 字符：{title[:20]}…"))

        # 空容器：下一行就是同长度闭合
        nxt = lines[i].strip() if i < len(lines) else ""
        if nxt.startswith(":") and set(nxt) == {":"} and len(nxt) >= colons:
            findings.append(("W", "EMPTY_CONTAINER", i, "容器内没有内容"))

        stack.append((i, colons, ctype))

    for lineno, colons, ctype in stack:
        findings.append(("E", "UNCLOSED", lineno,
                         f"`{':' * colons} {ctype}` 未闭合（吞掉了后续 {len(lines) - lineno} 行）"))

    return findings, saw_container


def run(root):
    pages, errors, warns, containers = 0, [], [], 0
    for p in iter_pages(root):
        pages += 1
        findings, saw = scan_file(p)
        containers += 1 if saw else 0
        for lvl, code, ln, detail in findings:
            rec = (os.path.relpath(p, root), ln, code, detail)
            (errors if lvl == "E" else warns).append(rec)
    return pages, containers, errors, warns


def report(root):
    pages, containers, errors, warns = run(root)
    if pages == 0:
        print("E0 ROOT_NOT_FOUND 未扫到任何页面", file=sys.stderr)
        return 2
    if containers == 0:
        print("E1 NO_CONTAINERS 一个容器都没扫到，拒绝判定", file=sys.stderr)
        return 2
    for path, ln, code, detail in errors:
        print(f"E  {code} {path}:{ln} {detail}")
    for path, ln, code, detail in warns[:60]:
        print(f"W  {code} {path}:{ln} {detail}")
    if len(warns) > 60:
        print(f"... 其余 {len(warns) - 60} 条 W 省略")
    print(f"pages={pages} pages_with_containers={containers} E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


def selftest():
    d = tempfile.mkdtemp()
    base = os.path.join(d, "docs", "A")
    os.makedirs(base, exist_ok=True)

    def w(name, text):
        with open(os.path.join(base, name), "w", encoding="utf-8") as f:
            f.write(text)

    w("ok.md", "# ok\n\n::: tip 一句话\n好\n:::\n")
    w("unclosed.md", "# x\n\n::: warning 说明\n内容\n\n## 后面还有一节\n")
    w("stray.md", "# x\n\n:::\n正文\n")
    w("unknown.md", "# x\n\n::: tipp 打错了\n内容\n:::\n")
    w("short.md", "# x\n\n:::: tip 外层\n内层\n:::\n::::\n")
    w("empty.md", "# x\n\n::: info\n:::\n")
    w("longtitle.md", "# x\n\n::: tip " + "很长的标题" * 10 + "\n内容\n:::\n")
    w("case.md", "# x\n\n::: Tip 大写\n内容\n:::\n")
    w("nested.md", "# x\n\n:::: details 外层\n\n::: tip 内层\n内容\n:::\n\n::::\n")
    w("fenced.md", "# x\n\n```markdown\n::: tip 这是示例\n:::\n```\n")

    pages, containers, errors, warns = run(d)
    ecode = {c for _, _, c, _ in errors}
    wcode = {c for _, _, c, _ in warns}
    pname = lambda recs, n: any(p.endswith(n) for p, *_ in recs)

    cases = [
        ("E1-activity", pages == 10 and containers >= 8),
        ("ok-clean", not pname(errors + warns, "ok.md")),
        ("E2-unclosed", "UNCLOSED" in ecode and pname(errors, "unclosed.md")),
        ("E3-stray", "STRAY_CLOSE" in ecode),
        ("E4-unknown", "UNKNOWN_TYPE" in ecode),
        ("E5-short", "CLOSE_TOO_SHORT" in ecode),
        ("W1-empty", "EMPTY_CONTAINER" in wcode),
        ("W2-long", "TITLE_TOO_LONG" in wcode),
        ("W3-case", "TYPE_CASE" in wcode),
        ("nested-ok", not pname(errors, "nested.md")),
        ("fenced-ignored", not pname(errors + warns, "fenced.md")),
    ]
    ok = 0
    for name, cond in cases:
        print(("PASS " if cond else "FAIL ") + name)
        ok += 1 if cond else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return report(a.root)


if __name__ == "__main__":
    sys.exit(main())
