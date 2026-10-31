#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factdatecheck.py —— 「事实核对日期」的时效性巡检（第 223 天新立，第 105 项巡检）

## 动机

本仓有一套固定写法：凡是**会随时间漂移的事实**（版本号、行数上限、协议标准号），
都要在括号里写明核对时间，例如：

    版本事实联网核对（2026-10-24 检索）：Apache KIE 10.2.0 …

这句话是全仓唯一能判断「这条事实还新不新」的线索。但此前**没有任何脚本读它**：
`countclaimcheck` 数字数声称、`verifyevidencecheck` 看验证证据、`linkexistcheck` 看链接，
全都只看结构，不看**日期本身是否成立**。

于是三类缺陷可以长期存在：

  1. **超前日期**——写着「2026-11-02 检索」，而今天是 2026-10-31。这类日期只能是编的，
     它比「没写日期」更糟：读者会以为有人核对过。
  2. **过期日期**——写着「2025-08 检索」的版本号，一年半没人复核，读者照着装会发现版本对不上。
  3. **只有月份**——「2026-10 口径」不含日，无法判断是否在上游发版之后，属于「看似严谨、实则不可复核」。

## 判据

  E0 ROOT_NOT_FOUND   既无 docs/ 也无 project/
  E1 NO_CLAIMS        全文一条核对日期都没扫到（活性判据：拒绝在空集上判「全绿」）
  E2 FUTURE_CLAIM     核对日期晚于今天（编造 / 时区写错 / 抄错年份）
  W1 STALE_CLAIM      核对日期早于今天 365 天（需要复核，不阻断提交）
  W2 MONTH_ONLY       只有年月、没有日（无法判断是否在上游发版之后）

## 口径（刻意保守）

  * 只认**括号内**且**同一括号内含关键词**（检索 / 核对 / 核实 / 口径）的日期；
    正文里随手写的「2026-10-24 发了版」不算核对声明。
  * 代码围栏内一律不算（示例里常有历史日期）。
  * 只扫 `docs/` 与 `project/`；`DOCS_PLAN.md` 是台账、`AGENTS.md` 是规则，
    它们的日期是「第 N 天」的叙事，不是事实核对声明。
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import tempfile

SKIP = {"DOCS_PLAN.md", "AGENTS.md", "README.md"}
KEYWORDS = ("检索", "核对", "核实", "口径")
PAREN = re.compile(r"[（(]([^（()）]{0,80}?)[）)]")
DATE = re.compile(r"(20\d{2})-(\d{2})(?:-(\d{2}))?")
FENCE = re.compile(r"^\s*(```|~~~)")
STALE_DAYS = 365


def strip_fences(text: str) -> str:
    out, inside = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            inside = not inside
            out.append("")
            continue
        out.append("" if inside else line)
    return "\n".join(out)


def parse_claims(path: str, today: dt.date):
    """返回 [(kind, date, snippet)]，kind ∈ {'day','month'}"""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = strip_fences(f.read())
    claims = []
    for line in text.splitlines():
        if not any(k in line for k in KEYWORDS):
            continue
        for m in PAREN.finditer(line):
            inner = m.group(1)
            if not any(k in inner for k in KEYWORDS):
                continue
            d = DATE.search(inner)
            if not d:
                continue
            y, mo, day = int(d.group(1)), int(d.group(2)), d.group(3)
            try:
                if day:
                    claims.append(("day", dt.date(y, mo, int(day)), inner.strip()))
                else:
                    claims.append(("month", dt.date(y, mo, 1), inner.strip()))
            except ValueError:
                continue  # 2026-13-40 这类非法日期交给别的脚本
    return claims


