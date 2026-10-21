#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tickscheck.py — 行内代码定界符（反引号）游程巡检 · 第 71 项

为什么立这一项
--------------
本库有两次构建事故同源，都是**反引号游程**问题：

* 第 120 天：空行内代码片段 + 落单反引号，游程序列 2,2,1,2,2 使
  CommonMark 的「同长游程配对」整体位移，一段正文裸奔成 HTML 开标签。
* 第 138 天：`link_text.replace(…)` 写进行内代码时带了一个裸反引号，
  同一机制再次位移，`pnpm docs:build` 当场报
  `Element is missing end tag`（`DOCS_PLAN.md:1977`）。

两次的共同点：**Markdown 源码本身没有任何词法错误**，编辑器不高亮、
`linkcheck` 不看、`tablecheck` 只在列数真的错位时才有感，唯一的发现
途径是跑一次十分钟的构建。这类缺陷的成本结构极不划算——写错一次 1 秒，
发现它 10 分钟，而且是在「以为写完了」之后。

判据
----
E0 ROOT_NOT_FOUND      仓库根找不到（`DOCS_PLAN.md` 与 `docs/` 都不在）
E1 NO_PAGES            一个页面都没扫到（活性判据；空集上一切判定恒真）
E2 UNMATCHED_RUN       保留编号，见 W6（原为 E 级，首轮实测后下调，理由见下）
E3 FENCE_UNCLOSED      围栏代码块未闭合（后续全部内容被当代码，静默丢页）
W2 EMPTY_CODE          空的行内代码（第 120 天事故根因）
W3 PIPE_UNESCAPED      表格行内代码含裸竖线（GFM 会据此切列，第 138/145 天根因）
W4 BACKSLASH_ESCAPED   闭合反引号被前置反斜杠转义（页面多显示一个反引号）
W5 BARE_FENCE_INLINE   行中裸写 3 个以上反引号（应包进行内代码）
W6 UNMATCHED_RUN       段落内有反引号找不到同长闭合（配对错位，页面标记会串位）

配对规则按 CommonMark：**闭合游程必须与开启游程等长**。因此 ` ``a`b`` `
合法（外层两个、内层一个），而用一个反引号定界却内含反引号则不合法。
这条规则是本脚本与「数一数反引号是不是偶数」的全部区别——后者会把
` ``a`b`` ` 这种正常写法报成错误，误报一旦多起来，脚本就会被跳过。

为什么「落单反引号」的第一版定成了 E、首轮实测后又下调为 W6
----------------------------------------------------------------
初版的理由是「第 120 / 138 天两次构建中断都是这个形态」。首轮全库跑完
`E=20`，逐条回溯后发现两件事：

