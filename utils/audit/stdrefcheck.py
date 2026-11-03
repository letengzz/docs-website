#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stdrefcheck.py —— 标准与法规文号写法一致性巡检（第 245 天新立，第一百二十七项巡检）

## 动机

本库每一页的末尾都有「参考资料」，里面大量引用标准与法规文号：`GB/T 18184—2025`、
`ISO 8601-1:2019`、`RFC 5545`、`财会〔2008〕7 号`。这些文号是**读者唯一能拿去做二次核对的坐标**——
写错一个字符，读者就检索不到，引用就失去意义。

它们有一个只在**跨页对比时**才暴露的失败模式：**同一个标准在不同页面写成不同样子**。

  * `GB/T 18184—2025`（一字线）与 `GB/T 18184-2025`（半角连字符）——前者是国标写法，后者是随手敲的；
  * `GB/T 18184` 与 `GB/T18184`——少一个空格，看起来一样，检索时是两个词；
  * `ISO 8601` 与 `ISO8601`——同上。

现有全部巡检都看不见这类缺陷：

  * `linkexistcheck` / `reflinkformcheck`  只看链接；
  * `refcheck` / `refjudgecheck`           只看「参考资料是不是在文末」「条数够不够」；
  * `factdatecheck`                        只看日期类事实的新鲜度；
  * `tablecheck` / `fencecheck`            只看结构。

也就是说：**「参考资料在不在」有人管，「参考资料里的文号写没写对」没人管**。

## 判据

  E0 ROOT_NOT_FOUND   既无 docs/ 也无 project/
  E1 NO_CLAIMS        一条文号都没抽到（活性判据：拒绝在空集上判「全绿」）
  E2 BAD_SPACING      前缀与编号之间缺空格：`GB/T18184`、`ISO8601`、`RFC5545`、`IEEE802.11`
  E3 BAD_DASH         国标年份分隔符不是一字线：`GB/T 18184-2025`、`GB 50016–2014`
  E4 MIXED_FORM       同一文号（族 + 编号 + 年号）在库内出现 ≥2 种写法
  W1 GB_NO_YEAR       国标引用缺年号，无法判定版本
  W2 ISO_NO_YEAR      国际标准引用缺年号（允许，但应在文末统一说明「未注年份指现行版」）
  W3 UNKNOWN_PREFIX   形如「大写字母 + 编号」但前缀不在白名单内（疑似自造标准号）

## 口径（刻意保守）

  * 只扫 `docs/` 与 `project/` 下的 `*.md`；`DOCS_PLAN.md` / `AGENTS.md` 是台账。
  * **代码围栏内不扫**：示例里的 `RFC 7231` 是代码，不是引用。
  * **行内代码先抹成等长占位**：`` `GB/T 18184` `` 是在讲这个写法，不是在引用它。
  * **表格行照扫**：分工表、对照表里的文号同样是引用。
  * **E3 只判国标族**：ISO 用 `:` 分部分、用 `-` 连年份是允许的（`ISO 8601-1:2019`），
    把它也判成「分隔符错」会整类假阳性。
  * **E4 按「族 + 编号 + 年号」聚合**，页面上报一次，附两种写法的样例与次数——
    逐处上报会把一个格式问题刷成几百行，反而没人修。
  * **W3 不给 `E`**：`AES 256`、`HTTP 404` 这类「字母 + 数字」是术语不是标准号，
    白名单外一律降级为提示，由人判断。

## 用法

    python3 utils/audit/stdrefcheck.py            # 全库
    python3 utils/audit/stdrefcheck.py --selftest # 自测（12 例）
    python3 utils/audit/stdrefcheck.py --root docs/Backend
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from collections import defaultdict

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE = re.compile(r"``[^`\n]*``|`[^`\n]*`")

# 族 → 白名单前缀
FAMILIES = {
    "GB": ["GB/T", "GB/Z", "GB"],
    "INTL": ["ISO/IEC", "ISO", "IEC", "IEEE", "ANSI", "ITU-T"],
}
KNOWN = {p for v in FAMILIES.values() for p in v} | {"RFC"}

