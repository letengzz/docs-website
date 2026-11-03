#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""promiserefcheck.py —— 「正文指代 ⇄ 后方实物」巡检（第 243 天新立，第 125 项巡检）

## 动机

本库写文档有一个固定句式：先给结论，再说「如下表」「见下图」。这个句式很好用，但它有一个
**只在渲染后才会暴露**的失败模式：句子说了「下面这张表」，而下面根本没有表——可能是在编辑时
被删掉、可能是从别的页面复制过来忘了改、也可能是表格被误写成了代码块。

这一类缺陷能通过现有全部巡检：

  * `headingcheck` / `levelskipcheck` / `sectionnumcheck`  只看标题；
  * `tablecheck`       只看**已经存在**的表的列数是否对齐（没有表就不报）；
  * `linkexistcheck`   只看链接目标是否存在（「下表」不是链接）；
  * `fencecheck`       只看围栏是否闭合；
  * `svgrefcheck`      只看 SVG 内部引用。

也就是说：**「表/图存在但坏了」有人管，「表/图根本没出现」没人管**。而后者对读者的伤害更大：
读者会往上往下找，找不到就怀疑自己漏看了。

## 判据

  E0 ROOT_NOT_FOUND   既无 docs/ 也无 project/
  E1 NO_PAGES         一页都没扫到（活性判据：拒绝在空集上判「全绿」）
  W1 FIG_MISSING        承诺了「下图 / 见下图」，之后 `LOOK` 行内没有配图或示意图块
  W2 TABLE_MISSING      承诺了「下表 / 见下表」，之后 `LOOK` 行内没有表格
  W3 FIG_UP_MISSING     承诺了「上图 / 见上图」，之前 `LOOK` 行内没有配图或示意图块
  W4 TABLE_UP_MISSING   承诺了「上表 / 如上表」，之前 `LOOK` 行内没有表格

四条分开而不是合成一条，是因为**图和表的补法完全不同**：缺图要补 SVG 并写相对路径，
缺表要把段落改写成表格（或删掉那句指代）。混成一个码，修的时候还得再判一次。

## 口径（刻意保守）

  * 只扫 `docs/` 与 `project/` 下的 `*.md`；`DOCS_PLAN.md` / `AGENTS.md` 是台账，不在范围内。
  * **代码围栏内不扫**：示例里的「见下表」是文本，不是指代。
  * **行内代码先抹掉**：`` `下表` `` 是在讲这个词，不是在指代。
  * **标题行不扫**：`## 下表怎么读` 是标题，不是承诺。
  * **表格行不扫**：单元格里写「见下表」是表内交叉引用，不是散文里的承诺——
    这一条把 `ShellStartup` 那类「表里指表」的假阳性整类挡掉。
  * **页内不足 40 行不判**：未完成页缺图缺表是预期内的。
  * **向下窗口 `LOOK=15` 行**：再远就不算「下方」，读者也不会往下翻那么久。
  * **向上回看到上一个标题为止**（最多 80 行）：一张表可能有二三十行，「上表」隔着一张长表
    再出现是常态；但跨过标题就不算同一节，必须重报。
  * **左侧必须有边界**：中文无词边界，「线上表的成本」「设备上表现不同」都会命中「上表」，
    因此要求指代词左侧是行首、空白或标点。代价是「据上表」这类写法会漏，宁可漏不可刷屏。
  * 判据是 `W` 不是 `E`：指代落空不影响构建，只影响阅读——和 `tailcheck` 的 W 级一致。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

MIN_LINES = 40
LOOK = 15
FENCE = re.compile(r"^\s*(```|~~~)")
HEAD = re.compile(r"^\s{0,3}#{1,6}\s")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")
IMG = re.compile(r"!\[|<img\s", re.I)
INLINE = re.compile(r"`[^`]*`")

# 左侧边界：中文没有词边界，「线上表的成本」「设备上表现不同」都会命中「上表」。
# 口径：指代词左侧必须是行首、空白或标点——这一条把上述两类假阳性挡掉，
# 代价是「据上表」「按上表」这类不带标点的写法会漏掉（宁可漏，不可刷屏）。
BOUND = r"(?:^|[\s，。：；、（）()「」『』“”\"'])"
DOWN_FIG = re.compile(BOUND + r"(如下图|见下图|下图|下面的图|后面的图)")
DOWN_TAB = re.compile(BOUND + r"(如下表|见下表|下表|下面的表|后面的表)")
UP_FIG = re.compile(BOUND + r"(如上图|见上图|上图)")
UP_TAB = re.compile(BOUND + r"(如上表|见上表|上表)")


def strip_code(text: str) -> list[tuple[int, str, bool]]:
    """返回 [(行号, 已抹掉行内代码的行, 是否在围栏内)]。"""
    out, inside = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            out.append((i, "", True))
            continue
        if inside:
            out.append((i, "", True))
        else:
            out.append((i, INLINE.sub("``", line), False))
    return out


def has_table(lines: list[str], lo: int, hi: int) -> bool:
    for i in range(max(0, lo), min(len(lines), hi)):
        if TABLE_ROW.match(lines[i]):
            # 表格必须有分隔行（否则只是散落的竖线）
            if i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]):
                return True
            if i - 1 >= 0 and TABLE_SEP.match(lines[i - 1]):
                return True
    return False


def has_figure(lines: list[str], lo: int, hi: int) -> bool:
    for i in range(max(0, lo), min(len(lines), hi)):
        if IMG.search(lines[i]) or FENCE.match(lines[i]):
            return True
    return False


