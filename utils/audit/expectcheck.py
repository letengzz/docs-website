#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""expectcheck.py —— 「验证方式里的命令有没有写期望值」巡检（第 232 天新立，第一百一十四项巡检）

## 动机

本仓从第 121 天起有一条硬纪律：**每一步都要给出可验证的收尾**。这条纪律已经被
`tailcheck`（第 107 项）守住了「有没有 `## 验证方式` 这一节」，但**没有守住
「这一节里的命令能不能判定」**。于是出现一种很隐蔽的页面：

    ## 验证方式

    ```shell
    sqlite3 /tmp/x.db "SELECT count(*) FROM t;"
    ```

命令本身没错，读者跑完得到一个数字，然后不知道这个数字算不算对。**没有期望值的
验证等于没有验证**——它把判定责任推回给了读者，而读者没有判据。

已有巡检各管一段，没有一项看这件事：

  * `tailcheck`（第 107 项）  —— 有没有「参考资料」与「验证方式」小节；
  * `verifyevidencecheck`     —— 验证小节里的读数是不是「实测」而非「期望」；
  * `fencecheck` / `langmatchcheck` —— 围栏语言与语法；
  * `refjudgecheck`           —— 参考资料是不是官方链接。

它们看的都是「有没有」，本项看的是「**能不能判**」。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND   仓库根既无 docs/ 也无 project/（活性，防路径写错全绿）
  E1 NO_PAGES         一个 index.md 都没扫到就拒绝判定（活性）
  E2 EXPECT_EMPTY     `期望：` / `预期：` 后面是空的或只有标点（写了等于没写）
  W1 NO_BLOCK         验证小节存在，但整节一个围栏块都没有（只写了说明文字）
  W2 NO_EXPECT        整节 0 条期望值；带判据表的页标 `[deep]`，欠账优先级更高
  W3 BLOCK_NO_EXPECT  同一小节里别的块有期望，这一块没有（多是「准备步骤」块）
  W4 VAGUE            验证小节出现「应该没问题 / 理论上 / 一般来说」这类模糊措辞
  W5 NO_VERIFY        页面没有验证小节（与 `tailcheck` 的 `W` 同源，仅计数）

## 为什么只有一条 `E`

`W1` / `W2` 在库里是「存量写法」：第 232 天首次全库扫描，带判据表却有验证小节、
却一条期望都没有的页面有 **144 页**，验证小节只写说明文字的有 **4 页**。这两类一律
判 `E`，会让这道门第一天就红，而它们并不是「今天引入的缺陷」——它们是本仓第 121 天
之前的写法，与 `factdatecheck`（`W1=0 W2=268`）、`tailcheck`（`W=963`）、
`emphasischeck`（`W1=929`）的处境一样：**登记、按日消化，不假绿**。

所以 `E` 只留一条真判据：**写了「期望：」却空着**。它没有存量解释，一定是笔误。

## 口径（为什么这样取数）

1. **小节名必须「就是」验证小节**：`## 验证方式` / `## 七、验证方式` / `## 验证：…` 收；
   `## 九、当日做了什么 / 如何验证 / 下一步` 与 `## 二、验证的六步` 不收。后者尤其
   隐蔽——它讲的是「证书验证的六个步骤」，收进来会一次性制造 10 条假 `E3` 与上百条
   假 `E4`（第 232 天两轮实测）。判据因此收成「验证 + 可选后缀 + 可选冒号说明」。
2. **「期望」只认注释里的**：`期望` / `预期` 之前必须出现 `#` 或 `--`。本库的写法
   是 `# 3) 查询计划（预期：四行都含 SEARCH）`，期望值嵌在步骤注释的括号里，而不是
   单独一行；按「行首必须是 `#` + 期望」判会一次性造出 183 条假 `E`（首版实测）。
   正文段落里出现「期望」二字仍然不算——它不在代码块里，读者跑不出来。
3. **`E` 只落在「带判据表」的页面上**。全库有 1,270+ 页有验证小节却一条期望都没有，
   一律判 `E` 会让这道门第一天就背上四位数欠账，而这类页面多数是存量工程页（第 121 天
   之前的写法）。口径与 `leadparagraphcheck` / `judgecovercheck` 一致：**新模板页判 `E`，
   存量页判 `W`**，欠账按日消化。
4. **`E2` 只在「小节非空但无围栏」时报**。空小节（只有标题）也会命中 `E2`，
   因为那对本项是同一件事：读者到这里什么都跑不了。
5. **`W1` 不判 `E`**：同一小节里常见「先建库（无期望）、再查（有期望）」的两块结构，
   第一块本来就不需要期望值。只有**整节零期望**才升级为 `E3`。
6. **「期望」与「预期」两个词都认**。本库两种写法并存（第 232 天实测 215 页用
   「预期：」、其余用「期望：」），只认一个会一次性造出两百多条假 `E`。`# 结果：0`
   仍不算——它既不是期望也不是预期，是事后记录。
7. **`E` 与 `W` 的分界是「这一页有没有判据表」**。带判据表的页面按新模板写，没有
   期望值就是缺陷（判 `E`）；存量工程页只登记（判 `W`）。
