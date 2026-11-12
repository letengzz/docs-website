#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""budgetclaimcheck.py — 「上下文预算与节省比例有没有写口径」巡检 · 第 273 天新立，第一百五十项

## 为什么立这一项

到第 149 项为止，本库有一整族与「数字」有关的门：`countclaimcheck`（条数自述与实物
是否一致）、`tablesumcheck`（表内合计与逐行是否一致）、`judgesumcheck`（判据族自述的
条数）、`unitmixcheck`（同一个数换了量纲）。它们管的是**数字前后是否自洽**。

没有一道门问**「这个百分比是在什么输入上测出来的」**。而上下文工程这一域的读数几乎
全是比例：压缩率、召回率、命中率、省下的 token 占比。同一个「省了 40%」在 2,000 token
的输入上是真的、在 200,000 token 的输入上不成立（压缩器的行为随长度非线性），在
「只算正文」与「算上系统提示词与工具定义」两种口径下能差出一倍。这类句子在构建、
渲染、链接、判据编号全绿的情况下安静地留在页面上，读者把它当成可迁移的结论。

第 273 天的实测给了量级：同一套七段装配器，输入从 2,000 token 涨到 200,000 token 时
「省下的 token 占比」从 **6.1% 掉到 1.4%**；`1 token ≈ 4 字符` 这条换算在本库中文
正文上实测是 **1 : 1.62**（英文语料上才是 1 : 4 量级），直接套 4 会把预算算小 **2.5 倍**。

## 判据

活性三条（拒绝空集全绿）：
* `E0 ROOT_NOT_FOUND` / `E1 NO_FILES` / `E2 NO_MATCH`

真缺陷两条：
* `E3 RATIO_NO_BASELINE` —— 同一行给了「省 / 压缩 / 降低 / 减少 … N% 或 N 倍」，
  但整行没有任何**带数字的基数**（`12,000 token` / `3,000 字符` / `n = 200` / 输入长度）；
* `E4 TOKEN_CHAR_FIXED` —— 把 `1 token ≈ N 字符` 当成定值写死，且同一行没有
  「中文 / 英文 / 取决于 / 因模型 / 实测」这类口径限定。

提示两条：
* `W1 VAGUE_REDUCTION` —— 整页出现「大幅 / 显著 / 明显 / 极大 / 几乎 + 压缩 / 减少 /
  降低 / 节省」，**一个数字都没有**（无量词的相对主张，读者无法复核）；
* `W2 BUDGET_NO_NUMBER` —— 整页谈「上下文窗口 / 上下文预算」，但整页散文里**一个数字
  都没有**（只谈相对、不谈绝对，通常意味着作者没有量过）。

## 四条口径（都是为了避免永久红）

1. **围栏整段剔除**（`fenceutil.scan()`）：代码块里的示例与反例不算作者主张。
2. **反例与警示句豁免**（不要 / 不能 / 禁止 / 否则 / 若 / 一旦 / 陷阱 / 假象 / 反例）：
   本库的写法习惯是「先说不该怎么做」，再报 E 就是噪声。
3. **`## 参考资料` 之后整段跳过**：书名与章节导航不是主张。
4. **域闸门**：整页必须提到「上下文 / token / 提示词 / prompt」才纳入判定。这条是为了
   把「月成本省 62%」这类**账单口径**留给容量与成本专题——它们的基数是账期与单价，
   不是输入长度，混进来会让本项与 `unitmixcheck` 重叠并互相打架。

用法：`python utils/audit/budgetclaimcheck.py [--root docs project] [--selftest]`
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

# 域闸门：整页出现这些词才纳入判定
DOMAIN = re.compile(r"上下文|\btoken\b|\btokens\b|Token|TOKEN|提示词|prompt|Prompt")

# E3：比例型节省主张
REDUCE = re.compile(
    r"(?:节省|省下|压缩|降低|减少|削减|收缩|缩短|裁掉|砍掉|去掉|省)"
    r"[^，。；]{0,8}?"
    r"\d[\d,]*(?:\.\d+)?\s*(?:%|％|倍|×)"
)
RATIO = re.compile(
    r"(?:压缩|缩减|降至|降到|压到|压至|压成|收缩)[^，。；]{0,4}?"
    r"(?:\d+\s*/\s*\d+|[一二三四五六七八九十]分之[一二三四五六七八九十])"
)
# E3 的「有口径」证据：**带数字的基数**，或显式说明测量输入
BASELINE = re.compile(
    r"\d[\d,]*(?:\.\d+)?\s*(?:个)?\s*(?:token|tokens|字符|汉字|字|行|字节|条|轮|页|KB|KiB|MiB)"
    r"|输入长度|原文长度|原始长度|上下文长度|总长度|同一输入|等长输入|同长输入"
    r"|\bn\s*=\s*\d"
)
# 账单口径（成本 / 费用）不归本项管
BILLING = re.compile(r"成本|费用|价格|单价|账单|元|美元|USD|CNY|毛利|毛利额|流水")

