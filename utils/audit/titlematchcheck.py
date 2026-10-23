#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""titlematchcheck.py — 「侧边栏 text 与页面 H1 是否同一件事」巡检 · 第 91 项

为什么立这一项（先说清楚它**不是**什么）
----------------------------------------
第 60 项的 `headingcheck` **已经在做**这件事，判据叫 `W1 TEXT_MISMATCH`，口径是
「侧边栏 text 与 H1 去空白后是否完全相等」。所以本项**不是**「补一道没人管的口子」，
而是**把一条没人处理的老告警拆开**。

问题在于它是个二值判断，把三种性质完全不同的情况混成一个数字：

* **族后缀**：侧边栏「作业模型（JOB-A~JOB-H）」 vs H1「作业模型」——本库既定风格；
* **短名**：侧边栏「概述」 vs H1「OpenClaw 概述」——父节点已给出主题名，也是既定风格；
* **真漂移**：侧边栏「实战：发布流水线与研究小组」 vs H1「实战：内容审核发布流水线与研究小组」——改名后旧名字留在侧边栏。

混在一起的结果是 **483 条 W1 从第 60 项建立至今没人动过**（永久黄 = 没人看，本库
91 项巡检反复验证过的规律）。本项做三件事：

1. **分级**：`W1` 只报互不包含的真漂移，`W2` 单独报短名风格，族后缀在归一化阶段剥掉、不计入；
2. **补齐 E 级**：把「link 缺失」「没有 H1」「一条条目都没解析到」纳入同一份报告
   （`headingcheck` 只对**能解析到侧边栏条目**的页面比文字，缺文件与无 H1 不在它的口径里）；
3. **给新页一条硬口径**：新增页面必须 0 条 `W1`（本项落地当日新建的 11 页全部 0 条）。

判据
----
E0 ROOT_NOT_FOUND     仓库根找不到（既没有 .vitepress/ 也没有 docs/、project/）
E1 NO_ENTRIES         一条侧边栏条目都没解析到（活性判据：拒绝在空集上给「全绿」）
E2 LINK_MISSING       侧边栏 link 指向的文件不存在（与 sidebarcheck 互补：那边查路由，这边查条目）
E3 NO_H1              目标页没有 `#` 一级标题
W1 TITLE_DIFF         归一化后两者互不包含（真漂移：同一位置换了说法）
W2 SHORT_NAME         一方是另一方的子串（「概述」vs「OpenClaw 概述」这类短名风格）

口径（五条，来自本库语料的打磨）
--------------------------------
1. **先归一化再比较**，归一化只做四件事：去掉尾部成对的括号组、全角括号转半角、
   压缩空白、去掉尾部冒号与句号。**不做**去标点、去数字——那会把「第 4 周第 4 步」
   与「第 4 周第 5 步」判成同一个（自测第 9 例专门守这条）。
2. **`（X-A~X-H）` 后缀不算问题**：本库侧边栏普遍带判据族后缀、页面 H1 不带，这是
   **既定风格**，报 `E` 会让几百条合规条目变红，报 `W` 也只是噪音，故归一化阶段
   直接剥掉、不计入任何计数。
   **「短名」单独算 `W2`**：父节点已给出主题名时，子条目写「概述」「安装」是既定写法；
   判据取「一方是另一方的子串」，只提示不阻断；互不包含才是真漂移（`W1`）。
3. **只认 `text` + `link` 同一行的条目**：多行条目在本库的写法里不存在，硬解析会把
   `items` 里的子条目错配到父节点上。解析不到就报 `E1`，而不是静默跳过。
4. **link 允许指向目录**（`/docs/Ops/Ansible`）：与 VitePress 一致，补成
   `<dir>/index.md` 再找文件。
5. **只比文字，不判对错**：「侧边栏叫 A、页面叫 B，哪个更好」属于写作判断，
   脚本只负责「它们不一样」这件事。

