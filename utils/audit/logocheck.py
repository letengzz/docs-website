#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logocheck.py —— 主题首页 Logo 的形态巡检（第 240 天新立，第一百二十二项巡检）

## 动机（本仓「一条硬性写作规定没人看」的第 N 次）

`AGENTS.md` 第 7 节第 8 条把主题首页的 Logo 写成了硬要求：

> 每个技术主题的**首页（`index.md`）必须放置该技术的官方 Logo**：Logo 使用 **PNG 格式**，
> 下载到主题 `assets/`（如 `assets/nginx-logo.png`），并用既有缩放写法
> `<p style="text-align:center;"><img src="./assets/xxx-logo.png" style="zoom:75%;" /></p>`
> 统一缩放到 **75%** 且**水平居中**（注意 `./` 前缀，否则 VitePress 构建无法解析）。

这条规定有五个可判的点（有 Logo / 是 PNG / 居中 / 75% / 带 `./`），而既有的门一道都不看：

  * `imageorigincheck`（第 98 项）—— 看图片路径的形态（相对 / 绝对 / 外链），不认「这一页该不该有图」；
  * `orphanassetcheck` —— 看 assets 里有没有没人引用的文件，方向相反；
  * `imagebytescheck` —— 看图片文件本身（大小、尺寸），不看引用写法；
  * `linkexistcheck` —— 看目标文件在不在，不看它是不是 Logo、是不是 PNG；
  * `altqualitycheck` —— 看 alt 文案，Logo 的 alt 恰好是最容易被写成空的地方。

于是五件事可以同时全错而全绿：首页放了一张 `logo.svg`（AGENTS 要求 PNG）、没居中、
`zoom:50%`、路径写成 `/assets/...`（构建期解析不到）、图片文件其实不存在——
`pnpm docs:build` 只会因为最后一条（且在 `ignoreDeadLinks` 之外）报错，其余四条静默。

**为什么「没居中 / 没缩放」值得单独成项**：Logo 是主题的识别锚点。一张 512 px 的 PNG
按原尺寸铺在正文里，会把首屏挤满，读者第一眼看到的是一张巨大的图而不是「这是什么技术」；
反过来缩到 10%，Logo 上的文字就不可读。75% 是这一仓反复用出来的取值，统一才有视觉一致性。

## 判据（三真 + 四提示）

  * `E0 ROOT_NOT_FOUND`  —— 仓库根既无 `docs/` 也无 `project/`；
  * `E1 NO_PAGES`        —— 一页主题首页都没扫到就拒绝判定（活性，防「路径写错全绿」）；
  * `E2 LOGO_NOT_PNG`    —— Logo 引用的不是 `.png`（写成 `.svg` / `.jpg` / 无扩展名）；
  * `E3 EXTERNAL_LOGO`   —— Logo 用了外链（`http(s)://`），离线/断网即失效；
  * `W1 NO_LOGO`         —— 主题首页完全没有 Logo（存量欠账，按「只读不改正文」登记）；
  * `W2 NOT_CENTERED`    —— 没有包在 `text-align:center` 的 `<p>` 里；
  * `W3 ZOOM_MISMATCH`   —— 缺少 `zoom:75%`，或缩放值不是 75%；
  * `W4 NO_DOT_SLASH`    —— 路径没有 `./` 前缀（VitePress 构建期解析不到）；
  * `N1 PAGES` / `N2 WITH_LOGO` / `N3 BY_RULE` / `N4 GROUP` 只计数。

## 口径（被真实语料打出来的四条）

1. **只扫 `docs/<分类>/<主题>/index.md`（深度恰好三段）**。`docs/<分类>/index.md` 是分类
   目录页（`AGENTS.md` 第 6 节要求「只放 `# 分类名` + 子目录链接列表」），它不该有 Logo；
   `project/**` 的首页是项目章节导航，也不是「技术主题」。把这两类算进来会得到上百条假 `W1`。
2. **必须先剥围栏与行内代码**。本仓大量页面在代码块里写 `<img src="./assets/x-logo.png">`
   作为**写法示例**（`AGENTS.md` 第 7 节第 8 条本身就在示范），复用第 88 项的共享底座
   `fenceutil.scan()` 整段剔除，再剥一次行内代码；否则「示范」会被判成「缺陷」，
   而误报会把真欠账埋掉（本库 100+ 项巡检反复验证的规律）。
3. **「有 Logo」按 `src` 里出现 `logo` 判**（大小写不敏感）。文件名规范是 `xxx-logo.png`
   （`nginx-logo.png`、`trainingqualification-logo.png`），不按文件名判会漏掉全部合规写法。
4. **`W1` 不做成 `E`**。存量主题里有一批首页确实没有 Logo（早期页面），一次判 `E` 会让
   这道门第一天就红一片、第二天被整体跳过——与 `depthcheck`、`assetweightcheck` 的阈值取舍同一条纪律。
5. **分组页与入口页不算主题首页**（`N4 GROUP`）。判据两条：没有 H2 且正文 60% 以上是列表项
   （`Frontend/Basic`）、或首段自称「入口页 / 不是专题」（`AI/Java`）。第一轮没排除时
   报 `W1=14`，逐条打开发现其中 4 条是纯链接的分组目录页——**误报比漏报贵**。

