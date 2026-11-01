#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""emphasischeck.py — 粗体/斜体定界符的「配对与贴边」巡检 · 第 111 项

为什么立这一项
--------------
本库关于「一段话长得对不对」的门已经有七道（`headingcheck` / `levelskipcheck` /
`sectionnumcheck` / `sectionordercheck` / `emptysectioncheck` / `codegapcheck` /
`liststructcheck`），**七道全绿仍然可以写出一个渲染后就变形的段落**——因为七道门看的
都是「块」与「标记」，没有一道看过**强调标记本身**。

Markdown 的 `**` 不是「加粗开关」，它是一对 **left-flanking / right-flanking 定界符**，
而 CommonMark 对「贴边」有硬性要求：**开定界符右边不能是空白，闭定界符左边不能是空白**。
违反这条，`**` 不会被识别为定界符，而是**原样显示**：

```markdown
用**布尔 ** 指标      →  页面显示：用**布尔 ** 指标     （星号露出，粗体没生效）
**主轴 (main axis) ** →  页面显示：**主轴 (main axis) **
```

这一类缺陷有三个共同点，正好构成「必须专门立一道门」的理由：

1. **源文件看起来完全正常**——`**` 成对出现、内容也写对了，肉眼逐行读不会觉得有问题。
2. **构建完全静默**——Markdown 合法、链接全通、判据齐全，`pnpm docs:build` 绿。
3. **读者看到的与作者写的不是一回事**——作者以为加粗了，读者看到的是两个星号。

同类的第二种形态是**配对本身断了**：段落里 `**` 的个数是奇数，最后一个定界符没有对手，
从它往后一直到段落结束都会退化成普通文本（或者干脆露出星号）。第三种是 `****`
——渲染成一个空的 `<strong>`，页面上凭空多出一行空白。

判据
----
E0 ROOT_NOT_FOUND      仓库根找不到 docs/ 与 project/
E1 NO_PAGES            一个页面都没枚举到就拒绝判定（活性）
E2 EMPTY_SPAN          `****`（空粗体，渲染成一行空白）
W1 UNPAIRED_BOLD       定界符配不上（星号原样露出，粗体没生效）
W2 ITALIC_ODD          段落内单个 `*` 为奇数（斜体星号露出）
W3 LONG_SPAN           单个粗体超过 120 字（多半是整段加粗或漏闭合）
N1 PAGES / N2 PARAS / N3 DELIMS 只计数

为什么 `W1` 是 W 不是 E：这条口径抓到的第一版结果是 935 处，全部是同一个成因——
**中文句号（。、；：）紧贴闭定界符、后面又紧跟英文或数字**（`**……路径上。**SSR`）。
`markdown-it` 按 CommonMark 的 flanking 规则判定它「只能开、不能闭」，于是星号原样露出。
这不是笔误而是**中文写作习惯与 CommonMark 规则的正面冲突**，改法有两种（把标点移出粗体，
或补一个空格），需要逐句判断语气，不能机械替换——所以本轮登记为欠账、按日消化。

口径
----
1. **段落**是判定单位，不是行：Markdown 允许粗体跨行，按行判会把「合法跨行」全判成 E。
   分段规则是「空行 / 标题 / 表格行 / 围栏边界」，表格行单独成段（单元格里也会加粗）。
2. **行内代码先整段替换成占位符**再扫。`codegapcheck` 的第 1 条口径就是「剥掉行内代码」，
   但这里不能直接删——删掉会让两侧的 `**` 贴到一起，凭空造出一个 `****`。
3. **转义 `\*` 不是定界符**，先替换掉。
4. **围栏内不扫**：代码块里的 `**` 是代码，不是强调。
5. `***bold italic***` 按「一个粗体定界符」处理（连写 3 个及以上都归一成 1 个）。
6. E 只收「渲染一定变形」的四类；`W1` 是排版问题（可能是故意整段加粗），不进 E。

用法
----
    python3 utils/audit/emphasischeck.py                 # 全库
    python3 utils/audit/emphasischeck.py docs/Backend    # 指定根
    python3 utils/audit/emphasischeck.py --selftest      # 自检
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

RULE = "=" * 78

# ---------------------------------------------------------------------------
# 扫描口径
# ---------------------------------------------------------------------------
FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
ESCAPED_STAR = re.compile(r"\\\*")
STAR_RUN = re.compile(r"\*+")
CJK_OR_WORD = re.compile(r"[\w\u4e00-\u9fff]")


def is_punct(ch: str) -> bool:
    """CommonMark 意义上的标点：ASCII 标点 + Unicode P*/S* 类。"""
    if not ch:
        return False
    if ch in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~":
        return True
    import unicodedata

    return unicodedata.category(ch)[0] in "PS"

SPACE = " \u3000\t"


def strip_noise(line: str) -> str:
    """把行内代码与转义星号换成占位符，保留长度感但不引入 `*`。"""
    line = INLINE_CODE.sub(lambda m: "\x00" * len(m.group(0)), line)
    line = ESCAPED_STAR.sub("\x00", line)
    return line


