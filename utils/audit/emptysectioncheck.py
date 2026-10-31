#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""emptysectioncheck.py — 「小节里有没有内容」巡检 · 第 103 项

为什么立这一项
--------------
本库已有六道门围着「一节该长什么样」转，但它们**全部只看小节的外壳**：

* `headingcheck`（第 84 项）      —— 有没有且只有一个 H1、层级对不对；
* `levelskipcheck`（第 85 项）    —— 标题有没有跳级；
* `sectionnumcheck`（第 76 项）   —— 小节编号连不连续、标题重不重；
* `sectionordercheck`（第 89 项） —— 末节是不是参考资料、验证节位置对不对；
* `leadparagraphcheck`（第 90 项）—— H1 下方有没有定位段；
* `placeholdercheck`（第 94 项）  —— 正文里有没有「待补充」这类标记。

六道门全绿的页面可以是这个样子：

    ## 五、常见错误
    ## 六、验证方式

两个标题之间**一个字都没有**。它的编号连续、层级正确、末节合规、没有占位词——
可读者点到这一节，看到的只有一个标题，然后直接被带到下一节。这类缺陷的代价与
第 94 项（占位词）同族：**结构全绿、内容为零**；区别是它连「待补充」都懒得写。

判据
----
E0 ROOT_NOT_FOUND   仓库根既没有 docs/ 也没有 project/
E1 NO_PAGES         一个 .md 都没扫到（活性判据：拒绝在空集上给「全绿」）
E2 NO_SECTIONS      一个二级及以下标题都没解析到（活性判据：解析器坏了也会「全绿」）
W1 EMPTY_SECTION    标题之后、下一个同级或更高级标题之前，没有任何内容行
W2 EMPTY_LEAF       叶子标题（H4~H6）下无内容（更细的层级空了，说明大纲在漂）
N1 LEAF_GROUP       只有子标题、自己没有正文（合法的分组写法，只计数不判错）

口径（四条，全部来自真实语料）
------------------------------
1. **「内容」的判定要宽**：任何非空行都算内容——列表、表格、图片、`:::` 容器、
   `>` 引用、甚至一句「见下」都算。本项只抓**彻底的空**，不评价写得好不好；
   把「一句话太短」也判成错，会一次造出几百条噪声（对照第 91 项 `titlematchcheck`
   的教训：二值判断混进多种性质，永久黄等于没人看）。
2. **围栏里的假标题不算标题**：`fenceutil.scan()` 给出的 mask 要整段跳过，否则
   `shell` 里的 `## 步骤` 会被当成真章节，把它上面的小节判成「有内容」。
3. **frontmatter 不算内容**：本库只有根 `index.md` 用 frontmatter，但它恰好出现在
   H1 之前；不跳过会把「H1 前有内容」误算成第一节非空。
4. **分组标题归 `N1` 不归 `W1`**：本库大量页面用「## 三、核心概念」下挂几个 H3、
   自己只在开头写半句引导。**只要它下面有子标题且子标题有内容**，这是合法结构，
   只计数；反过来「有子标题但子标题自己也全是空的」会由子标题各自的 `W1` 报出来。

纪律
----
* **只读**：不写文件、不自动删空节、不自动合并小节——「这两个标题该不该合并」
  是作者判断。本项只负责列出「哪个文件、第几行、哪个标题、空到哪一行」。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/emptysectioncheck.py
    python3 utils/audit/emptysectioncheck.py --root . --limit 30
    python3 utils/audit/emptysectioncheck.py --summary
    python3 utils/audit/emptysectioncheck.py --selftest
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fenceutil  # noqa: E402

HEAD_RE = re.compile(r"^(#{2,6})\s+(.*\S)\s*$")
FM_RE = re.compile(r"^---\s*$")


def _pages(root: Path):
    for base in ("docs", "project"):
        d = root / base
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            yield p


def _norm(p: Path, root: Path) -> str:
    try:
        return p.relative_to(root).as_posix()
    except ValueError:
        return p.as_posix()


def analyse(text: str):
    """返回 (sections, empty, empty_leaf, leaf_group)。

    sections: [(lineno, level, title)]
    empty:    [(lineno, level, title)]        W1
    """
    lines = text.split("\n")
    mask, _blocks, _unclosed = fenceutil.scan(text)

    # frontmatter：只在文件开头出现
    fm_skip = set()
    if lines and FM_RE.match(lines[0]):
        for i in range(1, len(lines)):
            fm_skip.add(i)
            if FM_RE.match(lines[i]):
                break

    # 收集标题与其后第一行有效内容的行号
    heads = []
    for i, ln in enumerate(lines):
        if i in mask or i in fm_skip:
            continue
        m = HEAD_RE.match(ln)
        if m:
            heads.append((i, len(m.group(1)), m.group(2).strip()))

    sections = [(i, lv, t) for i, lv, t in heads]
    empty, empty_leaf, leaf_group = [], [], []
    head_lines = {h[0] for h in heads}

    for idx, (i, lv, t) in enumerate(heads):
        end = len(lines)
        for j, lv2, _t2 in heads[idx + 1:]:
            if lv2 <= lv:
                end = j
                break
        kids = [h[0] for h in heads if i < h[0] < end]
        has_child = bool(kids)
        # 自己的正文只在「第一个子标题之前」找；子标题之后的内容属于子节
        limit = kids[0] if kids else end
        has_own = False
        for k in range(i + 1, limit):
            if k in head_lines and k not in mask:
                continue
            if k in fm_skip and k not in mask:
                continue
            if lines[k].strip() or k in mask:
                has_own = True
                break

        if has_own:
            continue
        if has_child:
            leaf_group.append((i, lv, t))       # 合法分组，只计数
            continue
        if lv >= 4:
            empty_leaf.append((i, lv, t))       # W2
        else:
            empty.append((i, lv, t))            # W1

    return sections, empty, empty_leaf, leaf_group


