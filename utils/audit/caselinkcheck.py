#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 79 项巡检：链接目标的「大小写」与磁盘真实文件名是否一致（caselinkcheck）。

立这一项的直接原因：本库日常在 Windows 上写文档、在 Linux（GitHub Actions）上构建。
Windows 的文件系统大小写不敏感，于是 `![x](../assets/Foo.svg)` 在本地**能渲染**、
`linkcheck.py` 也**判它存在**（`os.path.exists` 走的是不敏感比较），但推上去之后
Linux 上找不到 `assets/Foo.svg`，页面里的图静默变成破图。

既有的六个链接类巡检都不覆盖这个方向：
- `linkcheck` / `barelinkcheck` 判「目标存在与否」，不敏感文件系统上只会说「存在」；
- `sidebarlink` 判侧边栏链接，同样走 `os.path.exists`；
- `anchorcheck` / `intraanchorcheck` 判锚点；
- `selflinkcheck` 判自链接。

判据
----
E0 ROOT_NOT_FOUND   仓库根识别失败（活性前置：必须同时存在 AGENTS.md 与 docs/）
E1 CASE_MISMATCH    某一段路径「不区分大小写能命中、区分大小写命不中」（唯一门禁）
E2 NO_LINKS         扫到 0 条可解析的相对链接（活性判据，防「根找对了但正则失效」）
W1 SHADOW_CASE      同一目录里存在仅大小写不同的两个条目（Windows 上本不该出现，出现即隐患）

退出码：0 = 无 E；1 = 有 E；2 = 用法/环境错误。
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

ROOT_MARKERS = ("AGENTS.md", "docs")
SCAN_ROOTS = ("docs", "project")

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^()\s]+)\)")
HTML_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")

OPTS = {
    "case_check": True,     # 关掉做变异测试：退化成「只判存在」
    "mask_fences": True,    # 关掉做变异测试：围栏里的示例会被误判
    "mask_inline": True,    # 关掉做变异测试：行内代码里的示例会被误判
    "handle_parent": True,  # 关掉做变异测试：`../` 段处理失效
}


def find_root(start: str) -> str | None:
    cur = os.path.abspath(start)
    while True:
        if all(os.path.exists(os.path.join(cur, m)) for m in ROOT_MARKERS):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def iter_markdown(root: str):
    for base in SCAN_ROOTS:
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in ("assets", "node_modules", ".vitepress")]
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def mask_line(line: str, opts) -> str:
    """把行内代码替换成等长空格（保留行内列位置），不改变行数。"""
    if not opts["mask_inline"]:
        return line
    out = []
    i, n = 0, len(line)
    while i < n:
        if line[i] == "`":
            j = i
            while j < n and line[j] == "`":
                j += 1
            ticks = line[i:j]
            end = line.find(ticks, j)
            if end == -1:
                out.append(line[i:])
                break
            out.append(" " * (end + len(ticks) - i))
            i = end + len(ticks)
        else:
            out.append(line[i])
            i += 1
    return "".join(out)


def iter_links(text: str, opts):
    """产出 (行号, 目标)。先按行剥围栏，再按行剥行内代码。"""
    in_fence = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)[0]
            if in_fence is None:
                in_fence = marker
            elif in_fence == marker:
                in_fence = None
            if opts["mask_fences"]:
                continue
        if in_fence is not None and opts["mask_fences"]:
            continue
        for lm in LINK_RE.finditer(mask_line(line, opts)):
            yield lineno, lm.group(1).strip()
        # HTML 写法（`<img src="./assets/favicon.png">`）最容易在 Windows 上「假通过」
        for hm in HTML_RE.finditer(mask_line(line, opts)):
            yield lineno, hm.group(1).strip()


def _real_names(directory: str) -> dict[str, str]:
    try:
        entries = os.listdir(directory)
    except OSError:
        return {}
    return {e.lower(): e for e in entries}


def resolve_case(base_dir: str, target: str, opts):
    """逐段解析，返回 (真实路径, 第一处大小写不符的段) ；不存在时返回 (None, None)。"""
    target = target.split("#", 1)[0]
    if not target or target.startswith("/") or SCHEME_RE.match(target):
        return None, None
    target = target.replace("\\", "/")
    if "%" in target:
        return None, None
    cur = base_dir
    mismatch = None
    for part in target.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not opts["handle_parent"]:
                return None, None
            cur = os.path.dirname(cur)
            continue
        names = _real_names(cur)
        if part in names.values():
            cur = os.path.join(cur, part)
            continue
        hit = names.get(part.lower())
        if hit is not None:
            if mismatch is None:
                mismatch = (part, hit)
            cur = os.path.join(cur, hit)
            continue
        return None, None
    if not os.path.exists(cur):
        return None, None
    return cur, mismatch


def shadow_cases(directory: str):
    try:
        entries = os.listdir(directory)
    except OSError:
        return []
    seen, dup = {}, []
    for e in entries:
        key = e.lower()
        if key in seen and seen[key] != e:
            dup.append((seen[key], e))
        seen[key] = e
    return dup