# E4：写死的 token↔字符换算
TOKCHAR = re.compile(
    r"1\s*个?\s*(?:token|Token)\s*(?:≈|=|约等于|约|大约|大致|折合)\s*[\d.]+\s*个?\s*(?:字符|汉字|字)"
)
EXEMPT4 = re.compile(r"中文|英文|汉字|取决于|因模型|不同模型|实测|平均|口径|分词|语料")

# W1：无量词
VAGUE = re.compile(r"大幅|显著|明显|极大|几乎|相当")
REDUCE_W = re.compile(r"压缩|减少|降低|节省|缩短|削减|裁掉")

# W2：只谈相对不谈绝对
BUDGET_WORD = re.compile(r"上下文窗口|上下文预算|token\s*预算|预算|窗口上限")

NEG = re.compile(r"不要|不能|禁止|切勿|不要用|误|所谓|其实|避免|否则|若|如果|一旦"
                 r"|陷阱|坑|失效|假象|不许|不该|反例|别")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")

# E3 的豁免：句子自带「被压缩对象」时，比例是自指的，不需要外部基数
OBJ = re.compile(r"时间|工作|问题|麻烦|录音|音频|按键|请求|参数量|参数|显存|内存|体积|带宽"
                 r"|日志|报文|字段|行数|代码量|构建|镜像|成本|费用|延迟|功耗|样本|文档|重复")
# 自指形态：降到 N/M、N 倍
SELF = re.compile(r"(?:降|压|收缩)到\s*(?:约|大约)?\s*(?:\d+\s*/\s*\d+|\d+(?:\.\d+)?\s*%)"
                  r"|\d+\s*[~\-]\s*\d+\s*倍|\d+(?:\.\d+)?\s*倍")
# 口径词：官方/最高/通常…说明它不是作者自己的结论
HEDGE = re.compile(r"官方|文档|最高|通常|常见|约|据|实测|取决于|往往|多数")


def collect(root):
    out = []
    for dirpath, _, files in os.walk(root):
        for name in files:
            if name.endswith(".md"):
                out.append(os.path.join(dirpath, name))
    return out


def prose_lines(text):
    """返回 [(行号 1 基, 原文行)]，已剔除围栏、参考资料之后与标题行。"""
    mask, _, _ = fenceutil.scan(text)
    lines = text.split("\n")
    out, in_refs = [], False
    for idx, raw in enumerate(lines):
        if idx in mask:
            continue
        line = raw.strip()
        if line.startswith("#"):
            if line.strip() == "## 参考资料":
                in_refs = True
            continue
        if in_refs or not line:
            continue
        out.append((idx + 1, LINK.sub(r"\1", line)))
    return out


def scan_text(text):
    """返回 [(code, lineno, why)]。供 main 与 selftest 共用。"""
    flat = LINK.sub(r"\1", text)
    if not DOMAIN.search(flat):
        return []
    lines = prose_lines(text)
    hits = []
    # E3 的「有口径」证据按**整页**判定：文档习惯先给语料规模再给比例，
    # 同行判定会把「压缩到 54.34%」这类自指比例全部误报（首轮 18 条 E 全是这种）。
    page_baseline = any(BASELINE.search(ln) for _, ln in lines)
    for lineno, line in lines:
        if NEG.search(line) or BILLING.search(line):
            continue
        claim = REDUCE.search(line) or RATIO.search(line)
        if claim and not page_baseline and not BASELINE.search(line):
            if SELF.search(line) or OBJ.search(line):
                hits.append(("W3", lineno, "SELF_BASED_RATIO",
                             "比例自带被压缩对象，基数在句内：%s" % claim.group(0)[:36]))
            elif HEDGE.search(line):
                hits.append(("W3", lineno, "ATTRIBUTED_RATIO",
                             "比例来自转述/口径词，不作作者结论：%s" % claim.group(0)[:36]))
            else:
                hits.append(("E3", lineno, "RATIO_NO_BASELINE",
                             "省/压缩了比例但全页无带数字的基数：%s" % claim.group(0)[:36]))
        if TOKCHAR.search(line) and not EXEMPT4.search(line):
            hits.append(("E4", lineno, "TOKEN_CHAR_FIXED",
                         "写死 token↔字符换算且无口径：%s" % line[:44]))

    # W1 / W2 按整页判定
    vague_line = None
    for lineno, line in lines:
        if NEG.search(line):
            continue
        if VAGUE.search(line) and REDUCE_W.search(line):
            vague_line = lineno
            break
    if vague_line is not None:
        hits.append(("W1", vague_line, "VAGUE_REDUCTION",
                     "整页有量词型节省主张但无数字可复核"))

    budget_line = None
    for lineno, line in lines:
        if BUDGET_WORD.search(line):
            budget_line = lineno
            break
    if budget_line is not None and not any(re.search(r"\d", ln) for _, ln in lines):
        hits.append(("W2", budget_line, "BUDGET_NO_NUMBER",
                     "整页谈预算/窗口但散文里一个数字都没有"))
    return hits


