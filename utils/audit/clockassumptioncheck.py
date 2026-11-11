#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""clockassumptioncheck.py — 「有没有把墙钟当单调时钟」巡检 · 第 272 天新立，第一百四十九项

## 为什么立这一项

到第 148 项为止，本库有一整族与「时间」有关的门，但它们管的都是**时区与表达**：

* `timezoneassumptioncheck`（第 146 项）—— 固定偏移当成了时区、本地时间当成了唯一键；
* `unitmixcheck`（第 104 项）—— 同一个数换了量纲；
* `factdatecheck` —— 页面里的日期是否过期。

没有一道门问**「这段代码/这段流程拿哪个时钟算时间长度」**。而这一类写法的失败方式极其
隐蔽：机器上的 NTP 每小时磨 0.3 s 的漂移时，`now() - start` 算出来的「耗时 5,000 ms」
可能是 4,996 ms 也可能是 5,011 ms；闰秒那天那一分钟是 61 秒；一次 `step` 回拨让「最近
5 分钟」的窗口变成 5 分 12 秒。构建不报错、渲染正常、链接全通，只有下游的限流、租约、
去重窗口在边界上抖。

第 272 天的实测给了它具体的量级：租约 30 s、双方偏差 5 s 时重叠窗口 **5.0 s（16.7%）**；
偏差 35 s 时 **100%**；去重窗口 300 s 在回拨 90 s 后实际只剩 **210 s（30%）**。

## 判据

活性三条（拒绝空集全绿）：
* `E0 ROOT_NOT_FOUND` / `E1 NO_FILES` / `E2 NO_MATCH`

真缺陷两条：
* `E3 WALLCLOCK_INTERVAL` —— 同一句里既有「时长类词」（超时/间隔/窗口/租约/TTL/重试…）
  又用墙钟 API（`time.time()` / `datetime.now()` / `CURRENT_TIMESTAMP` …）算差值，
  且没有同时给出单调时钟；
* `E4 TIMESTAMP_ORDER_KEY` —— 明确「按时间戳排序 / 以时间戳为序」，但同一句没有配套的
  误差界、单调序号或「同一台机器」限定。

提示两条：
* `W1 MONOTONIC_UNNAMED` —— 整页提到「单调时钟」但从头到尾没点名任何 API
  （`CLOCK_MONOTONIC` / `perf_counter` / `steady_clock` …），读者知道该用却不知道写哪个；
* `W2 SQL_CLOCK_WINDOW` —— SQL 里用 `now() - interval` 算窗口。两侧同源（都是服务端时钟），
  单独看不算缺陷，只在应用侧时钟参与写入时才出问题，所以只提示不报错。

## 四条口径（都是为了避免永久红）

1. **围栏整段剔除**（`fenceutil.scan()`）：代码块里的示例不算作者主张，否则本专题自己的
   反例代码会把门顶红。
2. **反例与警示句豁免**（不要/不能/禁止/误/其实/避免/否则/若/如果/一旦/陷阱）：作者已经在
   提醒读者，再报 E 就是噪声——本库的写法习惯是「先说不该怎么做，再说该怎么做」。
3. **`## 参考资料` 之后整段跳过**：书名与章节导航不是主张。
4. **链接只保留文本**：`[用单调时钟](url)` 的主张在文本里，URL 里的 `now` 不算。

用法：`python utils/audit/clockassumptioncheck.py [--root docs project] [--selftest]`
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

DURATION = re.compile(r"超时|间隔|耗时|窗口|租约|TTL|重试|退避|过期|心跳|冷却|时长")
# E3 只认**应用侧**两个墙钟读数相减：`time.time()` / `datetime.now()` 取的都是本机墙钟，
# 相减得到「时长」正是本项要抓的写法。SQL 侧的 `now() - interval` 两侧同源（都是服务端时钟），
# 单独降为 W2 提示——两者的失效条件不同，混在一个判据里会让存量页面永久飘红。
APP_SUB = re.compile(r"(?:time\.time\(\)|datetime\.now\(\)|Date\.now\(\)"
                     r"|currentTimeMillis|LocalDateTime\.now\(\)|Instant\.now\(\))"
                     r"\s*[-−]"
                     r"|[-−]\s*(?:start|begin|time\.time\(\))\b")
DB_SUB = re.compile(r"(?:\bnow\(\)|\btime\(\)|CURRENT_TIMESTAMP)\s*[-−]"
                    r"|[-−]\s*(?:interval|1 day|1 hour)\b")
MONO = re.compile(r"CLOCK_MONOTONIC|CLOCK_BOOTTIME|perf_counter|monotonic_ns"
                  r"|monotonic\(\)|steady_clock|nanoTime|elapsedRealtime"
                  r"|单调时钟|单调时间|单调序号")
ORDER = re.compile(r"按[^，。；]{0,8}时间戳[^，。；]{0,6}(排序|排|作序)"
                   r"|时间戳[^，。；]{0,6}(作为|当作|用作|做)[^，。；]{0,4}(排序键|顺序|依据)"
                   r"|以时间戳为序|按时间(升序|降序)|按时间戳升序|按时间戳降序")
