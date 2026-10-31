#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""relrefcheck.py —— 「相对指代」巡检 · 第 106 项

为什么立这一项
--------------
本库关于「一页之内能不能找到东西」的门已经有五道：

* `headingcheck`      —— H1 唯一、与侧边栏一致；
* `levelskipcheck`    —— 标题不跳级；
* `sectionnumcheck`   —— 章节序号连续；
* `sectionordercheck` —— 「验证 / 判据 / 参考资料」的先后顺序；
* `emptysectioncheck` —— 小节里有没有内容。

五道门全绿，仍然可以写出这样的句子：

    ## 三、容差口径
    ……（正文）……

    ## 四、部分匹配
    详见上一节。

它在**今天**是对的：上一节确实是「容差口径」。但只要有人在这两节之间插一节、
或者把「部分匹配」拆成独立页面，这句话就永久指错——而**构建不会报错、读者不会
举报、作者也早忘了自己写过这一句**。第 105 项（事实日期）解决的是「日期会不会过期」，
这一项解决的是「位置会不会过期」。

判据
----
E0 ROOT_NOT_FOUND      仓库根既没有 docs/ 也没有 project/
E1 NO_PAGES            一个 .md 都没扫到（活性）
E2 NO_REFS             一条位置指代都没解析到（活性：正则写坏了也会全绿）
W1 BARE_POSITIONAL     裸位置指代：同一句里既没有命名锚点（「…」/《…》/`…`/Markdown 链接），
                       也没有页码或小节名，只有「上文 / 下一节 / 如前所述」
W2 NUM_OUT_OF_RANGE    「第 N 节 / 第 N 章」的 N 大于本页 H2 数量（指到不存在的节）
N1 NUMERIC_REFS        数字定位指代总数（计数：它们至少能被核对）
N2 FIGURE_REFS         图表指代总数（「下图 / 上表 / 如表 2」——图在本页内，允许）

口径（四条，全部来自真实语料）
------------------------------
1. **只判「裸」的**。「见《三单匹配与容差》一节」「见[下一节](../InvoiceMatch/index.md)」
   都是好写法：它们自带名字或链接，重排后仍然可解析。**裸位置指代才是负债**，
   把带锚点的一起判，会把每一页都判成问题（首版实测 205 条，其中带锚点的占七成）。
2. **图表指代不算缺陷**。「如下表所示」「见上图」在同页内是稳定的，本库 3,000 多张
   配图大量依赖这种写法；把它们判成 W1 会立刻制造上千条噪声。
3. **围栏与行内代码先剥掉**。示例代码里的 `// 见上一节` 是注释，不是文档结构。
   与第 98 / 104 项同一处理：先剥代码区，再判正文。
4. **N 的上界用 H2 数量，且只对 `docs/` 生效**。本库技术页的章节序号一律用 `## 一、`，
   所以「第 N 节」的上界就是 H2 的个数；`第 N 章` 同理。判 W2 只认「N > H2 数」，
   不判「序号的写法对不对」（那是 `sectionnumcheck` 的事）。`project/` 目录例外：
   那里的「第 26 章」指项目**全局**章节序列（跨页），页内 H2 数不是上界——首轮 36 条
   W2 全部来自 project/，抽查确认后整体豁免，只保留 N1 计数。

用法
----
    python3 utils/audit/relrefcheck.py                 # 扫全库
    python3 utils/audit/relrefcheck.py --root DIR      # 指定根（自测与回归用）
    python3 utils/audit/relrefcheck.py --verbose       # 连 N 类计数一起列
    python3 utils/audit/relrefcheck.py --selftest      # 跑内建用例
退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

# 裸位置指代：不带名字、不带数字，重排一定指错
BARE_RE = re.compile(
    r"(见|如|参)(上文|下文|前文|后文)"
    r"|(如|正|同)(上|前)所述"
    r"|(上一|下一|前一|后一|上|下)(节|章|小节|部分)"
    r"|(本节|本章)(开头|末尾|前面|后面)"
)

# 数字定位：「第 3 节」「第 12 章」——可核对，但可能越界
NUM_RE = re.compile(r"第\s*([0-9]{1,3}|[一二三四五六七八九十]{1,3})\s*(节|章|小节|部分)")

# 图表指代：允许，只计数
FIG_RE = re.compile(r"(如下|见|如)(图|表|上图|下表|前面那张图)")

# 命名锚点：出现任一种即认为「这句话自带坐标」
ANCHOR_RE = re.compile(r"《[^》]{1,40}》|「[^」]{1,40}」|`[^`\n]{1,60}`|\]\([^)]{1,120}\)")

# 数字定位的豁免：句内有跨页链接或书名号时，「第 N 节」指的是**别处**的章节
FOREIGN_RE = re.compile(r"\]\([^)]{1,120}\)|《[^》]{1,40}》|`[^`\n]{1,60}`|[A-Za-z]{4,}")

INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
H2_RE = re.compile(r"^##\s+\S", re.M)

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


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


def _sentences(line):
    """按句末标点切句，返回 [(start, end)]；用于「同一句里有没有锚点」的判定。"""
    spans, start = [], 0
    for i, ch in enumerate(line):
        if ch in "。！？；!?;":
            spans.append((start, i + 1))
            start = i + 1
    if start < len(line):
        spans.append((start, len(line)))
    return spans


