#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fencepathcheck.py —— 代码块「标题 ⇄ 围栏语言 ⇄ 路径形态」一致性巡检（第 81 项巡检）

背景
----
本仓 4,900 余个代码块带标题语法 ```` ```ts [src/main.ts] ````（AGENTS.md 4.4 条）。
标题的作用是告诉读者「这段代码放在哪个文件」，于是它同时承担了三件事：

  1. 语言：围栏声明的语言应该与文件扩展名一致；
  2. 位置：标题应该是读者工程里的相对路径，而不是某台机器上的绝对路径；
  3. 身份：同一页里同一个标题出现两次，通常意味着一段代码被贴了两遍而只改了一处。

既有的门禁都不读这三件事：`fencecheck` 只看「有没有 info string、语言在不在白名单」，
`langmatchcheck` 只看「围栏语言与块内内容像不像」，`linkcheck` 只看 Markdown 链接——
于是「标着 `java` 的块写着 `[main.go]`」这种**复制就错**的债全库静默：构建通过、
读者照着建文件，编译器报的第一个错与文档毫无关系。

判据（E 为错误、W 为提示）
--------------------------
  E0 ROOT_NOT_FOUND        给定的根目录不存在
  E1 NO_FENCES             一页带标题的代码块都没扫到（活性判据）
  E2 TITLE_LANG_MISMATCH   标题扩展名与围栏语言不属于同一族（`[main.go]` + ```java）
  E3 TITLE_EMPTY           空标题 `[]`
  W1 TITLE_NOT_PATH        标题不是路径（`[终端]`、`[输出]`、`[目录结构]`）
  W2 TITLE_DUP_IN_PAGE     同页同一标题出现 ≥2 次
  W3 TITLE_ABSOLUTE        标题以 `/`、`~` 或盘符开头（读者复制会指向本机）
  W4 TITLE_PLACEHOLDER     标题含 `<...>` 或 `xxx`/`...` 占位

口径说明（为什么这样取数）
--------------------------
1. **只判「两处都确定」的冲突**：标题没有扩展名、或围栏语言是 `text`/`mermaid`/`diff`
   这类中性语言时，不做语言判定——判据的第一版若把 `[终端]` 全算成错误，会立刻产生
   上千条噪声，而噪声会让人跳过这个检查。
2. **扩展名 → 语言族用白名单表**，表外的扩展名不进 E2（宁可漏，不可误报）。
3. **`Dockerfile` / `Makefile` 这类无扩展名但确定语言的标题**单列白名单，不算 W1。
4. **三处放行是刻意的**：`.ts` 里贴 JS、`.vue` 里贴 `<script>`/`<style>` 片段、`.env`
   标 `dotenv`——这三种在真实语料里都是「片段级」写法，判成错误会制造假警报。
5. **W2 只提示不判错**：同一页两段代码共用一个文件名是合法的（如「反例 / 正例」），
   但值得人看一眼是不是漏改了其中一段。

用法
----
    python3 utils/audit/fencepathcheck.py [--root .] [--selftest] [--verbose]

