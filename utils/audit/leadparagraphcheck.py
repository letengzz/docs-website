#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""leadparagraphcheck.py — 「H1 下方有没有一句话定位」巡检 · 第 90 项

为什么立这一项
--------------
`AGENTS.md` 第 5 节第 1 条把「一句话定位」写成硬要求：**H1 下方用 1~2 句说明
「这是什么、解决什么问题、适用于谁」**。这条要求被违反了四道旧门一道都拦不住：

* `headingcheck`（第 84 项）：只看 H1 有几个、标题层级对不对 → 管标题；
* `sectionordercheck`（第 89 项）：只看末节是不是参考资料 → 管结尾；
* `tablecheck` / `imagebytescheck`：只看表格与图片本身 → 管素材；
* `judgecovercheck`：只看判据表在不在 → 管判据。

于是出现一种很隐蔽的页面：**标题、判据、配图、参考资料全都齐，但读者点进来第一屏
看不到「这页到底讲什么」**——因为 H1 下面直接就是一张图、一个列表，或者一个
`::: tip` 容器。它不会让构建失败，也不会让链接失效，只会让读者多点一次返回。

判据
----
E0 ROOT_NOT_FOUND    仓库根找不到（或既没有 docs/ 也没有 project/）
E1 NO_PAGES          一个 index.md 都没扫到（活性判据：拒绝在空集上给「全绿」）
E2 NO_H1             页面里没有 `#` 一级标题（无法定位「H1 下方」）
E3 NO_LEAD_DEEP      **带判据表的页面**（即按「完整主题模板」写的新页）H1 与首个 H2
                     之间既没有普通段落、也没有含文字的容器
W1 LEAD_IN_CONTAINER 定位写在了 `::: tip` / `::: info` / `>` 引用块里，没有独立段落（风格建议）
W2 LEAD_MISSING      不带判据表的存量章节页没有定位段（欠账，逐日补）
W3 LEAD_LONG         首个 H2 之前存在超过 200 字的段落（开篇过长，定位被淹没）
W4 LEAD_MANY         首个 H2 之前有超过 3 个普通段落（开篇碎成多段）

口径（四条，全部来自真实语料的打磨）
------------------------------------
1. **Logo 不算「没有定位」**：第 7 节第 8 条要求主题首页在 H1 下方放官方 Logo，
   所以「H1 → 图片 → 段落」是合规顺序。判据只看「有没有段落」，不看「第一个块是
   不是图片」。
2. **容器里的文字算「有定位」但只报 W1**：`::: tip 一句话理解` 确实传达了信息，
   但它不满足「1~2 句说明这是什么」的叙述要求；报 E 会把大量合规页面打成红灯，
   报 W 才既能提示、又不淹没真缺陷。
3. **围栏与行内代码必须跳过**：复用 `fenceutil.scan()`（第 88 项的共享底座），
   本项不写第五份围栏正则。
4. **只扫 `index.md`**：页面正文一律以「英文目录 + index.md」组织（第 3 节），
   平铺的 `.md` 是历史遗留，不在本项范围内。

纪律
----
* **只读**：不写文件、不改台账、不自动补段落（补什么话属于写作，交人工）。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/leadparagraphcheck.py              # 全库
    python3 utils/audit/leadparagraphcheck.py --root . --limit 50
    python3 utils/audit/leadparagraphcheck.py --selftest
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402

SKIP_DIRS = {".git", ".vitepress", "node_modules", ".workbuddy", "assets", "public"}
ROOTS = ("docs", "project")

H1_RE = re.compile(r"^#\s+\S")
H2_RE = re.compile(r"^##\s+\S")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)")
TABLE_RE = re.compile(r"^\s*\|")
LINK_ONLY_RE = re.compile(r"^[-*+]\s+\[[^\]]+\]\([^)]+\)\s*$")
JUDGE_HEAD_RE = re.compile(r"^\|\s*编号\s*\|", re.M)

LEAD_MAX_CHARS = 200
LEAD_MAX_PARAS = 3


def is_paragraph(line: str) -> bool:
    """普通段落行：非空、不是标题/列表/表格/容器/围栏/图片/HTML 块引用。"""
    s = line.strip()
    if not s:
        return False
    if s.startswith(("#", "```", "~~~", ":::", "|", ">", "<!--")):
        return False
    if LIST_RE.match(line) or TABLE_RE.match(line):
        return False
    if s.startswith("![") or s.startswith("<img") or s.startswith("<p") or s.startswith("<div"):
        return False
    return True


def analyze(text: str):
    """返回 (status, detail)：status ∈ {'ok','no_h1','no_lead','container','long','many'}。

    detail 带上首个段落的前 30 字或最长段落的字数，便于人工定位。
    """
    mask, _, _ = scan(text)
    lines = text.split("\n")

    h1 = None
    for i, line in enumerate(lines):
        if i in mask:
            continue
        if H1_RE.match(line):
            h1 = i
            break
    if h1 is None:
        return "no_h1", ""

    paras, has_container_text, in_container = [], False, False
    longest = 0
    link_items, other_items = 0, 0
    for i in range(h1 + 1, len(lines)):
        if i in mask:
            continue
        line = lines[i]
        if H2_RE.match(line):
            break
        s = line.strip()
        if s.startswith(":::"):
            in_container = not in_container if s.startswith(":::") and len(s) > 3 else in_container
            continue
        if in_container and s:
            has_container_text = True
            continue
        if s.startswith(">"):
            # 引用块（本库 project/ 页面常用作开篇）与容器同类：有信息，但不是叙述段落
            if len(s.lstrip("> ").strip()) > 0:
                has_container_text = True
            continue
        if LIST_RE.match(line):
            if LINK_ONLY_RE.match(s):
                link_items += 1
            else:
                other_items += 1
            continue
        if is_paragraph(line):
            paras.append(s)
            longest = max(longest, len(s))

    if not paras:
        # 目录页豁免：H1 下面只有「链接列表」（第 6 节：目录页 = 主题名 + 子页链接列表）
        if link_items and not other_items and not has_container_text:
            return "toc", "%d 条子页链接" % link_items
        if has_container_text:
            return "container", ""
        # 带判据表的页面 = 按「完整主题模板」写的新页，定位段是硬要求（E）
        if JUDGE_HEAD_RE.search(text):
            return "no_lead_deep", ""
        return "no_lead", ""
    if len(paras) > LEAD_MAX_PARAS:
        return "many", "首个 H2 前有 %d 段" % len(paras)
    if longest > LEAD_MAX_CHARS:
        return "long", "最长段落 %d 字" % longest
    return "ok", paras[0][:30]