def scan_page(path: str) -> tuple[list[tuple[str, str, str]], dict[str, int]]:
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    counters = {"pages": 0, "skipped": 0, "promises": 0}
    if len(raw.splitlines()) < MIN_LINES:
        counters["skipped"] = 1
        return [], counters

    rows = strip_code(raw)
    lines = [ln for _no, ln, _f in rows]
    flags = [f for _no, _l, f in rows]
    findings: list[tuple[str, str, str]] = []
    counters["pages"] = 1

    for idx, (no, line, in_fence) in enumerate(rows):
        if in_fence or not line.strip() or HEAD.match(line) or TABLE_ROW.match(line):
            continue
        for rx, code, need, where in (
            (DOWN_FIG, "FIG_MISSING", "fig", "down"),
            (DOWN_TAB, "TABLE_MISSING", "tab", "down"),
            (UP_FIG, "FIG_UP_MISSING", "fig", "up"),
            (UP_TAB, "TABLE_UP_MISSING", "tab", "up"),
        ):
            for m in rx.finditer(line):
                counters["promises"] += 1
                if where == "down":
                    lo, hi = idx + 1, idx + 1 + LOOK
                else:
                    lo = 0
                    for j in range(idx - 1, max(-1, idx - 80), -1):
                        if HEAD.match(lines[j]):
                            lo = j + 1
                            break
                    hi = idx
                hit = has_figure(lines, lo, hi) if need == "fig" else has_table(lines, lo, hi)
                if not hit:
                    arrow = "后" if where == "down" else "前"
                    kind = "配图/示意图" if need == "fig" else "表格"
                    findings.append(("W", code, f"{path}:{no} 「{m.group(1)}」{arrow} 一段内无{kind}"))
    return findings, counters


def walk(root: str) -> list[str]:
    out = []
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, _dirnames, filenames in os.walk(d):
            for fn in filenames:
                if fn.endswith(".md"):
                    out.append(os.path.join(dirpath, fn))
    return sorted(out)


def report(root: str) -> int:
    if not any(os.path.isdir(os.path.join(root, b)) for b in ("docs", "project")):
        print("E0 ROOT_NOT_FOUND", root)
        return 2
    pages = walk(root)
    if not pages:
        print("E1 NO_PAGES")
        return 2
    E = W = prom = skipped = 0
    for p in pages:
        f, c = scan_page(p)
        prom += c["promises"]
        skipped += c["skipped"]
        for sev, code, detail in f:
            print(f"{sev}1 {code} {detail}")
            E += sev == "E"
            W += sev == "W"
    print(f"pages={len(pages)} skipped={skipped} promises={prom} E={E} W={W}")
    return 0 if E == 0 else 1


def _write(td: str, rel: str, body: str) -> str:
    p = os.path.join(td, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(body)
    return p


def selftest() -> int:
    ok = total = 0
    filler = "# T\n\n" + "正文一行。\n" * 45

    def case(name: str, body: str, want_codes: list[str]):
        nonlocal ok, total
        total += 1
        with tempfile.TemporaryDirectory() as td:
            p = _write(td, "docs/A/X/index.md", body)
            f, c = scan_page(p)
            got = [code for _s, code, _d in f]
            if c["pages"] == 0:
                print(f"FAIL {name}: skipped (body too short?)")
                return
            if sorted(got) == sorted(want_codes):
                ok += 1
            else:
                print(f"FAIL {name}: got={got} want={want_codes}")

    case("下图为图", filler + "\n如下图：\n\n![x](assets/a.png)\n", [])
    case("下表为表", filler + "\n如下表：\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n", [])
    case("下图实为表", filler + "\n见下图：\n\n| a | b |\n| --- | --- |\n", ["FIG_MISSING"])
    case("下表实为图", filler + "\n见下表：\n\n![x](assets/a.png)\n", ["TABLE_MISSING"])
    case("下表落空", filler + "\n见下表：\n\n" + "正文。\n" * 20, ["TABLE_MISSING"])
    case("超窗口不算", filler + "\n见下图：\n\n" + "正文。\n" * 20 + "\n![x](a.png)\n", ["FIG_MISSING"])
    case("上表成立", filler + "\n| a | b |\n| --- | --- |\n\n如上表所示。\n", [])
    case("上表落空", filler + "\n如上表所示。\n", ["TABLE_UP_MISSING"])
    case("围栏内不算", filler + "\n```text\n见下表：\n```\n", [])
    case("行内代码不算", filler + "\n写作 `下表` 这个词。\n", [])
    case("标题不算", filler + "\n## 下表怎么读\n", [])
    case("一行两处各算", filler + "\n见下图；见下表：\n", ["FIG_MISSING", "TABLE_MISSING"])

    total += 1
    with tempfile.TemporaryDirectory() as td:
        p = _write(td, "docs/A/X/index.md", "# T\n")
        f, c = scan_page(p)
        if c["skipped"] == 1 and c["pages"] == 0 and not f:
            ok += 1
        else:
            print(f"FAIL activity: skipped={c['skipped']} pages={c['pages']}")
    total += 1
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "docs"), exist_ok=True)
        if report(td) == 2:
            ok += 1
        else:
            print("FAIL no-pages")
    print(f"selftest {ok}/{total} {'PASS' if ok == total else 'FAIL'}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return report(a.root)


if __name__ == "__main__":
    sys.exit(main())
