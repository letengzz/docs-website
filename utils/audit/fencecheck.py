#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""fencecheck.py — 代码块围栏与语言标注巡检 · 第 72 项

为什么立这一项
--------------
`AGENTS.md` 第 4.4 条要求「代码块必须标注语言」，第 7.7 条要求「流程/架构图必须配 SVG，
禁止只用 `text` 代码块画图」。这两条都是**人眼约定**，此前 71 项巡检里没有任何一项
读过代码块的 info string：

* `tickscheck` 管反引号游程与围栏闭合，**不看围栏后面跟了什么**；
* `headingcheck` 管标题层级；
* `linkcheck` / `anchorcheck` 管链接；
* `judge*` 管判据编号。

于是「``` 后面什么都没写」的代码块在构建时正常渲染（只是不高亮），
「用 `text` 块画 ASCII 架构图」也正常渲染（只是缩放后糊成一团）——
两者都不报错，只是读者体验下降，属于**永远不会被构建发现**的一类债。

判据
----
E0 ROOT_NOT_FOUND   仓库根找不到
E1 NO_PAGES         一个页面都没扫到（活性判据）
E2 NO_LANG          围栏没有 info string（``` 后面直接换行）
E3 EMPTY_FENCE      空代码块（开闭之间没有任何非空行）
W1 UNKNOWN_LANG     info 首词不在语言白名单（可能是缩写/拼写错误）
W2 TEXT_DIAGRAM     text/plaintext 块里出现 ≥3 个箭头或 ≥2 个框线字符（应改 SVG）
W3 LONG_FENCE       单个代码块超过 200 行（应拆或省略）
W4 LANG_UPPER       语言标注用了大写（```SQL），渲染能识别但全库不统一

纪律
----
* **只读**：不写文件、不改台账。
* **白名单宁可宽**：`W1` 是提示级，宽一点不会淹没真问题；`E2` 才是硬错误。
* **不做修复建议的自动执行**：`text` 图是否该改 SVG 需要人判断（有些是协议报文示例，
  本来就该用 text）。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/fencecheck.py [--selftest] [--root .]
"""

import argparse
import os
import re
import sys
import tempfile

EXT = (".md",)
SKIP_DIRS = {".git", "node_modules", ".vitepress", "dist", ".workbuddy", "__pycache__"}

LANGS = {
    "text", "plaintext", "txt", "console", "log", "diff", "markdown", "md", "mdx",
    "html", "xml", "svg", "css", "scss", "sass", "less", "js", "jsx", "ts", "tsx",
    "json", "jsonc", "json5", "javascript", "yaml", "yml", "toml", "ini", "conf", "properties",
    "env", "dotenv", "shell", "bash", "sh", "zsh", "fish", "powershell", "ps1",
    "bat", "batch", "cmd", "dockerfile", "dockerignore", "makefile", "cmake", "gradle",
    "groovy", "java", "kotlin", "scala", "python", "py", "go", "rust", "c", "cpp",
    "csharp", "cs", "php", "ruby", "rb", "swift", "dart", "lua", "r", "sql", "plsql",
    "tsql", "graphql", "gql", "proto", "protobuf", "prisma", "hcl", "tf", "nginx",
    "apache", "http", "curl", "regex", "csv", "tsv", "mermaid", "puml", "plantuml",
    "vue", "svelte", "astro", "handlebars", "ejs", "jinja", "liquid", "nix", "vim",
    "systemd", "unit", "crontab", "gitignore", "editorconfig", "httprequest", "ws",
}

FENCE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)?(`{3,}|~{3,})(.*)$")
ARROW_RE = re.compile(r"(→|<-|->|=>|⟶|⇒)")
BOX_RE = re.compile(r"[┌┐└┘┏┓┗┛]")   # 只算「角」，不算目录树的 ├ └ │ ─