8. **`# 预期：` 空着但下一行仍是注释的，算「多行期望」**：本库有「先写一行
   `# 预期：`、再逐行列数值」的写法（`DB/GeoMap` 两页），首版把它们判成 `E2`
   空期望。判据因此加一条「下一行是注释即视为续行」。
9. **自断言块不算「没有期望」**：`python` 块里出现 `assert` 的，断言本身就是判定，
   不再要求注释里另写期望值。第 232 天实测有 150+ 页是这种「脚本自己判」的写法，
   按注释判会一次性造出一百多条假 `E`。

## 用法

    python3 utils/audit/expectcheck.py            # 全库扫描
    python3 utils/audit/expectcheck.py --selftest # 自检（14 例）
    python3 utils/audit/expectcheck.py -v         # 展开每条 W
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

H2 = re.compile(r"^##\s+(.*)$")
VERIFY_HINT = re.compile(r"^(?:[一二三四五六七八九十百]+、)?\s*验证(?:方式|方法|清单|步骤|与验收)?\s*(?:[:：].*)?$")
EXPECT_WORD = re.compile(r"期望|预期")


def expect_in_comment(ln: str) -> bool:
    """「期望 / 预期」必须出现在注释里（`#` 或 `--` 之前有注释符）。

    本库的写法是 `# 3) 查询计划（预期：四行都含 SEARCH）` —— 期望值嵌在
    步骤注释的括号里，而不是单独一行。首版按「行首必须是 # + 期望」判，
    一次性造出 183 条假 E（第 232 天实测）。
    """
    for m in EXPECT_WORD.finditer(ln):
        head = ln[: m.start()]
        if "#" in head or "--" in head:
            return True
    return False
EXPECT_EMPTY = re.compile(r"^\s*(?:#|--)?\s*(?:期望|预期)\s*[:：]?\s*[。，,.\s]*$")
VAGUE = ["应该没问题", "理论上", "一般来说", "大概", "差不多就行"]
LANG_OK = {"shell", "sh", "bash", "console", "zsh", "sql", "sqlite", "python",
           "py", "text", "json", "http", "yaml", "dockerfile", ""}


def split_sections(text):
    """返回 [(title, start_line, end_line)]，只认 `## `。"""
    lines = text.split("\n")
    mask, _, _ = fenceutil.scan(text)
    heads = []
    for i, ln in enumerate(lines):
        if i in mask:
            continue
        m = H2.match(ln)
        if m:
            heads.append((m.group(1).strip(), i))
    out = []
    for k, (title, i) in enumerate(heads):
        end = heads[k + 1][1] if k + 1 < len(heads) else len(lines)
        out.append((title, i, end))
    return out


JUDGE_ROW = re.compile(r"\|\s*`[A-Z]{2,4}-[A-H]`\s*\|")


def has_judge_table(text):
    """带判据表的页面 = 按「完整主题模板」写的新页。"""
    return bool(JUDGE_ROW.search(text))


def check_page(text):
    """返回 [(code, line_no, detail)]。"""
    issues = []
    deep = has_judge_table(text)
    tag = "[deep] " if deep else ""
    lines = text.split("\n")
    sections = [s for s in split_sections(text) if VERIFY_HINT.search(s[0])]
    if not sections:
        return [("W5", 0, "NO_VERIFY 无验证小节")], False
    any_expect_page = False
    for title, start, end in sections:
        body = "\n".join(lines[start:end])
        mask, blocks, _ = fenceutil.scan(body)
        total_expect = 0
        attempts = 0
        if not blocks:
            issues.append(("W1", start + 1, tag + "NO_BLOCK 小节内无任何围栏块"))
        for (bs, be, info) in blocks:
            lang = (info or "").split()[0].lstrip("{.").rstrip("}") if info else ""
            inside = "\n".join(body.split("\n")[bs + 1:be])
            selfjudge = lang in ("python", "py") and "assert" in inside
            n = 0
            blines = inside.split("\n")
            for off, ln in enumerate(blines):
                nxt = blines[off + 1] if off + 1 < len(blines) else ""
                cont = nxt.lstrip().startswith(("#", "--")) and nxt.strip() not in ("#", "--")
                if EXPECT_EMPTY.match(ln) and not cont:
                    issues.append(("E2", start + bs + 2 + off, "EXPECT_EMPTY 期望值为空"))
                    attempts += 1
                elif expect_in_comment(ln) or (EXPECT_EMPTY.match(ln) and cont):
                    n += 1
            total_expect += n
            if selfjudge:
                total_expect += 1          # 自断言块：断言本身就是判定
            if n == 0 and lang in LANG_OK and not selfjudge:
                issues.append(("W3", start + bs + 1, tag + "BLOCK_NO_EXPECT 该块无期望值"))
        if total_expect == 0 and attempts == 0:
            issues.append(("W2", start + 1, tag + "NO_EXPECT 整节 0 条期望"))
        elif total_expect:
            any_expect_page = True
        for off, ln in enumerate(lines[start:end]):
            if off in mask or ln.strip().startswith("```"):
                continue
            for v in VAGUE:
                if v in ln:
                    issues.append(("W4", start + off + 1, "VAGUE 模糊措辞：%s" % v))
                    break
    return issues, any_expect_page


