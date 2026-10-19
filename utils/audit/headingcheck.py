#!/usr/bin/env python3
"""headingcheck.py — 页面 H1 巡检（第 60 项）

判据
----
E0 ROOT_NOT_FOUND      仓库根找不到 docs/ 与 project/
E1 NO_PAGES            一个页面都没枚举到就拒绝判定（活性）
E2 NO_H1               页面没有一级标题（读者失去页名，outline 从第一个 H2 开始）
E3 MULTI_H1            一页出现多个 H1（VitePress 侧边栏/搜索结果会取错标题）
W1 TEXT_MISMATCH       侧边栏 text 与页面 H1 不一致（标题漂移，只统计不阻断）
W2 FENCE_SKIPPED       围栏代码块里的 `# xxx` 被跳过（仅统计，证明剥离生效）

设计取舍
--------
* H1 只在「围栏之外」统计：Markdown 代码块里的 `# 注释`（shell、python、yaml）
  是合法内容，若计入会产生海量假 E3。
* W1 只做「去空白后完全相等」的比较，不做模糊匹配：模糊匹配会把「标题漂移」
  判成一致，而这正是要抓的东西。
* 侧边栏解析不追求完整 TS 解析，只按「text 与 link 成对出现」取数；解析不到
  link 的 text 直接跳过，避免把「分组标题」误判成页面。

用法
----
    python3 utils/audit/headingcheck.py            # 巡检
    python3 utils/audit/headingcheck.py --selftest # 自测
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$")
SIDEBAR_ENTRY = re.compile(r'text:\s*"([^"]+)"\s*,\s*link:\s*"([^"]+)"', re.S)
SKIP_DIRS = {"assets", "node_modules", ".vitepress", ".git"}


def iter_pages(root: Path):
    for base in ("docs", "project"):
        d = root / base
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("index.md")):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            yield p


def scan_headings(text: str):
    """返回 (h1 列表, 围栏内被跳过的井号行数)。

    围栏按 CommonMark 处理：开围栏记下字符与长度，只有「同字符且长度不短于
    开围栏」的行才能关闭它。否则 ````markdown 里嵌 ```shell 会被误判成
    「围栏结束」，把后面的示例代码当成正文 —— 这是本脚本第一版唯一的假阳性来源。
    """
    h1s: list[str] = []
    skipped = 0
    marker = ""  # 空串表示不在围栏内
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            run = m.group(1)
            if not marker:
                marker = run
            elif run[0] == marker[0] and len(run) >= len(marker):
                marker = ""
            continue
        if marker:
            if line.lstrip().startswith("#"):
                skipped += 1
            continue
        h = H1.match(line)
        if h:
            h1s.append(h.group(1).strip())
    return h1s, skipped


def load_sidebar_texts(root: Path) -> dict[str, str]:
    """{页面绝对路径: 侧边栏 text}；同一 link 多次出现时保留第一个。"""
    out: dict[str, str] = {}
    cfg = root / ".vitepress"
    if not cfg.is_dir():
        return out
    for f in sorted(cfg.glob("*.ts")):
        src = f.read_text(encoding="utf-8", errors="replace")
        for text, link in SIDEBAR_ENTRY.findall(src):
            if not link.startswith(("/docs/", "/project/")):
                continue
            target = root / link.lstrip("/")
            out.setdefault(str(target), text)
    return out


def run(root: Path) -> int:
    docs_ok = (root / "docs").is_dir()
    proj_ok = (root / "project").is_dir()
    if not (docs_ok or proj_ok):
        print("E0 ROOT_NOT_FOUND: 既没有 docs/ 也没有 project/")
        return 2

    pages = list(iter_pages(root))
    if not pages:
        print("E1 NO_PAGES: 未枚举到任何页面，拒绝判定")
        return 2

    sidebar = load_sidebar_texts(root)
    errors: list[str] = []
    warns: list[str] = []
    fence_skipped = 0
    by_path: dict[str, str] = {}

    for p in pages:
        text = p.read_text(encoding="utf-8", errors="replace")
        h1s, skipped = scan_headings(text)
        fence_skipped += skipped
        rel = p.relative_to(root).as_posix()
        if not h1s:
            errors.append(f"E2 NO_H1: {rel}")
            continue
        if len(h1s) > 1:
            errors.append(f"E3 MULTI_H1: {rel} -> {h1s}")
            continue
        by_path[str(p)] = h1s[0]
        side = sidebar.get(str(p))
        if side is not None and side.strip() != h1s[0].strip():
            warns.append(f"W1 TEXT_MISMATCH: {rel} | sidebar={side!r} | h1={h1s[0]!r}")

    print(f"pages={len(pages)} sidebar_links={len(sidebar)} fence_hash_skipped={fence_skipped}")
    for line in errors:
        print(line)
    print(f"E={len(errors)} W={len(warns)}")
    for line in warns[:40]:
        print(line)
    if len(warns) > 40:
        print(f"... 其余 {len(warns) - 40} 条 W1 省略")
    return 1 if errors else 0


def selftest() -> int:
    """五个最小用例：正常 / 缺 H1 / 多 H1 / 围栏内井号 / 侧边栏漂移。"""
    cases = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "A").mkdir(parents=True)
        (root / "project").mkdir()
        (root / ".vitepress").mkdir()

        # 1 正常：单个 H1，无围栏
        (root / "docs" / "A" / "index.md").write_text("# 正常页\n\n正文\n", encoding="utf-8")
        # 2 缺 H1
        (root / "docs" / "B").mkdir()
        (root / "docs" / "B" / "index.md").write_text("## 只有二级\n", encoding="utf-8")
        # 3 多 H1
        (root / "docs" / "C").mkdir()
        (root / "docs" / "C" / "index.md").write_text("# 一\n\n# 二\n", encoding="utf-8")
        # 4 围栏内的井号不算 H1
        (root / "docs" / "D").mkdir()
        (root / "docs" / "D" / "index.md").write_text(
            "# 围栏页\n\n```shell\n# 这是注释\n```\n", encoding="utf-8"
        )
        (root / ".vitepress" / "x.ts").write_text(
            'const A = [{ text: "正常页", link: "/docs/A/index.md" },'
            ' { text: "漂移标题", link: "/docs/D/index.md" }];\n',
            encoding="utf-8",
        )

        pages = list(iter_pages(root))
        cases.append(("枚举到 4 页", len(pages) == 4))

        h1, skipped = scan_headings("# 正常页\n\n正文\n")
        cases.append(("单 H1 正常解析", h1 == ["正常页"] and skipped == 0))

        h1, _ = scan_headings("## 只有二级\n")
        cases.append(("缺 H1 不被误判", h1 == []))

        h1, _ = scan_headings("# 一\n\n# 二\n")
        cases.append(("多 H1 全部取到", h1 == ["一", "二"]))

        h1, skipped = scan_headings("# 围栏页\n\n```shell\n# 这是注释\n```\n")
        cases.append(("围栏内井号被跳过", h1 == ["围栏页"] and skipped == 1))

        nested = "# 嵌套页\n\n````markdown\n```shell\n# 里面的注释\n```\n````\n"
        h1, skipped = scan_headings(nested)
        cases.append(("四反引号围栏内的三反引号不关闭围栏", h1 == ["嵌套页"] and skipped == 1))

        sidebar = load_sidebar_texts(root)
        drift = any(
            sidebar.get(str(root / "docs" / "D" / "index.md")) == "漂移标题"
            and scan_headings((root / "docs" / "D" / "index.md").read_text(encoding="utf-8"))[0][0]
            != "漂移标题"
            for _ in [0]
        )
        cases.append(("侧边栏漂移可被检出", drift))

    ok = 0
    for name, passed in cases:
        print(("PASS " if passed else "FAIL ") + name)
        ok += 1 if passed else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(Path(args.root).resolve())


if __name__ == "__main__":
    sys.exit(main())
