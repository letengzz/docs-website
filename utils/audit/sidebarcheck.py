#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""sidebarcheck.py — 「侧边栏条目 ⇄ 实际页面」一致性巡检 · 第 79 项

为什么立这一项
--------------
全库的导航有三层：`nav.ts`（顶部）、`sidebar.ts`（路径前缀 → 分支）、各分支文件（树）。
已有的门禁里，`linkcheck` 只查**页面正文里的相对链接**，`orphanassetcheck` 只查**图片**，
`anchorcheck` 只查**页内锚点**——三层导航里没有一道门管「侧边栏指向的那个文件是否存在、
标题是否还对得上」。

于是这一类债全库静默：

* 页面被改名/移动，侧边栏还指着旧路径 → 点进去 404，构建只报警告；
* 页面 H1 改了，侧边栏文字没改 → 读者在菜单里看到的名字和正文标题不是一个东西；
* 侧边栏写的是相对路径（少一个 `/`）→ VitePress 按当前页解析，跳到错误位置。

这三种都属于「构建绿、点进去错」，是 `linkcheck` 与 `headingcheck` 之间的洞。

判据
----
E0 ROOT_NOT_FOUND    仓库根或 .vitepress 目录找不到
E1 NO_ENTRIES        一条 `{ text, link }` 都没解析到（活性判据）
E2 DEAD_LINK         侧边栏条目指向的文件不存在
E3 BAD_LINK_FORM     link 不以 `/` 开头（会被当成相对路径解析）
W1 TEXT_H1_MISMATCH  侧边栏 text 与目标页 H1 不一致（去掉判据族括号后比较）
W2 EMPTY_TEXT        条目 text 为空

纪律
----
* **只读**：不写文件、不改台账。
* **E 与 W 的分界**：文件不存在是**读者点进去就错**（E）；标题措辞不同只是**不一致**
  （W）——很多条目是刻意的短名（如「概述」对应「Redis 概述」），不该报错。
* **只解析 `text` 与 `link` 紧邻的写法**：库内三种分支文件都是 `{ text: "…", link: "…" }`
  或反序，正则按两种顺序各扫一次；动态拼接（`...spread`）不参与，避免误判。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/sidebarcheck.py [--selftest] [--root .] [--limit 20]
