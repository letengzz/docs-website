#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""containershapecheck.py —— 提示容器「形状」巡检（第 134 项巡检）

## 为什么立这一项

`AGENTS.md` 第 4 节把五类提示容器与用途写死了：`tip` 建议、`warning` 补充说明、
`danger` 易错点、`info` 背景版本、`details` 折叠详情；并且单独加了一句：

> `:::danger` 容器中，易错点用有序列表逐条写清，并给出正确写法。

现有巡检里，容器被分成两截：**语法层**归第 82 项 `containercheck`（开闭配对、多余闭合、
未知类型、闭合冒号数、空容器、标题过长、类型大小写），**一个容器的内容层**归第 79 项
`dangerfixcheck`（只读 `::: danger`：有没有列表、是否超过 18 行、是否裸句）。两者之间空着一块：

* **类型选错**：`tip` 写了十行以上——它按约定是「一句话总结」，写长说明作者真正该用
  `warning`；没有任何判据看过这件事（第 82 项只看标题长度，不看正文行数）。
* **有分条、但没有出路**：`danger` 列了五条错误做法却不给正确写法。第 79 项的裸句判据
  要求「正文 ≤ 3 行」才触发，**长块反而漏判**——越详细越安全，恰好倒过来了。
* **嵌套容器**：第 82 项按栈判开闭，不判「容器里再开容器」；本库约定不嵌套，但没人拦。

交叠部分（未闭合 / 未知类型）本项**故意保留**：两项的扫法与统计口径不同（第 82 项按行
压栈，本项按文件解析并顺带统计每类容器的行数分布），**两处读数不一致就说明有一方口径分叉**。
当前两处报同一条（`docs/Backend/TaxInvoice/index.md:62` 的 `::: info`），一致。

## 判据（两真四提示）

* `E0 ROOT_NOT_FOUND` / `E0 READ_FAIL` —— 活性，防「扫了个空目录也算全绿」
* `E1 NO_FILES` —— 同上
* `E2 UNCLOSED_CONTAINER` —— `:::` 开了没关（或被代码围栏吞掉）
* `E2 UNKNOWN_CONTAINER` —— 容器名不在允许清单（拼错即静默降级成默认 tip）
* `W1 DANGER_WITHOUT_LIST` —— `danger` 有 ≥2 行正文却没有列表项
* `W2 DANGER_NO_FIX` —— `danger` 有列表，但通篇没有「正确 / 应当 / 改为 / 不要」这类修正提示
* `W4 TIP_TOO_LONG` —— `tip` 块正文超过 8 行（它是一句话总结，不是小节）
* `W5 NESTED_CONTAINER` —— 容器嵌套（VitePress 支持，但本库约定不嵌套）

## 口径是被真实语料打回来的（三轮）

**第一轮**：把「`danger` 里没有列表」判成 `E3`，全库报 **1,334** 条。逐条打开发现本库
大量 `danger` 是**一句话的强提醒**（「部署前必须跑一次 `pnpm build`」），它不该被强制拆成
列表——按 `E` 处理等于要求重写一千多页。降级为 `W1`。

**第二轮**：降级后 `W1` 仍是 1,334，其中绝大多数是**单句**块。加「正文 ≥2 行」的条件后
降到 471 —— 单句 `danger` 放行，多段 `danger` 才要求列点，这才符合「易错点逐条写清」的原意。

**第三轮**：`code-group` 被当成未知容器（报 5 条 `E2`）。它是 VitePress 内置的代码组容器，
补进允许清单后 `E2` 只剩 1 条——那一条是真的没闭合（`:::info` 开了没关）。

**还有一个「不混报」的除法**：一个块已经有 `W1`（没有列表）时不再报 `W2`（没有修正提示）。
两种情况修法不同（补列表 vs 补一句话），混报只会让人先删掉一条看着碍眼的告警。

## 收口读数

`--selftest 15/15`；全库 `docs`：`pages=2860 E=1 W=1330`（`W1=471` / `W2=800` / `W4=59`）；
`project`：`pages=313 E=0 W=207`。唯一一条 `E` 落在未提交的并行会话产物上，按惯例不碰。

## 口径