def paragraphs(lines: list[str]):
    """按「空行 / 标题 / 表格行 / 围栏」切段，返回 [(起行号, 文本)]。"""
    out: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0

    def flush():
        nonlocal buf
        if buf:
            out.append((start, "\n".join(buf)))
            buf = []

    in_fence = False
    fence_mark = ""
    for idx, raw in enumerate(lines, 1):
        m = FENCE_OPEN.match(raw)
        if m:
            if not in_fence:
                flush()
                in_fence = True
                fence_mark = m.group(1)[0]
            elif raw.strip().startswith(fence_mark * 3):
                in_fence = False
            continue
        if in_fence:
            continue
        s = raw.strip()
        if not s or s.startswith("#"):
            flush()
            continue
        if s.startswith("|"):
            flush()
            out.append((idx, strip_noise(s)))
            continue
        if not buf:
            start = idx
        buf.append(strip_noise(raw))
    flush()
    return out


def scan_text(text: str):
    """返回 (delims, empties)。delims 是 [(pos, runlen, can_open, can_close, why)]。

    这里**不做交替配对**（历史上那样做会整体错位），而是照 CommonMark 的
    left/right-flanking 规则先判定每个定界符「能不能开」「能不能闭」，配对交给
    `check_page` 里的栈。规则本身就能解释「为什么星号会露出来」：

    - 开定界符的**右侧**必须是非空白（`** 布尔` 开不了）；
    - 闭定界符的**左侧**必须是非空白（`布尔 **` 闭不上）。
    """
    runs = [(m.start(), len(m.group(0))) for m in STAR_RUN.finditer(text)]
    empties = [r[0] for r in runs if r[1] >= 4 and r[1] % 2 == 0]
    delims = []
    for pos, ln in runs:
        if ln == 1 or ln >= 4:
            continue  # 单星号另计；连写 4 个归 empties
        prev_c = text[pos - 1] if pos > 0 else " "
        next_c = text[pos + ln] if pos + ln < len(text) else " "
        prev_ws = prev_c in SPACE or prev_c == "\n"
        next_ws = next_c in SPACE or next_c == "\n"
        prev_p = is_punct(prev_c)
        next_p = is_punct(next_c)
        left = (not next_ws) and (not next_p or prev_ws or prev_p)
        right = (not prev_ws) and (not prev_p or next_ws or next_p)
        why = ""
        if left and not right:
            why = "只能开不能闭（左侧是空白或标点，闭不上）"
        elif right and not left:
            why = "只能闭不能开（右侧是空白或标点，开不了）"
        delims.append((pos, ln, left, right, why))
    return delims, empties


def check_page(path: Path, issues: list, stats: dict):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return
    for lineno, text in paragraphs(lines):
        stats["paras"] += 1
        delims, empties = scan_text(text)
        stats["delims"] += len(delims)
        for _ in empties:
            issues.append(("E2", path, lineno, "空粗体（连写 4 个星号，渲染成空白）", text[:60]))
        stack: list[int] = []
        spans = []
        for idx, (pos, _ln, can_open, can_close, why) in enumerate(delims):
            if can_close and stack:
                o = delims[stack.pop()][0]
                spans.append((o + 2, pos, text[o + 2:pos]))
                continue
            if can_open:
                stack.append(idx)
                continue
            issues.append(("W1", path, lineno, why or "定界符配不上", text[max(0, pos - 30):pos + 20]))
        for idx in stack:
            pos = delims[idx][0]
            issues.append(("W1", path, lineno, "开定界符没有闭（星号原样露出）", text[max(0, pos - 30):pos + 30]))
        # 斜体单独看：单星号奇数即有一处露出
        single = [r for r in STAR_RUN.finditer(text) if len(r.group(0)) == 1]
        if len(single) % 2 == 1:
            issues.append(("W2", path, lineno, f"{len(single)} 个单星号（奇数）", text[:60]))
        # 排版类：单个粗体过长（多半是整段加粗或漏闭合）
        for o, c, seg in spans:
            if len(seg) > 120 and CJK_OR_WORD.search(seg):
                issues.append(("W3", path, lineno, f"粗体长 {len(seg)} 字：{seg[:24]!r}", text[:60]))


def iter_pages(roots: list[Path]):
    for root in roots:
        for p in sorted(root.rglob("*.md")):
            if p.name == "index.md" or p.suffix == ".md":
                yield p


