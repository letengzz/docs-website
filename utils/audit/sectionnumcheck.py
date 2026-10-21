#!/usr/bin/env python3
r"""sectionnumcheck.py — 同页小节编号与标题唯一性巡检（第 76 项）

存在的理由
----------
`headingcheck.py` 管「有没有且只有一个 H1」、`sidebartitlecheck.py` 管「菜单名与 H1
是否一致」、`anchorcheck.py` 管「链接里的 `#fragment` 能否对上」——**没有一项看
「同一页里的小节标题本身」**。

而本库的写法高度依赖小节编号：绝大多数页面用 `## 一、` `## 二、` 组织，右侧目录就是
按这个顺序给读者导航的。这里有两种静默失效：

1. **编号重复或跳号**。插入一节之后忘记重排，于是出现两个「## 三、」或者「三、」直接
   跳到「五、」。页面照样渲染、构建照样通过，只有读者会数错。
2. **标题同名**。同一页出现两个 `## 相关专题`、两个 `## 验证方式`。VitePress 会给后来
   的那个加 `-1` 后缀，于是**锚点悄悄变了**：外部链接与页内跳转都还能「点得动」，
   只是落在第一个同名标题上。

第 174 天立的 `anchorcheck` 只能在「有人链接了那个锚点」时才发现第二类问题；没有人
链接时它是看不见的。这一项把方向反过来：**先查标题集合，再查链接**。

判据
----
E0 ROOT_NOT_FOUND       仓库根找不到 docs/ 与 project/
E1 NO_PAGES             一个页面都没枚举到（拒绝判定）
E2 DUP_SECTION_TITLE    同页出现两个以上完全相同的 H2（锚点会被加 `-1` 后缀）
E3 REUSED_NUMBER        同一编号段内编号倒退（如 一、二、三、二）
E4 SEQ_GAP              同一编号段内跳号（如 一、二、四）
E5 FIRST_NOT_ONE        页面第一个编号小节不是「一」（读者打开就是「八、」）
W1 SEQ_RESTART          编号从头重新开始（可能是有意的分组，需人工确认）
W2 MIXED_STYLE          同页混用中文序号与阿拉伯序号（`## 一、` 与 `## 1.`）

设计取舍
--------
* **只认 `##`（H2）**。`###` 是节内小节，编号体系常与 H2 不同（如「2.1」），一起判会造噪声。
* **重启判 W 不判 E**。库里确实有「先讲原理（一~四）再讲操作（一~三）」的写法，
  重启是合法的分组信号；但**重启之后必须继续递增**，所以重启本身只提示，重启后跳号/倒退照样判 E。
* **跳号判 E、倒退判 E**。这两种没有任何合法解释：读者按编号找内容会找错地方。
* **标题同名只比去空白后的原文**，不做同义判断。同名标题在渲染层面一定会撞锚点，
  这是机制问题，不是文风问题。
* **围栏代码块内的 `##` 一律跳过**：本库大量页面在 `shell` / `python` 块里出现 `#` 注释，
  四反引号嵌套三反引号的写法也存在（第 68 项踩过这个坑），这里按「同字符、长度不短于开启
  围栏」才认闭合。

用法
----
    python3 utils/audit/sectionnumcheck.py            # 巡检
    python3 utils/audit/sectionnumcheck.py --selftest # 自测
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

H2 = re.compile(r"^##\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
CJK_NUM = re.compile(r"^([一二三四五六七八九十]+)、")
AR_NUM = re.compile(r"^(\d+)(?:[.．]\s+|[、]\s*)")
CJK_DIGITS = {c: i + 1 for i, c in enumerate("一二三四五六七八九")}

SKIP_DIRS = {"assets", "node_modules", ".vitepress", ".git"}


def cjk_to_int(s: str) -> int:
    """把「一」「十」「十二」「二十一」「三十」这类中文序号转成整数。"""
    if "十" not in s:
        return CJK_DIGITS.get(s, 0) if len(s) == 1 else 0
    head, _, tail = s.partition("十")
    tens = 1 if head == "" else CJK_DIGITS.get(head, 0)
    ones = 0 if tail == "" else CJK_DIGITS.get(tail, 0)
    return tens * 10 + ones


def iter_pages(root: Path):
    for base in ("docs", "project"):
        d = root / base
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            yield p


def h2_titles(text: str) -> list[str]:
    """返回页面里所有 H2 的标题文本，跳过围栏代码块。"""
    out: list[str] = []
    fence = None  # (char, length)
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            ticks = m.group(1)
            if fence is None:
                fence = (ticks[0], len(ticks))
            elif ticks[0] == fence[0] and len(ticks) >= fence[1] and line.strip() == ticks:
                fence = None
            continue
        if fence is not None:
            continue
        m2 = H2.match(line)
        if m2:
            out.append(m2.group(1).strip())
    return out


def check_page(rel: str, titles: list[str]):
    issues = []
    # E2 标题同名
    seen: dict[str, int] = {}
    for t in titles:
        seen[t] = seen.get(t, 0) + 1
    for t, n in seen.items():
        if n > 1:
            issues.append(("E2", rel, f"标题「{t}」在本页出现 {n} 次（锚点会被加 -1 后缀）"))

    cjk_seq = []
    ar_seq = []
    for t in titles:
        m = CJK_NUM.match(t)
        if m:
            cjk_seq.append(cjk_to_int(m.group(1)))
            continue
        m = AR_NUM.match(t)
        if m:
            ar_seq.append(int(m.group(1)))

    if cjk_seq and ar_seq:
        issues.append(("W2", rel, f"同页混用中文序号（{len(cjk_seq)} 节）与阿拉伯序号（{len(ar_seq)} 节）"))

    for label, seq in (("中文序号", cjk_seq), ("阿拉伯序号", ar_seq)):
        if not seq:
            continue
        if seq[0] > 1:
            issues.append(("E5", rel, f"第一个{label}小节是「{seq[0]}」而不是 1"))
        last = seq[0]
        for n in seq[1:]:
            if n == last + 1:
                last = n
                continue
            if n <= last:
                if n == 1:
                    issues.append(("W1", rel, f"{label}从 1 重新开始（上一节是 {last}），确认是否为有意的分组"))
                else:
                    issues.append(("E3", rel, f"{label}倒退：{last} 之后出现 {n}"))
                last = n
                continue
            issues.append(("E4", rel, f"{label}跳号：{last} 之后直接是 {n}"))
            last = n
    return issues


def check(root: Path):
    pages = 0
    issues = []
    for p in iter_pages(root):
        pages += 1
        rel = str(p.relative_to(root))
        issues.extend(check_page(rel, h2_titles(p.read_text(encoding="utf-8", errors="replace"))))
    return pages, issues


def selftest() -> int:
    cases = [
        ("normal.md", "# T\n\n## 一、甲\n\n## 二、乙\n\n## 三、丙\n", []),
        ("dup.md", "# T\n\n## 相关专题\n\na\n\n## 验证方式\n\nb\n\n## 相关专题\n\nc\n", ["E2"]),
        ("gap.md", "# T\n\n## 一、甲\n\n## 二、乙\n\n## 四、丁\n", ["E4"]),
        ("back.md", "# T\n\n## 一、甲\n\n## 二、乙\n\n## 三、丙\n\n## 二、乙二\n", ["E3"]),
        ("first.md", "# T\n\n## 八、甲\n\n## 九、乙\n", ["E5"]),
        ("restart.md", "# T\n\n## 一、甲\n\n## 二、乙\n\n## 一、丙\n\n## 二、丁\n", ["W1"]),
        ("mixed.md", "# T\n\n## 一、甲\n\n## 1. 乙\n", ["W2"]),
        ("zero.md", "# T\n\n## 0. 前置\n\n## 1. 甲\n\n## 2. 乙\n", []),
        ("ver.md", "# T\n\n## 4.x 新特性\n\n## 9.5 与日志\n\n## 参考资料\n", []),
        ("fence.md", "# T\n\n## 一、甲\n\n```shell\n## 这是注释\n## 二、另一条注释\n```\n\n## 二、乙\n", []),
        ("four.md", "# T\n\n## 一、甲\n\n````markdown\n```shell\n## 一、示例\n```\n````\n\n## 二、乙\n", []),
        ("ten.md", "# T\n\n" + "".join(f"## {c}、x\n\n" for c in ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]) + "## 十一、y\n", []),
    ]
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs").mkdir()
        for i, (name, body, expect) in enumerate(cases):
            d = root / "docs" / f"c{i}"
            d.mkdir()
            (d / "index.md").write_text(body, encoding="utf-8")
        pages, issues = check(root)
        codes_by_page: dict[str, set[str]] = {}
        for code, rel, _ in issues:
            codes_by_page.setdefault(Path(rel).parts[1], set()).add(code)
        for i, (name, _, expect) in enumerate(cases):
            got = sorted(codes_by_page.get(f"c{i}", set()))
            if got == sorted(expect):
                ok += 1
            else:
                print(f"FAIL {name}: expect={expect} got={got}")
        # E1：空仓库
        with tempfile.TemporaryDirectory() as td2:
            empty = Path(td2)
            (empty / "docs").mkdir()
            p2, _ = check(empty)
            if p2 == 0:
                ok += 1
            else:
                print("FAIL empty: expect 0 pages")
    print(f"selftest {ok}/{len(cases) + 1}")
    return 0 if ok == len(cases) + 1 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="同页小节编号与标题唯一性巡检（第 76 项）")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    if not (root / "docs").is_dir() and not (root / "project").is_dir():
        print("E0 ROOT_NOT_FOUND: 找不到 docs/ 与 project/")
        return 1
    pages, issues = check(root)
    if pages == 0:
        print("E1 NO_PAGES: 没有枚举到任何页面，拒绝判定")
        return 1

    order = {"E2": 0, "E3": 1, "E4": 2, "E5": 3, "W1": 4, "W2": 5}
    issues.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    for code, rel, msg in issues:
        print(f"{code} {rel}: {msg}")
    e = sum(1 for c, _, _ in issues if c.startswith("E"))
    w = sum(1 for c, _, _ in issues if c.startswith("W"))
    print(f"\npages={pages} E={e} W={w}")
    return 0 if e == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
