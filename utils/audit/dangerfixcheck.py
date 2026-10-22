#!/usr/bin/env python3
"""第 79 项巡检：`::: danger` 容器里到底有没有「可执行信息」。

为什么立这一项
--------------
`AGENTS.md` §4「提示容器」写着：

    `:::danger` 容器中，易错点用有序列表逐条写清，并给出正确写法。

这条约定此前**没有任何一项巡检在读**：`mdrender_check` 管容器配对与嵌套、
`stubcheck` 管整页占位、`depthcheck` 管篇幅、`headingcheck` 管标题结构。
于是「只喊危险、不说怎么改」的 danger 块可以长期存在——它读起来像警告，
对读者却没有任何可执行信息，而且**构建与全部巡检都是绿的**。

判据（v2，2026-10-22 重写）
--------------------------
E0 ROOT_NOT_FOUND    活性前置：仓库根必须同时有 AGENTS.md 与 docs/
E1 NO_BLOCKS         活性：扫到 0 个 ::: danger 块即失败（防「根找错了还 PASS」）
E2 DANGER_EMPTY      块内 0 行非空正文 —— 唯一的内容门禁
W1 DANGER_NO_LIST    块内既无列表、也无代码块（纯段落）
W2 DANGER_TOO_LONG   块正文超过 18 行（提示可能该拆或该换页面）
W3 DANGER_BARE       裸句：无列表/代码/链接/加粗/行内代码/修正词，且正文 ≤ 3 行

### v1 的门禁是错的，记在这里防复发

v1 把「块内没有修正词（正确/改为/应当/做法/判据）也没有代码块」当作 E2 门禁。
全库实跑后 **E=2074 / 3019 块**，逐个人工核对后确认这是**判据的代理失效**，不是语料坏：

- `docs/AI/AgentFramework/StateGraph/index.md:32` 写的是「正确写法是只放新增量：」，
  词表里没有「正确写法」这个整词（只有「正确」子串，本该命中）——同一段里还有
  「最常见的错误是……」，读者拿到的是明确的可执行建议，却被判「没给写法」。
- `docs/AI/AICodingAssistant/TeamStandard/index.md:35` 用有序列表写了三条纪律，
  每条都带动作（写进评审清单 / CI 粗筛 / 区分主观与交付），只是因为没出现那 8 个词而报 E2。

真正的语义是「块里有没有可执行信息」，而可执行信息的载体包括列表、代码、命令、
链接、加粗要点与行内标识符——**词表只是其中一种、而且覆盖不全**。
把词表当门禁会逼着人往块里塞「正确做法：」四个字而不改内容，这是最坏的结局。

于是 v2 把门禁收窄到**结构性可判定**的一类（空块，全库实测 0 条），
内容层面的缺信息量降为 W3 报告项。当前 W3 = 93 条，作为存量待办登记在
`DOCS_PLAN.md` 的「存量整理任务清单」里，按批次修，不阻塞构建。

实现纪律（本库踩过的坑）
------------------------
1. 先按「冒号数 ≥ 开标记」找闭合，再判开标记；`::::` 包 `:::` 是合法嵌套。
2. 行内代码 / 围栏只用于「有没有代码块」的判断，不影响行号。
3. 判定修正词时**不匹配块外内容**，避免把上一段的「正确做法」算进来。
4. 夹具里每个用例只让一条判据有可能响，其余维度写成合规形态；
   期望码按「恰好等于」比较，多一条少一条都算失败。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

OPEN_RE = re.compile(r"^(:{3,})[^\S\n]*(danger|warning|tip|info|details)\b(.*)$")
CLOSE_RE = re.compile(r"^(:{3,})[^\S\n]*$")

FIX_WORDS = ("正确", "改为", "应当", "应该", "做法", "判据", "等价写法", "修法")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
FENCE_RE = re.compile(r"^\s*(?:`{3,}|~{3,})")
LINK_RE = re.compile(r"\]\([^)]+\)")
STRONG_RE = re.compile(r"\*\*[^*]+\*\*")
TICK_RE = re.compile(r"`[^`]+`")

MAX_LINES = 18
BARE_MAX_LINES = 3


def iter_md(root: str):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("assets", "node_modules", ".vitepress", ".git", "public")]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(base, f)


def find_blocks(lines):
    """返回 [(start_idx, end_idx, body_lines)]，index 从 0 开始。"""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        m = OPEN_RE.match(lines[i])
        if not m or m.group(2) != "danger":
            i += 1
            continue
        colons = len(m.group(1))
        j = i + 1
        while j < n:
            c = CLOSE_RE.match(lines[j])
            if c and len(c.group(1)) >= colons:
                break
            j += 1
        body = lines[i + 1:j]
        out.append((i, min(j, n - 1), body))
        i = j + 1
    return out


def check_blocks(body):
    """返回该块的 [(code, msg)]。拆成纯函数，方便 selftest 直接喂正文。"""
    nonblank = [b for b in body if b.strip()]
    text = "\n".join(body)
    has_code = any(FENCE_RE.match(b) for b in body)
    has_list = any(LIST_RE.match(b) for b in body)
    has_fix = any(w in text for w in FIX_WORDS) or has_code
    out = []

    # E2：空块。结构性破损，唯一的内容门禁。
    if not nonblank:
        out.append(("E2", "danger 块内没有任何正文"))
        return out

    # W1：纯段落（既没列表也没代码），写法层面的可读性问题
    if not has_list and not has_code:
        out.append(("W1", "danger 块内没有列表或代码块（纯段落）"))

    # W2：过长
    if len(nonblank) > MAX_LINES:
        out.append(("W2", f"danger 块正文 {len(nonblank)} 行 > {MAX_LINES}"))

    # W3：裸句 —— 没有任何可执行载体，且短到不可能讲清怎么改
    has_carrier = (
        has_list
        or has_code
        or has_fix
        or bool(LINK_RE.search(text))
        or bool(STRONG_RE.search(text))
        or bool(TICK_RE.search(text))
    )
    if not has_carrier and len(nonblank) <= BARE_MAX_LINES:
        out.append(("W3", f"裸句：{len(nonblank)} 行纯文字，无可执行信息载体（列表/代码/链接/加粗/标识符）"))

    return out


def check_file(path, rel):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")
    findings = []
    for start, end, body in find_blocks(lines):
        for code, msg in check_blocks(body):
            findings.append((code, rel, start + 1, msg))
    return findings


def scan(root: str):
    docs = os.path.join(root, "docs")
    proj = os.path.join(root, "project")
    if not os.path.isfile(os.path.join(root, "AGENTS.md")) or not os.path.isdir(docs):
        return [("E0", root, 0, "仓库根缺少 AGENTS.md 或 docs/")], 0, 0
    findings = []
    pages = blocks = 0
    roots = [docs] + ([proj] if os.path.isdir(proj) else [])
    for r in roots:
        for p in iter_md(r):
            rel = os.path.relpath(p, root).replace("\\", "/")
            with open(p, encoding="utf-8", errors="replace") as f:
                txt = f.read()
            n = len(find_blocks(txt.split("\n")))
            pages += 1
            blocks += n
            if n:
                findings += check_file(p, rel)
    if blocks == 0:
        findings.append(("E1", root, 0, "扫到 0 个 ::: danger 块（活性判据失败）"))
    return findings, pages, blocks


# ------------------------------------------------------------------ selftest
# 夹具纪律：每个用例只让一条判据「有可能响」，其余维度都写成合规形态
# （有列表、有修正词），否则断言的是判据之间的叠加而不是这一条判据本身。
# 期望码集合按「恰好等于」比较，多一条少一条都算失败。
CASES = [
    # (名称, 内容, 期望码集合)
    # —— 合规基线：有列表 + 有修正词 -> 全清
    ("fix-word", "::: danger 坑\n1. 常见错法：直接比较 4326 距离。\n**正确做法**：先 `::geography`。\n:::", set()),
    # 代码块可替代列表
    ("code-only", "::: danger 坑\n```sql\nSELECT 1;\n```\n:::", set()),
    # 纯段落且短：无载体 -> W1 + W3
    ("no-carrier", "::: danger 坑\n这个很容易错。\n:::", {"W1", "W3"}),
    # 有列表但无修正词：列表本身就是载体，W3 不响
    ("list-only", "::: danger 坑\n1. 会错。\n2. 也会错。\n:::", set()),
    # 四冒号包三冒号：外层块边界不能被内层 `:::` 提前截断
    ("nested-four", ":::: danger 外层\n- 别这样。\n**正确做法**：改。\n::: tip 内层\n内容\n:::\n::::", set()),
    # warning 块的内容不得被当作 danger 扫描（另有合法 danger 块保证活性通过）
    ("not-danger", "::: danger 坑\n1. 错。\n**正确做法**：改。\n:::\n\n::: warning 说明\n随便写，没有修正词也没有列表。\n:::", set()),
    # 行内反引号里的 `::: danger` 不算开标记
    ("inline-colon", "正文里说 `::: danger` 不算块。\n\n::: danger 坑\n1. 错。\n**正确做法**：改。\n:::", set()),
    # 正文过长：有列表所以 W1/W3 都不响，只 W2
    ("too-long", "::: danger 坑\n" + "\n".join(f"- 第 {i} 条" for i in range(20)) + "\n**正确做法**：改。\n:::", {"W2"}),
    # 两块独立计数，只报坏的那块
    ("two-blocks", "::: danger 一\n1. 错。\n**正确做法**：改。\n:::\n\n::: danger 二\n就是错。\n:::", {"W1", "W3"}),
    # 空块：唯一的内容门禁
    ("empty-block", "::: danger 坑\n:::", {"E2"}),
    # 只有空白的块同样算空
    ("blank-block", "::: danger 坑\n\n   \n:::", {"E2"}),
    # 修正词无列表：词表本身就是载体，W3 不响
    ("fix-word-only", "::: danger 坑\n**应当**先归一化坐标系再比较。\n:::", {"W1"}),
    # 活性判据：全库 0 个 danger 块必须 E1，不能静默 PASS
    ("no-danger-at-all", "::: tip 只有提示\n内容\n:::", {"E1"}),
]


def selftest():
    ok = fail = 0
    for name, md, expect in CASES:
        d = tempfile.mkdtemp(prefix=f"danger-{name}-")
        os.makedirs(os.path.join(d, "docs", "X"), exist_ok=True)
        with open(os.path.join(d, "AGENTS.md"), "w", encoding="utf-8") as f:
            f.write("# a\n")
        p = os.path.join(d, "docs", "X", "index.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("# t\n\n" + md + "\n")
        got, _, _ = scan(d)
        codes = {c for c, *_ in got}
        if codes == expect:
            ok += 1
            print(f"PASS {name} -> {sorted(codes) or 'clean'}")
        else:
            fail += 1
            print(f"FAIL {name}: expect {sorted(expect)} got {sorted(codes)} :: {got}")
    print(f"\nselftest {ok}/{ok + fail}")
    return 0 if fail == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=os.getcwd())
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true", help="打印全部明细")
    ap.add_argument("--code", default="", help="只看某个码，如 W3 / E")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    findings, pages, blocks = scan(a.root)
    e = [f for f in findings if f[0].startswith("E")]
    w = [f for f in findings if f[0].startswith("W")]
    for code, rel, line, msg in sorted(findings):
        if a.code:
            if not code.startswith(a.code):
                continue
        elif not (a.list or code.startswith("E")):
            continue
        print(f"{code} {rel}:{line} {msg}")
    by = {}
    for code, *_ in findings:
        by[code] = by.get(code, 0) + 1
    print(f"\npages={pages} danger_blocks={blocks}")
    print("counts: " + " ".join(f"{k}={v}" for k, v in sorted(by.items())))
    print(f"E={len(e)} W={len(w)}")
    print("PASS" if not e else "FAIL")
    return 0 if not e else 1


if __name__ == "__main__":
    sys.exit(main())
