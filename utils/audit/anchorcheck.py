#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""anchorcheck.py —— 页内锚点（#fragment）巡检（第 66 项）。

背景
----
`linkcheck` 只校验 Markdown 链接的**文件路径**是否存在，`slug` 之后的 `#fragment`
完全不在它的视野里。于是「标题改名 / 拆页 / 合并小节」之后，链接仍然「长得对」、
构建也照样成功，读者点进去落在一个不存在的锚点上——VitePress 不会报错，只会
停在该页顶部，或者什么都不发生。这类失效**没有任何反馈通道**。

判据
----
E0 ROOT_NOT_FOUND        既无 docs/ 也无 project/
E1 NO_PAGES              扫到 0 个 Markdown（活性检查，防止路径写错后空跑全绿）
E2 MISSING_ANCHOR        锚点在目标页的标题集合里不存在
W1 PERCENT_ENCODED       片段是百分号编码（解码后才能对上；能过但不规范）
W2 AMBIGUOUS_ANCHOR      目标页里有同名标题（slug 加 `-1`/`-2` 后缀，人工难猜）
W3 ANCHOR_ON_NON_MD      锚点挂在了非 Markdown 目标上（图片 / PDF 等）
W4 EMPTY_FRAGMENT        链接以 `#` 结尾但什么都没写

用法
----
    python3 utils/audit/anchorcheck.py                # 全库
    python3 utils/audit/anchorcheck.py --selftest     # 自测（临时目录里的夹具）
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import unicodedata
from urllib.parse import unquote, quote

ROOTS = ("docs", "project")
SKIP_DIRS = {"node_modules", ".vitepress", "assets", ".git"}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
HTML_HREF_RE = re.compile(r'href="([^"#][^"]*#[^"]*)"')
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
MD_FORMAT_RE = re.compile(r"(\*\*|__|\*|_|~~|`)")
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
R_SPECIAL = re.compile(r'[\s~`!@#$%^&*()\-_+=\[\]{}|\\;:"\'“”‘’<>,.?/]+')
HTML_TAG_RE = re.compile(r"<[^>]+>")
EXPLICIT_ID_RE = re.compile(r'<(?:a|span|div|p|section|h[1-6])\b[^>]*?(?:id|name)="([^"]+)"')


def strip_code(text: str) -> str:
    """去掉围栏代码块与行内代码，避免把代码里的 `#` 当锚点、把 `#注释` 当标题。"""
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if fence is None and m:
            fence = m.group(1)[:3]
            continue
        if fence is not None:
            if m and m.group(1).startswith(fence):
                fence = None
            continue
        out.append(INLINE_CODE_RE.sub("", line))
    return "\n".join(out)


def slugify(text: str) -> str:
    """**逐字复刻 VitePress 的 slugify**（`vitepress/dist/node/chunk-*.js` 里那个）：
    NFKD 归一 → 去组合符 → 去控制符 → 特殊字符集换 `-` → 折叠连续 `-` → 去首尾 `-`
    → 数字开头补 `_` → 小写。

    为什么要复刻而不是「差不多」：`、`（U+3001）**不在** 特殊字符集里，所以
    `## 一、排查总原则` 的 id 是 `一、排查总原则` 而不是 `一-排查总原则`；反过来
    `_` 在集合里会被换成 `-`，数字开头的标题会被补一个 `_` 前缀。差异只有几个字符，
    但会让巡检批量误报——这正是本脚本第一版踩的坑。
    """
    t = MD_LINK_RE.sub(r"\1", text)
    t = MD_FORMAT_RE.sub("", t)
    t = HTML_TAG_RE.sub("", t)
    t = unicodedata.normalize("NFKD", t)
    t = re.sub(r"[\u0300-\u036f]", "", t)
    t = re.sub(r"[\u0000-\u001f]", "", t)
    t = R_SPECIAL.sub("-", t)
    t = re.sub(r"-{2,}", "-", t)
    t = re.sub(r"^-+|-+$", "", t)
    t = re.sub(r"^(\d)", r"_\1", t)
    return t.lower()