ORDER_SUPPORT = re.compile(r"误差|误差界|单调|序号|序列号|[Ff]encing|Lamport|逻辑时钟"
                           r"|同一台|本地时钟|同一机器|同机")
MONO_CLAIM = re.compile(r"单调时钟|单调时间")
MONO_API = re.compile(r"CLOCK_MONOTONIC|CLOCK_BOOTTIME|perf_counter|monotonic_ns"
                      r"|monotonic\(\)|steady_clock|nanoTime|elapsedRealtime")
NEG = re.compile(r"不要|不能|禁止|切勿|不要用|误|所谓|其实|避免|否则|若|如果|一旦"
                 r"|陷阱|坑|失效|假象|不许|不该")
# E4 的豁免：这些词说明作者正在讨论「按时间戳排序会错」这件事本身
ORDER_DISCUSS = re.compile(r"逆序|实测|统计|实验|反例|偏差|错")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def collect(root):
    out = []
    for dirpath, _, files in os.walk(root):
        for name in files:
            if name.endswith(".md"):
                out.append(os.path.join(dirpath, name))
    return out


def prose_clauses(text):
    """返回 [(行号 1 基, 句子)]，已剔除围栏、参考资料之后、标题行、链接 URL。"""
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
        line = LINK.sub(r"\1", line)
        for clause in re.split(r"[。；]", line):
            clause = clause.strip()
            if clause:
                out.append((idx + 1, clause))
    return out


def scan_text(text):
    """返回 [(code, lineno, why)]。供 main 与 selftest 共用。

    `W1` 按**整页**判定：一页里只要在别处点名过 API，就不算「知道该用却不知道写哪个」。
    """
    hits = []
    page_has_api = bool(MONO_API.search(LINK.sub(r"\1", text)))
    mono_line = None
    for lineno, clause in prose_clauses(text):
        if NEG.search(clause):
            continue
        if DURATION.search(clause) and APP_SUB.search(clause) and not MONO.search(clause):
            hits.append(("E3", lineno, "WALLCLOCK_INTERVAL",
                         "应用侧墙钟相减算时长，无单调时钟：%s" % clause[:44]))
        elif DURATION.search(clause) and DB_SUB.search(clause) and not MONO.search(clause):
            hits.append(("W2", lineno, "SQL_CLOCK_WINDOW",
                         "SQL 里用 now() 相减算窗口：%s" % clause[:44]))
        if (ORDER.search(clause) and not ORDER_SUPPORT.search(clause)
                and not ORDER_DISCUSS.search(clause)):
            hits.append(("E4", lineno, "TIMESTAMP_ORDER_KEY",
                         "时间戳当排序依据，无误差界/序号：%s" % clause[:48]))
        if MONO_CLAIM.search(clause) and mono_line is None:
            mono_line = lineno
    if mono_line is not None and not page_has_api:
        hits.append(("W1", mono_line, "MONOTONIC_UNNAMED",
                     "全页提到单调时钟但未点名任何 API"))
    return hits


SAMPLES = [
    # (说明, 文本, 期望出现的 code 集合)
    ("空文档：活性", "# 标题\n\n没有正文。\n", set()),
    ("围栏里的墙钟示例不算主张",
     "# t\n\n```python\nelapsed = time.time() - start  # 超时判定\n```\n", set()),
    ("时长词 + 墙钟，无单调：E3",
     "# t\n\n超时判定用 `time.time() - start` 与阈值比较。\n", {"E3"}),
    ("时长词 + 墙钟 + 单调：不报",
     "# t\n\n超时判定用 `time.time() - start`，但窗口长度另用 `CLOCK_MONOTONIC` 计。\n", set()),
    ("只有墙钟没有时长词：不报",
     "# t\n\n页面右上角展示 `datetime.now()` 的结果。\n", set()),
    ("绝对时刻比较不算间隔：不报",
     "# t\n\n过期未清：`ends_at < now()` 但仍处于启用状态。\n", set()),
    ("相减但没点名 API：不报",
     "# t\n\n整数相减得到时长，跨日不存在负值问题。\n", set()),
    ("SQL 里 now() 相减只提示：W2",
     "# t\n\n窗口取 `created_at >= now() - interval '1 day'`。\n", {"W2"}),
    ("反例句豁免",
     "# t\n\n不要用 `time.time()` 算超时，否则 NTP 一次 step 就让窗口变成 5 分 12 秒。\n", set()),
    ("时间戳排序无配套：E4",
     "# t\n\n跨机日志按时间戳排序后即可还原因果。\n", {"E4"}),
    ("时间戳排序带误差界：不报",
     "# t\n\n跨机日志按时间戳排序，但每条同时存误差界，重叠的两条不许断言先后。\n", set()),
    ("单调时钟无 API：W1",
     "# t\n\n计算间隔应当使用单调时钟。\n", {"W1"}),
    ("单调时钟带 API：不报",
     "# t\n\n计算间隔应当使用单调时钟（`CLOCK_MONOTONIC`）。\n", set()),
    ("参考资料之后跳过",
     "# t\n\n## 参考资料\n\n- 超时判定用 `time.time()` 的旧写法\n", set()),
    ("标题行跳过",
     "# 超时判定用 `time.time()`\n\n正文无关。\n", set()),
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
    ap.add_argument("--top", type=int, default=10)
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
