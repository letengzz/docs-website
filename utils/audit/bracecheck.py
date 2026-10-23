#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bracecheck.py —— Vue 插值（双花括号）巡检（第 87 项）。

为什么要有这一项
----------------
VitePress 把每个 `.md` 编译成 Vue 单文件组件，于是正文里的 `{{ ... }}` 会被当成
**Vue 插值表达式**去求值。这件事的三种后果按严重程度排：

1. **构建直接失败**：`{{.HostConfig.Memory}}` 不是合法 JS 表达式，`@vue/compiler-sfc`
   在 `Error parsing JavaScript expression: Unexpected token` 处抛错，整个 `docs:build`
   中断——**一次失败就是几分钟的构建时间**。
2. **静默吃掉内容**：`{{ token }}` 这种能解析的写法会被求值成空串，正文里那半句话就
   凭空消失，而构建成功、所有巡检全绿、读者只看到一句缺了半截的话。
3. **意料之外的行为**：`{{ baseUrl }}` 求值成 `undefined`，页面上真的印出 `undefined`。

第 136 天曾在 `DOCS_PLAN.md` 里把这项立为「第二十九项巡检 `bracecheck.py`」，但仓库里
**从来没有这个文件**（`utils/audit/` 下一直找不到，只有计划里的记录）。第 196 天新建
`EventOrderHub/DeployCompose` 时写进三行内联代码（`docker inspect -f '{{.HostConfig.NanoCpus}}'`），
`docs:build` 在 **2m57s** 后失败——**这就是「记在文档里 ≠ 有机器在守」的现价**。本项补上。

判据
----
E0 ROOT_NOT_FOUND     根目录不存在
E1 NO_PAGES           没扫到任何 Markdown（活性判据：拒绝在空集上给出全绿）
E2 INTERP             围栏代码块之外、且不在 `<span v-pre>` 里的 `{{`

W1 VPRE_COUNT         已用 `<span v-pre>...</span>` 正确转义的处数（只计数）
W2 VPRE_UNCLOSED      `<span v-pre>` 在文件结束前没有闭合（转义会一直吞到文末）

三处必须先定的口径
------------------
1. **围栏代码块里的 `{{ }}` 是安全的**。VitePress 对 fenced code 做了转义，`docs/Ops/Docker/Monitor`
   里的 `--format "table {{.Name}}\t{{.CPUPerc}}"` 一直构建正常。所以本项**只扫围栏外**——
   这与 `linkexistcheck` 恰好相反（那边要连围栏一起跳，因为示例里的假链接不该判死）。
2. **行内代码不是安全区**。`` `{{.HostConfig.Memory}}` `` 会被渲染成 `<code>` 元素，但
   `<code>` 里的文本照样进 Vue 模板编译——**这正是本次构建失败的那一行**。反例：
   `docs/Ops/Docker/NetworkAdvanced` 的 `docker network inspect` 示例在围栏内，安然无恙。
3. **必须认 `<span v-pre>` 这个既有约定**。库内 17+ 页用它绕开插值（`Tools/APITools/FAQ`、
   `Tools/Toolchain/Scaffold`、`Frontend/Frame/WxMini/Template` 等），写法统一是
   `<span v-pre>`{{baseUrl}}`</span>`——`v-pre` 元素内部不编译，是本库唯一被验证过的转义方式。

用法
----
    python3 utils/audit/bracecheck.py [根目录] [--fix] [--quiet] [--selftest]