1. 代码围栏内的一切都不算（```` ``` ```` 与 `~~~` 两种围栏都剥）。
2. 容器名取 `:::` 之后的第一个词，允许带中文标题：`::: tip 一句话理解`。
3. 容器结束以**单独一行 `:::`**为准；行内 `:::tip` 只出现在开头。
4. 「列表项」认 `-` `*` `+` 与 `1.` `1)`，且允许缩进。
5. 空块不判 `E3`（那是 `emptysectioncheck` 的事），只判形状。

用法：

    python3 utils/audit/containershapecheck.py
    python3 utils/audit/containershapecheck.py --selftest
    python3 utils/audit/containershapecheck.py --root docs --json

退出码：有 `E` 为 1，否则 0。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

ALLOWED = {"tip", "warning", "danger", "info", "details", "code-group", "raw"}
LIST_ITEM = re.compile(r"^\s{0,3}(?:[-*+]\s+|\d{1,3}[.)]\s+)")
OPEN = re.compile(r"^(\s*):::\s*([A-Za-z][\w-]*)?\s*(.*)$")
CLOSE = re.compile(r"^\s*:::\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
FIX_HINT = ("正确", "应当", "应该", "改为", "不要", "必须", "写成", "改成")


def iter_md(root):
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def scan_text(text):
    """返回容器块列表：dict(name, title, start, lines[], closed, nested)"""
    lines = text.splitlines()
    blocks, stack = [], []
    fence = None
    for idx, raw in enumerate(lines, 1):
        m = FENCE.match(raw)
        if m:
            mark = m.group(1)[0] * 3
            if fence is None:
                fence = mark
            elif mark == fence:
                fence = None
            continue
        if fence is not None:
            continue

        if CLOSE.match(raw):
            if stack:
                blk = stack.pop()
                blk["lines"] = lines[blk["start"]: idx - 1]
                blk["closed"] = True
                blocks.append(blk)
            else:
                blocks.append({"name": None, "title": "stray", "start": idx,
                               "lines": [], "closed": False, "stray": True})
            continue

        m = OPEN.match(raw)
        if m and m.group(2):
            name = m.group(2).lower()
            blk = {"name": name, "title": m.group(3).strip(), "start": idx,
                   "lines": [], "closed": False, "nested": bool(stack)}
            stack.append(blk)
    for blk in stack:                     # 未闭合
        blk["lines"] = lines[blk["start"]:]
        blocks.append(blk)
    return blocks


def check_file(path, root):
    rel = os.path.relpath(path, root)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:                # 活性：读不到也要报，不能默默跳过
        return [("E0", rel, 0, f"READ_FAIL: {exc}")]
    out = []
    for blk in scan_text(text):
        if blk.get("stray"):
            out.append(("E2", rel, blk["start"], "UNCLOSED_CONTAINER: 多余的 ::: 结束行"))
            continue
        base = blk["start"]
        if not blk["closed"]:
            out.append(("E2", rel, base, f"UNCLOSED_CONTAINER: :::{blk['name']} 未闭合"))
        if blk["name"] not in ALLOWED:
            out.append(("E2", rel, base,
                        f"UNKNOWN_CONTAINER: {blk['name']}（允许 {'/'.join(sorted(ALLOWED))}）"))
        body = [l for l in blk["lines"] if l.strip()]
        if blk["name"] == "danger":
            has_list = any(LIST_ITEM.match(l) for l in blk["lines"])
            if not has_list and len(body) >= 2:
                out.append(("W1", rel, base, "DANGER_WITHOUT_LIST: danger 内没有列表项"))
            elif has_list and not any(any(k in l for k in FIX_HINT) for l in body):
                # 已经有 W1 的块不再报 W2：修法不同，混报只会让人先删一条
                out.append(("W2", rel, base, "DANGER_NO_FIX: 未给出正确写法"))
        if blk["name"] == "tip" and len(body) > 8:
            out.append(("W4", rel, base, f"TIP_TOO_LONG: {len(body)} 行（上限 8）"))
        if blk.get("nested"):
            out.append(("W5", rel, base, "NESTED_CONTAINER: 容器嵌套"))
    return out


def run(root, as_json=False):
    if not os.path.isdir(root):
        print(json.dumps({"E0": 1, "msg": f"ROOT_NOT_FOUND: {root}"}) if as_json
              else f"E0 ROOT_NOT_FOUND {root}")
        return 1
    findings, pages = [], 0
    for path in iter_md(root):
        pages += 1
        findings.extend(check_file(path, root))
    if pages == 0:
        print("E1 NO_FILES 没有找到任何 .md")
        return 1
    cnt = {}
    for sev, rel, line, msg in findings:
        cnt[sev] = cnt.get(sev, 0) + 1
        if not as_json:
            print(f"{sev} {rel}:{line} {msg}")
    e = sum(v for k, v in cnt.items() if k.startswith("E"))
    w = sum(v for k, v in cnt.items() if k.startswith("W"))
    if as_json:
        print(json.dumps({"pages": pages, "E": e, "W": w, "by": cnt}, ensure_ascii=False))
    else:
        print(f"\npages={pages} E={e} W={w} " + " ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
        print("RESULT " + ("FAIL" if e else "OK"))
    return 1 if e else 0


CASES = [
    # (名称, markdown, 期望命中)
    ("合法 tip", "::: tip 一句话\n短句。\n:::", set()),
    ("未闭合", "::: warning 说明\n正文\n", {"E2"}),
    ("未知容器名", "::: note\n正文\n:::", {"E2"}),
    ("danger 无列表（多行）", "::: danger 注意\n第一句。\n第二句。\n:::", {"W1"}),
    ("danger 单句无列表放行", "::: danger 注意\n一句话就完了。\n:::", set()),
    ("danger 有列表", "::: danger 注意\n1. 坑一 → 正确写法是 A\n2. 坑二 → 应当改成 B\n:::", set()),
    ("danger 有列表无修正", "::: danger 注意\n1. 坑一\n2. 坑二\n:::", {"W2"}),
    ("danger 有列表有修正", "::: danger 注意\n1. 坑一\n   正确写法是 A。\n:::", set()),
    ("tip 过长", "::: tip 一句话\n" + "\n".join(f"行{i}" for i in range(9)) + "\n:::", {"W4"}),
    ("围栏内的 :::", "```shell\necho :::\n:::\n```\n", set()),
    ("嵌套容器", "::: info 背景\n::: tip 提示\n短\n:::\n:::", {"W5"}),
    ("多余结束行", "正文\n:::\n", {"E2"}),
    ("details 合法", "::: details 详细信息\n内容\n:::", set()),
    ("stray 结束行在围栏内", "```\n:::\n```\n", set()),
    ("danger 带修正但无列表", "::: danger 注意\n正确写法是 A。\n还差一句。\n:::", {"W1"}),
]


def selftest():
    ok = 0
    for name, md, expect in CASES:
        hits = {f[0] for f in check_file_text(md)}
        good = hits == expect
        ok += 1 if good else 0
        print(f"{'PASS' if good else 'FAIL'} {name} 得到 {sorted(hits)} 期望 {sorted(expect)}")
    print(f"\nselftest {ok}/{len(CASES)}")
    return 0 if ok == len(CASES) else 1


def check_file_text(text):
    """selftest 用：不落盘，直接检查一段 markdown"""
    out = []
    for blk in scan_text(text):
        rel, base = "<case>", blk["start"]
        if blk.get("stray"):
            out.append(("E2", rel, base, "")); continue
        if not blk["closed"]:
            out.append(("E2", rel, base, ""))
        if blk["name"] not in ALLOWED:
            out.append(("E2", rel, base, ""))
        body = [l for l in blk["lines"] if l.strip()]
        if blk["name"] == "danger":
            has_list = any(LIST_ITEM.match(l) for l in blk["lines"])
            if not has_list and len(body) >= 2:
                out.append(("W1", rel, base, ""))
            elif has_list and not any(any(k in l for k in FIX_HINT) for l in body):
                out.append(("W2", rel, base, ""))
        if blk["name"] == "tip" and len(body) > 8:
            out.append(("W4", rel, base, ""))
        if blk.get("nested"):
            out.append(("W5", rel, base, ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    code = run(args.root, args.json)
    if args.root == "docs":                # 默认同时扫 project/
        for extra in ("project",):
            if os.path.isdir(extra):
                code = max(code, run(extra, args.json))
    sys.exit(code)


if __name__ == "__main__":
    main()
