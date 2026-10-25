#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imageorigincheck.py —— 「配图来源与路径形态」巡检（第 208 天新立，第九十八项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

本库关于图片已经有四道门，各管一段：

  * `imagebytescheck`   —— 文件头是不是真的图片（防 404 页面被存成 .png）；
  * `assetsizecheck`    —— 单图字节数是否超预算；
  * `orphanassetcheck`  —— `assets/` 里有没有没人引用的图；
  * `linkexistcheck`    —— `E3 BROKEN_ASSET`：引用的图在磁盘上在不在。

四道门全部假设「引用本身是合规的」，**没有一道问「这张图是从哪来的、写成什么形态」**。
于是三类违反 `AGENTS.md` 第 7 节的写法长期无人拦：

  1. **外链图片**（第 7 节第 9 条：优先下载到本地 `assets/`，**不直接外链**）。外链的
     失效是**静默**的：图床改域名、对方站点防盗链，页面照常构建、照常发布，只是图上
     出现一个裂图标。构建期没有任何信号。
  2. **站内绝对路径**（第 7 节第 2 条：站点 `base` 是 `/docs-website/`，绝对路径必然
     失效）。写作时 `/assets/x.png` 看着最「像对的」，本地 `docs:dev` 甚至可能命中
     `public/` 里的同名文件，一上线就全裂。
  3. **跨主题引用**（第 7 节第 1 条：图片放「当前主题」的 `assets/`）。`../../Other/
     Topic/assets/x.png` 这种写法让「删主题」变成「删别人的图」，而且图片与正文的
     生命周期脱钩：改一张图会影响三个主题的渲染。

这三类都属于「构建全绿、页面全裂」或「构建全绿、维护成本悄悄上升」，与第 92/93 项
（SVG 溢出、SVG 对比度）是同一族问题：**图能编译，不代表图能用**。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND    根目录下既没有 docs/ 也没有 project/
  E1 NO_IMAGES         一条图片引用都没扫到（**活性判据：拒绝在空集上给全绿**）
  W1 EXTERNAL_IMAGE    引用以 http(s):// 或 // 开头（外链，违反第 7 节第 9 条）
  W2 ABSOLUTE_PATH     引用以 / 开头（站内绝对路径，`base` 不为根时必裂）
  W3 CROSS_TOPIC       相对路径解析后**跑出了当前主题目录**（跨主题借图）
  W4 DATA_URI          `data:image/...` 内联（体积失控，且 diff 不可读）
  W5 NOT_IN_ASSETS     解析后落在主题内，但不在任何 `assets/` 段下

## 关键口径（被真实语料打出来的四条）

1. **只扫 `docs/` 与 `project/` 下的 `*.md`**，不扫 `public/`：`public/` 里放的是
   全局资源（logo、背景图），它们本来就该用 `/` 开头的绝对路径引用（VitePress 会把
   `public/` 挂到站点根）。把 `public/` 算进来会得到一堆「正确写法被报成 W2」。
2. **围栏与行内代码必须跳过**——本库大量页面在代码块里写 `![](/assets/x.png)` 作为
   **反例**（`AGENTS.md` 第 7 节第 2 条本身就在讲这个错）。复用第 88 项的共享底座
   `fenceutil.scan()` 整段剔除，并对行内代码做一次剥离；否则「反例」会被判成「缺陷」，
   而**误报会把真欠账埋掉**（本库 98 项巡检反复验证的规律）。
3. **「主题目录」按路径前三段判定**：`docs/<分类>/<主题>/...` 或
   `project/<类别>/<项目>/...`。第三段之后随便多深都算同一主题（页面级 `assets/` 合法）。
4. **行内代码的反引号有单有双**：本库写作反例时常用双反引号包住一段含单反引号的
   文字（```` ``![](/assets/x.png)`` ````）。只认单反引号会把这一段当正文扫，自测第 9 例
   就是被这一条打出来的。
5. **外链只报 W 不报 E**：本库有少量历史页面引用了权威图源，是否必须本地化属于
   写作决定（有的图源不允许转载）；巡检只负责**列出清单**，不替人做合规判断。

## 与相邻巡检的边界（刻意不重复）

* **不判「文件在不在」**：那是 `linkexistcheck` 的 `E3 BROKEN_ASSET`。同一张图缺失
  被两道门各报一次，等于让维护者处理两遍同一个问题。
* **不判「字节是不是图片」**：那是 `imagebytescheck`。
* **不判「有没有人引用」**：那是 `orphanassetcheck`（反方向）。

## 纪律

* **只读**：不改图片路径、不下载外链、不移动文件。本项产出是「哪个文件的第几行、
  哪种形态、原始引用是什么」。
* `--selftest` 的夹具全部走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/imageorigincheck.py
    python3 utils/audit/imageorigincheck.py --root . --limit 40
    python3 utils/audit/imageorigincheck.py --selftest
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

MD_IMG_RE = re.compile(r"!\[[^\]\n]*\]\(\s*([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\s*\)")
HTML_IMG_RE = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
INLINE_CODE_RE = re.compile(r"(?P<tick>`{2,})[^\n]*?(?P=tick)|`[^`\n]*`")
REMOTE_PREFIX = ("http://", "https://", "//")


def iter_pages(root: str):
    for base in ("docs", "project"):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, _dirnames, filenames in os.walk(top):
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def topic_root(rel_path: str) -> str:
    """`docs/A/B/C/x.md` -> `docs/A/B`；`project/K/P/x.md` -> `project/K/P`。"""
    parts = rel_path.split(os.sep)
    return os.sep.join(parts[:3]) if len(parts) >= 3 else os.sep.join(parts[:2])


