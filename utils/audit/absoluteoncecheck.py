#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""absoluteoncecheck.py —— 「绝对化可靠性承诺」巡检（第 270 天新立，第一百四十七项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

既有 146 道门围着「页面长什么样」转：链接、标题、表格、容器、图片、判据编号、
时间口径……**没有一道打开正文问「这句话是不是把不可能的承诺当成了结论」**。

事件驱动集成里最常见的一句就是「保证不丢不重」「恰好一次」。这类话在
构建、渲染、链接检查里全部正常，却是读者照着做时会踩的第一坑：
至少一次投递 + 下游幂等才有「恰好一次的效果」，而这句话把两个层的责任
压成了一个形容词。第 270 天实测：去掉 `UNIQUE(event_id)` 后 2% 重放直接多出
1,000 行；去掉 `WHERE lsn < :incoming` 后 59,859 行的新值被旧值覆盖。

## 判据（E = 必须修，W = 登记长尾）

    E0 ROOT_NOT_FOUND     给定根目录不存在
    E1 NO_FILES            一个 Markdown 都没扫到（活性：拒绝在空集上给全绿）
    E2 NO_MATCH            全库一条承诺句都没有（活性：防止匹配器整体失效）
    E3 BARE_EXACTLY_ONCE   「恰好一次 / Exactly-Once」类承诺，同页无任何配套机制
    E4 BARE_ZERO_LOSS      「不丢不重 / 零丢失 / 保证不丢」类承诺，同页无任何配套机制
    W1 ABSOLUTE_WITH_CAVEAT 有配套机制，但措辞仍是绝对化的（提示，不自动改）

## 四条口径（都是为了避免永久红）

1. **代码围栏整段剔除**：用公共 `fenceutil.scan()`，示例里的字符串不算作者主张。
2. **行内代码与链接 URL 剔除**：`` `Exactly-Once` `` 是被引用的术语，`[x](...once)`
   里的路径同理；剥完再匹配。
3. **反例与警示句豁免**：含「不要 / 不是 / 不等于 / 别把 / 所谓 / 其实 / 需要 /
   只有 / 依赖 / 靠 / 条件 / 前提 / 并非 / 做不到」等词的句子，作者已经在给结论
   加限定或提醒读者，再报 E 就是噪声。首版不豁免时，全库 15 篇「恰好一次」
   里有 12 篇是「所谓恰好一次其实是……」这类反例句。
4. **配套机制按「同页」判定，不按「同段」判定**：文档习惯先给结论、后文再展开
   幂等与位点；按段判会把正常写法全判成 E。已有配套但措辞绝对化的，只报 W1，
   把「改措辞」留给人判断，不批量替换正文。

## 与相邻巡检的边界

`secretliteralcheck` 查疑似真实凭据字面量、`timezoneassumptioncheck` 查时间口径、
`enumerclaimcheck` 查「N 条」声明与列表条数；本脚本不碰数字、不碰路径、不碰
版本，只读**可靠性承诺的措辞与它有没有配套机制**。

用法：
    python3 utils/audit/absoluteoncecheck.py [--root docs project] [--selftest] [--top 15]
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402

ONCE_RE = re.compile(r"恰好一次|Exactly[- ]?Once|Exactly[- ]?once|exactly[- ]?once")
LOSS_RE = re.compile(
    r"不丢不重|零丢失|绝不丢|绝不重|保证不丢|保证不重复|不会重复|"
    r"100\s*%\s*可靠|完全不丢|绝不丢失"
)

INLINE_RE = re.compile(r"`[^`\n]*`")
# 整段链接（含链接文字）剔除：书名与章节导航里的术语不是作者主张
LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")

# 反例 / 限定 / 警示：出现即说明作者没有在做绝对化承诺
EXEMPT_WORDS = (
    "反例", "不要", "禁止", "不是", "不等于", "并非", "别把", "不要把", "不能把",
    "所谓", "其实", "做不到", "无法", "不能", "不会自动", "不等于", "并非",
    "需要", "只有", "依靠", "依赖", "靠", "条件", "前提", "效果", "等价于",
    "会", "导致", "坑", "危险", "注意", "避免", "误", "错", "应该", "而非",
    "而不是", "不应", "切勿", "失效", "如果", "若", "一旦", "假设", "假如",
    "当成", "判成", "跳过", "安静的失败", "代价", "换来", "换成", "真相是",
    "本质", "声称", "宣称", "误区", "别写", "写成", "拆成", "收口",
    "不承诺", "不保证", "不宣称", "无法保证", "做不到", "不意味着",
)

# 配套机制：同页出现即认为作者知道这条承诺需要什么
CAVEAT_WORDS = (
    "幂等", "去重", "唯一键", "唯一约束", "UNIQUE", "processed_event",
    "事务", "位点", "至少一次", "条件 upsert", "版本条件", "lsn", "LSN",
    "outbox", "发件箱", "校验和", "对账", "重放", "水位", "死信",
)


def strip_noise(line: str) -> str:
    """剔掉行内代码与整段链接，返回可作为「作者主张」的纯文本。"""
    return LINK_RE.sub("", INLINE_RE.sub("", line))


def is_exempt(sentence: str) -> bool:
    return any(w in sentence for w in EXEMPT_WORDS)


def has_caveat(text_without_fences: str) -> bool:
    return any(w in text_without_fences for w in CAVEAT_WORDS)


