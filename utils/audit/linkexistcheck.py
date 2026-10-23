#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""linkexistcheck.py —— 相对链接目标存在性巡检（第 86 项）。

为什么要有这一项
----------------
本库有四道「链接门」，但没有一道真的在查「目标文件在不在」：

  * `linkformcheck` 判语法形态（是不是一个合法链接）；
  * `sidebarcheck` 判侧边栏里的路径有没有对应页面；
  * `anchorcheck` 判锚点（`#片段`）是否存在；
  * `casecheck` 判路径拼写的大小写。

而 `.vitepress/config.mts` 里的 `ignoreDeadLinks: true` 把构建期唯一的硬校验关掉了。
于是死链既能构建成功、也能通过全部巡检，只有在读者点下去的那一刻才暴露。

第 195 天的一次性脚本在本库抓出 37 条死链（16 个文件），形态高度一致：**子目录页面引用
同级章节时少写一级 `../`**。那批已全部修好，但巡检没写下来——本项就是把那次的一次性
脚本固化成可复跑的判据。

判据
----
E0 ROOT_NOT_FOUND     根目录不存在
E1 NO_PAGES           没扫到任何 Markdown（活性判据：拒绝在空集上给出全绿）
E2 BROKEN_MD          相对 `.md` 链接的目标不存在
E3 BROKEN_ASSET       相对图片/资源链接的目标不存在
E4 BROKEN_DIR         以 `/` 结尾的目录链接，目标目录不存在

W1 ABS_PATH           以 `/` 开头的站内绝对路径（VitePress 会补 base，降为计数）
W2 NO_EXT             链接目标既无扩展名也不以 `/` 结尾（无法判定，交人工）

三处必须先定的口径（这是本项真正的难点）
----------------------------------------
1. **必须跳过围栏代码块与行内代码**。首版直接扫 `\\]\\(([^)]+)\\)`，全库报 98 条，其中大半是
   代码里的示例文本与 URL 编码文件名；去掉围栏与行内代码、再 `unquote()` 之后降到 59 条，
   再限定「必须含 `.md` 或以 `/` 结尾」才降到 37 条——**误报率 62%，而一个会误报的巡检
   一定会被无视**，所以三道过滤缺一不可。
2. **`<...>` 形式的链接合法**。`[主键回填](<BasicOperation.md#主键-自动递增-回填>)` 是
   CommonMark 的尖括号目标写法，路径里带 `<` 不是缺陷。
3. **修复要用「前缀搜索」而不是「改一个字符」**：对每条死链剥离前导 `../` 后依次试
   `''` / `../` / `../../` / `../../../` / `../../../../`，**只有唯一命中才改**，
   0 个或多个命中一律交人工——宁可留一条 E，也不猜。

刻意不查的
----------
* `http(s)://`、`mailto:`、`tel:`、`data:`；
* 纯锚点 `#xxx`；
* `public/` 下的全局资源（不经 Markdown 相对引用）。

与第 84 项（`casecheck`）的分工
-------------------------------
`casecheck` 管「路径拼写大小写」，本项管「层级对不对」。两者会有交集：一条链接可能既
大小写错又少一层 `../`。交叉验证时以 `casecheck` 的逐段 `listdir` 结果为准，本项只判
`os.path.exists`。

用法
----
    python3 utils/audit/linkexistcheck.py [根目录] [--quiet]
    python3 utils/audit/linkexistcheck.py [根目录] --fix     # 唯一命中时才改写
    python3 utils/audit/linkexistcheck.py --selftest

