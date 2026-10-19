#!/usr/bin/env python3
"""refjudgecheck.py — 跨页判据引用一致性巡检（第 63 项）

问题：页面里大量出现「见 `PLG-C`」「见 `EVR-G`」这类跨页判据引用。判据在源页被改名、
拆页或删除后，引用仍然「长得对」，构建也不报错——读者按 ID 去目标页找，找不到那一行，
而链接文字还写着「见某条判据」。既有巡检各看一段：
  judgeidcheck     只看前缀是否撞号
  judgesumcheck    只看目录页总览表条数
  judgecovercheck  只看单页「声明 ⇄ 定义表」是否一致
没有一项看「被引用的 ID 在全库是否存在」。

判据：
  E0 ROOT_NOT_FOUND     根目录不存在
  E1 NO_PAGES           没有可扫描页面（活性判据）
  E2 UNDEFINED_REF      引用的 ID 在全库任何定义表里都不存在
  W2 DUPLICATE_DEF      同一个 ID 在多个页面的定义表里出现（重复定义，读者无法确定看哪一页）
  W1 NO_PATH            引用了别页定义的 ID，但本页没有链接到任何定义它的页面（读者找不到）

用法：
  python3 utils/audit/refjudgecheck.py [--root .] [--selftest]
"""
import argparse
import os
import re
import sys
import tempfile

ID_RE = re.compile(r"`([A-Z]{2,4}-[A-H])`")
ID_PLAIN = re.compile(r"([A-Z]{2,4}-[A-H])")
FENCE_RE = re.compile(r"^(\s{0,3})(`{3,}|~{3,})")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def iter_md(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("node_modules", ".vitepress")]
        for fn in filenames:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def strip_fences(text):
    """按 CommonMark 规则跳过围栏代码块（同字符、长度不短于开围栏才关闭）。"""
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = (m.group(2)[0], len(m.group(2)))
                continue
            out.append(line)
        else:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= fence[1]:
                fence = None
            continue
    return "\n".join(out)


def tables(lines):
    """返回表格块：每块为行列表（以 | 开头）。"""
    block, res = [], []
    for line in lines:
        if line.strip().startswith("|"):
            block.append(line)
        else:
            if block:
                res.append(block)
                block = []
    if block:
        res.append(block)
    return res


def collect(path):
    text = strip_fences(open(path, encoding="utf-8").read())
    lines = text.splitlines()
    defined, def_lines = set(), set()
    for tb in tables(lines):
        if len(tb) < 3:
            continue
        ids = []
        for row in tb[2:]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if not cells:
                continue
            head = cells[0].replace("**", "").replace("`", "").strip()
            m = re.match(r"([A-Z]{2,4}-[A-H])(?![A-Za-z0-9])", head)
            if m:
                ids.append(m.group(1))
                def_lines.add(row)
        if len(ids) >= 4:
            defined.update(ids)
    refs = set()
    for line in lines:
        if line in def_lines:
            continue
        refs.update(ID_RE.findall(line))
    links = set(LINK_RE.findall(text))
    return defined, refs, links


def norm(p):
    return os.path.normpath(p)


def resolve_links(page, links):
    base = os.path.dirname(page)
    out = set()
    for l in links:
        if l.startswith(("http://", "https://", "#", "mailto:")):
            continue
        l = l.split("#")[0]
        if not l:
            continue
        out.add(norm(os.path.join(base, l)))
    return out