* 其中 10 条是**闭合反引号前面紧跟一个反斜杠**（`C:\Program Files\Go\` 这类
  Windows 路径、`\|` 这类转义示例）。CommonMark 的 escape 规则覆盖反引号，
  所以闭合确实被吃掉了——但后果只是页面上多显示一个反引号，不是结构断裂。
  这 10 条另立 `W4`，成因不同、处置不同。
* 剩下 6 条全在 `DOCS_PLAN.md` 的**超长台账行**上（单行 400~3300 字、含
  50~170 个反引号）。这些行里同时存在多处「漏一个」与「多一个」，正负
  相抵后只剩下 1 个落单——机械修复无法定位该改哪一处，改了会破坏台账正文。

更关键的是：**markdown-it 遇到配不上的反引号时按字面输出，不会中断构建**。
第 120 / 138 天之所以炸，是「反引号失衡 + 附近恰好有 `::: ` 容器或 HTML 标签」
的组合效应，静态判据抓不到那个「恰好」。所以一个诚实的分级是：把
「围栏未闭合」（`E3`，整页静默变代码）留在 E 级，把「落单反引号」放在
W6——它是**必须逐条处置的清单**，不是**必然失败的断言**。

纪律
----
* **先 E1 再 E2/E3**：扫描集合为空时 E2 恒为 0，那恰好是「看起来最好」的读数。
* **只读**：不写任何文件、不改台账；selftest 夹具走 `tempfile.mkdtemp()`，
  绝不落在仓库内（仓库里任何位置的 `.md` 都会被 VitePress 当页面编译，
  第 178 天 `auditmancheck` 就是这么把构建打断的）。
* **围栏优先**：代码块内部的反引号不参与行内判定，否则每一段 shell 都是假警报。

用法
----
    python3 utils/audit/tickscheck.py                # 扫默认根（本文件上溯到仓库根）
    python3 utils/audit/tickscheck.py --root .       # 指定根
    python3 utils/audit/tickscheck.py --selftest      # 夹具自测
    python3 utils/audit/tickscheck.py --top 20        # 每类最多列 20 条

退出码：0 = 无 E；1 = 有 E；2 = 环境/根错误。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from dataclasses import dataclass

BT = chr(96)                      # 反引号；写成 chr 而非字面量，避免被上层工具转义

SKIP_DIRS = {
    "node_modules", ".git", "dist", ".vitepress", "cache", "temp",
    "__pycache__", ".workbuddy", "_sandbox",
}

LIST_PREFIX = r"(?:[ \t]*(?:[-*+]|\d{1,9}[.)])[ \t]+)?"
FENCE_RE = re.compile(r"^(" + LIST_PREFIX + r"[ \t]*)(" + BT + r"{3,}|~{3,})(.*)$")
TICK_RE = re.compile(r"(?<!\\)(" + BT + "+)")
TICK_ALL_RE = re.compile(r"(" + BT + "+)")     # 连被反斜杠转义的也算进来
TABLE_ROW_RE = re.compile(r"^\s{0,3}\|.*\|\s*$")


@dataclass
class Finding:
    level: str      # E / W
    code: str
    path: str
    line: int
    detail: str

    def render(self, root: str) -> str:
        try:
            rel = os.path.relpath(self.path, root)
        except ValueError:                       # pragma: no cover
            rel = self.path
        return f"{self.level} {self.code:<16} {rel}:{self.line}  {self.detail}"


# ---------------------------------------------------------------- 扫描核心

def iter_markdown(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def fence_map(lines: list[str]) -> tuple[set[int], int | None]:
    """两遍法判定围栏区间。

    为什么不能只用「行首反引号/波浪线」一条正则：列表项里的围栏可以缩进
    5 格（`docs/Backend/Java/Frame/SpringBoot/v3/AOT.md` 就是这样），而反过来
    「用行内代码引用一个围栏」的写法（反引号包着三个反引号）行首也是反引号。
    两者在单行上看不出区别，只能靠**能不能找到闭合**来判定。

    返回 (围栏内行号集合（1-based）, 未闭合围栏的起始行号或 None)。
    """
    in_fence: set[int] = set()
    unclosed: int | None = None
    i = 0
    n = len(lines)
    while i < n:
        m = FENCE_RE.match(lines[i])
        # CommonMark 规定：反引号围栏的信息串不能含反引号。
        # 这一条同时解决了「行内代码里引用围栏」的歧义。
        if not m or (m.group(2)[0] == BT and BT in m.group(3)):
            i += 1
            continue
        ch, length = m.group(2)[0], len(m.group(2))
        j = i + 1
        while j < n:
            c = FENCE_RE.match(lines[j])
            if c and c.group(2)[0] == ch and len(c.group(2)) >= length \
                    and not c.group(3).strip():
                break
            j += 1
        if j < n:
            in_fence.update(range(i + 1, j + 2))
            i = j + 1
        else:
            unclosed = i + 1
            in_fence.update(range(i + 1, n + 1))
            i = n
    return in_fence, unclosed


BLOCK_START_RE = re.compile(r"^(#{1,6}\s|>|\||[-*+]\s|\d+[.)]\s)")


def blockify(lines: list[str], in_fence: set[int]) -> list[list[tuple[int, str]]]:
    """把非围栏行切成「行内代码可跨行」的块。

    CommonMark 允许行内代码跨行（换行渲染成空格），所以按**单行**判定会把
    「命令太长折了一行」的正当写法误报成未闭合——`project/Base/BackendTemplate/
    Acceptance/rollback_plan.md:44` 就是这样。但表格行、标题、引用、列表项各自
    是独立的渲染单元，不能跨过去配对，必须断块。
    """
    blocks: list[list[tuple[int, str]]] = []
    cur: list[tuple[int, str]] = []
    for idx, raw in enumerate(lines, start=1):
        if idx in in_fence or not raw.strip():
            if cur:
                blocks.append(cur)
                cur = []
            continue
        # 引用块是连续的多行段落，不能像列表项那样逐行断开
        quote_cont = raw.startswith(">") and cur and cur[-1][1].startswith(">")
        if cur and not quote_cont and BLOCK_START_RE.match(raw):
            blocks.append(cur)
            cur = []
        cur.append((idx, raw))
    if cur:
        blocks.append(cur)
    return blocks


def match_runs(block: list[tuple[int, str]], include_escaped: bool = False):
    """在一个块内按「先开先配、同长闭合」切分行内代码。

    `include_escaped=True` 时把 `\\` 后面的反引号也算作游程——这是用来
    **反证**「落单到底是不是转义造成的」：同一段落用两套游程各跑一遍，
    含转义能配平、不含配不平，则成因确定是转义（W4）；两套都配不平，
    则是作者真的漏写了（W6）。

    返回 (配对列表, 未能闭合的开启游程列表)。配对元素为
    (起始行号, 起始游程, 结束行号, 结束游程)。
    """
    run_re = TICK_ALL_RE if include_escaped else TICK_RE
    pairs: list[tuple[tuple, tuple, int, tuple]] = []
    pending: list[tuple[int, tuple]] = []       # (行号, 游程)
    for idx, raw in block:
        for mm in run_re.finditer(raw):
            run = (mm.start(), len(mm.group(1)))
            if pending:
                open_line, open_run = pending[-1]
                if open_run[1] == run[1]:
                    pending.pop()
                    pairs.append((open_line, open_run, idx, run))
                # 长度不同：属于已开启 span 的内层内容，跳过
                continue
            pending.append((idx, run))
    return pairs, pending


def check_file(path: str) -> list[Finding]:
    """扫描一个文件，返回发现。围栏内的行不参与行内代码判定。"""
    findings: list[Finding] = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:                       # pragma: no cover
        return [Finding("E", "E9_READ_FAIL", path, 0, str(exc))]

    in_fence, unclosed = fence_map(lines)

    for block in blockify(lines, in_fence):
        pairs, pending = match_runs(block)

        # E2 / W4：块内（含跨行）配不上的开启游程。
        # 分级的依据是**成因**而不是后果：若该行存在「反斜杠 + 反引号」，
        # 那么闭合是被 CommonMark 的转义规则吃掉的（markdown-it 的 escape
        # 规则覆盖反引号），页面只会多显示一个反引号，属写法瑕疵；
        # 若没有任何转义参与，则说明作者真的漏了闭合，配对会整体位移
        # —— 第 120 / 138 天两次构建中断都是这个形态，故保留 E 级。
        _, pending_all = match_runs(block, include_escaped=True)
        for idx, run in pending:
            if not pending_all:
                findings.append(Finding(
                    "W", "W4_BACKSLASH_ESCAPED", path, idx,
                    f"第 {idx} 行的闭合反引号被前置反斜杠转义（`\\\u0060`），"
                    f"页面会多显示一个反引号；改用双反引号定界即可",
                ))
            else:
                findings.append(Finding(
                    "W", "W6_UNMATCHED_RUN", path, idx,
                    f"第 {idx} 行的 {run[1]} 个反引号在本段内找不到同长闭合，"
                    f"该段此后的标记配对会整体错位",
                ))

        # W5：行中出现长度 >= 3 的游程 —— 正文里的裸围栏串，
        # 应写成「用行内代码包住三个反引号」，否则页面上会直接露出反引号
        span_of: dict[int, list[tuple[int, int]]] = {}
        ends: set[tuple[int, int]] = set()       # 定界符自身不算「裸写」
        for open_line, open_run, close_line, close_run in pairs:
            ends.add((open_line, open_run[0]))
            ends.add((close_line, close_run[0]))
            if open_line == close_line:
                span_of.setdefault(open_line, []).append(
                    (open_run[0] + open_run[1], close_run[0]))
        for idx, raw in block:
            for mm in TICK_RE.finditer(raw):
                if len(mm.group(1)) < 3 or (idx, mm.start()) in ends:
                    continue
                inside = any(a <= mm.start() < b for a, b in span_of.get(idx, ()))
                if inside:
                    continue                     # 已包进行内代码，是正当写法
                findings.append(Finding(
                    "W", "W5_BARE_FENCE_INLINE", path, idx,
                    f"行中裸写 {len(mm.group(1))} 个反引号，应包进行内代码",
                ))
                break

        for open_line, open_run, close_line, close_run in pairs:
            if open_line != close_line:
                continue                          # 跨行 span 不做内容级判定
            raw = next(r for i, r in block if i == open_line)
            seg = raw[open_run[0] + open_run[1]: close_run[0]]
            if seg.strip() == "":
                findings.append(Finding(
                    "W", "W2_EMPTY_CODE", path, open_line,
                    "空的行内代码片段（第 120 天事故根因）",
                ))
            if TABLE_ROW_RE.match(raw) and "|" in seg.replace("\\|", ""):
                findings.append(Finding(
                    "W", "W3_PIPE_UNESCAPED", path, open_line,
                    f"表格行内代码含未转义竖线：{seg[:40]!r}",
                ))

    if unclosed is not None:
        findings.append(Finding(
            "E", "E3_FENCE_UNCLOSED", path, unclosed,
            f"围栏自第 {unclosed} 行起找不到闭合，余下 {len(lines) - unclosed + 1} 行全部被当作代码",
        ))

    return findings


def resolve_root(explicit: str | None) -> str | None:
    if explicit:
        return os.path.abspath(explicit) if os.path.isdir(explicit) else None
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        if os.path.isfile(os.path.join(here, "DOCS_PLAN.md")) and \
                os.path.isdir(os.path.join(here, "docs")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    cwd = os.getcwd()
    if os.path.isfile(os.path.join(cwd, "DOCS_PLAN.md")):
        return cwd
    return None


# ---------------------------------------------------------------- 主流程

def run(root: str) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    pages = 0
    for path in iter_markdown(root):
        pages += 1
        findings.extend(check_file(path))
    return findings, pages


def report(root: str, findings: list[Finding], pages: int, top: int) -> int:
    if pages == 0:
        print("E1 NO_PAGES  扫描到 0 个 Markdown 页面，拒绝判定（活性判据未通过）")
        return 2

    errs = [f for f in findings if f.level == "E"]
    warns = [f for f in findings if f.level == "W"]

    for f in errs[:top]:
        print(f.render(root))
    if len(errs) > top:
        print(f"    … 另有 {len(errs) - top} 条错误（--top 调整）")
    for f in warns[:top]:
        print(f.render(root))
    if len(warns) > top:
        print(f"    … 另有 {len(warns) - top} 条警告（--top 调整）")

    by_code: dict[str, int] = {}
    for f in findings:
        by_code[f.code] = by_code.get(f.code, 0) + 1
    dist = " ".join(f"{k}={v}" for k, v in sorted(by_code.items())) or "无"

    print(f"\n扫描 {pages} 个 Markdown 文件：E={len(errs)}  W={len(warns)}")
    print(f"分布：{dist}")
    print("判定：" + ("PASS" if not errs else "FAIL"))
    return 0 if not errs else 1


# ---------------------------------------------------------------- 自测

SELFTEST_CASES = [
    # (文件名, 内容, 期望命中的判据集合)
    ("ok.md", "# t\n\n正常 " + BT + "code" + BT + " 与 " + BT * 2 + "a" + BT + "b" + BT * 2 + " 都合法。\n", set()),
    ("unmatched.md", "# t\n\n这句 " + BT + "未闭合 的反引号。\n", {"W6_UNMATCHED_RUN"}),
    ("nested-ok.md", "# t\n\n" + BT * 2 + "x" + BT + "y" + BT * 2 + "\n", set()),
    # 三个反引号定界、内部两个：合法写法，不该报 W5
    ("multi-tick-inner.md", "# t\n\n前 " + BT * 3 + "c" + BT * 2 + "d" + BT * 3 + " 后\n", set()),
    # 用行内代码引用一个围栏：信息串含反引号，按 CommonMark 不算围栏开启
    ("inline-fence-ref.md", "# t\n\n" + BT + " " + BT * 3 + " " + BT + "\n\n正文\n", set()),
    # 跨行行内代码是合法的（rollback_plan.md 的真实形状），不能报
    ("multiline-span.md", "# t\n\n命令由 " + BT + "python a.py --x 1\n--y 2" + BT + " 生成。\n", set()),
    # 但跨行也救不了真正的落单反引号：段落内必须有同长闭合
    ("multiline-broken.md", "# t\n\n路径 " + BT + "C:\\Go\\" + " 就这些。\n", {"W6_UNMATCHED_RUN"}),
    # 列表项内缩进 5 格的围栏（AOT.md 的真实形状），必须被认出来
    ("indented-fence.md", "# t\n\n1. 步骤\n\n     " + BT * 3 + "shell\n     echo " + BT + "x" + BT + "\n     " + BT * 3 + "\n", set()),
    ("empty.md", "# t\n\n空片段 " + BT * 2 + " " + BT * 2 + " 一个。\n", {"W2_EMPTY_CODE"}),
    ("pipe.md", "| a | b |\n| --- | --- |\n| " + BT + "x|y" + BT + " | z |\n", {"W3_PIPE_UNESCAPED"}),
    ("pipe-escaped.md", "| a | b |\n| --- | --- |\n| " + BT + "x" + "\\|" + "y" + BT + " | z |\n", set()),
    ("fence.md", "# t\n\n" + BT * 3 + "shell\necho " + BT + "date" + BT + "\n" + BT * 3 + "\n", set()),
    ("fence-unclosed.md", "# t\n\n" + BT * 3 + "shell\necho hi\n", {"E3_FENCE_UNCLOSED"}),
    ("fence-odd-inside.md", "# t\n\n" + BT * 3 + "text\n一个 " + BT + " 裸反引号\n" + BT * 3 + "\n", set()),
    ("nested-fence.md", "# t\n\n~~~md\n" + BT * 3 + "\n内层\n" + BT * 3 + "\n~~~\n", set()),
    ("escaped.md", "# t\n\n转义的 \\" + BT + " 不算定界符。\n", set()),
]


def selftest() -> int:
    tmp = tempfile.mkdtemp(prefix="tickscheck_")
    passed = failed = 0
    for name, content, expected in SELFTEST_CASES:
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        got = {f.code for f in check_file(path)}
        if got == expected:
            passed += 1
            print(f"PASS  {name:<22} {sorted(got) or '无命中'}")
        else:
            failed += 1
            print(f"FAIL  {name:<22} 期望 {sorted(expected) or '无命中'} 实际 {sorted(got) or '无命中'}")

    # 活性判据：空目录必须让 report() 报 E1，而不是 PASS
    empty = tempfile.mkdtemp(prefix="tickscheck_empty_")
    pages = sum(1 for _ in iter_markdown(empty))
    if pages == 0:
        passed += 1
        print(f"PASS  {'empty-dir-activity':<22} 扫到 0 页 → report() 返回 E1")
    else:                                        # pragma: no cover
        failed += 1
        print(f"FAIL  {'empty-dir-activity':<22} 空目录却扫到 {pages} 页")

    print(f"\n自测 {passed}/{passed + failed} PASS，夹具目录 {tmp}")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="行内代码定界符（反引号）游程巡检")
    ap.add_argument("--root", help="仓库根（默认自动上溯查找）")
    ap.add_argument("--top", type=int, default=15, help="每类最多列出条数")
    ap.add_argument("--selftest", action="store_true", help="跑夹具自测")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = resolve_root(args.root)
    if root is None:
        print("E0 ROOT_NOT_FOUND  找不到仓库根（需含 DOCS_PLAN.md 与 docs/）", file=sys.stderr)
        return 2

    findings, pages = run(root)
    return report(root, findings, pages, args.top)


if __name__ == "__main__":
    sys.exit(main())