退出码：0 = 无 E（W 不影响退出码）；1 = 存在 E；2 = 参数或根目录错误。
"""

import argparse
import os
import re
import sys
import tempfile

FENCE = re.compile(r"^(?P<ticks>`{3,})[ \t]*(?P<lang>[A-Za-z0-9#+_.-]*)[ \t]*(?:\[(?P<title>[^\]]*)\])?[ \t]*$")

# 扩展名 → 允许的围栏语言族
EXT_LANG = {
    "py": {"python", "py"},
    "ts": {"ts", "typescript", "tsx", "js"},
    "tsx": {"tsx", "ts", "typescript", "js"},
    "mts": {"ts", "typescript"},
    "js": {"js", "javascript", "jsx"},
    "jsx": {"jsx", "js", "javascript"},
    "mjs": {"js", "javascript", "mjs"},
    "cjs": {"js", "javascript"},
    "sh": {"shell", "bash", "sh", "zsh", "console"},
    "bash": {"shell", "bash", "sh"},
    "zsh": {"shell", "zsh", "sh"},
    "ps1": {"powershell", "ps1"},
    "yaml": {"yaml", "yml"},
    "yml": {"yaml", "yml"},
    "json": {"json", "jsonc"},
    "jsonc": {"jsonc", "json"},
    "toml": {"toml"},
    "properties": {"properties", "ini", "text"},
    "ini": {"ini", "properties"},
    "env": {"properties", "dotenv", "bash", "shell", "text"},
    "css": {"css"},
    "scss": {"scss", "css"},
    "less": {"less", "css"},
    "html": {"html"},
    "htm": {"html"},
    "vue": {"vue", "html", "ts", "js", "css"},
    "svelte": {"svelte", "html"},
    "sql": {"sql"},
    "java": {"java"},
    "kt": {"kotlin"},
    "kts": {"kotlin"},
    "go": {"go"},
    "rs": {"rust"},
    "c": {"c", "cpp"},
    "h": {"c", "cpp"},
    "cpp": {"cpp", "c"},
    "cs": {"csharp", "cs"},
    "php": {"php"},
    "rb": {"ruby"},
    "xml": {"xml", "html"},
    "md": {"md", "markdown"},
    "gradle": {"groovy", "gradle"},
}

# 无扩展名但语言确定的文件名
BARE_NAMES = {
    "dockerfile": {"dockerfile", "docker"},
    "makefile": {"makefile", "make"},
    "gemfile": {"ruby"},
}

NEUTRAL_LANGS = {"", "text", "plain", "plaintext", "mermaid", "diff", "log", "csv", "http", "output"}

PLACEHOLDER = re.compile(r"[<>]|\bxxx\b|\.\.\.")


def scan_file(path):
    """返回 (title_blocks, findings)；finding 为 (code, line, detail)。"""
    try:
        text = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return [], []
    lines = text.split("\n")
    blocks, out = [], []
    in_fence, ticks = False, ""
    for no, line in enumerate(lines, 1):
        m = FENCE.match(line.strip())
        if not in_fence:
            if not m:
                continue
            ticks = m.group("ticks")
            in_fence = True
            title = m.group("title")
            if title is None:
                continue
            blocks.append((no, (m.group("lang") or "").lower(), title.strip()))
            continue
        # 关闭围栏
        if line.strip().startswith(ticks) and line.strip().strip("`") == "":
            in_fence = False

    seen = {}
    for no, lang, title in blocks:
        if title == "":
            out.append(("E3_TITLE_EMPTY", no, "空标题 []"))
            continue
        low = title.lower()
        base = os.path.basename(title.replace("\\", "/"))
        ext = base.rsplit(".", 1)[1].lower() if "." in base else ""
        is_bare_known = base.lower() in BARE_NAMES

        seen.setdefault(title, []).append(no)

        if lang not in NEUTRAL_LANGS:
            allowed = EXT_LANG.get(ext) or BARE_NAMES.get(base.lower())
            if allowed and lang not in allowed:
                out.append(
                    ("E2_TITLE_LANG_MISMATCH", no, "标题 %s（. %s）与语言 %s 不匹配" % (title, ext, lang))
                )

        if title.startswith(("/", "~")) or re.match(r"^[A-Za-z]:[\\/]", title):
            out.append(("W3_TITLE_ABSOLUTE", no, "绝对路径：%s" % title))
        if PLACEHOLDER.search(title):
            out.append(("W4_TITLE_PLACEHOLDER", no, "占位符：%s" % title))
        if not ext and not is_bare_known:
            out.append(("W1_TITLE_NOT_PATH", no, "不是路径：%s" % title))

    for title, nos in seen.items():
        if len(nos) >= 2:
            out.append(("W2_TITLE_DUP_IN_PAGE", nos[1], "标题重复 %d 次：%s" % (len(nos), title)))

    return blocks, out


def walk(root, verbose=False):
    pages = 0
    blocks_total = 0
    counts = {}
    details = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", ".vitepress", ".workbuddy"}]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            blocks, out = scan_file(path)
            if not blocks:
                continue
            pages += 1
            blocks_total += len(blocks)
            for code, no, detail in out:
                counts[code] = counts.get(code, 0) + 1
                details.append((code, path, no, detail))
                if verbose:
                    print("%-24s %s:%d  %s" % (code, path, no, detail))
    return pages, blocks_total, counts, details


def selftest():
    cases = [
        ("```java [src/Main.java]\nclass A {}\n```\n", set()),
        ("```java [src/main.go]\nclass A {}\n```\n", {"E2_TITLE_LANG_MISMATCH"}),
        ("```ts [src/a.ts]\nconst a = 1\n```\n", set()),
        ("```ts [终端]\n$ ls\n```\n", {"W1_TITLE_NOT_PATH"}),
        ("```text [输出]\nOK\n```\n", {"W1_TITLE_NOT_PATH"}),
        ("``` []\nx\n```\n", {"E3_TITLE_EMPTY"}),
        ("```sh [/etc/nginx/nginx.conf]\nlisten 80;\n```\n", {"W3_TITLE_ABSOLUTE"}),
        ("```ts [src/<your-app>/main.ts]\nx\n```\n", {"W4_TITLE_PLACEHOLDER"}),
        ("```json [package.json]\n{}\n```\n```json [package.json]\n{}\n```\n", {"W2_TITLE_DUP_IN_PAGE"}),
        ("```dockerfile [Dockerfile]\nFROM nginx\n```\n", set()),
        ("```text\nplain fence, no title\n```\n", set()),
        ("```yaml [application.yml]\na: 1\n```\n", set()),
    ]
    ok = 0
    tmp = tempfile.mkdtemp()
    for i, (body, expect) in enumerate(cases, 1):
        path = os.path.join(tmp, "case-%02d.md" % i)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        _, out = scan_file(path)
        got = {c for c, _, _ in out}
        status = "PASS" if got == expect else "FAIL got=%s expect=%s" % (sorted(got), sorted(expect))
        if got == expect:
            ok += 1
        print("case-%02d %s" % (i, status))
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not os.path.isdir(args.root):
        print("E0_ROOT_NOT_FOUND %s" % args.root)
        return 2

    pages, blocks, counts, details = walk(args.root, args.verbose)
    if blocks == 0:
        print("E1_NO_FENCES 没有扫到任何带标题的代码块")
        return 1

    errors = [d for d in details if d[0].startswith("E")]
    print("pages=%d titles=%d E=%d W=%d" % (pages, blocks, len(errors), len(details) - len(errors)))
    for code in sorted(counts):
        print("  %-24s %d" % (code, counts[code]))
    for code, path, no, detail in errors:
        print("%s %s:%d  %s" % (code, path, no, detail))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