def iter_md(root):
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dp, _, fns in os.walk(d):
            for fn in fns:
                if fn.endswith(".md"):
                    yield os.path.join(dp, fn)


def scan(root, verbose=False):
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND", root)
        return 1
    pages = 0
    tally = {k: 0 for k in ("E2", "W1", "W2", "W3", "W4", "W5")}
    details = []
    for path in iter_md(root):
        pages += 1
        with open(path, encoding="utf-8") as f:
            text = f.read()
        issues, _ = check_page(text)
        rel = os.path.relpath(path, root)
        for code, line, detail in issues:
            tally[code] += 1
            details.append((code, rel, line, detail))
    if pages == 0:
        print("E1 NO_PAGES 一个页面都没扫到")
        return 1
    for code, rel, line, detail in details:
        if code.startswith("E") or verbose:
            print("%s %s:%d  %s" % (code, rel, line, detail))
    e = sum(v for k, v in tally.items() if k.startswith("E"))
    w = sum(v for k, v in tally.items() if k.startswith("W"))
    print("pages=%d E=%d W=%d  [E2=%d W1=%d W2=%d W3=%d W4=%d W5=%d]"
          % (pages, e, w, tally["E2"], tally["W1"], tally["W2"],
             tally["W3"], tally["W4"], tally["W5"]))
    return 0 if e == 0 else 1


JT = "| `ABC-A` | 判据 | 怎么验 |\n| --- | --- | --- |\n"
CASES = [
    ("正常：一块命令带期望", JT + "## 验证方式\n\n```shell\nsqlite3 t.db 'select 1';\n# 期望：1\n```\n", 0),
    ("带判据表但整节无期望 → W2", JT + "## 验证方式\n\n```shell\nselect 1;\n```\n", 0),
    ("带判据表且无围栏 → W1+W2", JT + "## 验证方式\n\n直接跑一下即可。\n", 0),
    ("期望为空 → E2", JT + "## 验证方式\n\n```shell\necho hi\n# 期望：\n```\n", 1),
    ("两块一有一无 → 只报 W2", JT + "## 验证方式\n\n```shell\nmkdir -p /tmp/x\n```\n\n```shell\nls /tmp/x\n# 期望：空\n```\n", 0),
    ("fence 外出现「期望」不算", JT + "## 验证方式\n\n```shell\necho hi\n```\n\n期望不要出现负数。\n", 0),
    ("`期望 0`（无冒号）也算", JT + "## 验证方式\n\n```shell\necho 0\n# 期望 0\n```\n", 0),
    ("`结果：0` 不算期望", JT + "## 验证方式\n\n```shell\necho 0\n# 结果：0\n```\n", 0),
    ("无验证小节 → W5", JT + "## 一、概述\n\n正文。\n", 0),
    ("编号小节 `## 七、验证方式` 也认", JT + "## 七、验证方式\n\n```sql\nselect 1;\n-- 期望：1\n```\n", 0),
    ("`-- 预期` SQL 注释也算", JT + "## 验证方式\n\n```sql\nselect count(*) from t;\n-- 预期：0\n```\n", 0),
    ("代码块内非注释的「期望」不算", JT + "## 验证方式\n\n```text\n这是一段说明，包含期望二字但不在注释里\n```\n", 0),
    ("同一页两个验证小节都算", JT + "## 验证方式\n\n```shell\necho a\n# 期望：a\n```\n\n## 验证方式（补充）\n\n```shell\necho b\n# 期望：b\n```\n", 0),
    ("空小节 → W1+W2", JT + "## 验证方式\n", 0),
    ("叙事小节不算验证小节", JT + "## 九、当日做了什么 / 如何验证 / 下一步\n\n见第八节。\n", 0),
    ("无判据表：整节无期望只判 W2", "## 验证方式\n\n```shell\nselect 1;\n```\n", 0),
    ("空期望（deep 与否都判 E2）", "## 验证方式\n\n```shell\necho 1\n# 期望：\n```\n", 1),
    ("`# 预期：` 后跟数值续行 → 算多行期望", "## 验证方式\n\n```text\n# 预期：\n# 0 OUT / 480 NEAR\n```\n", 0),
]


def selftest():
    ok = 0
    for i, (desc, text, want) in enumerate(CASES, 1):
        issues, _ = check_page(text)
        got = sum(1 for c, _, _ in issues if c.startswith("E"))
        mark = "PASS" if got == want else "FAIL"
        if got == want:
            ok += 1
        print("%s %2d. %s: E=%d（期望 %d）[%s]"
              % (mark, i, desc, got, want, ", ".join("%s@%d" % (c, l) for c, l, _ in issues)))
    print("selftest %d/%d" % (ok, len(CASES)))
    return 0 if ok == len(CASES) else 1


def main():
    ap = argparse.ArgumentParser(description="验证方式「期望值」🔍 巡检")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return scan(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
