#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enumerclaimcheck.py —— 「列举声明」与紧随清单条数的一致性巡检（第 126 项）。

为什么需要它
------------
本库大量页面用「三个必须写进数据模型」「五类漏检方式」这类**列举声明**给读者一个
结构预期，后面紧跟一个列表。这类文字有一个特点：**写的时候改过条数，改完忘了改前面**。
此时页面读起来完全通顺、构建不报错、判据条数也对，只有读者会发现「说好三条，只列了两条」。

既有巡检各管一段，没有一项看这里：
  - `countclaimcheck` 只看「全书 N 章 / 共 N 页」这类**章节规模**声明；
  - `judgesumcheck` 只看判据总览表的条数；
  - `liststructcheck` 只看列表的缩进与标记类型；
  - `sectionnumcheck` 只看小节编号连续性。
「一句『三条』⇄ 紧跟的三行列表」这一对，此前没有任何脚本核对。

判据
----
  E0 ROOT_NOT_FOUND        扫描根不存在
  E1 NO_CLAIMS             活性：一条列举声明都没找到，拒绝判定（防扫错目录全绿）
  E2 CLAIM_THEN_HEADING    冒号结尾的列举声明后面直接是标题/容器/文件尾（列举彻底缺失）
  W1 COUNT_MISMATCH        声明条数 ≠ 紧随列表的顶层条目数
  W2 NO_LIST_AFTER_CLAIM   冒号结尾的列举声明后面是段落（可能是有意为之，需人工看一眼）
  W3 NESTED_AMBIGUOUS      列表里有子项，条目数可能被误算（提示，不判定）

口径（为什么这样取数）
--------------------
1. 只认**行末是冒号**的声明：`三个必须写进数据模型：`。行中出现「三种形态」但句尾是句号的，
   属于叙述而非列举，不判（否则误报率极高）。
2. 量词只认「条 / 类 / 个 / 步 / 种 / 点 / 件 / 层 / 段 / 章 / 页」。`三月`、`三维` 这类
   数字不是量词搭配，自然不匹配。
3. 数字同时支持中文（一~十五）与阿拉伯（2~15），因为本库两种写法都有。
4. 顶层条目 = 缩进与首项相同的列表行；更深缩进的算子项，只置 `W3` 提示。
5. 围栏代码块、表格行、容器标记行（`::: tip`）全部跳过——那里出现冒号是语法不是列举。

用法
----
  python3 utils/audit/enumerclaimcheck.py                 # 扫 docs 与 project
  python3 utils/audit/enumerclaimcheck.py --root docs
  python3 utils/audit/enumerclaimcheck.py --selftest      # 自测
退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

CN = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
      "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15}

# 「三个必须写进数据模型：」「五类漏检方式：」「两条路：」
# 取「离冒号最近」的那个数量词，且量词与冒号之间不超过 9 个字、不含引号与括号：
#   「三个必须写进数据模型：」        → 3
#   「五个读数里有三个直接改变实现：」 → 3（不是 5）
#   「两个专题的边界在于「讲引擎还是讲产品」：」→ 不匹配（离冒号太远）
CLAIM = re.compile(
    r"(?:^|[，。；、\s（(])([一二两三四五六七八九十]{1,2}|1[0-5]|[2-9])\s*"
    r"(条|类|个|步|种|点|件|层|段)"
    r"[^：:。；\n「」（）()]{0,9}[：:]\s*$"
)
LIST = re.compile(r"^(\s*)(?:[-*+]|\d{1,3}[.)])\s+\S")
FENCE = re.compile(r"^\s*(```|~~~)")
CONTAINER = re.compile(r"^\s*:::")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")


def cn2int(s: str) -> int:
    if s.isdigit():
        return int(s)
    return CN.get(s, -1)


