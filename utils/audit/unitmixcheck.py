#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""unitmixcheck.py — 「同一个数换了量纲」巡检 · 第 104 项

为什么立这一项
--------------
本库有一整族与「数字」有关的巡检，但它们只看**形态**：

* `countclaimcheck` —— 「十页 / 80 条」这类计数与实物是否相符；
* `nearthdupcheck`  —— 两页里有没有近乎逐字重复的句子；
* `verifyevidencecheck` —— 验证节里有没有命令与期望输出。

没有一道门看**单位**。而本库最贵的一次口径事故恰好出在单位上：`LoyaltyProgram`
的目录页写「负债口径差 21.31 个百分点（约 **256 万元**）」，按同页自己的口径
（1,200 万积分、100 分 = 1 元）算出来是 **2,557,500 分 ≈ 2.56 万元**——差 100 倍。
同一张 SVG 里还并排写着「59.31% → 负债 **711.7 万元**」与「71,172 元」。三个数字
各自都长得像真的，读者按任何一个都能算出「合理」的结论。

这类缺陷的形态非常固定：**同一个数，换了一个量纲单位**。它不违反任何语法、不
触发任何构建错误，只在读者拿计算器复核时才暴露。

判据
----
E0 ROOT_NOT_FOUND       仓库根既没有 docs/ 也没有 project/
E1 NO_PAGES             一个 .md 都没扫到（活性判据）
E2 NO_UNITS             一条「数字 + 金额单位」都没解析到（活性判据：正则坏了也会全绿）
W1 SAME_MANTISSA        同一页里**同一个尾数**配了量纲不同的金额单位（如 `256 万元` 与 `256 元`）
W2 YUAN_FEN_MIX         同一页里「元」与「分」两种金额单位并存（口径混用，需人工确认）
W3 WAN_NO_UNIT          「数字 + 万」后面没跟「元」（口语写法，只计数不判错）
N1 MONEY_MENTIONS       金额提及总数（计数）
N2 MONEY_PAGES          含金额提及的页面数（计数）

口径（四条，全部来自真实语料）
------------------------------
1. **围栏与行内代码里的金额不算**：示例代码里的 `price = 199 元` 是演示，不是口径。
   这与第 98 项（配图来源）的处理一致：先剥代码区，再判正文。
2. **只判「同尾数不同量纲」**，不判「同页出现多种单位」——本库大量页面同时用「元」
   与「万元」来描述不同量级的事，那是正常写作。判 W1 时要求尾数**完全相等**
   （去掉千分位后），把误报压到可人工复核的量级。
3. **W2 不判错、只判需确认**：`分` 在本库既可能是「一分钱」，也可能是「得分 / 分钟」，
   正则只认「数字 + 分」且**前面不是「得」「积」「评」**的形态。
4. **比值只认 10² / 10⁴ / 10⁸**：量纲错位几乎总是整百整万，比值不是这三个数的一律
   不报——否则「3,000 元」与「3 万元」会被误判。

用法
----
    python3 utils/audit/unitmixcheck.py            # 扫全库
    python3 utils/audit/unitmixcheck.py --root DIR # 扫指定根（自测与回归用）
    python3 utils/audit/unitmixcheck.py --selftest # 跑内建用例
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

MONEY_RE = re.compile(r"(?<![\d.])([\d][\d,]*(?:\.\d+)?)\s*(亿元|万元|亿|万|元|分)(?![位素钟])")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

# 单位 → 「分」为基准的倍数
FACTOR = {"亿元": 10 ** 10, "亿": 10 ** 10, "万元": 10 ** 6, "万": 10 ** 6, "元": 100, "分": 1}
SCALES = (100, 10000, 100000000)


def _strip_code(text):
    """把围栏块与行内代码替换成等长空白，保持行号不变。"""
    mask, _blocks, _unclosed = fenceutil.scan(text)
    lines = text.split("\n")
    for i in range(len(lines)):
        if i in mask:
            lines[i] = ""
        else:
            lines[i] = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), lines[i])
    return "\n".join(lines)


LABEL_RE = re.compile(r"([\u4e00-\u9fa5A-Za-z]{2,8})\s*$")
STOP = {"达到", "约为", "大约", "其中", "合计", "共计", "总共", "至少", "最多", "仅有", "只剩"}


def _label(line, cut):
    """取金额前紧邻的 2~8 个中文/字母作为「指标名」，取不到返回 None。"""
    head = line[:cut].rstrip(" 　 \t")
    head = re.sub(r"[，,。；;：:、=＝+\-*/（(\[\]）\"“”]+$", "", head)
    m = LABEL_RE.search(head)
    if not m:
        return None
    lab = m.group(1)
    if lab in STOP or len(lab) < 2:
        return None
    # 量词 / 比较词 / 单位字出现在标签里，说明取到的不是「指标名」
    if re.search(r"[份个张条次天年月日差元万亿%]", lab):
        return None
    return lab


