#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""行内 HTML 结构巡检（第一百二十项巡检）。

立这一项的直接原因：本库关于「一页长得对不对」的门已经很多，但没有一道看
**行内 HTML 标签本身**。VitePress 的 Markdown 里允许直接写 HTML，AGENTS.md 还
规定了两种固定写法（居中图片的 `<p>` + `<img>`、缩放的 `<img style="zoom:25%">`）。
标签写坏了不会有任何提示：

- `<p style="text-align:center;"><img src="./a.png" /></p>` 少写一个 `</p>`，
  后面整段正文会被吞进 `<p>` 里，渲染成一整块行内元素；
- `<img>` 少写 `src`，页面上是一个空白框，`linkexistcheck` 只查链接、不查标签；
- 外链图片（`src="https://..."`）会在网络不通时变成破图，而构建是成功的；
- 正文里裸写 `<`（`a <b` 这种连写）会被浏览器当成标签开头，吃掉后半句。

判据：三真 + 四提示 + 计数。

  E1 NO_PAGES        活性：一页都没扫到就拒绝给全绿
  E2 UNCLOSED_BLOCK  块级标签（p/div/span/table/details/summary）开闭计数不配对
  E3 STRAY_CLOSE     出现闭标签但本页没有对应的开标签
  E4 SCRIPT          出现 <script> / <iframe>（构建与安全都不该有）
  W1 IMG_NO_SRC      <img> 缺 src 或 src 为空
  W2 UNKNOWN_TAG     形似标签但不在白名单（泛型 <T>、数学 a <b 都会落到这里）
  W3 EXTERNAL_IMG    <img src="http(s)://..."> 外链图片
  N1 PAGES / N2 TAGS / N3 BLOCKS / N4 IMGS / N5 BY_TAG（只计数）

口径取舍：
1. 代码围栏与行内代码先剥掉——那里面的 `<` 是代码，不是标签（本库 17,900+ 个围栏，
   不剥会让 Java 泛型与 shell 重定向造出上万条假阳性）。
2. `UNKNOWN_TAG` 只做 W 不做 E：本库确实存在「`<T>` 表示泛型」「`a <b` 表示小于」
   这类正当写法，判 E 会让这道门第二天就被整体跳过（与 `quotecheck` 的 `W3`、
   `depthcheck` 的阈值是同一条纪律）。
3. `E2` 只认块级标签，且按**页**计数而不是按行：本库有跨行的 `<p>`（图片与说明
   文字分两行写），按行判会造出假阳性。