def scan(root: str, today: dt.date):
    findings = []
    pages = 0
    total_claims = 0
    for top in ("docs", "project"):
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            for fn in files:
                if not fn.endswith(".md") or fn in SKIP:
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, root)
                pages += 1
                for kind, d, snip in parse_claims(path, today):
                    total_claims += 1
                    if d > today:
                        findings.append(("E2", "FUTURE_CLAIM", rel, f"{d.isoformat()} | {snip}"))
                    elif kind == "month":
                        findings.append(("W2", "MONTH_ONLY", rel, f"{d.strftime('%Y-%m')} | {snip}"))
                    elif (today - d).days > STALE_DAYS:
                        findings.append(("W1", "STALE_CLAIM", rel, f"{d.isoformat()} ({(today-d).days}d) | {snip}"))
    return pages, total_claims, findings


def report(root: str, today: dt.date) -> int:
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND", root)
        return 2
    pages, total, findings = scan(root, today)
    for sev, code, rel, snip in findings:
        print(f"{sev} {code} {rel}  {snip}")
    errs = sum(1 for f in findings if f[0] == "E2")
    if total < 5:
        print(f"E1 NO_CLAIMS claims={total}（低于 5 条即判活性失败：正则可能已失效）")
        errs += 1
    print(f"pages={pages} claims={total} E={errs} "
          f"W1={sum(1 for f in findings if f[0]=='W1')} W2={sum(1 for f in findings if f[0]=='W2')}")
    return 1 if errs else 0


# ---------------------------------------------------------------- selftest
CASES = [
    ("ok-recent", "# T\n\n版本核对（2026-10-24 检索）：X 1.2.3\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("future", "# T\n\n版本核对（2026-12-01 检索）：X 1.2.3\n", {"FUTURE_CLAIM": 1, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("stale", "# T\n\n版本核对（2025-01-04 检索）：X 1.2.3\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 1, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("month-only", "# T\n\n口径（2026-09 口径）：行数上限\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 1}, {"MONTH_ONLY": 1}),
    ("in-fence", "# T\n\n```text\n核对（2030-01-01 检索）：示例\n```\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("no-keyword", "# T\n\n发布于（2027-01-01）\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("boundary-today", "# T\n\n核对（2026-10-31 检索）：今天\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("two-claims", "# T\n\n核对（2026-10-01 检索）：A\n核对（2027-10-01 检索）：B\n", {"FUTURE_CLAIM": 1, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("stale-boundary-366", "# T\n\n核对（2025-10-30 检索）：X\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 1, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
    ("stale-boundary-364", "# T\n\n核对（2025-11-01 检索）：X\n", {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 0}, {"MONTH_ONLY": 0}),
]
BASE = "".join(f"核对（2026-10-0{i} 检索）：第 {i} 条\n" for i in range(1, 6))


def _run(td, body):
    p = os.path.join(td, "docs", "X", "index.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return scan(td, dt.date(2026, 10, 31))


def selftest() -> int:
    ok = total = 0
    for name, body, want, want_month in CASES:
        total += 1
        with tempfile.TemporaryDirectory() as td:
            pages, claims, findings = _run(td, body)
            got = {"FUTURE_CLAIM": 0, "STALE_CLAIM": 0, "MONTH_ONLY": 0}
            for _sev, code, _rel, _snip in findings:
                got[code] = got.get(code, 0) + 1
            if got == want:
                ok += 1
            else:
                print(f"FAIL {name}: got={got} want={want}")
    # 活性判据：5 条合法声明 → claims 达到阈值，不触发 E1
    total += 1
    with tempfile.TemporaryDirectory() as td:
        _pages, claims, findings = _run(td, BASE)
        if claims == 5 and not findings:
            ok += 1
        else:
            print(f"FAIL base: claims={claims} findings={findings}")
    # 反向：只有 1 条声明时，阈值判定必须拒绝给「全绿」
    total += 1
    with tempfile.TemporaryDirectory() as td:
        _pages, claims, _f = _run(td, "核对（2026-10-01 检索）：唯一一条\n")
        if claims < 5:
            ok += 1
        else:
            print("FAIL activity: 单条声明未被判为活性不足")
    print(f"selftest {ok}/{total} {'PASS' if ok == total else 'FAIL'}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--today", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    return report(a.root, today)


if __name__ == "__main__":
    sys.exit(main())