def analyse(text):
    """返回 (mentions, w1, w2, w3)。

    mentions: [(lineno, mantissa, unit, value_fen, label)]
    w1: [(mantissa, units, [lineno...])]      同尾数、量纲差 10^4 / 10^8
    w2: bool                                  元与分并存
    w3: [(label, ratio, [lineno...])]         同一指标名下的金额相差 >= 50 倍
    """
    body = _strip_code(text)
    mentions = []
    for i, line in enumerate(body.split("\n"), start=1):
        for m in MONEY_RE.finditer(line):
            if m.group(2) == "分":
                head2 = line[max(0, m.start() - 2):m.start()]
                if any(ch in head2 for ch in "得积评工满"):
                    continue
            mant = m.group(1).replace(",", "")
            try:
                val = float(mant)
            except ValueError:
                continue
            mentions.append((i, mant, m.group(2), val * FACTOR[m.group(2)], _label(line, m.start())))

    by_mant = {}
    for ln, mant, unit, fen, _lab in mentions:
        by_mant.setdefault(mant, []).append((ln, unit, fen))

    w1 = []
    for mant, rows in by_mant.items():
        units = {r[1] for r in rows}
        if len(units) < 2:
            continue
        vals = sorted({round(r[2], 6) for r in rows})
        hit = any(
            vals[i] and round(vals[j] / vals[i]) in (10000, 100000000)
            for i in range(len(vals)) for j in range(i + 1, len(vals))
        )
        if hit:
            w1.append((mant, sorted(units), [r[0] for r in rows]))

    units_all = {m[2] for m in mentions}
    w2 = "元" in units_all and "分" in units_all

    by_label = {}
    for ln, _mant, _unit, fen, lab in mentions:
        if lab:
            by_label.setdefault(lab, []).append((ln, fen))
    # 标签按「最短后缀」归并：`负债` 与 `另一处写负债` 视为同一个指标
    labels = sorted(by_label, key=len)
    canon = {}
    for lab in labels:
        for short in labels:
            if short != lab and len(short) < len(lab) and lab.endswith(short):
                canon[lab] = short
                break
        else:
            canon[lab] = lab
    merged = {}
    for lab, rows in by_label.items():
        merged.setdefault(canon[lab], []).extend(rows)
    by_label = merged
    w3 = []
    for lab, rows in by_label.items():
        lines = {r[0] for r in rows}
        if len(lines) < 2:
            continue
        vals = [r[1] for r in rows if r[1] > 0]
        if len(vals) < 2:
            continue
        ratio = max(vals) / min(vals)
        if ratio >= 50:
            w3.append((lab, round(ratio), sorted(lines)))
    return mentions, w1, w2, w3


def load_pages(root):
    pages = []
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, _dirnames, filenames in os.walk(d):
            for fn in filenames:
                if fn.endswith(".md"):
                    pages.append(os.path.join(dirpath, fn))
    return sorted(pages)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    ap.add_argument("--limit", type=int, default=25, help="最多打印多少条明细（0 表示不限）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    if not (os.path.isdir(os.path.join(root, "docs")) or os.path.isdir(os.path.join(root, "project"))):
        print(f"E0 ROOT_NOT_FOUND  {root}")
        return 1
    pages = load_pages(root)
    if not pages:
        print(f"E1 NO_PAGES  {root}")
        return 1

    total = money_pages = w1n = w2n = w3n = 0
    detail1, detail2 = [], []
    for path in pages:
        text = open(path, encoding="utf-8", errors="replace").read()
        mentions, w1, w2, w3 = analyse(text)
        total += len(mentions)
        money_pages += 1 if mentions else 0
        w3n += len(w3)
        for lab, ratio, lns in w3:
            detail2.append(f"W3 LABEL_RATIO    {os.path.relpath(path, root)}  ->  {lab} 差 {ratio} 倍  行 {lns[:4]}")
        for mant, units, lns in w1:
            w1n += 1
            detail1.append(f"W1 SAME_MANTISSA  {os.path.relpath(path, root)}  ->  {mant} {'/'.join(units)}  行 {lns[:4]}")
        if w2:
            w2n += 1
            detail2.append(f"W2 YUAN_FEN_MIX   {os.path.relpath(path, root)}")

    if total == 0:
        print(f"E2 NO_UNITS  pages={len(pages)}")
        return 1

    show = (lambda xs: xs) if args.limit == 0 else (lambda xs: xs[: args.limit])
    for line in show(detail1) + show(detail2):
        print(line)
    print(
        f"pages={len(pages)} money_pages={money_pages} mentions={total} "
        f"E=0 W1={w1n} W2={w2n} W3={w3n}"
    )
    return 0 if w1n == 0 else 2


def _make(d, files):
    for rel, content in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)


def selftest():
    cases = []

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n损失约 2.56 万元。\n"})
    cases.append(("干净页（单一单位）", d, (0, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n口径差约 256 万元，另一处写 256 元。\n"})
    cases.append(("同尾数量纲错位（W1）", d, (1, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n金额 12,000 元；单位精确到 1 分。\n"})
    cases.append(("元与分并存（W2）", d, (0, 1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n```sql\n-- 示例：256 万元 与 256 元\nSELECT 1;\n```\n"})
    cases.append(("围栏里的金额不算", d, (0, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n示例写作 `256 万元` 与 `256 元`。\n"})
    cases.append(("行内代码里的金额不算", d, (0, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n本月 300 万元，上月 3 万元。\n"})
    cases.append(("尾数不同不报（比值虽为 100）", d, (0, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n他得了 98 分。\n"})
    cases.append(("「得分」不是金额", d, (0, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n规模约 3 万，增长 2 亿。\n"})
    cases.append(("口语单位不误报", d, (0, 0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n负债 711.7 万元。\n\n另一处写负债 71,172 元。\n"})
    cases.append(("同指标差 100 倍（W3）", d, (0, 0, 1)))

    d = tempfile.mkdtemp()
    _make(d, {"project/Complete/P/index.md": "# 项目\n\n成本 1.8 万元，报价 1.8 元。\n"})
    cases.append(("project 目录也扫（W1）", d, (1, 0, 0)))

    ok = 0
    for name, root, expect in cases:
        pages = load_pages(root)
        w1 = w2 = w3 = 0
        for p in pages:
            _m, a, b, c = analyse(open(p, encoding="utf-8").read())
            w1 += len(a)
            w2 += 1 if b else 0
            w3 += len(c)
        got = (w1, w2, w3)
        if got == expect:
            ok += 1
        else:
            print(f"FAIL {name}: got={got} want={expect}")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