## 终态读数（第 240 天）

    pages=193 group=7 with_logo=176 E=0 W=10 W1=10

`W1=10` 是真实存量欠账（`Ops/VM`、`Ops/JumpServer`、`Ops/DatabaseOps`、`Tools/VersionControl`、
`Tools/Build`、`DB/Relational` 等），按「只读不改正文」的纪律登记，按日补齐官方 Logo。

## 用法

    python3 utils/audit/logocheck.py --root .
    python3 utils/audit/logocheck.py --root . --verbose
    python3 utils/audit/logocheck.py --selftest
"""
import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from fenceutil import scan as fence_scan  # 第 88 项起的共享底座
except Exception:  # pragma: no cover - 单独拷走本脚本时降级
    fence_scan = None

IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
SRC_RE = re.compile(r"""src\s*=\s*["']([^"']+)["']""", re.I)
INLINE_RE = re.compile(r"`[^`\n]*`")
P_OPEN_RE = re.compile(r"<p\b[^>]*>", re.I)


def strip_code(text):
    """剥掉围栏与行内代码，保留行结构（行数不变，便于回溯行号）。"""
    if fence_scan is not None:
        try:
            mask, _blocks, _unclosed = fence_scan(text)
            lines = text.split("\n")
            for i in range(len(lines)):
                if i in mask:
                    lines[i] = ""
            return INLINE_RE.sub(lambda m: " " * len(m.group(0)), "\n".join(lines))
        except Exception:
            pass
    out, infence = [], False
    for line in text.splitlines(True):
        if re.match(r"^\s*(```|~~~)", line):
            infence = not infence
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(("" if infence else line))
    return INLINE_RE.sub(lambda m: " " * len(m.group(0)), "".join(out))


def topic_pages(root):
    """docs/<分类>/<主题>/index.md —— 深度恰好三段。"""
    base = os.path.join(root, "docs")
    pages = []
    if not os.path.isdir(base):
        return pages
    for cat in sorted(os.listdir(base)):
        catdir = os.path.join(base, cat)
        if not os.path.isdir(catdir) or cat.startswith("."):
            continue
        for topic in sorted(os.listdir(catdir)):
            tdir = os.path.join(catdir, topic)
            idx = os.path.join(tdir, "index.md")
            if os.path.isdir(tdir) and os.path.isfile(idx):
                pages.append((os.path.join("docs", cat, topic, "index.md"), idx, cat, topic))
    return pages


def is_group_page(body):
    """分组页 / 入口页不是「技术主题首页」，不参与 Logo 判定。

    两条判据（任一命中即视为分组页）：
      1. 没有 H2，且正文 60% 以上是列表项或容器标记 —— 纯链接目录（`Frontend/Basic`）；
      2. H1 之后的第一段自称「入口页 / 不是专题」—— 明确声明自己不是专题（`AI/Java`）。
    """
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    if any(l.startswith("## ") for l in lines):
        pass
    else:
        rest = [l for l in lines if not l.startswith("#")]
        if rest:
            listy = sum(1 for l in rest
                        if l.startswith(("- ", "* ", "+ ")) or re.match(r"^\d+\.\s", l)
                        or l.startswith(":::"))
            if listy / len(rest) >= 0.6:
                return True
    lead = " ".join(lines[:12])
    if "入口页" in lead or "不是专题" in lead:
        return True
    return False


def check_page(rel, text):
    """返回 (list of (code, msg), has_logo)"""
    body = strip_code(text)
    issues = []
    logos = []
    for m in IMG_RE.finditer(body):
        tag = m.group(0)
        src = SRC_RE.search(tag)
        if not src:
            continue
        url = src.group(1)
        if "logo" not in url.lower():
            continue
        start = body.rfind("<", 0, m.start() + 1)
        line_start = body.rfind("\n", 0, start) + 1
        line_end = body.find("\n", m.end())
        line = body[line_start: line_end if line_end != -1 else len(body)]
        logos.append((url, line))
    if not logos:
        issues.append(("W1", "主题首页没有 Logo（AGENTS 7.8 要求官方 Logo PNG）"))
        return issues, False

    url, line = logos[0]
    low = url.lower()
    if re.match(r"^https?://", low):
        issues.append(("E3", "Logo 用了外链：%s（断网即失效）" % url))
    elif not low.endswith(".png"):
        issues.append(("E2", "Logo 不是 PNG：%s" % url))
    elif not url.startswith("./"):
        issues.append(("W4", "Logo 路径缺 ./ 前缀：%s" % url))

    p = P_OPEN_RE.search(line)
    centered = bool(p) and re.search(r"text-align\s*:\s*center", p.group(0), re.I)
    if not centered:
        issues.append(("W2", "Logo 没有包在 text-align:center 的 <p> 里"))

    z = re.search(r"zoom\s*:\s*([0-9.]+)\s*%", line, re.I)
    if not z:
        issues.append(("W3", "Logo 缺 zoom:75%"))
    elif abs(float(z.group(1)) - 75.0) > 0.01:
        issues.append(("W3", "Logo 缩放是 %s%%，应为 75%%" % z.group(1)))
    return issues, True


def run(root, verbose=False):
    if not os.path.isdir(os.path.join(root, "docs")):
        print("E0 ROOT_NOT_FOUND: %s 下没有 docs/" % root)
        return 2
    pages = topic_pages(root)
    if not pages:
        print("E1 NO_PAGES: 没扫到任何 docs/<分类>/<主题>/index.md")
        return 2

    counts = {}
    by_rule = {}
    with_logo = 0
    groups = 0
    rows = []
    for rel, path, cat, topic in pages:
        try:
            text = open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            text = open(path, encoding="utf-8", errors="replace").read()
        if is_group_page(strip_code(text)):
            groups += 1
            continue
        issues, has = check_page(rel, text)
        with_logo += 1 if has else 0
        for code, msg in issues:
            counts[code] = counts.get(code, 0) + 1
            by_rule[code] = by_rule.get(code, 0) + 1
            rows.append((code, rel, msg))

    order = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "W1": 4, "W2": 5, "W3": 6, "W4": 7}
    rows.sort(key=lambda r: (order.get(r[0], 9), r[1]))
    for code, rel, msg in rows:
        if code.startswith("E") or verbose:
            print("%s %s :: %s" % (code, rel, msg))
    if not verbose:
        e_rows = [r for r in rows if r[0].startswith("E")]
        if len(rows) > len(e_rows):
            print("... 其余 %d 条 W 省略（--verbose 查看）" % (len(rows) - len(e_rows)))

    e = sum(v for k, v in counts.items() if k.startswith("E"))
    w = sum(v for k, v in counts.items() if k.startswith("W"))
    print("pages=%d group=%d with_logo=%d E=%d W=%d %s" % (
        len(pages), groups, with_logo, e, w,
        " ".join("%s=%d" % (k, by_rule[k]) for k in sorted(by_rule, key=lambda x: order.get(x, 9)))))
    return 0 if e == 0 else 1


SELFTEST = [
    # (页内容, 期望问题码集合)
    ('# X\n\n<p style="text-align:center;"><img src="./assets/x-logo.png" style="zoom:75%;" /></p>\n', set()),
    ('# X\n\n正文没有图。\n', {"W1"}),
    ('# X\n\n<p style="text-align:center;"><img src="./assets/x-logo.svg" style="zoom:75%;" /></p>\n', {"E2"}),
    ('# X\n\n<p style="text-align:center;"><img src="https://cdn.x.com/x-logo.png" style="zoom:75%;" /></p>\n', {"E3"}),
    ('# X\n\n<img src="./assets/x-logo.png" style="zoom:75%;" />\n', {"W2"}),
    ('# X\n\n<p style="text-align:center;"><img src="./assets/x-logo.png" /></p>\n', {"W3"}),
    ('# X\n\n<p style="text-align:center;"><img src="./assets/x-logo.png" style="zoom:50%;" /></p>\n', {"W3"}),
    ('# X\n\n<p style="text-align:center;"><img src="/assets/x-logo.png" style="zoom:75%;" /></p>\n', {"W4"}),
    ('# X\n\n<p style="text-align: center;"><img src="./assets/x-logo.png" style="zoom: 75%;" /></p>\n', set()),
    ('# X\n\n```html\n<img src="./assets/x-logo.svg" />\n```\n', {"W1"}),
    ('# X\n\n示例：`<img src="./x-logo.jpg">` 不是真图。\n', {"W1"}),
    ('# X\n\n<p style="text-align:center;"><img src="./assets/nginx-logo.png" style="zoom:75%;" /></p>\n',
     set()),
]


def selftest():
    ok = 0
    for i, (text, expect) in enumerate(SELFTEST, 1):
        issues, _ = check_page("docs/A/T/index.md", text)
        got = set(c for c, _ in issues)
        if got == expect:
            ok += 1
        else:
            print("  case %d FAIL: 期望 %s 实际 %s" % (i, sorted(expect), sorted(got)))
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "docs", "A", "T"), exist_ok=True)
    open(os.path.join(d, "docs", "A", "T", "index.md"), "w").write(SELFTEST[0][0])
    pages = topic_pages(d)
    if len(pages) == 1:
        ok += 1
    else:
        print("  case %d FAIL: 主题首页识别 %d" % (len(SELFTEST) + 1, len(pages)))
    os.makedirs(os.path.join(d, "docs", "A2"), exist_ok=True)
    open(os.path.join(d, "docs", "A2", "index.md"), "w").write(SELFTEST[1][0])
    if len(topic_pages(d)) == 1:
        ok += 1
    else:
        print("  case %d FAIL: 分类目录页被误算成主题首页" % (len(SELFTEST) + 2))
    print("--selftest %d/%d" % (ok, len(SELFTEST) + 2))
    return 0 if ok == len(SELFTEST) + 2 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    sys.exit(run(a.root, a.verbose))


if __name__ == "__main__":
    main()