def scan(root: str, opts=None):
    opts = opts or OPTS
    findings, scanned = [], 0
    dirs_seen = set()
    for md in iter_markdown(root):
        with open(md, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        rel = os.path.relpath(md, root).replace("\\", "/")
        for lineno, target in iter_links(text, opts):
            scanned += 1
            if not opts["case_check"]:
                continue
            _, mismatch = resolve_case(os.path.dirname(md), target, opts)
            if mismatch:
                findings.append({
                    "code": "E1",
                    "file": rel,
                    "line": lineno,
                    "message": f"链接写 `{mismatch[0]}`，磁盘真实名是 `{mismatch[1]}`：{target}",
                })
        d = os.path.dirname(md)
        if d not in dirs_seen:
            dirs_seen.add(d)
            for a, b in shadow_cases(d):
                findings.append({
                    "code": "W1",
                    "file": os.path.relpath(d, root).replace("\\", "/"),
                    "line": 0,
                    "message": f"同目录存在仅大小写不同的条目：`{a}` / `{b}`",
                })
    if scanned == 0:
        findings.append({"code": "E2", "file": "-", "line": 0,
                         "message": "扫到 0 条相对链接（活性判据：正则或根目录有问题）"})
    return findings, scanned


FIXTURES = {
    "case-01-exact": {
        "docs/a/index.md": "![图](../assets/Foo.svg)\n",
        "docs/assets/Foo.svg": "<svg/>",
    },
    "case-02-file-case": {
        "docs/a/index.md": "![图](../assets/foo.svg)\n",
        "docs/assets/Foo.svg": "<svg/>",
    },
    "case-03-dir-case": {
        "docs/a/index.md": "见 [概述](../sub/index.md)\n",
        "docs/Sub/index.md": "# 概述\n",
    },
    "case-04-parent": {
        "docs/a/b/index.md": "见 [总览](../../Overview/index.md)\n",
        "docs/a/Overview/index.md": "# 总览\n",
    },
    "case-05-external": {
        "docs/a/index.md": "见 [官网](https://istio.io/latest/docs/)\n",
    },
    "case-06-anchor": {
        "docs/a/index.md": "见 [本页某节](#jump)\n",
    },
    "case-07-in-fence": {
        "docs/a/index.md": "```markdown\n![x](../assets/foo.svg)\n```\n见 [a](../assets/Foo.svg)\n",
        "docs/assets/Foo.svg": "<svg/>",
    },
    "case-08-inline-code": {
        "docs/a/index.md": "示例 `![x](../assets/foo.svg)` 只是说明\n",
        "docs/assets/Foo.svg": "<svg/>",
    },
    "case-09-nested": {
        "docs/a/index.md": "![x](../Assets/Sub/Pic.svg)\n",
        "docs/assets/Sub/Pic.svg": "<svg/>",
    },
    "case-10-missing": {
        "docs/a/index.md": "见 [不存在的页](../Nope/index.md)\n",
    },
}

# 每个用例的期望：E1 出现（True）或不出现（False）
EXPECT = {
    "case-01-exact": False,
    "case-02-file-case": True,
    "case-03-dir-case": True,
    "case-04-parent": False,
    "case-05-external": False,
    "case-06-anchor": False,
    "case-07-in-fence": False,
    "case-08-inline-code": False,
    "case-09-nested": True,
    "case-10-missing": False,
}

MUTATIONS = {
    "M1-close-case-check": ({"case_check": False}, {"case-02-file-case", "case-03-dir-case", "case-09-nested"}),
    "M2-no-fence-mask": ({"mask_fences": False}, {"case-07-in-fence"}),
    "M3-no-inline-mask": ({"mask_inline": False}, {"case-08-inline-code"}),
    "M4-no-parent": ({"handle_parent": False}, {"case-02-file-case", "case-03-dir-case", "case-09-nested"}),
    "M5-equivalent": ({"case_check": True}, set()),
}


def write_fixture(root: str, name: str) -> str:
    base = os.path.join(root, name)
    for rel, content in FIXTURES[name].items():
        p = os.path.join(base, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    return base


def run_case(root: str, name: str, opts) -> bool:
    base = os.path.join(root, name)
    findings, _ = scan(base, opts)
    return any(f["code"] == "E1" for f in findings)


def selftest() -> int:
    sandbox = os.path.join(tempfile.gettempdir(), "caselinkcheck-sandbox")
    os.makedirs(sandbox, exist_ok=True)
    fails = 0
    for name in FIXTURES:
        base = write_fixture(sandbox, name)
        got = run_case(sandbox, name, OPTS)
        want = EXPECT[name]
        ok = got == want
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  selftest {name}: 期望 E1={want} 实际={got}  ({base})")
    total = len(FIXTURES)
    print(f"-- selftest {total - fails}/{total}")
    return 0 if fails == 0 else 1


def mutate() -> int:
    sandbox = os.path.join(tempfile.gettempdir(), "caselinkcheck-mutate")
    os.makedirs(sandbox, exist_ok=True)
    for name in FIXTURES:
        write_fixture(sandbox, name)
    bad = 0
    for label, (override, expected_failures) in MUTATIONS.items():
        opts = dict(OPTS)
        opts.update(override)
        failed = {n for n in FIXTURES if run_case(sandbox, n, opts) != EXPECT[n]}
        ok = failed == expected_failures
        bad += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  mutate {label}: 失败集合={sorted(failed)} 期望={sorted(expected_failures)}")
    print(f"-- mutate {len(MUTATIONS) - bad}/{len(MUTATIONS)}")
    return 0 if bad == 0 else 1


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    if "--mutate" in argv:
        return mutate()
    start = next((a for a in argv[1:] if not a.startswith("-")), os.getcwd())
    root = find_root(start)
    if not root:
        print(f"E0 ROOT_NOT_FOUND  在 {start} 及其上级都没找到 AGENTS.md + docs/")
        return 2
    findings, scanned = scan(root)
    errors = [f for f in findings if f["code"].startswith("E")]
    warns = [f for f in findings if f["code"].startswith("W")]
    for f in errors + warns:
        loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
        print(f"{f['code']} {loc}  {f['message']}")
    print(f"root={root} links={scanned} E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