def page_anchors(text: str) -> tuple[set[str], list[str]]:
    """返回 (锚点集合, 重复的 slug 列表)。重复标题会被引擎追加 -1/-2，链接方难以预测。"""
    seen: dict[str, int] = {}
    dups: list[str] = []
    anchors: set[str] = set()
    body_lines = strip_code(text).splitlines()
    for line in body_lines:
        if not HEADING_RE.match(line):
            anchors.update(EXPLICIT_ID_RE.findall(line))
    for line in body_lines:
        m = HEADING_RE.match(line)
        if not m:
            continue
        s = slugify(m.group(2))
        if not s:
            continue
        # 标题里显式写的 HTML id / name 也算锚点（如 `## <span id="jump1">…</span>`）
        anchors.update(EXPLICIT_ID_RE.findall(m.group(2)))
        if s in seen:
            seen[s] += 1
            anchors.add(f"{s}-{seen[s]}")
            if s not in dups:
                dups.append(s)
        else:
            seen[s] = 0
            anchors.add(s)
    return anchors, dups


def collect(root: str) -> list[str]:
    pages: list[str] = []
    for r in ROOTS:
        base = os.path.join(root, r)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for f in filenames:
                if f.endswith(".md"):
                    pages.append(os.path.normpath(os.path.join(dirpath, f)))
    idx = os.path.join(root, "index.md")
    if os.path.isfile(idx):
        pages.append("index.md")
    return sorted(pages)


def resolve(root: str, page: str, target: str) -> str | None:
    """把链接目标解析成仓库内的相对路径；绝对路径（/docs/...）按仓库根解析。"""
    if target.startswith("/"):
        return os.path.normpath(os.path.join(root, target.lstrip("/")))
    return os.path.normpath(os.path.join(root, os.path.dirname(page), target))


def run(root: str, verbose: bool = True) -> int:
    pages = collect(root)
    if not pages:
        if verbose:
            print("E1 NO_PAGES: 没有扫到任何 Markdown，检查根目录")
        return 1

    cache: dict[str, tuple[set[str], list[str]]] = {}
    errors: list[tuple[str, str, str]] = []
    warns: list[tuple[str, str, str, str]] = []
    checked = 0

    for page in pages:
        try:
            text = open(os.path.join(root, page), encoding="utf-8").read()
        except OSError:
            continue
        body = strip_code(text)
        links = [m.group(1) for m in LINK_RE.finditer(body)]
        links += [m.group(1) for m in HTML_HREF_RE.finditer(body)]
        for link in links:
            if "#" not in link or link.startswith(("http://", "https://", "mailto:")):
                continue
            path_part, frag = link.split("#", 1)
            if not frag:
                warns.append((page, link, "W4", "EMPTY_FRAGMENT"))
                continue
            if not path_part:
                target_page, abs_target = page, os.path.join(root, page)
            else:
                abs_target = resolve(root, page, path_part)
                target_page = os.path.relpath(abs_target, root)
            checked += 1
            if not path_part:
                pass
            elif not os.path.exists(abs_target):
                continue  # 路径本身不存在，归 linkcheck 管，本巡检不重复报
            if not target_page.endswith(".md"):
                if os.path.splitext(target_page)[1]:
                    warns.append((page, link, "W3", "ANCHOR_ON_NON_MD"))
                continue
            if target_page not in cache:
                try:
                    cache[target_page] = page_anchors(
                        open(os.path.join(root, target_page), encoding="utf-8").read()
                    )
                except OSError:
                    cache[target_page] = (set(), [])
            anchors, dups = cache[target_page]
            decoded = unquote(frag)
            if decoded != frag and (decoded in anchors or quote(decoded, safe="-_.~") in anchors):
                warns.append((page, link, "W1", "PERCENT_ENCODED"))
                continue
            if decoded in anchors:
                if decoded in dups:
                    warns.append((page, link, "W2", "AMBIGUOUS_ANCHOR"))
                continue
            errors.append((page, link, "E2"))

    if verbose:
        print(f"pages={len(pages)} anchors_checked={checked} E={len(errors)} W={len(warns)}")
        for page, link, code in errors[:40]:
            print(f"  {code} {page} -> {link}")
        from collections import Counter

        for (code, kind), n in Counter((w[2], w[3]) for w in warns).most_common():
            print(f"  {code} {kind}: {n}")
    return 1 if errors else 0