def analyze(path: str):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    mask, _, _ = scan(text)
    lines = text.split("\n")
    # 保留真实行号，并把「参考资料」之后的内容整段排除（书名/链接不算主张）
    raw_lines = [(i + 1, strip_noise(lines[i])) for i in range(len(lines)) if i not in mask]
    plain = "\n".join(s for _, s in raw_lines)
    caveat = has_caveat(plain)
    hits, in_refs = [], False
    for lineno, raw in raw_lines:
        s = raw.strip()
        if re.match(r"^#{1,6}\s", s) and "参考资料" in s:
            in_refs = True
        if in_refs:
            continue
        if not s or s.startswith("|") or s.startswith("!["):
            continue  # 表格与图片行不算主张句
        if re.match(r"^#{1,6}\s", s):
            continue  # 章节标题不算主张句
        if is_exempt(s):
            continue
        for rx, code in ((ONCE_RE, "E3"), (LOSS_RE, "E4")):
            if not rx.search(s):
                continue
            if caveat:
                hits.append(("W1", "ABSOLUTE_WITH_CAVEAT", lineno, s[:80], rx.search(s).group()))
            else:
                hits.append((code, "BARE_EXACTLY_ONCE" if code == "E3" else "BARE_ZERO_LOSS",
                             lineno, s[:80], rx.search(s).group()))
    return plain, hits


def walk(roots):
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if name.endswith(".md"):
                    yield os.path.join(dirpath, name)


def check(roots, top=15):
    if not any(os.path.isdir(r) for r in roots):
        print("E0 ROOT_NOT_FOUND 给定根目录都不存在")
        return 1
    files = list(walk(roots))
    if not files:
        print("E1 NO_FILES 一个 Markdown 都没扫到")
        return 1
    errors, warns, total_matches = [], [], 0
    for p in files:
        _plain, hits = analyze(p)
        total_matches += len(hits)
        for code, name, line, snippet, word in hits:
            rec = (code, name, p, line, snippet, word)
            (errors if code.startswith("E") else warns).append(rec)
    if total_matches == 0:
        print("E2 NO_MATCH 全库一条可靠性承诺都没匹配到（匹配器可能失效）")
        return 1
    print(f"absoluteoncecheck pages={len(files)} matches={total_matches} "
          f"E={len(errors)} W={len(warns)}")
    for code in ("E3", "E4"):
        rows = [r for r in errors if r[0] == code]
        for r in rows[:top]:
            print(f"  {r[0]} {r[1]} {r[2]}:{r[3]} 「{r[4]}」 命中={r[5]}")
        if len(rows) > top:
            print(f"  ... 另有 {len(rows) - top} 条 {code}")
    ws = [r for r in warns if r[0] == "W1"]
    for r in ws[:top]:
        print(f"  W1 {r[1]} {r[2]}:{r[3]} 「{r[4]}」 命中={r[5]}")
    if len(ws) > top:
        print(f"  ... 另有 {len(ws) - top} 条 W1")
    return 1 if errors else 0


SELFTEST = [
    # (文本, 期望判据集合)
    ("# 标题\n\n这条链路保证不丢不重。\n", {"E4"}),
    ("# 标题\n\n这条链路保证不丢不重，靠下游幂等与唯一键收口。\n", set()),  # 含「靠」豁免
    ("# 标题\n\n我们提供恰好一次投递，无需额外处理。\n", {"E3"}),
    ("# 标题\n\n所谓「恰好一次」其实是至少一次加下游幂等的效果。\n", set()),
    ("# 标题\n\n不要用「不丢不重」写验收条件。\n", set()),
    ("# 标题\n\n```text\n保证不丢不重\n```\n\n正常说明。\n", set()),
    ("# 标题\n\n术语 `Exactly-Once` 见 [官方文档](https://x/once)。\n", set()),
    ("# 标题\n\n我们提供恰好一次投递。\n\n## 配套\n\n下游有 `UNIQUE(event_id)` 与位点事务。\n", {"W1"}),
    ("# 标题\n\n本页讲至少一次投递与幂等，不承诺不丢不重。\n", set()),
    ("# 标题\n\n系统保证不重复、零丢失。\n", {"E4"}),
]


def selftest() -> int:
    ok = 0
    for i, (text, expect) in enumerate(SELFTEST, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(text)
            path = f.name
        try:
            _plain, hits = analyze(path)
            got = {h[0] for h in hits}
            if got == expect:
                ok += 1
            else:
                print(f"  selftest #{i} FAIL expect={sorted(expect)} got={sorted(got)}")
        finally:
            os.unlink(path)
    # 活性判据：空目录必须报 E1
    with tempfile.TemporaryDirectory() as d:
        rc = check([d])
        if rc == 1:
            ok += 1
        else:
            print("  selftest E1 FAIL 空目录未报错")
    # 活性判据：全库无承诺句必须报 E2
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "a.md"), "w", encoding="utf-8") as f:
            f.write("# 标题\n\n这是一段普通说明，没有可靠性承诺。\n")
        rc = check([d])
        if rc == 1:
            ok += 1
        else:
            print("  selftest E2 FAIL 无命中未报错")
    print(f"selftest {ok}/{len(SELFTEST) + 2}")
    return 0 if ok == len(SELFTEST) + 2 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="+", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return check(a.root, a.top)


if __name__ == "__main__":
    sys.exit(main())