def scan_file(path: str, rel: str, out: list) -> int:
    """返回本文件找到的声明条数"""
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        return 0
    found = 0
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith("|") or CONTAINER.match(line):
            continue
        m = CLAIM.search(line)
        if not m:
            continue
        n = cn2int(m.group(1))
        if n < 2:
            continue
        found += 1
        # 找下一个非空行
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        # 容器式列举：::: danger 里每条以 **加粗** 起头，等价于列表项
        if j < len(lines) and CONTAINER.match(lines[j]):
            depth, bold = 1, 0
            k2 = j + 1
            while k2 < len(lines) and depth:
                c2 = lines[k2]
                if CONTAINER.match(c2):
                    depth += 1 if c2.strip().startswith(":::") and len(c2.strip()) > 3 else -1
                elif re.match(r"^\s*\*\*[^*]+\*\*", c2):
                    bold += 1
                k2 += 1
            if bold != n:
                out.append(("W1", rel, i + 1, f"声明 {n} 条，容器内加粗条目 {bold} 条"))
            continue
        if j >= len(lines) or HEADING.match(lines[j]):
            # 标题式列举：紧随其后出现 ≥2 个同级标题，视为「用标题代替列表」
            if j < len(lines) and HEADING.match(lines[j]):
                lvl = len(lines[j].strip().split(" ")[0])
                same = 0
                for k in range(j, min(j + 40, len(lines))):
                    h = HEADING.match(lines[k])
                    if h and len(lines[k].strip().split(" ")[0]) == lvl:
                        same += 1
                if same >= 2:
                    out.append(("W2", rel, i + 1, f"声明 {n} 条，以 {same} 个同级标题代替列表"))
                    continue
            out.append(("E2", rel, i + 1, f"声明 {n} 条，后面没有任何列举"))
            continue
        # 表格式列举：冒号后紧跟表格
        if lines[j].lstrip().startswith("|"):
            rows = 0
            k3 = j
            while k3 < len(lines) and lines[k3].lstrip().startswith("|"):
                rows += 1
                k3 += 1
            data = max(0, rows - 2)
            if data != n:
                out.append(("W1", rel, i + 1, f"声明 {n} 条，表格数据行 {data} 行"))
            continue
        lm = LIST.match(lines[j])
        if not lm:
            out.append(("W2", rel, i + 1, f"声明 {n} 条，但紧跟的是段落而非列表"))
            continue
        base = len(lm.group(1))
        items, nested = 0, 0
        k = j
        in_code = False
        while k < len(lines):
            cur = lines[k]
            if FENCE.match(cur):
                in_code = not in_code
                k += 1
                continue
            if in_code:
                k += 1
                continue
            if not cur.strip():
                # 松散列表：空行后若是「同级新条目 / 更深缩进的续块 / 容器」都算列表内
                nx = k + 1
                while nx < len(lines) and not lines[nx].strip():
                    nx += 1
                if nx >= len(lines):
                    break
                nl = lines[nx]
                nm = LIST.match(nl)
                if nm and len(nm.group(1)) <= base:
                    k = nx
                    continue
                if nl.startswith(" " * (base + 1)) or CONTAINER.match(nl):
                    k = nx
                    continue
                break
            mm = LIST.match(cur)
            if mm:
                ind = len(mm.group(1))
                if ind <= base:
                    items += 1
                else:
                    nested += 1
                k += 1
                continue
            # 续行：缩进 >= base 且不是新块
            if cur.startswith(" " * (base + 2)) or cur.startswith("\t"):
                k += 1
                continue
            break
        if items != n:
            out.append(("W1", rel, i + 1, f"声明 {n} 条，实际顶层条目 {items} 条"))
        elif nested:
            out.append(("W3", rel, i + 1, f"声明 {n} 条，另有 {nested} 个子项（人工确认）"))
    return found


def run(roots: list[str]) -> int:
    files, claims, out = 0, 0, []
    for root in roots:
        if not os.path.isdir(root):
            print(f"E0 ROOT_NOT_FOUND  {root}")
            return 1
        for dirpath, _d, names in os.walk(root):
            for name in names:
                if not name.endswith(".md"):
                    continue
                p = os.path.join(dirpath, name)
                files += 1
                claims += scan_file(p, os.path.relpath(p), out)
    if claims == 0:
        print("E1 NO_CLAIMS  一条列举声明都没扫到，拒绝判定")
        return 1
    for lv, rel, ln, msg in out:
        print(f"{lv} {rel}:{ln}  {msg}")
    e = sum(1 for r in out if r[0].startswith("E"))
    w = len(out) - e
    print(f"files={files} claims={claims} E={e} W={w}")
    return 1 if e else 0


SELFTEST = [
    # (内容, 期望级别或 None)
    ("三个必须写进数据模型：\n1. 甲\n2. 乙\n3. 丙\n", None),
    ("三个必须写进数据模型：\n1. 甲\n2. 乙\n", "W1"),
    ("三种形态：\n- 甲\n- 乙\n- 丙\n", None),
    ("两个前提：\n\n- 甲\n- 乙\n", None),
    ("五个坑：\n", "E2"),
    ("五个坑：\n## 下一节\n", "E2"),
    ("三条判据：\n这里是一段解释文字。\n", "W2"),
    ("三种形态的判别式是「同一用户的两次写会不会落两个库」，见下文。\n", None),
    ("```text\n三个必须：\n```\n", None),
    ("| 三个必须： | 说明 |\n| --- | --- |\n", None),
    ("::: danger 三件事必须写进数据模型\n1. 甲\n2. 乙\n3. 丙\n:::\n", None),
    ("三条：\n- 甲\n  - 甲一\n  - 甲二\n- 乙\n- 丙\n", "W3"),
    ("2 条：\n- 甲\n- 乙\n", None),
    ("2 条：\n- 甲\n", "W1"),
    ("十一类：\n" + "".join(f"- 第{i}项\n" for i in range(1, 12)), None),
]


def selftest() -> int:
    ok = 0
    for idx, (body, want) in enumerate(SELFTEST, 1):
        with tempfile.TemporaryDirectory() as d:
            sub = os.path.join(d, "docs", "T")
            os.makedirs(sub)
            open(os.path.join(sub, "index.md"), "w", encoding="utf-8").write(body)
            out = []
            scan_file(os.path.join(sub, "index.md"), "index.md", out)
            got = out[0][0] if out else None
            good = got == want
            ok += good
            print(f"  {'PASS' if good else 'FAIL'}  #{idx:02d} 期望 {want} 实际 {got}")
    print(f"selftest {ok}/{len(SELFTEST)}")
    return 0 if ok == len(SELFTEST) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="*", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(a.root)


if __name__ == "__main__":
    sys.exit(main())
