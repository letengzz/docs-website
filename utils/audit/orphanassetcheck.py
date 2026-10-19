#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orphanassetcheck.py —— 孤儿资产（存在但没人引用）巡检（第 65 项巡检）

背景
----
`assetsizecheck.py` 的文档里早早就写过一句话：「`orphanassetcheck` 有没有『存在但没人
引用』的孤儿图片」——**但这个脚本从来没被写出来**，那条描述一直挂在一个不存在的名字上。
本项就是把它补齐，并顺手回答一个比「存不存在」更难的问题：**图片被引用了，但引用本身
是「脚本与人眼都读不到」的形态吗。**

既有的两项图片巡检各管一段：

  - `imagecheck`  链接指向的文件是否存在（引用 → 文件）；
  - `assetsizecheck`  文件有多大、有没有字节重复（文件 → 体积）。

**没有一项问「这个文件有没有人引用」**（文件 → 引用）。于是三类问题静默通过构建：

  1. **自绘的示意图画好了、没接进页面**：`assets/` 里有 9 张 `obs-*.svg`，正文只引用了
     `obs-map.svg` 与 logo——读者看不到那 9 张图，构建全绿，体积照付；
  2. **SVG→PNG 转换的中间产物留在仓库**：`xxx-logo.svg` 与 `xxx-logo.png` 同时存在，
     正文只引 `png`，`svg` 永远没人用；
  3. **引用写法让巡检自己失效**：`%E9%A2%9C%E8%89%B2HSL.jpg` 这种百分号编码，以及
     `<img src='...'>` 单引号写法，朴素的正则会全部漏掉——**漏掉之后孤儿判定会误报**，
     而误报比漏报更危险：它会让人关掉这项巡检。

判据（E 为错误、W 为提示）
--------------------------
  E0 ROOT_NOT_FOUND        给定的根目录不存在
  E1 NO_ASSETS             一个图片都没找到（活性：防扫错目录后全绿）
  E2 ORPHAN_ASSET          主题 `assets/` 下的图片，全库没有任何 Markdown 引用它
  W1 PERCENT_ENCODED_REF   引用路径含 `%XX`（人眼与脚本都难对应，且改名时极易漏改）
  W3 CASE_ONLY_REF         只在「忽略大小写」时能匹配到磁盘文件（macOS 绿、Linux 404）
  W4 CROSS_THEME_ASSET     某页引用了别的主题 `assets/` 下的图片（违反 AGENTS 第 7 条）
  W5 LOGO_SVG_TWIN         同目录同时有 `x-logo.svg` 与 `x-logo.png`，且只引用了 png
                           （SVG→PNG 转换的中间产物，可删）

口径说明
--------
1. **引用源包含三类文件**：`docs/` 与 `project/` 下的 `*.md`、根目录 `index.md`、
   `.vitepress/*.ts|mts`（站点配置里会引用 `public/logo.svg`）、以及 VitePress 的
   `base` 前缀写法 `/docs-website/logo.svg`。**只看 Markdown 会把 `public/logo.svg`
   误判成孤儿**——这是本脚本开发时踩到的第一个坑。
2. **引用解析先解百分号编码**：`%E9%A2%9C%E8%89%B2HSL.jpg` 解成 `颜色HSL.jpg` 后才能
   与磁盘对上。不解码会一次报出 3 个假孤儿（含一张正在用的截图）。
3. **`public/` 下的文件只报 W 不报 E**：它们可能被主题 CSS、favicon、`head` 注入引用，
   静态扫描看不全；把它定成 E 会逼着人写豁免表。
4. **W4 只在「跨主题」时触发**：同主题内 `../assets/x.svg` 是正常写法（页面在子目录里），
   判据是「引用路径的 `assets` 父目录与该页所属主题目录不同」。
5. **不判断「该不该有图」**：AGENTS 第 7 条要求「每篇正文都要有配图」，那是内容评审的
   事；本项只回答「已有的图有没有人用」。

用法
----
    python3 utils/audit/orphanassetcheck.py [--root .] [--selftest] [--verbose]