def collect(root):
    pages = []
    for base in ROOTS:
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            if "index.md" in filenames:
                pages.append(os.path.join(dirpath, "index.md"))
    return sorted(pages)


def run(root, limit=40, quiet=False):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND: %s" % root)
        return 1
    if not any(os.path.isdir(os.path.join(root, b)) for b in ROOTS):
        print("E0 ROOT_NOT_FOUND: 既没有 docs/ 也没有 project/")
        return 1
    pages = collect(root)
    if not pages:
        print("E1 NO_PAGES: 一个 index.md 都没扫到")
        return 1

    buckets = {"no_h1": [], "no_lead_deep": [], "no_lead": [], "container": [], "long": [], "many": [], "toc": [], "ok": []}
    for page in pages:
        with open(page, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        status, detail = analyze(text)
        buckets[status].append((os.path.relpath(page, root), detail))

    if not quiet:
        for rel, _ in buckets["no_h1"][:limit]:
            print("E2 NO_H1: %s" % rel)
        for rel, _ in buckets["no_lead_deep"][:limit]:
            print("E3 NO_LEAD_DEEP: %s（带判据表的页面缺定位段）" % rel)
        for rel, _ in buckets["no_lead"][:limit]:
            print("W2 LEAD_MISSING: %s（H1 与首个 H2 之间没有段落）" % rel)
        for rel, _ in buckets["container"][:limit]:
            print("W1 LEAD_IN_CONTAINER: %s（定位写在容器里）" % rel)
        for rel, d in buckets["long"][:limit]:
            print("W3 LEAD_LONG: %s（%s）" % (rel, d))
        for rel, d in buckets["many"][:limit]:
            print("W4 LEAD_MANY: %s（%s）" % (rel, d))

    e = len(buckets["no_h1"]) + len(buckets["no_lead_deep"])
    w = (len(buckets["container"]) + len(buckets["no_lead"])
         + len(buckets["long"]) + len(buckets["many"]))
    print(
        "pages=%d ok=%d toc=%d E2_NO_H1=%d E3_NO_LEAD_DEEP=%d W1_CONTAINER=%d W2_MISSING=%d W3_LONG=%d W4_MANY=%d"
        % (
            len(pages),
            len(buckets["ok"]),
            len(buckets["toc"]),
            len(buckets["no_h1"]),
            len(buckets["no_lead_deep"]),
            len(buckets["container"]),
            len(buckets["no_lead"]),
            len(buckets["long"]),
            len(buckets["many"]),
        )
    )
    return 0 if e == 0 else 1


def _make(root, files):
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)


def selftest():
    cases = []

    # ① 标准形态：H1 → Logo → 段落 → H2 → 全绿
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n<p><img src=\"./assets/a.png\"></p>\n\n这是定位句。\n\n## 一、正文\n\n内容。\n"})
    cases.append(("标准形态（Logo + 段落）", d, "ok"))

    # ② H1 下面直接一个列表 → E3
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n- 要点一\n- 要点二\n\n## 一、正文\n"})
    cases.append(("H1 后只有非链接列表", d, "no_lead"))

    # ⑦ 只有子页链接列表 → 目录页豁免（toc）
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n- [子页](Sub/index.md)\n", "docs/A/Sub/index.md": "# Sub\n"})
    cases.append(("目录页（只有链接列表）", d, "toc"))

    # ⑧ 带判据表但没有定位段 → E3
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n## 一、正文\n\n| 编号 | 判据 | 看什么现象 |\n| --- | --- | --- |\n| `A-A` | x | y |\n"})
    cases.append(("带判据表却无定位段", d, "no_lead_deep"))

    # ③ 只有图片和表格 → E3
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n![](./assets/a.svg)\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\n## 一、正文\n"})
    cases.append(("H1 后只有图与表", d, "no_lead"))

    # ④ 定位写在容器里 → W1
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n::: tip 一句话理解\n这是定位。\n:::\n\n## 一、正文\n"})
    cases.append(("定位写在容器里", d, "container"))

    # ⑤ 首段过长 → W2
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n" + "很长的段落。" * 60 + "\n\n## 一、正文\n"})
    cases.append(("首段超 200 字", d, "long"))

    # ⑥ 围栏里的「段落」不算段落 → E3
    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# A\n\n```text\n这是在围栏里\n```\n\n## 一、正文\n"})
    cases.append(("围栏里的文字不算定位", d, "no_lead"))

    ok = 0
    for name, d, want in cases:
        page = os.path.join(d, "docs/A/index.md")
        with open(page, encoding="utf-8") as f:
            got, _ = analyze(f.read())
        flag = "PASS" if got == want else "FAIL(got=%s want=%s)" % (got, want)
        if got == want:
            ok += 1
        print("  %-24s %s" % (name, flag))
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(os.path.abspath(args.root), args.limit, args.quiet)


if __name__ == "__main__":
    sys.exit(main())
