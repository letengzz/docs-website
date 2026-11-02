#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sectionxrefcheck.py —— 「页内节号引用指向的那一节还在不在」巡检（第 237 天新立，第一百一十九项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

本仓关于「页面结构」的门已经有五道，各看一层：

  * `headingcheck.py`       —— 每页只有一个 H1，且与侧边栏一致；
  * `levelskipcheck.py`     —— 标题层级不跳级；
  * `sectionnumcheck.py`    —— 编号小节是否连续（一、二、三……）；
  * `sectionordercheck.py`  —— 「验证方式」是否在「参考资料」之前；
  * `emptysectioncheck.py`  —— 有没有只有标题、没有正文的空小节。

五道全绿，仍然可以写出这样一句话：

    这个口径的推导见第四节。

而这一页只有三节——第四节在两个月前的内容合并里被删掉了。渲染器不会报错
（它就是一段普通文字），链接检查也扫不到（它没有链接），期望值齐全，构建通过。
读者按提示往右看，发现右边只有「参考资料」。**代价不是不好看，是读者被指向了
一个不存在的地方，然后开始怀疑整篇文档。**

同类缺陷已经收过两次：第 116 项 `cmdtargetcheck` 管「命令指向的脚本还在不在」，
第 101 项 `ghostgatecheck` 管「注释里提到的兄弟脚本还在不在」。这一项补的是
**正文里的节号引用**。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND        仓库根不存在（活性判据）
  E1 NO_PAGES              一页都没扫到（活性判据：拒绝在空集上给全绿）
  E2 XREF_OUT_OF_RANGE     引用的节号大于本页实有编号小节数
  E3 XREF_ZERO             引用「第 0 节」（编号从 1 开始，0 一定是笔误）
  W1 XREF_KEYWORD_MISS     引用带了关键词（`代码` 或「引号」包裹），目标节标题不含它
  W2 NO_NUMBERED_SECTIONS  页内出现节号引用，但本页的小节没有编号（无法核对）
  N1 PAGES / N2 REFS / N3 NUMBERED  只计数

## 口径（四条，都是被真实语料逼出来的）

1. **只认 `## 一、` 与 `## 1.` 两种编号小节**。库内小节标题的编号写法就这两种；
   把 `###` 也算进来会让「第 8 节」对上一个三级小节，判据就失去意义。
2. **代码围栏与行内代码整体抹掉再扫**。教程里大量出现「第 3 节」作为示例文本
   （如本文件），不抹掉会立刻造出上百条假阳性。抹除时按字符替换为空格，
   行号与列位置不变，报出来的行号仍然可信。
3. **只判「第 N 节」这一种句式**，不判「上文/下文/上一节」——那三种没有可核对的
   锚点，判了也只能猜。宁可漏，不可误报：**会大面积报红的门禁第二天就会被关掉**。
4. **W1 只在关键词被显式包裹时判**（`` `xxx` `` 或「xxx」）。裸文本「见第三节时钟
   口径」里的「时钟口径」可能只是行文，不是标题；把它当关键词会误报。

## 纪律