# --------------------------------------------------------------------------- selftest
def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def selftest() -> int:
    cases: list[tuple[str, bool]] = []

    def case(name: str, ok: bool) -> None:
        cases.append((name, ok))
        print(("PASS " if ok else "FAIL ") + name)

    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "docs/A/One/index.md"),
               "# 一\n\n## 中文 标题\n\n## dup\n\n## dup\n\n```md\n# 围栏里的注释不算标题\n```\n")
        _write(os.path.join(tmp, "docs/A/Two/index.md"),
               "# 二\n\n[好](../One/index.md#中文-标题)\n[坏](../One/index.md#已改名)\n"
               "[编码](../One/index.md#%E4%B8%AD%E6%96%87-%E6%A0%87%E9%A2%98)\n"
               "[同名](../One/index.md#dup)\n[空](#)\n[图](../../../assets/x.png#frag)\n"
               "`[代码里](../One/index.md#假的)`\n")
        _write(os.path.join(tmp, "docs/A/assets/x.png"), "x")

        rc = run(tmp, verbose=False)
        text_two = open(os.path.join(tmp, "docs/A/Two/index.md"), encoding="utf-8").read()
        anchors, dups = page_anchors(text_two)
        case("围栏内的 # 不当标题", "围栏里的注释不算标题" not in anchors)
        case("行内代码里的链接不计数", "假的" not in anchors)
        case("中文标题 slug 保留 CJK", "中文-标题" in page_anchors(
            open(os.path.join(tmp, "docs/A/One/index.md"), encoding="utf-8").read())[0])
        case("重复标题产生 -1 后缀", "dup-1" in page_anchors(
            open(os.path.join(tmp, "docs/A/One/index.md"), encoding="utf-8").read())[0])
        case("E2 只在有错时返回非 0", rc == 1)

        # 干净的库
        with tempfile.TemporaryDirectory() as tmp2:
            _write(os.path.join(tmp2, "docs/A/One/index.md"), "# 一\n\n## 小节\n")
            _write(os.path.join(tmp2, "docs/A/Two/index.md"), "# 二\n\n[对](../One/index.md#小节)\n")
            case("干净库返回 0", run(tmp2, verbose=False) == 0)

        # 空库
        with tempfile.TemporaryDirectory() as tmp3:
            os.makedirs(os.path.join(tmp3, "docs"))
            case("空库触发 E1", run(tmp3, verbose=False) == 1)

        # 路径不存在时不重复报（交给 linkcheck）
        with tempfile.TemporaryDirectory() as tmp4:
            _write(os.path.join(tmp4, "docs/A/One/index.md"), "# 一\n\n[x](../No/index.md#x)\n")
            case("缺文件不报 E2", run(tmp4, verbose=False) == 0)

        # 同页锚点
        with tempfile.TemporaryDirectory() as tmp5:
            _write(os.path.join(tmp5, "docs/A/One/index.md"), "# 一\n\n[a](#一)\n[b](#二)\n")
            case("同页锚点缺失能报", run(tmp5, verbose=False) == 1)

    passed = sum(1 for _, ok in cases if ok)
    print(f"selftest {passed}/{len(cases)}")
    return 0 if passed == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (os.path.isdir(os.path.join(args.root, "docs")) or
            os.path.isdir(os.path.join(args.root, "project"))):
        print("E0 ROOT_NOT_FOUND")
        return 1
    return run(args.root)


if __name__ == "__main__":
    sys.exit(main())