def run(root: Path, limit: int, verbose: bool) -> int:
    if not (root / "docs").is_dir() and not (root / "project").is_dir():
        print(f"E0 ROOT_NOT_FOUND: {root}")
        return 1
    pages = list(_pages(root))
    if not pages:
        print("E1 NO_PAGES: 没扫到任何 .md")
        return 1

    total_sections = 0
    w1 = w2 = n1 = 0
    rows = []
    for p in pages:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        sections, empty, empty_leaf, leaf_group = analyse(text)
        total_sections += len(sections)
        n1 += len(leaf_group)
        rel = _norm(p, root)
        for i, lv, t in empty:
            w1 += 1
            rows.append(f"W1 EMPTY_SECTION  {rel}:{i + 1}  {'#' * lv} {t}")
        for i, lv, t in empty_leaf:
            w2 += 1
            rows.append(f"W2 EMPTY_LEAF     {rel}:{i + 1}  {'#' * lv} {t}")

    if total_sections == 0:
        print("E2 NO_SECTIONS: 一个二级以下标题都没解析到")
        return 1

    shown = rows if verbose else rows[:limit]
    for r in shown:
        print(r)
    if not verbose and len(rows) > limit:
        print(f"…另有 {len(rows) - limit} 条同类提示（--verbose 全列）")

    print(f"\npages={len(pages)} sections={total_sections} "
          f"W1={w1} W2={w2} N1_LEAF_GROUP={n1}")
    return 0


def _make(d: str, files: dict) -> None:
    for rel, body in files.items():
        p = Path(d) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


def selftest() -> int:
    cases = []

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n引言。\n\n## 一、有内容\n\n正文。\n"})
    cases.append(("正常页面", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n引言。\n\n## 一、有内容\n\n正文。\n\n## 二、空的\n\n## 三、又有\n\n正文。\n"})
    cases.append(("H2 完全空", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、空到文末\n"})
    cases.append(("末节空", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、分组\n\n### 1.1 有内容\n\n正文。\n"})
    cases.append(("只有子标题但有内容（N1，不算错）", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、分组\n\n### 1.1 空\n\n### 1.2 空\n\n## 二、有\n\n正文。\n"})
    cases.append(("分组与子节全空（父节只计数）", d, (2, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、代码\n\n```shell\necho hi\n```\n"})
    cases.append(("围栏算内容", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、围栏里假标题\n\n```shell\n## 这不是标题\n```\n\n## 二、空\n"})
    cases.append(("围栏里的假标题不算标题", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、列表\n\n- 一项\n"})
    cases.append(("列表算内容", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、容器\n\n::: tip 提示\n建议。\n:::\n"})
    cases.append(("容器算内容", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、图\n\n![图](../../assets/x.svg)\n"})
    cases.append(("图片算内容", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "---\nlayout: home\n---\n\n# 标题\n\n## 一、有\n\n正文。\n"})
    cases.append(("frontmatter 被跳过", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、有\n\n#### 深一层空\n\n## 二、有\n\n正文。\n"})
    cases.append(("叶子标题空（W2）", d, (0, 1)))

    d = tempfile.mkdtemp()
    _make(d, {"project/Complete/P/index.md": "# 项目\n\n## 一、空\n\n## 二、有\n\n正文。\n"})
    cases.append(("project 目录也扫", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、有\n\n正文。\n\n### 1.1 空\n"})
    cases.append(("叶子 H3 空算 W1（H3 非叶子层级）", d, (1, 0)))

    ok = 0
    for name, d, (exp_w1, exp_w2) in cases:
        pages = list(_pages(Path(d)))
        w1 = w2 = 0
        for p in pages:
            _s, e, el, _g = analyse(p.read_text(encoding="utf-8"))
            w1 += len(e)
            w2 += len(el)
        good = (w1 == exp_w1 and w2 == exp_w2)
        ok += good
        print(f"{'PASS' if good else 'FAIL'}  {name}: W1={w1}(期望 {exp_w1}) W2={w2}(期望 {exp_w2})")
    print(f"\nselftest {ok}/{len(cases)} PASS")
    return 0 if ok == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="小节内容空壳巡检")
    ap.add_argument("--root", default=".", help="仓库根（含 docs/ 或 project/）")
    ap.add_argument("--limit", type=int, default=30, help="最多打印多少条")
    ap.add_argument("--verbose", action="store_true", help="全列")
    ap.add_argument("--summary", action="store_true", help="只打印汇总")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.summary:
        a.limit = 0
    return run(Path(a.root).resolve(), a.limit, a.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