"""

import argparse
import os
import re
import sys
import tempfile

TS_FILES = ("backend.ts", "frontend.ts", "db.ts", "ops.ts", "AI.ts", "tools.ts",
            "project.ts", "sidebar.ts", "nav.ts")
SKIP_H1_PREFIX = ("第 ",)

PAT_A = re.compile(r'\{\s*text:\s*"([^"]*)"\s*,\s*link:\s*"([^"]*)"')
PAT_B = re.compile(r'\{\s*link:\s*"([^"]*)"\s*,\s*text:\s*"([^"]*)"')
JUDGE_TAIL = re.compile(r"\s*[（(][A-Z][A-Z0-9]*-[A-Z]~[A-Z][A-Z0-9]*-[A-Z][）)]\s*$")


def norm(s):
    s = JUDGE_TAIL.sub("", s.strip())
    # 只留字母、数字与汉字：标点差异（`·` / `-` / `（）` / 全角空格）不算漂移
    return "".join(ch for ch in s.lower() if ch.isalnum())


def consistent(h1, text):
    """首版直接比相等，全库报出 452 条 W——几乎全是刻意的短名
    （`环境搭建` ⇄ `Java 环境搭建`、`REST API` ⇄ `Spring Boot REST API`）。
    收窄为「相等，或一方是另一方的后缀」，才算真正的漂移。"""
    a, b = norm(h1), norm(text)
    return a == b or a.endswith(b) or b.endswith(a)


def collect(vp_dir):
    """返回 [(来源文件, text, link)]。"""
    out = []
    for name in TS_FILES:
        p = os.path.join(vp_dir, name)
        if not os.path.exists(p):
            continue
        src = open(p, encoding="utf-8").read()
        for m in PAT_A.finditer(src):
            out.append((name, m.group(1), m.group(2)))
        for m in PAT_B.finditer(src):
            out.append((name, m.group(2), m.group(1)))
    return out


def resolve(root, link):
    """把 /docs/X/Y/index.md 或 /docs/X/Y 映射到磁盘路径；返回候选列表。"""
    path = link.split("#")[0].strip()
    if not path.startswith("/"):
        return []
    rel = path.lstrip("/")
    cands = []
    if rel.endswith(".md"):
        cands.append(os.path.join(root, rel))
    else:
        cands.append(os.path.join(root, rel, "index.md"))
        cands.append(os.path.join(root, rel + ".md"))
    return cands


def h1_of(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        return None
    return None


def scan(root, limit=20):
    vp = os.path.join(root, ".vitepress")
    if not os.path.isdir(vp):
        return None, [("E0", "-", "ROOT_NOT_FOUND", vp)], []
    entries = collect(vp)
    errors, warns = [], []
    if not entries:
        errors.append(("E1", "-", "NO_ENTRIES", "未解析到任何 text/link 对"))
        return 0, errors, warns
    for src, text, link in entries:
        if not text.strip():
            warns.append(("W2", src, "EMPTY_TEXT", link))
            continue
        if not link.startswith("/"):
            errors.append(("E3", src, "BAD_LINK_FORM", link))
            continue
        cands = resolve(root, link)
        hit = next((c for c in cands if os.path.isfile(c)), None)
        if hit is None:
            errors.append(("E2", src, "DEAD_LINK", link))
            continue
        h1 = h1_of(hit)
        if h1 is None:
            warnings_note = "NO_H1"
            warns.append(("W1", src, "NO_H1", link))
            continue
        if not consistent(h1, text):
            warns.append(("W1", src, "TEXT_H1_MISMATCH", f"{text}  ⇄  {h1}"))
    return len(entries), errors[:limit * 50], warns[:limit * 50]


def report(root, limit=20):
    total, errors, warns = scan(root, limit)
    if total is None:
        print("E0 ROOT_NOT_FOUND", errors[0][3])
        return 2
    ecodes = {}
    for code, *_ in errors:
        ecodes[code] = ecodes.get(code, 0) + 1
    wcodes = {}
    for code, *_ in warns:
        wcodes[code] = wcodes.get(code, 0) + 1
    for code, src, kind, detail in errors[:40]:
        print(f"{code} {kind:16} {src:12} {detail}")
    for code, src, kind, detail in warns[:limit]:
        print(f"{code} {kind:16} {src:12} {detail}")
    print(f"entries={total} E={len(errors)} W={len(warns)} "
          f"E细节={ecodes} W细节={wcodes}")
    return 0 if not errors else 1


def selftest():
    root = tempfile.mkdtemp()
    vp = os.path.join(root, ".vitepress")
    os.makedirs(vp)
    os.makedirs(os.path.join(root, "docs", "A", "Good"))
    os.makedirs(os.path.join(root, "docs", "A", "Drift"))

    def page(rel, h1):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(f"# {h1}\n\n正文\n")

    page("docs/A/index.md", "A 分类")
    page("docs/A/Good/index.md", "标题一致")
    page("docs/A/Drift/index.md", "正文标题")

    open(os.path.join(vp, "backend.ts"), "w", encoding="utf-8").write("""
export const A = [
  { text: "A 分类", link: "/docs/A/index.md", items: [
    { text: "标题一致", link: "/docs/A/Good/index.md" },
    { link: "/docs/A/Drift/index.md", text: "菜单名" },
    { text: "已删除的页", link: "/docs/A/Gone/index.md" },
    { text: "相对路径", link: "docs/A/Good/index.md" },
    { text: "第 2 周第 2 步 · 某页（EOR-A~EOR-H）", link: "/docs/A/Drift/index.md" },
    { text: "  ", link: "/docs/A/Good/index.md" },
  ]},
];
""")
    total, errors, warns = scan(root)
    ecodes = {c for c, *_ in errors}
    wcodes = {c for c, *_ in warns}

    def has(code, kind):
        return any(c == code and k == kind for c, _, k, _ in errors + warns)

    cases = [
        ("entries-count", total == 7),
        ("E2-dead", has("E2", "DEAD_LINK")),
        ("E3-form", has("E3", "BAD_LINK_FORM")),
        ("W1-drift", has("W1", "TEXT_H1_MISMATCH")),
        ("W2-empty", has("W2", "EMPTY_TEXT")),
        ("judge-tail-norm", sum(1 for c, _, k, _ in warns
                                if k == "TEXT_H1_MISMATCH") == 2),
        ("codes-shape", ecodes <= {"E2", "E3"} and wcodes <= {"W1", "W2"}),
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
    ap.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return report(a.root, a.limit)


if __name__ == "__main__":
    sys.exit(main())