只读、不改文档。本项只负责把「哪个文件、第几行、引用了第几节、实有几节」列出来。
"""

import argparse
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCAN_DIRS = ("docs", "project")
FENCE_OPEN = re.compile(r"^(\s*)(```+|~~~+)\s*([\w+-]*)")   # 开围栏：允许带语言与 [路径] 标题
FENCE_CLOSE = re.compile(r"^(\s*)(```+|~~~+)\s*$")          # 闭围栏：反引号后不允许有内容
LINKSPAN = re.compile(r"!?\[[^\]\n]*\]\([^)\n]*\)")     # 整段 markdown 链接（含链接文字）
H2_NUM_CN = re.compile(r"^##\s+([一二三四五六七八九十]+)、\s*(.+?)\s*$")
H2_NUM_AR = re.compile(r"^##\s+(\d{1,2})[.、]\s*(.+?)\s*$")
XREF = re.compile(r"第\s*([一二三四五六七八九十]+|\d{1,2})\s*节")
KEYWORD = re.compile(r"第\s*(?:[一二三四五六七八九十]+|\d{1,2})\s*节\s*(?:[（(]\s*[`「]([^`」]{2,12})[`」]\s*[）)]|[`「]([^`」]{2,12})[`」])")

CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9}


def cn2int(s):
    """中文数字 / 阿拉伯数字 → int；认不出返回 None"""
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if "十" in s:
        head, _, tail = s.partition("十")
        tens = CN_DIGIT.get(head, 1) if head else 1
        ones = CN_DIGIT.get(tail, 0) if tail else 0
        return tens * 10 + ones
    return CN_DIGIT.get(s)


def strip_code(text):
    """返回 (clean, mask)：

    clean —— 围栏与行内代码、整段 markdown 链接都替换成等长空白；
    mask  —— 与 clean 等长，'x' 表示「可判的正文」，' ' 表示代码或链接。

    为什么要抹掉整段链接：跨页引用写成 `见[自动化页第 9 节](../Automation/index.md)`
    时，「第 9 节」指的是**另一个页面**的第 9 节，拿本页的节数去判必然误报。
    """
    clean, mask, inside = [], [], False
    for line in text.split("\n"):
        if not inside:
            if FENCE_OPEN.match(line):
                inside = True
                clean.append(" " * len(line))
                mask.append(" " * len(line))
                continue
            out, span = list(line), ["x"] * len(line)
            for mm in re.finditer(r"`[^`\n]*`", line):
                for k in range(mm.start(), mm.end()):
                    out[k], span[k] = " ", " "
            for mm in LINKSPAN.finditer(line):
                for k in range(mm.start(), mm.end()):
                    out[k], span[k] = " ", " "
            clean.append("".join(out))
            mask.append("".join(span))
            continue
        if FENCE_CLOSE.match(line):
            inside = False
        clean.append(" " * len(line))
        mask.append(" " * len(line))
    return "\n".join(clean), "\n".join(mask)


def numbered_sections(text):
    """返回 {序号: 标题}；两种编号写法取并集，重复序号取第一次出现"""
    found = {}
    for line in text.split("\n"):
        m = H2_NUM_CN.match(line) or H2_NUM_AR.match(line)
        if not m:
            continue
        n = cn2int(m.group(1))
        if n is None:
            continue
        found.setdefault(n, m.group(2).strip())
    return found


def check_page(text):
    """返回 (issues, counters)；issues = [(code, line, detail)]"""
    clean, mask = strip_code(text)
    secs = numbered_sections(clean)
    total = max(secs) if secs else 0
    issues, n_ref = [], 0
    clean_lines, mask_lines = clean.split("\n"), mask.split("\n")
    for idx, line in enumerate(clean_lines):
        if "第" not in line or "节" not in line:
            continue
        mrow = mask_lines[idx] if idx < len(mask_lines) else ""
        origin = text.split("\n")[idx]
        link_ends = [mm.end() for mm in LINKSPAN.finditer(origin)]
        for m in XREF.finditer(line):
            if m.start() < len(mrow) and mrow[m.start()] == " ":
                continue            # 落在代码里，不判
            # 跨页引用：`见[推送章节](../Push/index.md)第八节` —— 节号属于另一个页面
            if any(0 <= m.start() - e <= 40 for e in link_ends):
                continue
            # 限定词在发话人一侧：「该页」「AGENTS.md」「根目录」，或紧跟着一个链接
            head = line[max(0, m.start() - 60):m.start()]
            if re.search(r"(该页|页第|那册|一文|根目录|AGENTS\.md|[A-Za-z0-9_-]\.md)", head):
                continue
            if any(0 <= abs(e - m.start()) <= 90 for e in link_ends):
                continue
            n_ref += 1
            raw = m.group(1)
            n = cn2int(raw)
            if n is None:
                continue
            if n == 0:
                issues.append(("E3", idx + 1, "引用了「第 %s 节」：编号从 1 开始" % raw))
                continue
            if not secs:
                issues.append(("W2", idx + 1, "本页无编号小节，无法核对「第 %s 节」" % raw))
                continue
            if n > total:
                issues.append(("E2", idx + 1, "引用第 %d 节，本页只有 %d 节" % (n, total)))
                continue
            # 关键词可能在行内代码里：到原文里取，并用原始 mask 判它是不是代码
            kw = KEYWORD.search(origin)
            if kw:
                word = (kw.group(1) or kw.group(2) or "").strip()
                title = secs.get(n, "")
                if word and word not in title:
                    issues.append(("W1", idx + 1,
                                   "第 %d 节标题是「%s」，引用处写的是「%s」" % (n, title, word)))
    return issues, (1 if secs else 0, n_ref)


def list_pages(root):
    out = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            if "node_modules" in dirpath or "/assets" in dirpath:
                continue
            for fn in filenames:
                if fn.endswith(".md"):
                    out.append(os.path.join(dirpath, fn))
    return sorted(out)


def scan(root, verbose=False):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND: %s" % root)
        return 1
    tally = {"E2": 0, "E3": 0, "W1": 0, "W2": 0}
    pages = n_numbered = n_refs = 0
    for path in list_pages(root):
        text = open(path, encoding="utf-8").read()
        issues, (numbered, refs) = check_page(text)
        if not refs:
            continue
        pages += 1
        n_numbered += numbered
        n_refs += refs
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        for code, lineno, detail in issues:
            tally[code] += 1
            if code.startswith("E") or verbose:
                print("%s %s:%d  %s" % (code, rel, lineno, detail))
    if pages == 0:
        print("E1 NO_PAGES: 根 %s 下一处节号引用都没有扫到" % root)
        return 1
    e = tally["E2"] + tally["E3"]
    print("pages=%d numbered=%d refs=%d E=%d W1=%d W2=%d"
          % (pages, n_numbered, n_refs, e, tally["W1"], tally["W2"]))
    return 0 if e == 0 else 1


def selftest():
    good = "# 标题\n\n## 一、甲\n\n见第二节的说明。\n\n## 二、乙\n\n正文。\n"
    bad_range = "# 标题\n\n## 一、甲\n\n见第四节。\n\n## 二、乙\n\n正文。\n"
    zero = "# 标题\n\n## 一、甲\n\n见第 0 节。\n"
    unnumbered = "# 标题\n\n## 甲\n\n见第二节。\n"
    kw_ok = "# 标题\n\n## 一、甲\n\n## 二、时钟口径\n\n见第二节（`时钟口径`）。\n"
    kw_bad = "# 标题\n\n## 一、甲\n\n## 二、乙\n\n见第二节（`时钟口径`）。\n"
    in_fence = "# 标题\n\n## 一、甲\n\n```text\n见第九节\n```\n"
    in_code = "# 标题\n\n## 一、甲\n\n`见第九节` 是示例。\n"
    cn_11 = "# 标题\n\n" + "".join("## %s、第%s节\n\n正文。\n\n" % (c, c)
                                    for c in ("一", "二", "三", "四", "五", "六",
                                              "七", "八", "九", "十", "十一")) + "见第十一节。\n"
    cn_11_bad = "# 标题\n\n" + "".join("## %s、节\n" % c for c in ("一", "二", "三")) + "见第十一节。\n"
    ar_mix = "# 标题\n\n## 1. 甲\n\n## 2. 乙\n\n见第 2 节。\n"
    no_ref = "# 标题\n\n## 一、甲\n\n没有引用。\n"

    cases = [
        ("正常引用通过", good, set()),
        ("越界报 E2", bad_range, {"E2"}),
        ("第 0 节报 E3", zero, {"E3"}),
        ("无编号小节报 W2", unnumbered, {"W2"}),
        ("关键词匹配通过", kw_ok, set()),
        ("关键词不匹配报 W1", kw_bad, {"W1"}),
        ("围栏内不判", in_fence, set()),
        ("行内代码不判", in_code, set()),
        ("第十一节可解析", cn_11, set()),
        ("只到第三节时第十一节越界", cn_11_bad, {"E2"}),
        ("阿拉伯编号同样可判", ar_mix, set()),
        ("无引用页不计入", no_ref, None),
    ]
    ok = 0
    for i, (name, text, expect) in enumerate(cases, 1):
        issues, (numbered, refs) = check_page(text)
        got = {c for c, _, _ in issues}
        if expect is None:
            passed = refs == 0
        else:
            passed = got == expect
        ok += 1 if passed else 0
        print("%s %2d %s -> %s" % ("PASS" if passed else "FAIL", i, name,
                                   sorted(got) if got else "无告警"))
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description="页内节号引用巡检")
    ap.add_argument("root", nargs="?", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return scan(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