4. `<br/>`、`<img>`、`<hr>` 是自闭合，不参与配对计数。
"""
import argparse
import os
import re
import sys

ROOT_DEFAULT = "."
SKIP_DIRS = {".git", "node_modules", ".vitepress", "dist", ".workbuddy"}
BLOCK_TAGS = ("p", "div", "span", "table", "details", "summary", "ul", "ol")
VOID_TAGS = ("br", "img", "hr", "input", "meta", "link")
KNOWN_TAGS = set(BLOCK_TAGS) | set(VOID_TAGS) | {"b", "i", "strong", "em", "code", "kbd", "a", "sup", "sub", "small", "u", "s", "mark", "font"}
BAD_TAGS = ("script", "iframe", "object", "embed", "style")

FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
TAG = re.compile(r"<\s*(/?)\s*([A-Za-z][A-Za-z0-9-]*)((?:[^<>\"']|\"[^\"]*\"|'[^']*')*?)(/?)\s*>")
AUTOLINK = re.compile(r"<\s*(?:https?|mailto|ftp)://[^<>\s]*>", re.I)
IMG_SRC = re.compile(r"""\bsrc\s*=\s*["']([^"']*)["']""", re.I)


def strip_code(text):
    """剥掉围栏代码块与行内代码，保留行号结构。"""
    out, fence = [], None
    for line in text.split("\n"):
        m = FENCE_OPEN.match(line)
        if fence is None and m:
            fence = m.group(1)[0] * 3
            out.append("")
            continue
        if fence is not None:
            if m and m.group(1)[0] * 3 == fence:
                fence = None
            out.append("")
            continue
        out.append(re.sub(r"`[^`\n]*`", lambda mm: " " * len(mm.group(0)), line))
    return "\n".join(out)


def check_page(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    text = strip_code(raw)
    text = AUTOLINK.sub(lambda m: ' ' * len(m.group(0)), text)
    errs, warns = [], []
    tags = 0
    open_ct, close_ct, imgs = {}, {}, 0

    for m in TAG.finditer(text):
        close, name, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        # 先判「像不像标签」，再按标签名分级：正文里的 <Object, Object> 不能当成 <object>
        prose = any("一" <= ch <= "鿿" for ch in attrs) and "=" not in attrs
        looks = ((not attrs.strip()) or ("=" in attrs) or bool(selfclose) or bool(close)
                 or re.fullmatch(r"[\w-]+", attrs.strip() or "x") is not None)
        if prose or not looks:
            warns.append(("W2 UNKNOWN_TAG", name))
            continue
        tags += 1
        if name in BAD_TAGS:
            errs.append(("E4 SCRIPT", name))
            continue
        if name not in KNOWN_TAGS:
            warns.append(("W2 UNKNOWN_TAG", name))
            continue
        if name == "img":
            imgs += 1
            sm = IMG_SRC.search(attrs)
            if not sm or not sm.group(1).strip():
                warns.append(("W1 IMG_NO_SRC", name))
            elif sm.group(1).startswith(("http://", "https://")):
                warns.append(("W3 EXTERNAL_IMG", sm.group(1)[:60]))
            continue
        if name in VOID_TAGS:
            continue
        if close:
            close_ct[name] = close_ct.get(name, 0) + 1
        else:
            open_ct[name] = open_ct.get(name, 0) + 1

    for name, n in open_ct.items():
        if n != close_ct.get(name, 0):
            errs.append(("E2 UNCLOSED_BLOCK", "%s 开 %d 闭 %d" % (name, n, close_ct.get(name, 0))))
    for name, n in close_ct.items():
        if name not in open_ct:
            errs.append(("E3 STRAY_CLOSE", "%s 闭 %d 开 0" % (name, n)))
    return errs, warns, tags, len(open_ct), imgs


def walk(root):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".md"):
                yield os.path.join(cur, f)


def run(root):
    pages = 0
    E = []
    W = []
    n_tags = n_blocks = n_imgs = 0
    by_tag = {}
    for p in walk(root):
        if os.sep + "docs" + os.sep not in p and os.sep + "project" + os.sep not in p:
            continue
        pages += 1
        errs, warns, tags, blocks, imgs = check_page(p)
        n_tags += tags
        n_blocks += blocks
        n_imgs += imgs
        for code, detail in errs:
            E.append((code, p, detail))
        for code, detail in warns:
            W.append((code, p, detail))
            if code == "W2 UNKNOWN_TAG":
                by_tag[detail] = by_tag.get(detail, 0) + 1
    if pages == 0:
        print("E1 NO_PAGES  root=%s" % root)
        return 1
    for code, p, d in E:
        print("%s  %s  %s" % (code, p, d))
    for code, p, d in W[:40]:
        print("%s  %s  %s" % (code, p, d))
    wc = {}
    for code, _, _ in W:
        wc[code] = wc.get(code, 0) + 1
    print("pages=%d tags=%d blocks=%d imgs=%d E=%d W=%d %s" % (
        pages, n_tags, n_blocks, n_imgs, len(E), len(W), wc))
    if by_tag:
        print("W2 top:", sorted(by_tag.items(), key=lambda x: -x[1])[:8])
    return 1 if E else 0


def selftest():
    import tempfile
    cases = [
        ("<p><img src=\"./a.png\" /></p>\n", 0, "居中图片：合法"),
        ("<p><img src=\"./a.png\" />\n", 1, "缺 </p>：E2"),
        ("<img src=\"./a.png\" />\n</p>\n", 1, "多一个 </p>：E3"),
        ("<script>alert(1)</script>\n", 2, "<script> 开闭各一次：E4×2"),
        ("<details><summary>展开</summary>\n\n内容\n\n</details>\n", 0, "details 配对：合法"),
        ("文本 <T> 泛型说明\n", 0, "泛型 <T>：只 W2，不算 E"),
        ("a <b 与 c > d\n", 0, "裸小于号：只 W2"),
        ("```html\n<p>代码里的未闭合\n```\n", 0, "围栏内不判：合法"),
        ("行内 `<p>` 代码不判\n", 0, "行内代码不判：合法"),
        ("<img alt=\"无 src\" />\n", 0, "缺 src：只 W1"),
        ("<p style=\"text-align:center;\"><img src=\"https://x/a.png\" /></p>\n", 0, "外链图：只 W3"),
        ("<div><p>嵌套</p></div>\n", 0, "嵌套块：合法"),
        ("<table><tr><td>x</td></tr>\n", 1, "table 未闭合：E2"),
        ("<br/> 与 <hr/>\n", 0, "自闭合：合法"),
    ]
    ok = 0
    for text, expect_e, label in cases:
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs", "X"), exist_ok=True)
            p = os.path.join(d, "docs", "X", "index.md")
            open(p, "w", encoding="utf-8").write(text)
            errs, warns, *_ = check_page(p)
            got = len(errs)
            if got == expect_e:
                ok += 1
            else:
                print("FAIL %-28s expect E=%d got E=%d %s" % (label, expect_e, got, errs))
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=ROOT_DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    sys.exit(run(a.root))