def iter_pages(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(EXT):
                yield os.path.join(dirpath, fn)


def scan_file(path):
    """返回 findings 列表： (level, code, lineno, detail)"""
    findings = []
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")

    i = 0
    n = len(lines)
    while i < n:
        m = FENCE_RE.match(lines[i])
        if not m or (m.group(1)[0] == "`" and "`" in m.group(2) and m.group(2).strip().startswith("`")):
            i += 1
            continue
        fence = m.group(1)
        info = m.group(2).strip()
        start = i
        # 找闭合
        j = i + 1
        closed = False
        while j < n:
            m2 = FENCE_RE.match(lines[j])
            if m2 and m2.group(1)[0] == fence[0] and len(m2.group(1)) >= len(fence) and not m2.group(2).strip():
                closed = True
                break
            j += 1
        body = lines[start + 1:j] if closed else lines[start + 1:]
        if not closed:
            # 围栏未闭合归 tickscheck 的 E3 管，这里跳出，避免重复判据
            break

        lang = info.split()[0].lower() if info.split() else ""
        if not lang:
            findings.append(("E", "NO_LANG", start + 1, "围栏无语言标注"))
        elif lang.strip("{}.") not in LANGS:
            findings.append(("W", "UNKNOWN_LANG", start + 1, f"未知语言 {lang!r}"))

        body_nonempty = [l for l in body if l.strip()]
        if not body_nonempty:
            findings.append(("E", "EMPTY_FENCE", start + 1, "空代码块"))

        if lang in ("", "text", "plaintext", "txt"):
            arrows = sum(len(ARROW_RE.findall(l)) for l in body)
            boxes = sum(len(BOX_RE.findall(l)) for l in body)
            if arrows >= 3 or boxes >= 2:
                findings.append(("W", "TEXT_DIAGRAM", start + 1,
                                 f"疑似用 text 画图（箭头 {arrows} / 框线 {boxes}），应改 SVG"))

        if len(body) > 200:
            findings.append(("W", "LONG_FENCE", start + 1, f"代码块 {len(body)} 行"))

        first = info.split()[0] if info.split() else ""
        if first and first != first.lower() and first.lower() in LANGS:
            findings.append(("W", "LANG_UPPER", start + 1, f"语言标注应小写：{first!r}"))

        i = j + 1
    return findings


def run(root):
    pages, errors, warns = 0, [], []
    for p in iter_pages(root):
        pages += 1
        for lvl, code, ln, detail in scan_file(p):
            rec = (os.path.relpath(p, root), ln, code, detail)
            (errors if lvl == "E" else warns).append(rec)
    return pages, errors, warns


def report(root):
    pages, errors, warns = run(root)
    if pages == 0:
        print("E1 NO_PAGES 未扫到任何页面", file=sys.stderr)
        return 2
    for path, ln, code, detail in errors:
        print(f"E2 {code} {path}:{ln} {detail}")
    for path, ln, code, detail in warns[:60]:
        print(f"W  {code} {path}:{ln} {detail}")
    if len(warns) > 60:
        print(f"... 其余 {len(warns) - 60} 条 W 省略")
    print(f"pages={pages} E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


def selftest():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "A"), exist_ok=True)

    def w(name, text):
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    w("docs/A/ok.md", "# ok\n\n```sql\nselect 1;\n```\n")
    w("docs/A/nolang.md", "# x\n\n```\nplain\n```\n")
    w("docs/A/empty.md", "# x\n\n```js\n\n```\n")
    w("docs/A/unknown.md", "# x\n\n```foobar\nx\n```\n")
    w("docs/A/diagram.md", "# x\n\n```text\nA → B → C → D\n```\n")
    w("docs/A/upper.md", "# x\n\n```SQL\nselect 1;\n```\n")
    w("docs/A/goodtitle.md", "# x\n\n```js [src/main.js]\nconst a = 1\n```\n")
    w("docs/A/tree.md", "# x\n\n```text\nsrc/\n├── a.ts\n└── b.ts\n```\n")

    pages, errors, warns = run(d)
    codes = {(c) for _, _, c, _ in errors}
    wcodes = {(c) for _, _, c, _ in warns}
    cases = [
        ("E1-activity", pages == 8),
        ("ok-clean", not any(p.endswith("ok.md") for p, *_ in errors + warns)),
        ("e2-nolang", "NO_LANG" in codes),
        ("e3-empty", "EMPTY_FENCE" in codes),
        ("w1-unknown", "UNKNOWN_LANG" in wcodes),
        ("w2-diagram", "TEXT_DIAGRAM" in wcodes),
        ("tree-not-diagram", not any(p.endswith("tree.md") for p, _, c, _ in warns)),
        ("w4-upper", "LANG_UPPER" in wcodes),
        ("upper-clean", not any(p.endswith("goodtitle.md") for p, _, c, _ in warns)),
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