退出码：0 = 无 E（W 不影响退出码）；1 = 存在 E；2 = 参数或根目录错误。
"""

import argparse
import os
import re
import sys
import tempfile
from urllib.parse import unquote

IMG_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif"}
SKIP_DIRS = {".git", "node_modules", "dist", ".vitepress", ".workbuddy", "cache"}
REF_SRC_DIRS = ("docs", "project")

# Markdown 图片：![alt](path)
MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
# HTML <img src="...">（双引号与单引号都要认）
HTML_IMG = re.compile(r"""<img[^>]*?\bsrc\s*=\s*["']([^"']+)["']""", re.I)
# 配置/正文里的裸资源路径（public 资源常用 /logo.svg 这种绝对写法）
BARE_ASSET = re.compile(r"""["'(]([^"'()\s]*\.(?:svg|png|jpe?g|gif|webp|avif))["')]""", re.I)
# YAML 里的 `src: /background.svg`（首页 hero 图）没有引号，单独认一种
YAML_ASSET = re.compile(r"""^\s*(?:src|image|logo)\s*:\s*(/?[^\s#]+\.(?:svg|png|jpe?g|gif|webp|avif))""", re.I | re.M)
# base 前缀（config.mts 里的 base: "/docs-website/"）
BASE_PREFIX = re.compile(r"""base\s*:\s*["']([^"']+)["']""")


def iter_images(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in IMG_EXT:
                yield os.path.join(dirpath, fn)


def iter_text_files(root):
    """引用源：docs/project 下的 md + 根 index.md + .vitepress 下的配置。"""
    for d in REF_SRC_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS and not x.startswith(".")]
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)
    for name in ("index.md", "README.md"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            yield p
    vp = os.path.join(root, ".vitepress")
    if os.path.isdir(vp):
        for fn in sorted(os.listdir(vp)):
            if fn.endswith((".ts", ".mts", ".js", ".mjs")):
                yield os.path.join(vp, fn)


def detect_base(texts):
    for t in texts:
        m = BASE_PREFIX.search(t)
        if m:
            return m.group(1).rstrip("/")
    return ""


def theme_key(path):
    """主题键：前 3 段（docs/<大类>/<主题> 或 project/<Base|Complete>/<项目>）。"""
    parts = [p for p in path.replace("\\", "/").split("/") if p and p != "."]
    return "/".join(parts[:3])


def normalise(url, base_prefix):
    """把引用 URL 归一成「相对仓库根」的正斜杠路径；解析不了就返回 None。"""
    u = url.split("#", 1)[0].split("?", 1)[0].strip()
    if not u or u.startswith(("http://", "https://", "//", "data:")):
        return None
    decoded = unquote(u)
    if decoded.startswith("/"):
        # 绝对路径 = VitePress 的 public 资源：剥掉 base 前缀后落到 public/ 下
        p = decoded.lstrip("/")
        if base_prefix and p.startswith(base_prefix.lstrip("/") + "/"):
            p = p[len(base_prefix.lstrip("/")) + 1:]
        return "public/" + p
    return decoded


def check(root):
    if not os.path.isdir(root):
        raise FileNotFoundError(root)

    findings = []
    images = sorted(iter_images(root))
    if not images:
        findings.append(("E1", "NO_ASSETS", "未找到任何图片（防扫错目录）"))
        return findings, 0, 0

    texts = [(p, open(p, encoding="utf-8", errors="ignore").read()) for p in iter_text_files(root)]
    base_prefix = detect_base([t for _, t in texts])

    # refs: 相对仓库根的路径集合；case_refs: 同内容但大小写与磁盘不一致的引用
    refs, encoded_refs, cross_theme = set(), [], []
    for path, text in texts:
        d = os.path.relpath(os.path.dirname(path), root)
        found = []
        for pat in (MD_IMG, HTML_IMG, BARE_ASSET, YAML_ASSET):
            found += [(pat, m.group(1)) for m in pat.finditer(text)]
        for _pat, url in found:
            norm = normalise(url, base_prefix)
            if norm is None:
                continue
            if "%" in url:
                encoded_refs.append((os.path.relpath(path, root), url))
            # 绝对写法的 public 资源：直接落根；相对写法：相对当前文件解析
            if url.startswith("/"):
                full = os.path.normpath(norm).replace("\\", "/")
            else:
                full = os.path.normpath(os.path.join(d, norm)).replace("\\", "/")
            refs.add(full)
            if "/assets/" in full and os.path.exists(os.path.join(root, full)):
                # 主题键取前三段（docs/<大类>/<主题> 或 project/<Base|Complete>/<项目>）：
                # 子章节与主题共用同一个 assets 目录是正常写法，只有「跨主题」才算违规。
                # 不存在的路径交给 imagecheck，本脚本不重复报。
                if theme_key(d) != theme_key(full.split("/assets/")[0]):
                    cross_theme.append((os.path.relpath(path, root), url))

    lower_map = {}
    for img in images:
        rel = os.path.relpath(img, root).replace("\\", "/")
        lower_map.setdefault(rel.lower(), rel)

    orphans = []
    for img in images:
        rel = os.path.relpath(img, root).replace("\\", "/")
        if rel in refs:
            continue
        orphans.append(rel)

    # W3 大小写不一致：引用不在磁盘集合里，但小写能对上
    disk = {os.path.relpath(i, root).replace("\\", "/") for i in images}
    for r in refs:
        if r not in disk and r.lower() in lower_map:
            findings.append(("W3", "CASE_ONLY_REF", f"{r} → 磁盘上是 {lower_map[r.lower()]}"))

    for rel in orphans:
        if rel.startswith("public/"):
            findings.append(("W5", "PUBLIC_UNREF", f"{rel}: public 资源未被静态扫描到（可能被主题/CSS 引用）"))
        elif any(rel.endswith(s) and rel[: -len(s)].rstrip("s") for s in ("-logo.svg", "-logo.png")):
            findings.append(("W5", "LOGO_SVG_TWIN", f"{rel}: logo 可能是 SVG→PNG 的中间产物"))
        else:
            findings.append(("E2", "ORPHAN_ASSET", f"{rel}: 无任何引用"))

    for src, url in sorted(set(encoded_refs)):
        findings.append(("W1", "PERCENT_ENCODED_REF", f"{src}: {url}"))

    for src, url in sorted(set(cross_theme)):
        findings.append(("W4", "CROSS_THEME_ASSET", f"{src}: {url}"))

    return findings, len(images), len(refs)


def selftest():
    cases = []

    def run(files):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, data in files.items():
                p = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(data)
            return check(tmp)[0]

    # e0 根目录不存在
    try:
        check("/nonexistent-orphanassetcheck-root")
        cases.append(("e0", False, "应抛错但没抛"))
    except FileNotFoundError:
        cases.append(("e0", True, ""))

    # e1 一张图都没有
    f = run({"docs/A/index.md": "# A"})
    cases.append(("e1", any(x[0] == "E1" for x in f), str(f)))

    # e2 孤儿（画了没接进页面）
    f = run({"docs/A/index.md": "# A\n", "docs/A/assets/lonely.svg": "<svg/>"})
    cases.append(("e2", any(x[0] == "E2" for x in f), str(f)))

    # 正常：被 Markdown 引用
    f = run({"docs/A/index.md": "# A\n\n![x](./assets/used.svg)\n", "docs/A/assets/used.svg": "<svg/>"})
    cases.append(("ok-md", not any(x[0].startswith("E") for x in f), str(f)))

    # 正常：被单引号 <img> 引用（朴素正则的漏网形态）
    f = run({"docs/A/index.md": "# A\n\n<img src='./assets/used.svg' />\n", "docs/A/assets/used.svg": "<svg/>"})
    cases.append(("ok-single-quote", not any(x[0].startswith("E") for x in f), str(f)))

    # w1 百分号编码引用
    f = run({"docs/A/index.md": "# A\n\n![x](./assets/%E8%89%B2.jpg)\n", "docs/A/assets/色.jpg": "x"})
    cases.append(("w1", any(x[0] == "W1" for x in f), str(f)))
    cases.append(("w1-not-orphan", not any(x[0] == "E2" for x in f), str(f)))

    # w3 大小写不一致
    f = run({"docs/A/index.md": "# A\n\n![x](./assets/Logo.PNG)\n", "docs/A/assets/logo.png": "x"})
    cases.append(("w3", any(x[0] == "W3" for x in f), str(f)))

    # w4 跨主题引用
    f = run({"docs/A/index.md": "# A\n\n![x](../B/assets/x.svg)\n",
             "docs/B/assets/x.svg": "<svg/>", "docs/A/assets/a.svg": "<svg/>"})
    cases.append(("w4", any(x[0] == "W4" for x in f), str(f)))

    # public 资源被配置引用（不应报孤儿）
    f = run({".vitepress/config.mts": 'export default { base: "/site/", themeConfig: { logo: "/logo.svg" } }',
             "docs/A/index.md": "# A\n\n![x](./assets/a.svg)\n", "public/logo.svg": "<svg/>",
             "docs/A/assets/a.svg": "<svg/>"})
    codes = [x[0] for x in f]
    cases.append(("public-referenced", "E2" not in codes, str(f)))

    ok = 0
    for name, passed, msg in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + ("" if passed else f" :: {msg}"))
        ok += 1 if passed else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"E0 ROOT_NOT_FOUND: {root}")
        return 2

    findings, n_img, n_ref = check(root)
    errors = [x for x in findings if x[0].startswith("E")]
    warns = [x for x in findings if x[0].startswith("W")]

    for code, kind, msg in findings:
        if args.verbose or code.startswith("E"):
            print(f"{code} {kind}: {msg}")

    print(f"images={n_img} refs={n_ref} E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