def analyse(text, local_scope=True):
    """返回 (w1, w2, numeric_refs, figure_refs)。

    w1: [(lineno, token, sentence)]   裸位置指代
    w2: [(lineno, n, limit)]          数字定位越界

    local_scope=False 时不做 W2 判定：`project/` 下的「第 N 章」指的是项目全局章节
    序列（跨页），页内 H2 数不能当上界——第 106 天首轮 36 条 W2 全部来自这里，
    抽查 `BlogPlatform/ReleaseAcceptance/FAQ` 的「第 26 章引入」确认是跨页指代。
    """
    body = _strip_code(text)
    h2_count = len(H2_RE.findall(body))
    w1, w2, nums, figs = [], [], 0, 0

    for i, line in enumerate(body.split("\n"), start=1):
        if not line.strip():
            continue
        figs += len(FIG_RE.findall(line))
        spans = _sentences(line)
        for m in BARE_RE.finditer(line):
            # 图表指代优先：「如下表」里的「如下」不是位置指代
            tail = line[m.end():m.end() + 2]
            if tail[:1] in ("图", "表"):
                continue
            seg = next((line[a:b] for a, b in spans if a <= m.start() < b), line)
            if ANCHOR_RE.search(seg):
                continue
            w1.append((i, m.group(0), seg.strip()[:60]))
        for m in NUM_RE.finditer(line):
            nums += 1
            seg = next((line[a:b] for a, b in spans if a <= m.start() < b), line)
            if FOREIGN_RE.search(seg):
                continue          # 指向别页 / 别书，页内 H2 数不是它的上界
            raw = m.group(1)
            n = int(raw) if raw.isdigit() else CN_NUM.get(raw, 0)
            if local_scope and n and h2_count and n > h2_count:
                w2.append((i, n, h2_count))
    return w1, w2, nums, figs


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
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = args.root
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND", root)
        return 1

    pages = load_pages(root)
    if not pages:
        print("E1 NO_PAGES", root)
        return 1

    total_w1 = total_w2 = total_num = total_fig = 0
    offenders = []
    for p in pages:
        text = open(p, encoding="utf-8", errors="ignore").read()
        local = os.path.relpath(p, root).startswith("docs" + os.sep)
        w1, w2, nums, figs = analyse(text, local_scope=local)
        total_w1 += len(w1)
        total_w2 += len(w2)
        total_num += nums
        total_fig += figs
        if w1 or w2:
            offenders.append((os.path.relpath(p, root), w1, w2))

    if total_num == 0 and total_fig == 0 and total_w1 == 0:
        print("E2 NO_REFS 全库一条位置指代都没解析到（先确认正则）")
        return 1

    for rel, w1, w2 in sorted(offenders, key=lambda x: -(len(x[1]) + len(x[2])))[: (999 if args.verbose else 12)]:
        for ln, tok, seg in w1:
            print(f"W1 BARE_POSITIONAL  {rel}:{ln}  「{tok}」  {seg}")
        for ln, n, lim in w2:
            print(f"W2 NUM_OUT_OF_RANGE {rel}:{ln}  第 {n} 节，但本页只有 {lim} 个 H2")

    print(
        f"pages={len(pages)} W1={total_w1} W2={total_w2} N1={total_num} N2={total_fig} "
        f"(含指代的页 {len(offenders)})"
    )
    return 0


def _make(root, files):
    for rel, body in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(body)


def selftest():
    cases = []

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n正文。\n\n## 二、乙\n\n正文。\n"})
    cases.append(("干净页（无指代）", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n正文。\n\n## 二、乙\n\n如上所述，这里不再展开。\n"})
    cases.append(("「如上所述」裸指代（W1）", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n见《容差口径》一节。\n"})
    cases.append(("带书名号锚点不报", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n见[下一节](../B/index.md)。\n"})
    cases.append(("带链接锚点不报", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n```python\n# 见上一节\nx = 1\n```\n"})
    cases.append(("围栏里的注释不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n写作时可用 `详见下一节` 这种写法。\n"})
    cases.append(("行内代码里的不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n## 二、乙\n\n## 三、丙\n\n详见第 9 节。\n"})
    cases.append(("第 9 节越界（W2）", d, (0, 1)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n## 二、乙\n\n## 三、丙\n\n详见第 2 节。\n"})
    cases.append(("第 2 节未越界", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n下一节会给出完整表格。\n"})
    cases.append(("「下一节」裸指代（W1）", d, (1, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n如下表所示，三项都为 0。\n"})
    cases.append(("图表指代不算", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"docs/A/index.md": "# 标题\n\n## 一、甲\n\n## 二、乙\n\n## 三、丙\n\n## 四、丁\n\n见第 3 章。\n"})
    cases.append(("「第 3 章」在 4 个 H2 内", d, (0, 0)))

    d = tempfile.mkdtemp()
    _make(d, {"project/Complete/P/index.md": "# 项目\n\n## 一、甲\n\n如前所述，这里略。\n"})
    cases.append(("project 目录也扫（W1）", d, (1, 0)))

    ok = 0
    for name, root, expect in cases:
        w1 = w2 = 0
        for p in load_pages(root):
            a, b, _n, _f = analyse(open(p, encoding="utf-8").read())
            w1 += len(a)
            w2 += len(b)
        got = (w1, w2)
        if got == expect:
            ok += 1
        else:
            print(f"FAIL {name}: got={got} want={expect}")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