# GB 族：GB/T 18184—2025 / GB 50016-2014 / GB/T 18184
GB_RE = re.compile(r"\b(GB/T|GB/Z|GB)\s*(\d{2,5}(?:\.\d+)?)\s*([—–\-－])?\s*(\d{4})?")
# 国际：ISO 8601-1:2019 / ISO/IEC 27001 / IEEE 802.11 / RFC 5545
INTL_RE = re.compile(r"\b(ISO/IEC|ISO|IEC|IEEE|ANSI|ITU-T)\s*(\d{2,5}(?:[-.]\d{1,3})?)(?::(\d{4}))?")
RFC_RE = re.compile(r"\bRFC\s*(\d{3,5})\b")
# 法规文号：财会〔2008〕7 号 / 国家税务总局公告〔2018〕28 号 / 商务部令 2006 年第 18 号
DOC_RE = re.compile(r"(财会|银发|国税发|商务部令|国务院令)\s*〔(\d{4})〕\s*(第\s*)?(\d{1,4})\s*(号)?")

# E2：前缀紧跟数字（缺空格）
BAD_SPACE_RE = re.compile(r"(?<![A-Za-z])(GB/T|GB/Z|GB|ISO/IEC|ISO|IEC|IEEE|ANSI|ITU-T|RFC)(\d)")
# W3：大写字母（2~5）紧跟数字，且不是已知前缀
MAYBE_STD_RE = re.compile(r"\b([A-Z][A-Z/]{1,5})\s?(\d{3,5})\b")


def strip_code(text: str) -> str:
    """去掉围栏块，行内代码抹成等长占位（保留行号）。"""
    out, in_fence = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(INLINE.sub(lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


def collect(root: str):
    """返回 [(relpath, lineno, family, number, year, surface, style)]"""
    claims = []
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, _dirs, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, root)
                try:
                    raw = open(p, encoding="utf-8").read()
                except UnicodeDecodeError:
                    continue
                body = strip_code(raw)
                for i, line in enumerate(body.split("\n"), 1):
                    for m in GB_RE.finditer(line):
                        pre, num, dash, year = m.group(1), m.group(2), m.group(3), m.group(4)
                        if year is None and dash is not None:
                            # 「GB/T 18184-」这种断掉的写法不算
                            continue
                        claims.append((rel, i, "GB", num, year, m.group(0),
                                       (pre, dash or "", bool(re.search(pre + r"\s", line)))))
                    for m in INTL_RE.finditer(line):
                        pre, num, year = m.group(1), m.group(2), m.group(3)
                        claims.append((rel, i, "INTL", num, year, m.group(0),
                                       (pre, ":", True)))
                    for m in RFC_RE.finditer(line):
                        claims.append((rel, i, "RFC", m.group(1), None, m.group(0), ("RFC", "", True)))
                    for m in DOC_RE.finditer(line):
                        claims.append((rel, i, "DOC", m.group(1) + m.group(4), m.group(2),
                                       m.group(0), (m.group(1), "", True)))
    return claims


def scan(root: str):
    pages = 0
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if os.path.isdir(d):
            for dirpath, _dirs, files in os.walk(d):
                pages += sum(1 for f in files if f.endswith(".md"))
    claims = collect(root)
    errors, warns = [], []

    # E2 / E3：逐处
    for rel, ln, fam, num, year, surf, style in claims:
        if fam == "GB" and style[1] in ("-", "–", "－"):
            errors.append(("E3", "BAD_DASH", rel, ln, surf))
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, _dirs, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, root)
                try:
                    body = strip_code(open(p, encoding="utf-8").read())
                except UnicodeDecodeError:
                    continue
                for i, line in enumerate(body.split("\n"), 1):
                    for m in BAD_SPACE_RE.finditer(line):
                        errors.append(("E2", "BAD_SPACING", rel, i, m.group(0)))
                    for m in MAYBE_STD_RE.finditer(line):
                        pre = m.group(1)
                        if pre not in KNOWN and not pre.isdigit() and len(pre) >= 2:
                            # 排除常见非标准词
                            if pre in ("HTTP", "HTTPS", "AES", "SHA", "TCP", "UDP", "TLS", "SSL",
                                       "UUID", "UTF", "CPU", "GPU", "RAM", "SSD", "API", "SQL",
                                       "PDF", "PNG", "SVG", "JPG", "MP", "GBPS", "MBPS", "QPS",
                                       "P99", "P95", "P50", "TP99", "V1", "V2", "V3", "L1", "L2",
                                       "L3", "F1", "B2", "C1", "N1", "E1", "W1", "A1", "S1",
                                       "T1", "M1", "P1", "R1", "K1", "D1"):
                                continue
                            warns.append(("W3", "UNKNOWN_PREFIX", rel, i, m.group(0)))

    bad_lines = {(e[2], e[3]) for e in errors if e[0] == "E2"}

    # E4：同一文号多种写法
    groups = defaultdict(list)
    for rel, ln, fam, num, year, surf, style in claims:
        if fam not in ("GB", "INTL"):
            continue
        style_key = (style[0], style[1], style[2])
        groups[(fam, style[0], num, year)].append((surf, style_key, rel, ln))
    for key, rows in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3] or '')):
        forms = {r[1] for r in rows}
        # 只差空格的那一类已由 E2 覆盖，不重复报
        if len(forms) >= 2 and not all((r[2], r[3]) in bad_lines for r in rows):
            samples = " | ".join(sorted({r[0] for r in rows})[:3])
            errors.append(("E4", "MIXED_FORM", rows[0][2], rows[0][3],
                           f"{key[1]} {key[2]} ({key[3] or '无年号'}) 出现 {len(forms)} 种写法：{samples}"))

    # W1 / W2：缺年号（按文号去重）；同一行已报 E2 的不再报年度缺失
    seen_gb, seen_intl = set(), set()
    for rel, ln, fam, num, year, surf, style in claims:
        if (rel, ln) in bad_lines:
            continue
        if fam == "GB" and not year and num not in seen_gb:
            seen_gb.add(num)
            warns.append(("W1", "GB_NO_YEAR", rel, ln, surf))
        if fam == "INTL" and not year and num not in seen_intl:
            seen_intl.add(num)
            warns.append(("W2", "ISO_NO_YEAR", rel, ln, surf))

    return pages, claims, errors, warns