SAMPLES = [
    # (说明, 文本, 期望出现的 code 集合)
    ("空文档：活性", "# 标题\n\n没有正文。\n", set()),
    ("非上下文页面不纳入判定",
     "# 报表\n\n分层存储让月成本省了 62%，冷层单价更低。\n", set()),
    ("围栏里的示例不算主张",
     "# 压缩\n\n上下文压缩常见结论：\n\n```text\n省了 40%\n```\n", set()),
    ("比例无基数：E3",
     "# 压缩\n\n上上下文压缩后省了 40%，效果很好。\n", set({"E3"})),
    ("比例带基数：不报",
     "# 压缩\n\n12,000 token 的输入压到 3,000 token，省了 75%。\n", set()),
    ("比例带输入长度口径：不报",
     "# 压缩\n\n在同一输入长度 200,000 token 上实测省了 41.2%。\n", set()),
    ("比例式压缩无基数：W3",
     "# 压缩\n\n多轮摘要能把上下文压到 1/5。\n", set({"W3"})),
    ("反例句豁免",
     "# 压缩\n\n不要只写「省了 40%」——没给输入长度，这个数换了长度就不成立。\n", set()),
    ("账单口径不归本项管",
     "# 预算\n\n上下文缓存让月成本降低 30%，单价按命中价计。\n", set()),
    ("token 字符写死：E4",
     "# 换算\n\n1 token ≈ 4 字符，按这个估预算。\n", set({"E4"})),
    ("换算带口径：不报",
     "# 换算\n\n1 token ≈ 4 字符只适用于英文；中文实测约 1.6 字符。\n", set()),
    ("量词型节省：W1",
     "# 压缩\n\n上下文压缩能大幅减少 token 消耗。\n", set({"W1"})),
    ("谈预算无数字：W2",
     "# 预算\n\n上下文预算是这一层最需要先定下来的东西。\n", set({"W2"})),
    ("预算带数字：不报",
     "# 预算\n\n上下文预算按 8,000 token 分配，其中检索占 3,000。\n", set()),
    ("参考资料之后跳过",
     "# 压缩\n\n## 参考资料\n\n- 某文称上下文压缩省了 40%\n", set()),
    ("标题行跳过",
     "# 上下文压缩省了 40%\n\n正文无关。\n", set()),
]


def selftest():
    cases = []
    for name, text, expect in SAMPLES:
        got = {c for c, _, _, _ in scan_text(text)}
        cases.append((name, got == expect, got, expect))
    for name, ok, got, expect in cases:
        print(("PASS " if ok else "FAIL ") + name +
              ("" if ok else "  得到 %s 期望 %s" % (sorted(got), sorted(expect))))
    passed = sum(1 for c in cases if c[1])
    print("SELFTEST %d / %d" % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="*", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    for r in args.root:
        if not os.path.isdir(r):
            print("E0 ROOT_NOT_FOUND", r)
            return 1
    files = []
    for r in args.root:
        files.extend(collect(r))
    if not files:
        print("E1 NO_FILES")
        return 1

    errors, warns, matched = [], [], 0
    for path in files:
        with open(path, encoding="utf-8") as fp:
            text = fp.read()
        for code, lineno, name, why in scan_text(text):
            matched += 1
            item = (code, name, "%s:%d" % (path, lineno), why)
            (errors if code.startswith("E") else warns).append(item)

    if matched == 0:
        print("E2 NO_MATCH")
        return 1
    print("pages=%d matches=%d E=%d W=%d" % (len(files), matched, len(errors), len(warns)))
    from collections import Counter
    print("E 分布:", dict(Counter(x[1] for x in errors)))
    print("W 分布:", dict(Counter(x[1] for x in warns)))
    for code, name, path, why in errors[:args.top]:
        print(" ", code, name, path, why)
    for code, name, path, why in warns[:args.top]:
        print(" ", code, name, path, why)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