def classify(src: str, rel_path: str):
    """返回 (判据, 说明)；合规返回 (None, None)。"""
    s = src.strip()
    if s.startswith(REMOTE_PREFIX):
        return "W1", "外链图片"
    if s.startswith("data:"):
        return "W4", "data URI 内联"
    if s.startswith("/"):
        return "W2", "站内绝对路径"
    if s.startswith("#"):
        return None, None
    target = s.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None, None
    page_dir = os.path.dirname(rel_path)
    resolved = os.path.normpath(os.path.join(page_dir, target))
    troot = topic_root(rel_path)
    if resolved != troot and not resolved.startswith(troot + os.sep):
        return "W3", "跨主题引用"
    segs = resolved.split(os.sep)
    if "assets" not in segs:
        return "W5", "不在 assets/ 下"
    return None, None


def scan_text(text: str, rel_path: str):
    mask, _blocks, _unclosed = fenceutil.scan(text)
    hits = []
    for i, line in enumerate(text.split("\n")):
        if i in mask:
            continue
        clean = INLINE_CODE_RE.sub("", line)
        for m in MD_IMG_RE.finditer(clean):
            code, why = classify(m.group(1), rel_path)
            if code:
                hits.append((code, i + 1, why, m.group(1)))
        for m in HTML_IMG_RE.finditer(clean):
            code, why = classify(m.group(1), rel_path)
            if code:
                hits.append((code, i + 1, why, m.group(1)))
    return hits


def run(root: str, limit: int) -> int:
    if not any(os.path.isdir(os.path.join(root, d)) for d in ("docs", "project")):
        print("E0 ROOT_NOT_FOUND  %s 下既没有 docs/ 也没有 project/" % root)
        return 2

    counts = {k: 0 for k in ("W1", "W2", "W3", "W4", "W5")}
    pages = 0
    images = 0
    shown = 0
    details = []

    for path in iter_pages(root):
        rel = os.path.relpath(path, root)
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        pages += 1
        images += len(MD_IMG_RE.findall(text)) + len(HTML_IMG_RE.findall(text))
        for code, lineno, why, src in scan_text(text, rel):
            counts[code] += 1
            details.append((code, rel, lineno, src))
            if shown < limit:
                print("%-3s %-16s %s:%d  %s" % (code, why, rel, lineno, src))
                shown += 1

    if images == 0:
        print("E1 NO_IMAGES  扫了 %d 个页面，一条图片引用都没有（拒绝在空集上给全绿）" % pages)
        return 2

    total_w = sum(counts.values())
    print("")
    print("pages=%d images=%d W1=%d W2=%d W3=%d W4=%d W5=%d W=%d"
          % (pages, images, counts["W1"], counts["W2"], counts["W3"],
             counts["W4"], counts["W5"], total_w))
    if total_w > shown:
        print("（仅显示前 %d 条，其余 %d 条未列出）" % (shown, total_w - shown))
    return 0


# ---------------------------------------------------------------- selftest

def _mk(tmp: str, rel: str, body: str):
    p = os.path.join(tmp, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def selftest() -> int:
    cases = []

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/assets/x.svg", "<svg/>")
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](../assets/x.svg)\n")
    cases.append(("合规相对引用不报", 0, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](https://cdn.example.com/a.png)\n")
    cases.append(("外链报 W1", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](//cdn.example.com/a.png)\n")
    cases.append(("协议相对也报 W1", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](/assets/a.png)\n")
    cases.append(("绝对路径报 W2", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](data:image/png;base64,AAA)\n")
    cases.append(("data URI 报 W4", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](../../Other/assets/a.png)\n")
    cases.append(("跨主题报 W3", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n![](./img/a.png)\n")
    cases.append(("不在 assets 下报 W5", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n```md\n![](https://cdn.example.com/a.png)\n```\n")
    cases.append(("围栏内不报（反例豁免）", 0, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n写 ``![](https://x/a.png)`` 是反例。\n")
    cases.append(("行内代码不报", 0, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n<img src=\"https://cdn.example.com/a.png\" />\n")
    cases.append(("HTML img 外链报 W1", 1, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    _mk(tmp, "docs/A/T/P/index.md", "# P\n\n没有图片。\n")
    cases.append(("无图片报 E1 活性", 2, run_quiet(tmp)[0]))

    tmp = tempfile.mkdtemp()
    cases.append(("根目录缺失报 E0", 2, run_quiet(tmp)[0]))

    ok = 0
    for name, want, got in cases:
        flag = "PASS" if want == got else "FAIL"
        if want == got:
            ok += 1
        print("%-4s %-24s want=%s got=%s" % (flag, name, want, got))
    print("\nselftest %d/%d PASS" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def run_quiet(tmp: str):
    """跑一次扫描，返回 (首个判据计数, 状态码)；只用于 selftest。"""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = run(tmp, 0)
    out = buf.getvalue()
    if "E0" in out:
        return 2, code
    if "E1" in out:
        return 2, code
    for k in ("W1", "W2", "W3", "W4", "W5"):
        m = re.search(k + r"=(\d+)", out)
        if m and int(m.group(1)) > 0:
            return 1, code
    return 0, code


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return run(args.root, args.limit)


if __name__ == "__main__":
    sys.exit(main())