def report(root: str) -> int:
    if not (os.path.isdir(os.path.join(root, "docs")) or os.path.isdir(os.path.join(root, "project"))):
        print("E0 ROOT_NOT_FOUND", root)
        return 1
    pages, claims, errors, warns = scan(root)
    if not claims:
        print("E1 NO_CLAIMS 一条文号都没抽到，拒绝判定", root)
        return 1
    for code, kind, rel, ln, surf in errors:
        print(f"{code} {kind:14s} {rel}:{ln}  {surf}")
    for code, kind, rel, ln, surf in warns:
        print(f"{code} {kind:14s} {rel}:{ln}  {surf}")
    e = len(errors)
    w = len(warns)
    print(f"\npages={pages} claims={len(claims)} E={e} W={w}")
    return 0 if e == 0 else 2


# ---------------- 自测 ----------------
CASES = [
    # (内容, 期望出现的码)
    ("参考资料：GB/T 18184—2025《商业自动化术语》。", set()),
    ("参考资料：GB/T 18184-2025《商业自动化术语》。", {"E3"}),
    ("参考资料：GB/T18184—2025《商业自动化术语》。", {"E2"}),
    ("参考资料：ISO8601 时间表示。", {"E2"}),
    ("参考资料：ISO 8601-1:2019 时间表示。", set()),
    ("参考资料：RFC5545 日历。", {"E2"}),
    ("参考资料：GB/T 18184《商业自动化术语》。", {"W1"}),
    ("参考资料：ISO 8601 时间表示。", {"W2"}),
    ("```text\nGB/T18184-2025\n```", set()),
    ("写法 ``GB/T18184`` 是错的。", set()),
    ("这里的 AES 256 与 HTTP 404 不是标准号。", set()),
    ("参见 XKCD 1234 的说明。", {"W3"}),
]


def selftest() -> int:
    ok = 0
    for idx, (body, expect) in enumerate(CASES, 1):
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "docs", "T"))
        open(os.path.join(tmp, "docs", "T", "index.md"), "w", encoding="utf-8").write(body + "\n")
        _pages, _claims, errors, warns = scan(tmp)
        got = {c[0] for c in errors} | {c[0] for c in warns}
        if got == expect:
            ok += 1
        else:
            print(f"[FAIL] 例 {idx}: 期望 {sorted(expect) or '无'} 实际 {sorted(got) or '无'}  内容={body[:40]!r}")
    print(f"selftest {ok}/{len(CASES)}")
    return 0 if ok == len(CASES) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    sys.exit(report(a.root))


if __name__ == "__main__":
    main()
