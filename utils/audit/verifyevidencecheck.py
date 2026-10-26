#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""verifyevidencecheck.py —— 「验证方式」这一节里到底有没有证据（第 99 项巡检）

## 动机：第十次「某个维度整体没人看」

本库最早的几道门（历史名 `verifycheck`）只回答一个问题：**页里有没有「验证」这一节**。
`sectionordercheck`（第 74 项）管的是这一节的**位置**（必须在参考资料之前）。
`judgecovercheck`（第 62 项）管的是**判据表**在不在。

三道门全绿，仍然可以出现这样的页面：

    ## 验证方式

    1. 确认功能正常。
    2. 确认没有报错。

它结构正确、位置正确、判据齐全，**却没有一个字能被读者执行**。而 `AGENTS.md`
第 5 节第 8 条与第 9 节第 7 条把「验证方式」定义成**承诺级**要求：
「给出可验证的收尾（命令、预期输出、页面地址）」「验证方式写成『读者可执行的命令 +
预期输出』」。承诺级要求，从来没有一道门去看。

这一类缺陷的可怕之处与第 94 项（占位词）同族：**结构全绿、读者在第 3 屏撞墙**。
区别在于占位词至少长得像欠账（写着「待补充」），而「确认功能正常」长得像已经完成。

## 适用范围（为什么只扫 project/）

`project/` 下每一章都在承诺「读者照着做一遍就能跑起来」，验证是**合同条款**。
`docs/` 技术页的验证允许多种形态（打开页面看到某个现象、观察某个输出），
把「没有命令」判成缺陷会产生 168 条噪声（本机实测），把真欠账埋掉。
所以本项只判 `project/` 的**章节页**：

  * 跳过项目根目录页 `project/{Base,Complete}/<Project>/index.md`（那是目录页）；
  * 跳过没有「验证」小节的页（`N1` 只计数，理由见下）。

## 判据

  E0 ROOT_NOT_FOUND      仓库根或 project/ 找不到
  E1 NO_PAGES            一个章节页都没枚举到（活性判据，拒绝给全绿）
  W1 NO_EVIDENCE         有验证节，但节内既无代码块、也无「命令式」行内代码
  W2 NO_EXPECTATION      有可执行物，但节内没有任何「预期 / 输出 / 看到 / 返回」类断言词
  W3 EVIDENCE_ELSEWHERE  节内只有指路（「见上文」「见第 N 节」），证据不在本节

  计数项（不判错）：
  N1 NO_SECTION          章节页没有「验证」小节（设计章常常如此，口径见下）

## 口径（三条，都是被真实语料打出来的）

1. **`N1` 只计数不判错**。设计章（需求拆分、架构、数据库设计）的「验证」往往是评审清单，
   不是命令；把它们判成缺陷会立刻产生几十条噪声。真正该修的是**有节但无证据**的那批。
2. **「命令式行内代码」认三种形态**：含空格（`pnpm build`）、含斜杠（`/api/users`）、
   含括号（`health()`）。只认「反引号里有两个以上单词」会漏掉 `curl`-only 的写法。
3. **断言词表要宽**（预期 / **期望** / 应输出 / 看到 / 返回 / 等于 / EXIT / 状态码 /
   断言 / 报错 / 失败 / ⏳）。本库大量页面把期望写在代码块注释里，词表太窄会把它们
   误判成「无预期」。「期望」这个词是被 13 条 `W2` 打出来的——本库项目章节的**主流
   写法**恰恰是 `# 期望：...`（比「预期」更常用），首版词表里只有「预期」，于是 13 个
   写得好好的页面被判成缺预期。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

E0 = "E0 ROOT_NOT_FOUND"
E1 = "E1 NO_PAGES"
W1 = "W1 NO_EVIDENCE"
W2 = "W2 NO_EXPECTATION"
W3 = "W3 EVIDENCE_ELSEWHERE"

VERIFY_HEAD = re.compile(r"^##\s*[^\n]*验证[^\n]*$", re.M)
H2 = re.compile(r"^## ", re.M)
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})", re.M)
INLINE_CODE = re.compile(r"`([^`\n]+)`")
EXEC_INLINE = re.compile(r"`[^`\n]*[ /(][^`\n]*`")
ASSERT = re.compile(
    r"预期|期望|应输出|应当|应为|应该看到|看到|输出|返回|状态码|断言|报错|失败|成功|"
    r"等于|EXIT|exit code|PASS|PASSED|全绿|通过|一致|相同|⏳|✅"
)
POINTER = re.compile(r"见上文|见下文|见第\s*[一二三四五六七八九十\d]+\s*节|见后文|详见")


def section_body(text: str, start: int) -> str:
    """取 `## 验证…` 之后到下一个 H2 之间的正文（跳过围栏内的假 H2）。"""
    rest = text[start:]
    in_fence = False
    lines = rest.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        if FENCE_OPEN.match(line.strip()):
            in_fence = not in_fence
        if not in_fence and H2.match(line):
            break
        out.append(line)
    return "".join(out)


