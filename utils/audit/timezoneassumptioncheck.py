#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""timezoneassumptioncheck.py —— 时间口径表述巡检（第一百四十六项巡检）

## 动机

既有 145 道门围着「页面长什么样」转，没有一道打开正文问一句：
**这句话是不是把「固定 UTC 偏移」当成了「时区」，或者把「本地时间」当成了身份？**

这类表述在构建、渲染、链接检查里全部正常，却是跨区系统最主要的线上事故来源。
第 269 天新建「全球化与时区本地化工程」专题时，实测发现：把年初偏移当全年固定偏移，
`America/New_York` 有 65.19% 的小时会错 1 小时；折叠日用本地时间做唯一键会
吞掉 4.00% 的分钟。故立这一项，把这类**主张句**从散文里挑出来。

## 判据（分级 = 修法不同）

  E1 OFFSET_AS_ZONE  固定偏移写法 + 存储/字段语境，且无反例或警示标注（必须修）
  E2 LOCAL_AS_KEY    本地时间 + 唯一键/主键/排序/分区键，且无反例或警示标注（必须修）
  W1 OFFSET_IN_PROSE 固定偏移的普通提及（多为 ISO 时间戳说明，登记不阻断）
  W2 DST_DISMISS     「夏令时」+「忽略/不用考虑」类措辞（可能是无 DST 地区的合法说明）
  E0 ROOT_NOT_FOUND  扫描根不存在（退出码 2）

## 口径（四条，都是为了避免「永久红」）

1. **围栏不算**：代码块里的 `+08:00` 大多是示例时间戳或反例，用 `fenceutil.scan()` 整段剔除。
2. **行内代码与链接 URL 不算**：`` `+08:00` `` 是被引用的写法，不是作者的主张；
   `[x](...+08:00)` 里的字符串同理。
3. **反例与警示句不算**：含「不要 / 禁止 / 错误 / 不是 / 改为 / 正确写法 / 会吞 /
   导致 / 坑 / 注意 / 避免」等词的句子，作者已经在提醒读者，再报 E 就是噪声。
4. **ISO 8601 时间戳里的偏移不算**：`T05:30:00+08:00` 前面紧跟数字或冒号，
   用负向后顾断言排除；它正是正确的写法。

**只报 W 不自动改正文**：口径 3 是文字判断，批量替换必然改坏示例。
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan  # noqa: E402

OFFSET_RE = re.compile(
    r"(?<![0-9:])(?:UTC|GMT)\s*[+-]\s*\d{1,2}(?::\d{2})?|(?<![0-9:])[+-]\d{2}:\d{2}(?![0-9])"
)
INLINE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\]\([^)]*\)")

STORE_WORDS = ("存进", "存入", "存到", "存成", "存为", "落库", "字段", "列名",
               "zone_id", "ZoneId", "写成", "设为")
KEY_WORDS = ("唯一键", "主键", "排序", "分区键", "唯一索引")
DISMISS_WORDS = ("忽略", "不用考虑", "不会发生", "不存在", "没有夏令时", "无需考虑")
EXEMPT_WORDS = (
    "反例", "不要", "禁止", "错误", "不是", "改为", "正确写法", "不能", "不该", "不可",
    "会吞", "导致", "吞掉", "丢", "坑", "危险", "注意", "避免", "误", "错", "应该",
    "而非", "而不是", "不应", "切勿", "别把", "禁止把", "不要把", "不能把", "不该把",
    "错在", "漂移", "安静的失败", "如果", "若", "一旦", "假设", "假如",
    "当成", "判成", "跳过", "跑两次", "失效",
)


def strip_code(line: str) -> str:
    """去掉行内代码与链接 URL，只留散文。"""
    s = INLINE_RE.sub(" ", line)
    s = LINK_RE.sub("] ", s)
    return s


def classify(line: str):
    """返回该行产生的判据列表（可能多条 W）。"""
    s = strip_code(line)
    if not s.strip():
        return []
    exempt = any(w in s for w in EXEMPT_WORDS)
    has_offset = bool(OFFSET_RE.search(s))
    out = []
    if has_offset and any(w in s for w in STORE_WORDS) and not exempt:
        out.append(("E1", "OFFSET_AS_ZONE", s.strip()[:120]))
    if "本地时间" in s and any(w in s for w in KEY_WORDS) and not exempt:
        out.append(("E2", "LOCAL_AS_KEY", s.strip()[:120]))
    if has_offset and not out and not exempt:
        out.append(("W1", "OFFSET_IN_PROSE", s.strip()[:120]))
    if "夏令时" in s and any(w in s for w in DISMISS_WORDS) and not exempt:
        out.append(("W2", "DST_DISMISS", s.strip()[:120]))
    return out


def scan_file(path: str, rel: str, out: list) -> None:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    mask, _, _ = scan(text)
    for i, line in enumerate(text.split("\n")):
        if i in mask or line.lstrip().startswith("|"):
            continue
        for lvl, code, snippet in classify(line):
            out.append((lvl, code, rel, i + 1, snippet))


SELFTEST = [
    # (正文, 期望首条级别或 None)
    ("把 UTC+8 写进 zone_id 字段即可", "E1"),
    ("不要存 +08:00，要存 Asia/Shanghai", None),
    ("把 +08:00 当时区会吞数据", None),
    ("本地时间做唯一键会吞掉折叠日第二条", None),
    ("用本地时间做唯一键", "E2"),  # 没有任何警示词，是应当被抓出的主张句
    ("本地时间可以直接做唯一键", "E2"),
    ("时间戳 2026-11-01T05:30:00+08:00 是合法写法", None),
    ("我们统一按 UTC+8 排期", "W1"),
    ("该地区忽略夏令时切换", "W2"),
    ("```sql\nSELECT '2026-01-01 12:00:00+08:00';\n```", None),
    ("见 `UTC+8` 的说明", None),
    ("不要忽略夏令时，折叠日会重复一小时", None),
]


def selftest() -> int:
    ok = 0
    for idx, (body, want) in enumerate(SELFTEST, 1):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "index.md")
            open(p, "w", encoding="utf-8").write(body)
            out = []
            scan_file(p, "index.md", out)
            got = out[0][0] if out else None
            good = got == want
            ok += good
            print(f"  {'PASS' if good else 'FAIL'}  #{idx:02d} 期望 {want} 实际 {got}")
    print(f"selftest {ok}/{len(SELFTEST)}")
    return 0 if ok == len(SELFTEST) else 1


def run(roots, verbose=False) -> int:
    for r in roots:
        if not os.path.isdir(r):
            print(f"E0 ROOT_NOT_FOUND {r}")
            return 2
    out = []
    pages = 0
    for root in roots:
        for dp, _, fns in os.walk(root):
            for fn in fns:
                if not fn.endswith(".md"):
                    continue
                pages += 1
                p = os.path.join(dp, fn)
                scan_file(p, os.path.relpath(p).replace(os.sep, "/"), out)
    e = [x for x in out if x[0].startswith("E")]
    w = [x for x in out if x[0].startswith("W")]
    for lvl, code, rel, ln, snippet in (out if verbose else e):
        print(f"{lvl} {code} {rel}:{ln} :: {snippet}")
    print(f"pages={pages} matches={len(out)} E={len(e)} W={len(w)} "
          f"(W1={sum(1 for x in w if x[1]=='OFFSET_IN_PROSE')} W2={sum(1 for x in w if x[1]=='DST_DISMISS')})")
    return 1 if e else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="*", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(a.root, a.verbose)


if __name__ == "__main__":
    sys.exit(main())
