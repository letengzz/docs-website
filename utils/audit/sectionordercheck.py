#!/usr/bin/env python3
r"""sectionordercheck.py — 页面末节结构巡检（第 74 项）

存在的理由
----------
`refcheck.py` 管「有没有参考资料节」，`verifycheck.py` 管「有没有验证方式节」，
`sectioncheck.py` 管「某一节是不是空的」——**没有一项管「这些节的先后顺序」**。

而本库的约定写得很明确（`AGENTS.md` 第 5 节：「参考资料：文末附官方文档或权威链接」），
且日常维护动作是「新写的小节插在 `## 参考资料` **之前**」。这个动作有一个静默失效形态：
小节插到了参考资料**后面**。页面照样渲染、链接照样能点、构建照样通过，
只是读者看到的是「参考资料 → 然后又一段正文」——文末参考变成了文中参考。

判据
----
E0 ROOT_NOT_FOUND          仓库根找不到 docs/ 与 project/
E1 NO_PAGES                一个页面都没枚举到（拒绝判定）
E2 BODY_AFTER_REFS         参考资料之后还有「正文类」小节（验证方式 / 易错点 / 实操 / 案例 / 步骤 …）
W1 APPENDIX_AFTER_REFS     参考资料之后是「附录类」小节（分工 / 相关专题 / 延伸阅读 / 下一步）
W2 MULTI_REFS              一页出现两个以上参考资料节
N0 NO_REFS                 没有参考资料节的页数（`refcheck` 已管，这里只计数不判错）

设计取舍
--------
* **E2 与 W1 分开，是这一项最重要的判断**。全库首轮实测 90 页在参考资料之后有小节，
  逐页看下来**几乎全是「与某专题的分工」这类附录**——把它们判成 E 会立刻产生 90 条噪声，
  而一个天天报 90 条假错的检查，第二天就会被跳过。于是：附录类降为 W（格式债），
  只有「正文内容」排到参考资料之后才算结构性错误（读者会以为文章已经结束）。
* 只认 `##` 级（H2）。`###` 是某一节内部的小节，跟在参考资料下的 `###` 是「参考资料的子项」，
  不算违反顺序。
* 围栏代码块内的 `## xxx` 一律跳过：shell 注释与 Python 注释里出现 `##` 很常见。
* 分类只做「关键词包含」，不做语义判断：判错的代价是「一条 W 变成 E」或反之，
  两种都比「为了让脚本闭嘴而改写正确的文档」便宜。

用法
----
    python3 utils/audit/sectionordercheck.py            # 巡检
    python3 utils/audit/sectionordercheck.py --selftest # 自测
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
H2 = re.compile(r"^##\s+(.+?)\s*$")

REFS_WORDS = ("参考资料", "参考链接", "参考文献")
# 附录类：明确是「挂在正文之外的补充」
APPENDIX_WORDS = ("分工", "相关专题", "相关页面", "延伸阅读", "延伸", "下一步", "另见", "参见", "附录")

SKIP_DIRS = {"assets", "node_modules", ".vitepress", ".git"}


def iter_pages(root: Path):
    for base in ("docs", "project"):
        d = root / base
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            yield p


def h2_sections(text: str):
    """返回 [(行号, 标题)]，跳过围栏代码块内的内容。"""
    out = []
    in_fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = H2.match(line)
        if m:
            out.append((i, m.group(1).strip()))
    return out


def is_refs(title: str) -> bool:
    return any(w in title for w in REFS_WORDS)


def is_appendix(title: str) -> bool:
    return any(w in title for w in APPENDIX_WORDS)


def check(root: Path):
    issues = []  # (code, path, msg)
    pages = 0
    no_refs = 0
    for p in iter_pages(root):
        pages += 1
        rel = p.relative_to(root).as_posix()
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        secs = h2_sections(text)
        refs = [(ln, t) for ln, t in secs if is_refs(t)]
        if not refs:
            no_refs += 1
            continue
        if len(refs) > 1:
            issues.append(("W2", rel, f"出现 {len(refs)} 个参考资料节：" + "、".join(t for _, t in refs)))
        last_ln = refs[-1][0]
        after = [(ln, t) for ln, t in secs if ln > last_ln]
        for ln, t in after:
            if is_appendix(t):
                issues.append(("W1", rel, f"第 {ln} 行「{t}」在参考资料之后（附录类，建议前移）"))
            else:
                issues.append(("E2", rel, f"第 {ln} 行「{t}」是正文内容，却排在参考资料之后"))
    return pages, no_refs, issues


def selftest() -> int:
    cases = []
    good = """# 标题

正文。

## 一、概念

内容。

## 验证方式

```shell
echo ok
```

## 参考资料

- [A](https://example.com)
"""
    appendix_after = good.replace("## 参考资料", "## 一、原理\n\n内容。\n\n## 参考资料") + "\n## 与某专题的分工\n\n补充。\n"
    body_after = good + "\n## 二、易错点\n\n- 坑一\n"
    multi_refs = good + "\n## 参考资料\n\n- [B](https://example.org)\n"
    no_refs = "# 标题\n\n## 一、概念\n\n内容。\n"
    fence_case = """# 标题

```shell
## 这不是标题，是注释
```

## 参考资料

- [A](https://example.com)

```python
## 也不是标题
```
"""
    cases = [
        ("case-1-good", good, []),
        ("case-2-appendix-after", appendix_after, ["W1"]),
        ("case-3-body-after", body_after, ["E2"]),
        ("case-4-multi-refs", multi_refs, ["W2"]),
        ("case-5-no-refs", no_refs, []),
        ("case-6-fence", fence_case, []),
    ]
    ok = 0
    for name, body, expect in cases:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "docs" / "Page").mkdir()
            (root / "docs" / "Page" / "index.md").write_text(body, encoding="utf-8")
            pages, _no_refs, issues = check(root)
            codes = sorted({c for c, _, _ in issues})
            if codes == sorted(expect) and pages == 1:
                ok += 1
                print(f"  PASS {name}: {codes or '无问题'}")
            else:
                print(f"  FAIL {name}: 期望 {expect} 实际 {codes}（pages={pages}）")
    # 活性：空仓库必须报 0 页（由主流程判 E1）
    with tempfile.TemporaryDirectory() as td:
        pages, _, _ = check(Path(td))
        if pages == 0:
            ok += 1
            print("  PASS case-7-empty: pages=0（触发 E1）")
        else:
            print(f"  FAIL case-7-empty: pages={pages}")
    total = len(cases) + 1
    print(f"selftest {ok}/{total}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="页面末节结构巡检（第 74 项）")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    if not (root / "docs").is_dir() and not (root / "project").is_dir():
        print("E0 ROOT_NOT_FOUND: 找不到 docs/ 与 project/")
        return 1
    pages, no_refs, issues = check(root)
    if pages == 0:
        print("E1 NO_PAGES: 没有枚举到任何页面，拒绝判定")
        return 1

    order = {"E2": 0, "W1": 1, "W2": 2}
    issues.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    for code, rel, msg in issues:
        print(f"{code} {rel}: {msg}")
    e = sum(1 for c, _, _ in issues if c.startswith("E"))
    w = sum(1 for c, _, _ in issues if c.startswith("W"))
    print(f"\npages={pages} no_refs={no_refs} E={e} W={w}")
    return 0 if e == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