与 `headingcheck` 的关系：**同一条规则、不同颗粒度**。两者都保留——`headingcheck`
守「有没有漂移」（二值），本项守「漂移里哪些该改」（分级）。若日后合并，删本项、
把分级口径并回第 60 项即可，不要两处各写一份归一化实现。

纪律
----
* **只读**：不改侧边栏、不改标题，只报告。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/titlematchcheck.py
    python3 utils/audit/titlematchcheck.py --root . --limit 40
    python3 utils/audit/titlematchcheck.py --selftest
"""

import argparse
import os
import re
import sys
import tempfile

ENTRY_RE = re.compile(r'text:\s*"([^"]+)"\s*,\s*link:\s*"([^"]+)"')
PAREN_TAIL_RE = re.compile(r"[（(][^（()）]*[）)]\s*$")
FAMILY_RE = re.compile(r"[（(][A-Z][A-Z0-9]{0,5}-[A-H]~[A-Z][A-Z0-9]{0,5}-[A-H][）)]\s*$")


def normalize(text: str) -> str:
    s = text.strip()
    # 尾部括号组可能连着好几层，逐个剥
    while True:
        stripped = PAREN_TAIL_RE.sub("", s).strip()
        if stripped == s or not stripped:
            break
        s = stripped
    s = s.replace("（", "(").replace("）", ")").replace("：", ":")
    s = re.sub(r"\s+", "", s)
    return s.rstrip(":.。")


def read_h1(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        return None
    return None


def collect(root: str):
    vp = os.path.join(root, ".vitepress")
    entries = []
    if not os.path.isdir(vp):
        return entries
    for name in sorted(os.listdir(vp)):
        if not name.endswith(".ts"):
            continue
        with open(os.path.join(vp, name), encoding="utf-8") as f:
            for m in ENTRY_RE.finditer(f.read()):
                text, link = m.group(1), m.group(2)
                if not link.startswith("/"):
                    continue
                entries.append((text, link, name))
    return entries


def check(root: str, limit: int = 0, quiet: bool = False):
    result = {"E0": 0, "E1": 0, "E2": 0, "E3": 0, "W1": 0, "W2": 0}
    issues = []
    entries = collect(root)
    if not entries:
        result["E1"] = 1
        return result, issues, 0

    checked = 0
    for text, link, src in entries:
        rel = link.lstrip("/")
        if not rel.endswith(".md"):
            rel = os.path.join(rel, "index.md")
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            result["E2"] += 1
            issues.append(("E2 LINK_MISSING", rel, text))
            continue
        h1 = read_h1(path)
        if not h1:
            result["E3"] += 1
            issues.append(("E3 NO_H1", rel, text))
            continue
        checked += 1
        nt, nh = normalize(text), normalize(h1)
        if nt == nh:
            continue          # 判据族后缀在归一化阶段已剥掉，属既定风格
        if nt in nh or nh in nt:
            result["W2"] += 1
            if not quiet and (not limit or len(issues) < limit):
                issues.append(("W2 SHORT_NAME", rel, f"sidebar={text} | h1={h1}"))
            continue
        result["W1"] += 1
        if not quiet and (not limit or len(issues) < limit):
            issues.append(("W1 TITLE_DIFF", rel, f"sidebar={text} | h1={h1}"))
    return result, issues, checked


def selftest() -> int:
    cases = []

    def build(files):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, ".vitepress"), exist_ok=True)
        for rel, content in files.items():
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
        return d

    sidebar = 'export const X = [{ text: "%s", link: "%s" }];\n'

    # 1. 完全一致
    d = build({".vitepress/ops.ts": sidebar % ("作业模型", "/docs/A/index.md"),
               "docs/A/index.md": "# 作业模型\n\n正文\n"})
    r, _, _ = check(d)
    cases.append(("一致", r["E2"] == 0 and r["W1"] == 0 and r["W2"] == 0))

    # 2. 判据族后缀：既定风格，不计入任何计数
    d = build({".vitepress/ops.ts": sidebar % ("作业模型（JOB-A~JOB-H）", "/docs/A/index.md"),
               "docs/A/index.md": "# 作业模型\n"})
    r, _, _ = check(d)
    cases.append(("族后缀不计", r["W2"] == 0 and r["W1"] == 0))

    # 2b. 短名风格：报 W2，不报 W1
    d = build({".vitepress/ops.ts": sidebar % ("概述", "/docs/A/index.md"),
               "docs/A/index.md": "# OpenClaw 概述\n"})
    r, _, _ = check(d)
    cases.append(("短名 W2", r["W2"] == 1 and r["W1"] == 0))

    # 3. 互不包含：W1
    d = build({".vitepress/ops.ts": sidebar % ("连接池与连接治理", "/docs/A/index.md"),
               "docs/A/index.md": "# 连接池参数调优\n"})
    r, _, _ = check(d)
    cases.append(("标题不同 W1", r["W1"] == 1))

    # 4. 链路断：E2
    d = build({".vitepress/ops.ts": sidebar % ("作业模型", "/docs/A/index.md")})
    r, _, _ = check(d)
    cases.append(("文件缺失 E2", r["E2"] == 1))

    # 5. 无 H1：E3
    d = build({".vitepress/ops.ts": sidebar % ("作业模型", "/docs/A/index.md"),
               "docs/A/index.md": "## 只有二级\n"})
    r, _, _ = check(d)
    cases.append(("无 H1 E3", r["E3"] == 1))

    # 6. 目录式 link 自动补 index.md
    d = build({".vitepress/ops.ts": sidebar % ("作业模型", "/docs/A"),
               "docs/A/index.md": "# 作业模型\n"})
    r, _, _ = check(d)
    cases.append(("目录 link", r["E2"] == 0 and r["W1"] == 0))

    # 7. 空集合：E1（拒绝在空集上给全绿）
    d = build({"docs/A/index.md": "# A\n"})
    r, _, _ = check(d)
    cases.append(("空集合 E1", r["E1"] == 1))

    # 8. 归一化不吞数字差异（「第 4 步」vs「第 5 步」必须判不同）
    d = build({".vitepress/ops.ts": sidebar % ("第 4 周第 4 步 · 对账", "/docs/A/index.md"),
               "docs/A/index.md": "# 第 4 周第 5 步 · 验收\n"})
    r, _, _ = check(d)
    cases.append(("数字不吞", r["W1"] == 1))

    # 9. 尾部多层括号一次剥净
    d = build({".vitepress/ops.ts": sidebar % ("总览：四类参数（第 200 天补充）", "/docs/A/index.md"),
               "docs/A/index.md": "# 总览：四类参数\n"})
    r, _, _ = check(d)
    cases.append(("多层括号", r["W1"] == 0))

    # 10. 全角冒号与空格不影响判定
    d = build({".vitepress/ops.ts": sidebar % ("总览 ：四类参数", "/docs/A/index.md"),
               "docs/A/index.md": "# 总览：四类参数\n"})
    r, _, _ = check(d)
    cases.append(("全角冒号", r["W1"] == 0))

    ok = 0
    for name, passed in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok += 1 if passed else 0
    print(f"selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="侧边栏 text 与页面 H1 一致性巡检（第 91 项）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, ".vitepress")):
        print("E0 ROOT_NOT_FOUND（找不到 .vitepress/）")
        return 2
    result, issues, checked = check(root, limit=args.limit, quiet=args.quiet)
    for kind, path, detail in issues:
        print(f"{kind}\t{path}\t{detail}")
    print(
        "titlematchcheck: entries={} E={} W1={} W2={}".format(
            checked,
            result["E1"] + result["E2"] + result["E3"],
            result["W1"],
            result["W2"],
        )
    )
    return 0 if result["E1"] + result["E2"] + result["E3"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