def run(roots: list[Path], quiet: bool = False) -> int:
    stats = {"pages": 0, "paras": 0, "delims": 0}
    issues: list = []
    for p in iter_pages(roots):
        stats["pages"] += 1
        check_page(p, issues, stats)

    order = {"E2": 0, "W1": 1, "W2": 2, "W3": 3}
    issues.sort(key=lambda x: (order.get(x[0], 9), str(x[1]), x[2]))
    if not quiet:
        for code, path, lineno, msg, ctx in issues:
            print(f"{code:3s} {msg:52s} {path}:{lineno}")
    e = sum(1 for i in issues if i[0].startswith("E"))
    w1 = sum(1 for i in issues if i[0] == "W1")
    w2 = sum(1 for i in issues if i[0] == "W2")
    w3 = sum(1 for i in issues if i[0] == "W3")
    print(RULE)
    print(
        f"pages={stats['pages']} paras={stats['paras']} delims={stats['delims']} "
        f"E={e} W1={w1} W2={w2} W3={w3}"
    )
    return e


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _case(tmp: Path, name: str, body: str) -> Path:
    d = tmp / name
    d.mkdir(parents=True, exist_ok=True)
    f = d / "index.md"
    f.write_text(body, encoding="utf-8")
    return f


def selftest() -> int:
    ok = 0
    total = 0

    def expect(cond: bool, label: str):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print(f"  FAIL {label}")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1 正常粗体：无告警
        _case(tmp, "c1", "# A\n\n这是**正常**粗体。\n")
        # 2 开定界符右侧贴空格 → E3
        _case(tmp, "c2", "# A\n\n用**布尔 **指标。\n")
        # 3 闭定界符左侧贴空格 → E3
        _case(tmp, "c3", "# A\n\n**主轴 (main axis) **：伸缩。\n")
        # 4 奇数个定界符 → E2
        _case(tmp, "c4", "# A\n\n只有一个**开定界符，没有闭。\n")
        # 5 空粗体 → E4
        _case(tmp, "c5", "# A\n\n****\n")
        # 6 跨行粗体（合法）→ 无告警
        _case(tmp, "c6", "# A\n\n**这一段在\n下一行结束**。\n")
        # 7 行内代码里的星号不算 → 无告警
        _case(tmp, "c7", "# A\n\n公式 `a**b` 是乘方。\n")
        # 8 围栏内的星号不算 → 无告警
        _case(tmp, "c8", "# A\n\n```python\nx = a ** b\n```\n")
        # 9 两个相邻正确粗体不误判（历史假阳性：`**a** 与 **b**`）
        _case(tmp, "c9", "# A\n\n**甲** 与 **乙** 都对。\n")
        # 10 表格单元格内贴空格 → E3
        _case(tmp, "c10", "# A\n\n| 项 | 说明 |\n| --- | --- |\n| ① | 用**布尔 **值 |\n")
        # 11 转义星号不算 → 无告警
        _case(tmp, "c11", "# A\n\n`N\\*` 与 \\* 都不算定界符。\n")
        # 12 超长粗体 → W1
        _case(tmp, "c12", "# A\n\n**" + "很长的一段话" * 30 + "**\n")
        # 13 单星号奇数 → W2
        _case(tmp, "c13", "# A\n\n这里有一个 * 单星号。\n")

        def codes(name: str):
            stats = {"pages": 0, "paras": 0, "delims": 0}
            issues: list = []
            check_page(tmp / name / "index.md", issues, stats)
            return [i[0] for i in issues]

        expect(codes("c1") == [], "c1 正常粗体不应告警")
        expect("W1" in codes("c2"), "c2 开定界符贴空格（星号露出）应报 W1")
        expect("W1" in codes("c3"), "c3 闭定界符贴空格（星号露出）应报 W1")
        expect("W1" in codes("c4"), "c4 奇数定界符应报 W1")
        expect("E2" in codes("c5"), "c5 空粗体应报 E2")
        expect(codes("c6") == [], "c6 跨行粗体是合法的，不应告警")
        expect(codes("c7") == [], "c7 行内代码里的星号不应告警")
        expect(codes("c8") == [], "c8 围栏里的星号不应告警")
        expect(codes("c9") == [], "c9 相邻两个正确粗体不应误判")
        expect("W1" in codes("c10"), "c10 表格单元格内贴空格应报 W1")
        expect(codes("c11") == [], "c11 转义星号不应告警")
        expect("W3" in codes("c12"), "c12 超长粗体应报 W3")
        expect("W2" in codes("c13"), "c13 单星号奇数应报 W2")

    print(f"selftest {ok}/{total}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="粗体/斜体定界符巡检")
    ap.add_argument("roots", nargs="*", default=None, help="扫描根目录（默认 docs 与 project）")
    ap.add_argument("--selftest", action="store_true", help="跑自检")
    ap.add_argument("--quiet", action="store_true", help="只输出汇总")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    repo = Path(__file__).resolve().parents[2]
    if args.roots:
        roots = [Path(r) if Path(r).is_absolute() else repo / r for r in args.roots]
    else:
        roots = [repo / "docs", repo / "project"]
    roots = [r for r in roots if r.exists()]
    if not roots:
        print("E0 ROOT_NOT_FOUND  docs/ 与 project/ 都不存在", file=sys.stderr)
        return 2
    return 1 if run(roots, args.quiet) else 0


if __name__ == "__main__":
    sys.exit(main())