退出码：0 = 无 E 级；1 = 有 E 级；2 = 用法错误。
"""
import os
import re
import sys
import tempfile
from urllib.parse import unquote

LINK = re.compile(r'!?\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+?)(?:\s+"[^"]*")?\s*\)')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
INLINE = re.compile(r'(`+)(?!`)(.+?)(?<!`)\1(?!`)')
SKIP_DIRS = {".git", "node_modules", ".vitepress", ".workbuddy", "dist", "public"}
PREFIXES = ["", "../", "../../", "../../../", "../../../../", "../../../../../"]


def strip_noise(text):
    """去掉围栏代码块与行内代码，避免把示例文本当链接。"""
    out, fch, flen = [], None, 0
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            ch = m.group(1)[0]
            if fch is None:
                fch, flen = ch, len(m.group(1))
            elif ch == fch and len(m.group(1)) >= flen and not line.strip().strip(ch):
                fch, flen = None, 0
            out.append("")
            continue
        out.append("" if fch else INLINE.sub("``", line))
    return "\n".join(out)


def iter_pages(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def classify(target):
    """返回 (kind, path)。kind ∈ {'skip','md','asset','dir','noext'}"""
    t = target.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()
    if not t or t.startswith("#"):
        return "skip", t
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', t) or t.startswith("//"):
        return "skip", t
    if t.startswith("/"):
        return "abs", t
    t = t.split("#", 1)[0].split("?", 1)[0]
    t = unquote(t)
    if not t:
        return "skip", t
    if t.endswith(".md"):
        return "md", t
    if t.endswith("/"):
        return "dir", t
    if os.path.splitext(t)[1]:
        return "asset", t
    return "noext", t


def check_pages(root):
    pages, errs, warns = 0, [], []
    for page in iter_pages(root):
        pages += 1
        base = os.path.dirname(page)
        rel = os.path.relpath(page, root)
        try:
            text = open(page, encoding="utf-8").read()
        except UnicodeDecodeError:
            errs.append(("E5 NOT_UTF8", rel, ""))
            continue
        for m in LINK.finditer(strip_noise(text)):
            raw = m.group(1)
            kind, t = classify(raw)
            if kind == "skip":
                continue
            if kind == "abs":
                warns.append(("W1 ABS_PATH", rel, t))
                continue
            if kind == "noext":
                warns.append(("W2 NO_EXT", rel, t))
                continue
            full = os.path.normpath(os.path.join(base, t))
            if os.path.exists(full):
                continue
            code = {"md": "E2 BROKEN_MD", "asset": "E3 BROKEN_ASSET",
                    "dir": "E4 BROKEN_DIR"}[kind]
            errs.append((code, rel, t))
    return pages, errs, warns


def fix_pages(root):
    """对唯一可解析的死链做前缀搜索修复。返回 (改写数, 仍需人工数)。"""
    fixed = todo = 0
    for page in iter_pages(root):
        base = os.path.dirname(page)
        text = open(page, encoding="utf-8").read()
        clean = strip_noise(text)
        edits = []
        for m in LINK.finditer(clean):
            raw = m.group(1)
            kind, t = classify(raw)
            if kind in ("skip", "abs", "noext"):
                continue
            if os.path.exists(os.path.normpath(os.path.join(base, t))):
                continue
            stem = t
            while stem.startswith("../"):
                stem = stem[3:]
            hits = []
            for p in PREFIXES:
                cand = os.path.normpath(os.path.join(base, p + stem))
                if os.path.exists(cand):
                    hits.append(p + stem)
            if len(hits) == 1:
                edits.append((raw, hits[0]))
            else:
                todo += 1
        for old, new in edits:
            text = text.replace("(" + old, "(" + new, 1)
            fixed += 1
        if edits:
            open(page, "w", encoding="utf-8").write(text)
    return fixed, todo


def run(root=".", quiet=False, do_fix=False):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND", root)
        return 1
    pages, errs, warns = check_pages(root)
    if pages == 0:
        print("E1 NO_PAGES")
        return 1
    if do_fix:
        fixed, todo = fix_pages(root)
        print(f"fix: rewritten={fixed} needs_human={todo}")
        pages, errs, warns = check_pages(root)
    if not quiet:
        for code, path, tgt in errs:
            print(f"{code}  {path}  ->  {tgt}")
        for code, path, tgt in warns:
            print(f"{code}  {path}  ->  {tgt}")
    n_abs = sum(1 for w in warns if w[0].startswith("W1"))
    n_noext = sum(1 for w in warns if w[0].startswith("W2"))
    print(f"pages={pages} E={len(errs)} W1_ABS={n_abs} W2_NOEXT={n_noext}")
    return 1 if errs else 0


def selftest():
    checks = []

    def case(name, cond):
        checks.append((name, bool(cond)))

    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "docs", "A", "assets"))
    os.makedirs(os.path.join(tmp, "docs", "B"))
    open(os.path.join(tmp, "docs", "A", "assets", "x.svg"), "w").write("<svg/>")
    # 正确：同级目录
    open(os.path.join(tmp, "docs", "A", "ok.md"), "w").write(
        "[b](../B/index.md)\n![x](assets/x.svg)\n")
    open(os.path.join(tmp, "docs", "B", "index.md"), "w").write("# B\n")
    # 少写一层 ../
    open(os.path.join(tmp, "docs", "A", "bad.md"), "w").write(
        "[b](B/index.md)\n")
    # 图片路径错
    open(os.path.join(tmp, "docs", "A", "img.md"), "w").write("![x](./assets/none.svg)\n")
    # 围栏里的示例不能算
    open(os.path.join(tmp, "docs", "A", "fence.md"), "w").write(
        "```markdown\n[t](Nope/index.md)\n```\n")
    # 行内代码不能算
    open(os.path.join(tmp, "docs", "A", "inline.md"), "w").write(
        "写法是 `[t](Nope/index.md)`。\n")
    # 尖括号目标
    open(os.path.join(tmp, "docs", "A", "angle.md"), "w").write(
        "[b](<../B/index.md#top>)\n")
    # 绝对路径降为 W
    open(os.path.join(tmp, "docs", "A", "abs.md"), "w").write("[x](/docs/B/index.md)\n")

    pages, errs, warns = check_pages(tmp)
    codes = [e[0] for e in errs]
    hit = lambda code, name: any(c == code and p.endswith(name) for c, p, _ in errs)
    case("pages 计数为 8", pages == 8)
    case("少一层 ../ 报 E2", hit("E2 BROKEN_MD", "bad.md"))
    case("图片丢失报 E3", hit("E3 BROKEN_ASSET", "img.md"))
    case("同级正确链接不报错", not any(p.endswith("ok.md") for _, p, _ in errs))
    case("围栏内示例不报错", not any(p.endswith("fence.md") for _, p, _ in errs))
    case("行内代码不报错", not any(p.endswith("inline.md") for _, p, _ in errs))
    case("尖括号目标不报错", not any(p.endswith("angle.md") for _, p, _ in errs))
    case("绝对路径降为 W1", any(w[0].startswith("W1") and w[1].endswith("abs.md") for w in warns))
    case("E 级总数 = 2", len(errs) == 2)

    fixed, todo = fix_pages(tmp)
    case("唯一命中被修复", fixed == 1 and todo == 1)
    _, errs2, _ = check_pages(tmp)
    case("修复后 E2 消失、E3 仍在",
         len(errs2) == 1 and errs2[0][0].startswith("E3"))

    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        print(f"{'PASS' if c else 'FAIL'}  {name}")
    print(f"\nselftest {ok}/{len(checks)}")
    return 0 if ok == len(checks) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    do_fix = "--fix" in argv
    quiet = "--quiet" in argv
    rest = [a for a in argv[1:] if not a.startswith("--")]
    if len(rest) > 1:
        print("用法：linkexistcheck.py [根目录] [--fix] [--quiet] [--selftest]")
        return 2
    return run(rest[0] if rest else ".", quiet, do_fix)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