def classify(body: str) -> str | None:
    has_fence = "```" in body or "~~~" in body
    has_exec = bool(EXEC_INLINE.search(body))
    if not has_fence and not has_exec:
        return W3 if POINTER.search(body) else W1
    if not ASSERT.search(body):
        return W2
    return None


def scan(root: Path, verbose: bool) -> int:
    proj = root / "project"
    if not (root / "docs").is_dir() or not proj.is_dir():
        print(E0, root)
        return 2

    pages = sorted(p for p in proj.rglob("*.md") if p.is_file())
    chapters = [p for p in pages if len(p.relative_to(root).parts) >= 5]
    if not chapters:
        print(E1, "no chapter pages under project/*/*/<Chapter>/")
        return 2

    findings: list[tuple[str, str, str]] = []
    judged = 0
    n1 = 0
    for p in chapters:
        text = p.read_text(encoding="utf-8")
        m = VERIFY_HEAD.search(text)
        if not m:
            n1 += 1
            continue
        judged += 1
        code = classify(section_body(text, m.end()))
        if code:
            findings.append((code, str(p.relative_to(root)), ""))

    order = {W1: 0, W2: 1, W3: 2}
    findings.sort(key=lambda f: (order[f[0]], f[1]))
    for code, path, extra in findings:
        if verbose:
            print(f"{code}\t{path}{extra}")

    counts = {c: sum(1 for f in findings if f[0] == c) for c in (W1, W2, W3)}
    print(
        f"verifyevidencecheck: chapters={len(chapters)} judged={judged} "
        f"N1_NO_SECTION={n1} W1={counts[W1]} W2={counts[W2]} W3={counts[W3]}"
    )
    if not verbose and findings:
        for code, path, _ in findings[:5]:
            print(f"  {code}  {path}")
        if len(findings) > 5:
            print(f"  ... 其余 {len(findings) - 5} 条用 --verbose 查看")
    return 0


# ---------------------------------------------------------------- selftest

SELFTEST_CASES = [
    (
        "无证据：只有一句「确认功能正常」",
        "# T\n\n## 验证方式\n\n确认功能正常。\n",
        W1,
    ),
    (
        "有命令块与预期",
        "# T\n\n## 验证方式\n\n```shell\npnpm build\n```\n\n预期输出：`dist/` 生成且无报错。\n",
        None,
    ),
    (
        "只有命令式行内代码 + 断言词",
        "# T\n\n## 验证方式\n\n执行 `curl -i /api/health`，返回 200 即通过。\n",
        None,
    ),
    (
        "有代码块但没有断言词",
        "# T\n\n## 验证方式\n\n```shell\npnpm build\n```\n",
        W2,
    ),
    (
        "只在注释里写期望（词表要宽）",
        "# T\n\n## 验证方式\n\n```shell\npnpm test  # 全绿\n```\n",
        None,
    ),
    (
        "「期望：」是本库主流写法，必须认",
        "# T\n\n## 验证方式\n\n```shell\npsql -Atc 'select 1;'\n# 期望：1\n```\n",
        None,
    ),
    (
        "围栏里写「期望：」也要认",
        "# T\n\n## 验证方式\n\n```sql\nselect count(*) from t;\n-- 期望：0 行\n```\n",
        None,
    ),
    (
        "只有指路：见第 3 节",
        "# T\n\n## 验证方式\n\n见第 3 节的命令。\n",
        W3,
    ),
    (
        "围栏里的 `## ` 不算下一节（不能被截断）",
        "# T\n\n## 验证方式\n\n```shell\necho '## not a heading'\n```\n\n预期输出：原样打印。\n",
        None,
    ),
    (
        "「验证」出现在节标题中间也算",
        "# T\n\n## 五、验证方式与收尾\n\n`ls dist` 输出存在文件。\n",
        None,
    ),
    (
        "非验证小节不参与判定",
        "# T\n\n## 做了什么\n\n随口一句。\n",
        "SKIP",
    ),
    (
        "空验证节",
        "# T\n\n## 验证方式\n\n## 参考资料\n\n- x\n",
        W1,
    ),
    (
        "URL 形态也认（含斜杠）",
        "# T\n\n## 验证方式\n\n打开 `http://localhost:5173/` 看到列表页。\n",
        None,
    ),
    (
        "代码块内出现 `⏳` 也算预期标记",
        "# T\n\n## 验证方式\n\n```text\nL1 登录 ⏳ 未跑：本机无 Docker\n```\n",
        None,
    ),
]


def selftest() -> int:
    ok = 0
    for name, text, expect in SELFTEST_CASES:
        m = VERIFY_HEAD.search(text)
        if expect == "SKIP":
            got = "SKIP" if m is None else "JUDGED"
        elif m is None:
            got = "NO_SECTION"
        else:
            got = classify(section_body(text, m.end()))
        if got == expect:
            ok += 1
        else:
            print(f"FAIL {name}: expect={expect} got={got}")
    total = len(SELFTEST_CASES)
    print(f"{ok}/{total} {'PASS' if ok == total else 'FAIL'}")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return scan(Path(a.root).resolve(), a.verbose)


if __name__ == "__main__":
    sys.exit(main())