`--fix` 只处理一种最安全的形态：**一行里恰好一处 `{{`，且它落在一个行内代码里**——
在代码两侧套上 `<span v-pre>`。其余情形（一行多处、裸文本、跨行）一律交人工，
因为自动补 `<span>` 很容易把表格或列表结构改坏。
"""

import os
import re
import sys
import tempfile

SKIP_DIRS = {
    "node_modules", ".git", ".vitepress", ".workbuddy", "dist", "tmp",
    ".venv", "__pycache__", ".idea", ".vscode", "site", "public", ".trae",
}

# 根目录下这几篇是「规划 / 约定」而不是站点页面，不参与构建，也就不该被这条判据约束。
# 但根目录的 `index.md` **是首页**，必须扫——一刀切跳过根目录会漏掉首页。
SKIP_ROOT_FILES = {"DOCS_PLAN.md", "AGENTS.md", "README.md", "CLAUDE.md"}

FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
# `<span v-pre>...</span>`：非贪婪，允许内部再有 span（实际没有，但不要假设）
VPRE = re.compile(r"<span\b[^>]*\bv-pre\b[^>]*>.*?</span>", re.S)
VPRE_OPEN = re.compile(r"<span\b[^>]*\bv-pre\b[^>]*>")
# 行内代码：成对的等长反引号（支持 ``a`b`` 这种嵌一个反引号的写法）
INLINE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")


def fenced_lines(lines):
    """产出 (行号, 行文本, 是否在围栏内)。围栏解析要认字符与长度：

    本库有 3 篇用**四反引号围栏嵌三反引号**（`Others/TechWriting/Examples` 等），
    简单切换会在内层的 ``` 上提前闭合——`levelskipcheck` 在这里被误报打回过一次。
    """
    fence = None
    for i, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if m:
            mark = m.group(1)
            char, length = mark[0], len(mark)
            if fence is None:
                fence = (char, length)
                yield i, line, True
                continue
            if char == fence[0] and length >= fence[1]:
                # 闭合行本身也在围栏内（不该被当作内容）
                yield i, line, True
                fence = None
                continue
            yield i, line, True
            continue
        yield i, line, fence is not None


def scan_text(text):
    """返回 (e2 列表, w1 计数, w2 列表)；条目是 (行号, 该行原文)。"""
    e2, w2 = [], []
    w1 = 0
    in_vpre = False
    for lineno, line, inside_fence in fenced_lines(text.split("\n")):
        if inside_fence:
            in_vpre = False
            continue

        # 未闭合的 <span v-pre> 会一路吞到文末，单独记一条 W 并停止解释后面的行。
        # 判「有没有未闭合的标签」前必须先把行内代码屏蔽成空白——正文里**提到**
        # `<span v-pre>` 这个标签（本页判据表就是这么写的）不是真的开了个标签。
        code_free = INLINE.sub(lambda m: " " * len(m.group(0)), line)
        if in_vpre:
            if "</span>" in code_free:
                in_vpre = False
            continue
        if VPRE_OPEN.search(code_free) and "</span>" not in code_free.split("<span", 1)[-1]:
            w2.append((lineno, line))
            in_vpre = True
            continue

        # 先把已转义的区域整段抹掉，再找残留的 {{
        stripped, n = VPRE.subn("", line)
        w1 += n
        if "{{" in stripped:
            e2.append((lineno, line))
    return e2, w1, w2


def iter_pages(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        at_root = os.path.abspath(dirpath) == os.path.abspath(root)
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            if at_root and name in SKIP_ROOT_FILES:
                continue
            yield os.path.join(dirpath, name)


def check_pages(root):
    pages = 0
    errs, warns = [], []
    for path in iter_pages(root):
        pages += 1
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError) as exc:  # pragma: no cover
            errs.append((f"E1 READ_FAIL", rel, str(exc)))
            continue
        e2, w1, w2 = scan_text(text)
        for lineno, line in e2:
            snippet = line.strip()
            if len(snippet) > 96:
                snippet = snippet[:96] + "…"
            errs.append(("E2 INTERP", rel, f"{lineno}: {snippet}"))
        for lineno, line in w2:
            warns.append(("W2 VPRE_UNCLOSED", rel, f"{lineno}: {line.strip()[:80]}"))
        if w1:
            warns.append(("W1 VPRE_COUNT", rel, f"{w1} 处已转义"))
    return pages, errs, warns


def fix_pages(root):
    """只修「一行恰好一处 `{{` 且落在一个行内代码里」的形态。返回 (已修文件, 需人工文件)。"""
    fixed, manual = 0, 0
    for path in iter_pages(root):
        try:
            original = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        e2, _, _ = scan_text(original)
        if not e2:
            continue
        lines = original.split("\n")
        changed = False
        for lineno, line in e2:
            body = VPRE.sub("", line)
            if body.count("{{") != 1:
                manual += 1
                continue
            spans = [m for m in INLINE.finditer(body) if "{{" in m.group(0)]
            if len(spans) != 1:
                manual += 1
                continue
            m = spans[0]
            new_body = body[: m.start()] + "<span v-pre>" + m.group(0) + "</span>" + body[m.end():]
            # VPRE.sub 抹掉了旧转义区，若本行原本就有转义区则不敢改（交给人工）
            if VPRE.search(line):
                manual += 1
                continue
            lines[lineno - 1] = new_body
            changed = True
        if changed:
            open(path, "w", encoding="utf-8").write("\n".join(lines))
            fixed += 1
    return fixed, manual


def run(root, quiet=False, do_fix=False):
    if not os.path.isdir(root):
        print(f"E0 ROOT_NOT_FOUND  {root}")
        return 1
    if do_fix:
        fixed, manual = fix_pages(root)
        if not quiet:
            print(f"已修文件 {fixed} 个，需人工 {manual} 处\n")

    pages, errs, warns = check_pages(root)
    if pages == 0:
        print("E1 NO_PAGES  扫到 0 篇 Markdown，拒绝判定")
        return 1

    by_code = {}
    for code, path, detail in errs:
        by_code.setdefault(code, []).append((path, detail))
    for code in sorted(by_code):
        for path, detail in by_code[code] if not quiet else by_code[code][:5]:
            print(f"{code}  {path}  {detail}")
        if quiet and len(by_code[code]) > 5:
            print(f"{code}  ... 其余 {len(by_code[code]) - 5} 条省略")

    w1 = sum(int(d.split(" ")[0]) for c, _, d in warns if c.startswith("W1"))
    w2 = [w for w in warns if w[0].startswith("W2")]
    if w2 and not quiet:
        for _, path, detail in w2[:10]:
            print(f"W2 VPRE_UNCLOSED  {path}  {detail}")
    print()
    print(f"pages={pages} E={len(errs)} W1_VPRE={w1} W2_UNCLOSED={len(w2)}")
    return 0 if not errs else 1


def selftest():
    checks = []
    case = lambda name, ok: checks.append((name, ok))

    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "docs", "A"))
    w = lambda name, text: open(os.path.join(tmp, "docs", "A", name), "w", encoding="utf-8").write(text)

    # 1 围栏内的插值不该报错
    w("fence.md", "# 围栏\n\n```shell\ndocker inspect -f '{{.State}}' x\n```\n")
    # 2 行内代码里的未转义插值要报错（本次构建失败的形态）
    w("inline.md", "# 行内\n\n用 `docker inspect -f '{{.State.OOMKilled}}' x` 看。\n")
    # 3 已用 <span v-pre> 转义的不报错
    w("vpre.md", "# 转义\n\n用 <span v-pre>`{{baseUrl}}`</span> 表示变量。\n")
    # 4 裸文本里的插值要报错
    w("bare.md", "# 裸\n\n值是 {{ token }} 这样。\n")
    # 5 未闭合的 v-pre 记 W2
    w("open.md", "# 未闭合\n\n<span v-pre>后面都算转义 {{x}}\n")
    # 6 四反引号围栏内嵌三反引号，里面的 {{ }} 不该报错
    w("four.md", "# 四反引号\n\n````markdown\n```js\nconst s = `{{raw}}`;\n```\n````\n")
    # 7 修复目标：一行一处、落在行内代码里
    w("fixme.md", "# 待修\n\n看 `inspect -f '{{.HostConfig.Memory}}' app` 即可。\n")
    # 8 一行两处，--fix 应交给人工
    w("two.md", "# 两处\n\n`{{a}}` 与 `{{b}}` 都在代码里。\n")
    # 9 根目录的规划文件不该被扫
    open(os.path.join(tmp, "DOCS_PLAN.md"), "w", encoding="utf-8").write("{{不参与构建}}\n")

    pages, errs, warns = check_pages(tmp)
    names = {os.path.basename(p) for _, p, _ in errs}
    case("pages 计数为 8（根目录规划文件不扫）", pages == 8)
    case("行内代码未转义报 E2", "inline.md" in names)
    case("裸文本插值报 E2", "bare.md" in names)
    case("围栏内插值不报错", "fence.md" not in names)
    case("四反引号围栏内不报错", "four.md" not in names)
    case("v-pre 转义不报错", "vpre.md" not in names)
    case("未闭合 v-pre 记 W2", any(c.startswith("W2") and p.endswith("open.md") for c, p, _ in warns))
    case("E 级总数 = 4", len(errs) == 4)

    fixed, manual = fix_pages(tmp)
    _, errs2, warns2 = check_pages(tmp)
    names2 = {os.path.basename(p) for _, p, _ in errs2}
    case("两处「一行一 span」被自动修复", fixed == 2 and "fixme.md" not in names2 and "inline.md" not in names2)
    case("一行多处/裸文本交人工、未闭合仍记 W2",
         manual == 2 and {"two.md", "bare.md"} <= names2
         and any(c.startswith("W2") and p.endswith("open.md") for c, p, _ in warns2))

    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        print(f"{'PASS' if c else 'FAIL'}  {name}")
    print(f"\nselftest {ok}/{len(checks)}")
    return 0 if ok == len(checks) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    quiet = "--quiet" in argv
    do_fix = "--fix" in argv
    rest = [a for a in argv[1:] if not a.startswith("--")]
    if len(rest) > 1:
        print("用法：bracecheck.py [根目录] [--fix] [--quiet] [--selftest]")
        return 2
    return run(rest[0] if rest else ".", quiet, do_fix)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
