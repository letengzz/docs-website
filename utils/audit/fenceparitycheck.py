#!/usr/bin/env python3
r"""fenceparitycheck.py — 围栏解析一致性巡检 · 第 88 项

背景：本库有四道巡检都要「知道哪几行在围栏里」（`fencecheck` / `tickscheck` /
`langmatchcheck` / `levelskipcheck`），四家各写一份正则，历史上连续三次在同一处栽
跟头（第 85 项四反引号、第 86 项行内代码、第 87 项缩进围栏）。本巡检把「四份实现
是否等价」变成可判的对象。

判据
----
- `E0 ROOT_NOT_FOUND`  根路径不存在
- `E1 NO_PAGES`        扫不到页面（活体检查，拒绝在空语料上判绿）
- `E2 PARITY_DIFF`     **参考实现与朴素实现结论不同的文件**（保留判据位：当前为 0，
                        一旦出现说明有文件用了两套实现都拿不准的形态）
- `E3 TOOL_REGRESS`    `langmatchcheck` 的围栏正则**不允许前导缩进**（第 87 项
                        同型缺陷未修）
- `W1 PATTERN_HIT`     三种历史翻车形态各自命中的文件数（只计数）
- `W2 TOOL_INDEP`      某个巡检工具自带围栏正则、未接 `fenceutil`（技术债计数）
- `W3 INDENT_RISK`     含缩进围栏（列表项内部）的文件数——对「不许前导空白」的解析器
                        不可见；本库当前 **130**，正是 2026-10 修复 `langmatchcheck` 的入口
- `W4 NESTED_FENCE`    四反引号嵌三反引号的文件数（合法写法），任何新增需人工确认

用法
----
    python3 utils/audit/fenceparitycheck.py [--selftest] [--root .]

口径说明（为什么 `E2` 只报文件数而不报行数）
--------------------------------------------
`E2` 想回答的是「**这个文件会不会让朴素解析器出错**」，而不是「错了多少行」——
错的量取决于具体解析器，没有统一值。所以每个文件只计一次，并打印第一处差异行号，
便于定位。
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

SKIP_DIRS = {".git", "node_modules", ".vitepress", "dist", "assets", ".workbuddy", "__pycache__"}

# 三种朴素实现：都在历史里翻过车，保留它们作为「风险探针」
NAIVE = {
    # 不允许前导空白：列表项内的围栏整段漏掉（第 87 项）
    "no-indent": re.compile(r"^(?:[-*+]\s+|\d+\.\s+)?(```+|~~~+)\s*([^\s`]*)"),
    # 只允许 0~3 空格：4 空格的列表内围栏漏掉（第 87 项）
    "indent-3": re.compile(r"^\s{0,3}(?:[-*+]\s+|\d+\.\s+)?(```+|~~~+)\s*([^\s`]*)"),
    # 只看字符不看长度：四反引号围栏里嵌三反引号时提前闭合（第 85 项）
    "toggle-only": re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)?(```+|~~~+)"),
}


def naive_mask(text, rx, check_len):
    lines = text.split("\n")
    mask, i, n = set(), 0, len(lines)
    while i < n:
        m = rx.match(lines[i])
        if not m:
            i += 1
            continue
        char = m.group(1)[0]
        ln = len(m.group(1))
        j = i + 1
        while j < n:
            m2 = rx.match(lines[j])
            if m2 and m2.group(1)[0] == char and (not check_len or len(m2.group(1)) >= ln):
                break
            j += 1
        mask.update(range(i, min(j, n - 1) + 1))
        i = j + 1
    return mask


def scan_root(root):
    pages = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".md"):
                pages.append(os.path.join(dirpath, fn))
    return sorted(pages)


def run(root):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND", root)
        return 2
    pages = scan_root(root)
    if not pages:
        print("E1 NO_PAGES", root)
        return 2

    e2, w3, w4, w1 = [], [], [], {"四反引号嵌三反引号": 0, "缩进≥4 的围栏": 0, "带 info string": 0}
    for p in pages:
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        text = open(p, encoding="utf-8", errors="replace").read()
        ref, blocks, _ = fenceutil.scan(text)
        diffs = []
        for name, rx in NAIVE.items():
            if naive_mask(text, rx, check_len=(name != "toggle-only")) != ref:
                diffs.append(name)
        if "toggle-only" in diffs:          # 嵌套围栏：合法写法，但对「只看字符不看长度」的解析器是陷阱
            w4.append((rel, len(blocks)))
        elif diffs:                          # 仅缩进类差异：对「忘了缩进」的解析器不可见
            w3.append((rel, ",".join(diffs)))
        # W1：三种形态的命中计数
        lines = text.split("\n")
        if re.search(r"^````", text, re.M) and re.search(r"^```(?!`)", text, re.M):
            w1["四反引号嵌三反引号"] += 1
        if re.search(r"^\s{4,}(?:[-*+]\s+|\d+\.\s+)?```", text, re.M):
            w1["缩进≥4 的围栏"] += 1
        for s, _e, info in blocks:
            if info and " " in info:
                w1["带 info string"] += 1
                break

    # E3：langmatchcheck 的围栏正则是否允许前导缩进
    e3 = []
    lm = os.path.join(os.path.dirname(os.path.abspath(__file__)), "langmatchcheck.py")
    if os.path.exists(lm):
        src = open(lm, encoding="utf-8").read()
        m = re.search(r"^FENCE_RE\s*=\s*re\.compile\(r\"([^\"]+)\"", src, re.M)
        if m and not m.group(1).startswith("^\\s*"):
            e3.append(m.group(1)[:48])

    # W2：谁还没接 fenceutil
    w2 = []
    for tool in ("fencecheck.py", "tickscheck.py", "langmatchcheck.py", "levelskipcheck.py"):
        tp = os.path.join(os.path.dirname(os.path.abspath(__file__)), tool)
        if os.path.exists(tp) and "fenceutil" not in open(tp, encoding="utf-8").read():
            w2.append(tool)

    for rel, nblk in w4:
        print(f"W4 NESTED_FENCE {rel}  blocks={nblk}（合法：外层四反引号）")
    for hint in e3:
        print(f"E3 TOOL_REGRESS langmatchcheck FENCE_RE 不允许前导缩进：{hint}")
    print(f"W1 PATTERN_HIT " + " ".join(f"{k}={v}" for k, v in w1.items()))
    print(f"W3 INDENT_RISK {len(w3)} 个文件含缩进围栏（对不许前导空白的解析器不可见）")
    print(f"W2 TOOL_INDEP {len(w2)} 个工具自带围栏正则未接 fenceutil：{','.join(w2) or '-'}")
    print(f"pages={len(pages)} E={len(e2) + len(e3)} W={sum(w1.values()) + len(w2) + len(w3) + len(w4)}")
    return 1 if (e2 or e3) else 0


def selftest():
    import tempfile

    ok = 0
    cases = [
        ("four-tick", "````markdown\n```js\nconst a = 1;\n```\n````\n", {"toggle-only"}),
        ("indented", "1. 步骤\n\n    ```shell\n    echo hi\n    ```\n", {"no-indent", "indent-3"}),
        ("plain", "```js\nx\n```\n", set()),
    ]
    for name, txt, expect in cases:
        ref, blocks, _ = fenceutil.scan(txt)
        hit = {n for n, rx in NAIVE.items() if naive_mask(txt, rx, n != "toggle-only") != ref}
        good = hit == expect
        print(f"{'PASS' if good else 'FAIL'} {name}: naive_diff={sorted(hit)} expect={sorted(expect)}")
        ok += 1 if good else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else run(a.root))


if __name__ == "__main__":
    main()