def run(roots):
    if isinstance(roots, str):
        roots = [roots]
    errs, warns, pages = [], [], []
    for root in roots:
        if not os.path.isdir(root):
            errs.append("E0 ROOT_NOT_FOUND %s" % root)
            continue
        got = sorted(iter_md(root))
        if not got:
            errs.append("E1 NO_PAGES %s" % root)
        pages.extend(got)
    if not pages:
        return errs, [], 0, 0
    info = {}
    for p in pages:
        defined, refs, links = collect(p)
        info[p] = {"def": defined, "ref": refs, "targets": resolve_links(p, links)}
    owners = {}
    for p, d in info.items():
        for i in d["def"]:
            owners.setdefault(i, set()).add(norm(p))
    for i, ps in sorted(owners.items()):
        if len(ps) > 1:
            warns.append("W2 DUPLICATE_DEF %s -> %s" % (i, ", ".join(sorted(ps))))
    for p, d in info.items():
        for i in sorted(d["ref"]):
            if i not in owners:
                errs.append("E2 UNDEFINED_REF %s in %s" % (i, p))
                continue
            if i in d["def"]:
                continue
            if not (d["targets"] & owners[i]):
                warns.append("W1 NO_PATH %s in %s" % (i, p))
    return errs, warns, len(pages), len(owners)


# ---------------- selftest ----------------
SAMPLE = {
    "a/index.md": """# A

| 判据 | 内容 | 怎么验证 |
| --- | --- | --- |
| `AAA-A` | x | y |
| `AAA-B` | x | y |
| `AAA-C` | x | y |
| `AAA-D` | x | y |

引用本页 `AAA-B`，也引用别页 `[BBB](<B>)` 的 `BBB-A`。
""",
    "b/index.md": """# B

| 判据 | 内容 | 怎么验证 |
| --- | --- | --- |
| `BBB-A` | x | y |
| `BBB-B` | x | y |
| `BBB-C` | x | y |
| `BBB-D` | x | y |
""",
    "c/index.md": """# C

见 `CCC-A`（未定义）与 `BBB-B`（有定义但本页无链接）。

```markdown
| 判据 | 内容 |
| --- | --- |
| `ZZZ-A` | 围栏内不算 |
```
""",
    "d/index.md": """# D

| 判据 | 内容 | 怎么验证 |
| --- | --- | --- |
| `BBB-A` | 重复定义 | y |
| `BBB-B` | y | y |
| `BBB-C` | y | y |
| `BBB-D` | y | y |
""",
}
SAMPLE["a/index.md"] = SAMPLE["a/index.md"].replace("(<B>)", "(../b/index.md)")


def selftest():
    ok = 0
    total = 0
    with tempfile.TemporaryDirectory() as td:
        for rel, body in SAMPLE.items():
            p = os.path.join(td, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write(body)
        errs, warns, npages, nids = run(td)
        joined = "\n".join(errs + warns)

        def check(name, cond):
            nonlocal ok, total
            total += 1
            if cond:
                ok += 1
            else:
                print("FAIL", name, "|", joined[:300])

        check("pages==4", npages == 4)
        check("E2 c undef", any("E2 UNDEFINED_REF CCC-A in " in e for e in errs))
        check("fence skipped", not any("ZZZ-A" in e for e in errs))
        check("W2 duplicate", any("W2 DUPLICATE_DEF BBB-A" in w for w in warns))
        check("W1 no path", any("W1 NO_PATH BBB-B in " in w for w in warns))
        check("a links b ok", not any("W1 NO_PATH BBB-A in " in w for w in warns))
        check("no false E2 for AAA", not any("AAA-" in e for e in errs))
        check("ids counted", nids >= 7)
        # 空目录 → E1
        with tempfile.TemporaryDirectory() as empty:
            e2, _, _, _ = run(empty)
            check("E1 empty", any(x.startswith("E1 NO_PAGES") for x in e2))
        # 不存在 → E0
        e3, _, _, _ = run(os.path.join(td, "nope"))
        check("E0 missing", any(x.startswith("E0 ROOT_NOT_FOUND") for x in e3))
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    roots = [a.root] if a.root else ["docs", "project"]
    errs, warns, npages, nids = run(roots)
    for e in errs:
        print(e)
    if a.verbose:
        for w in warns:
            print(w)
    e_cnt = sum(1 for e in errs if e[:2] == "E2")
    w_cnt = len(warns)
    print("pages=%d judge_ids=%d E=%d W=%d" % (npages, nids, e_cnt, w_cnt))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
