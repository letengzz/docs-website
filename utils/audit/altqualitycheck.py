#!/usr/bin/env python3
"""配图 alt 文本质量巡检（第 68 项巡检）

存在的理由：`altcheck` 只回答「有没有 alt」，`imagecheck` 只回答「文件在不在」，
`orphanassetcheck` 只回答「有没有人引用」，`assetsizecheck` 只回答「多大」。
四项都通过，仍然可以出现 alt 是 `image-20250706231134947.png` 这种「等于没说」的情况——
对读屏用户，这等于一张图配了一句文件名；对搜素与站内检索，这等于没有描述。

判据：
  E0 ROOT_NOT_FOUND       既没有 docs/ 也没有 project/
  E1 NO_IMAGES            一张图都没扫到（拒绝判定）
  E2 ALT_EMPTY            markdown `![](x.png)` 空 alt（真缺陷，读屏直接跳过）
  E3 ALT_TOO_SHORT        alt 去标点后长度 < 2（中文一个字也算 1）
  W1 ALT_PLACEHOLDER      alt 是占位词（图/图片/截图/示意图/image/screenshot…）
  W2 ALT_DUP_IN_PAGE      同一页内 alt 完全重复
  W3 ALT_MARKUP           alt 里含 markdown/HTML 标记（`**`、`[]`、`<`、`|`）
  W4 ALT_IS_FILENAME      alt 就是文件名（含图片扩展名，或等于 basename）——格式债
  W5 HTML_NO_ALT          `<img>` 无 alt（本仓 logo 约定写法即如此，记为约定缺口）

用法：
  python3 utils/audit/altqualitycheck.py            # 扫 docs 与 project
  python3 utils/audit/altqualitycheck.py --selftest # 自测
退出码：0 = 无 E；1 = 有 E；2 = 用法/环境错误
"""
import os
import re
import sys

ROOTS = ("docs", "project")
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif")
MD_IMG = re.compile(r"!\[([^\]]*)\]\(\s*([^)\s]+)")
HTML_IMG = re.compile(r"<img\b[^>]*>", re.I)
ALT_ATTR = re.compile(r"""alt\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
SRC_ATTR = re.compile(r"""src\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
FENCE = re.compile(r"^\s*(```|~~~)")
PLACEHOLDER = {
    "图", "图片", "图像", "截图", "示意图", "配图", "图片1", "截图1", "示例图",
    "image", "img", "picture", "pic", "screenshot", "photo", "figure", "fig",
    "无", "暂无", "空", "test", "tmp",
}
PUNCT = re.compile(r"[\s\.,;:!\?\-_/\\\(\)\[\]\{\}\"'`~@#\$%\^&\*\+=\|<>，。；：！？、（）【】《》“”‘’—…·]+")


def strip_md(text):
    """去掉行内代码与链接语法，避免把示例当成真实图片。"""
    text = re.sub(r"`[^`]*`", "", text)
    return text


def collect(path, lines):
    """返回 [(lineno, alt, src)]，跳过代码围栏内的内容。"""
    out = []
    in_fence = False
    for i, raw in enumerate(lines, 1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = strip_md(raw)
        for m in MD_IMG.finditer(line):
            alt, src = m.group(1), m.group(2)
            if src.lower().endswith(IMG_EXT) or "/assets/" in src:
                out.append((i, alt, src))
        for m in HTML_IMG.finditer(line):
            tag = m.group(0)
            a = ALT_ATTR.search(tag)
            s = SRC_ATTR.search(tag)
            if not s:
                continue
            src = s.group(1) or s.group(2) or s.group(3) or ""
            if not (src.lower().endswith(IMG_EXT) or "/assets/" in src):
                continue
            alt = "" if a is None else (a.group(1) or a.group(2) or a.group(3) or "")
            out.append((i, alt, "<" + src))
    return out


def norm(alt):
    return PUNCT.sub("", alt.strip()).lower()


def check_page(rel, lines):
    errs, warns = [], []
    imgs = collect(rel, lines)
    seen = {}
    for lineno, alt, src in imgs:
        base = os.path.basename(src.split("?")[0])
        a = alt.strip()
        if a == "":
            if src.startswith("<"):
                warns.append(("W5", lineno, "HTML_NO_ALT", src[1:]))
            else:
                errs.append(("E2", lineno, "ALT_EMPTY", src))
            continue
        if a.lower() == base.lower() or (a.lower().endswith(IMG_EXT) and "/" not in a):
            warns.append(("W4", lineno, "ALT_IS_FILENAME", a))
        n = norm(a)
        if len(n) < 2:
            errs.append(("E3", lineno, "ALT_TOO_SHORT", a))
        if n in PLACEHOLDER:
            warns.append(("W1", lineno, "ALT_PLACEHOLDER", a))
        if re.search(r"(\*\*|\[|\]|<|\|)", a):
            warns.append(("W3", lineno, "ALT_MARKUP", a))
        key = a.lower()
        if key in seen:
            warns.append(("W2", lineno, "ALT_DUP_IN_PAGE", "第 %d 行重复：%s" % (seen[key], a)))
        else:
            seen[key] = lineno
    return imgs, errs, warns


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules"]
        for fn in filenames:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def main():
    bases = [r for r in ROOTS if os.path.isdir(r)]
    if not bases:
        print("E0 ROOT_NOT_FOUND: 既没有 docs/ 也没有 project/（请 cd 到仓库根再跑）")
        return 2
    pages = images = 0
    E, W = [], []
    for base in bases:
        for path in sorted(walk(base)):
            pages += 1
            try:
                lines = open(path, encoding="utf-8").read().splitlines()
            except UnicodeDecodeError:
                continue
            imgs, errs, warns = check_page(path, lines)
            images += len(imgs)
            for code, ln, name, detail in errs:
                E.append((code, path, ln, name, detail))
            for code, ln, name, detail in warns:
                W.append((code, path, ln, name, detail))
    if images == 0:
        print("E1 NO_IMAGES: 扫了 %d 页但一张图都没有，拒绝判定" % pages)
        return 2
    for code, path, ln, name, detail in E:
        print("%s %s:%d %s %s" % (code, path, ln, name, detail))
    for code, path, ln, name, detail in W:
        print("%s %s:%d %s %s" % (code, path, ln, name, detail))
    print("pages=%d images=%d E=%d W=%d" % (pages, images, len(E), len(W)))
    by = {}
    for code, *_ in E + W:
        by[code] = by.get(code, 0) + 1
    print("by_code=" + " ".join("%s:%d" % (k, by[k]) for k in sorted(by)))
    return 1 if E else 0


def selftest():
    cases = []

    def page(*lines):
        return list(lines)

    # 1 正常
    imgs, e, w = check_page("t", page("![证书链的三个节点](assets/a.svg)"))
    cases.append(("正常 alt 无告警", len(imgs) == 1 and not e and not w))
    # 2 空 alt
    imgs, e, w = check_page("t", page("![](assets/a.svg)"))
    cases.append(("空 alt → E2", any(x[0] == "E2" for x in e)))
    # 3 alt 是文件名
    imgs, e, w = check_page("t", page("![image-20250706231134947.png](assets/a.png)"))
    cases.append(("文件名当 alt → W4（格式债）", any(x[0] == "W4" for x in w) and not e))
    # 4 太短
    imgs, e, w = check_page("t", page("![图](assets/a.svg)"))
    cases.append(("单字 alt → E3 且 W1", any(x[0] == "E3" for x in e) and any(x[0] == "W1" for x in w)))
    # 5 HTML img 无 alt
    imgs, e, w = check_page("t", page('<p><img src="./assets/a.png" style="zoom:75%;" /></p>'))
    cases.append(("HTML 无 alt → W5（logo 约定）", any(x[0] == "W5" for x in w) and not e))
    # 6 HTML img 有 alt
    imgs, e, w = check_page("t", page('<img src="./assets/a.png" alt="部署拓扑" />'))
    cases.append(("HTML 有 alt 通过", len(imgs) == 1 and not e and not w))
    # 7 围栏内不算
    imgs, e, w = check_page("t", page("```markdown", "![](x.png)", "```"))
    cases.append(("代码围栏内不计", len(imgs) == 0))
    # 8 重复 alt
    imgs, e, w = check_page("t", page("![链路图](assets/a.svg)", "![链路图](assets/b.svg)"))
    cases.append(("同页重复 → W2", any(x[0] == "W2" for x in w)))
    # 9 含标记
    imgs, e, w = check_page("t", page("![**重点** 链路](assets/a.svg)"))
    cases.append(("含 markdown 标记 → W3", any(x[0] == "W3" for x in w)))
    # 10 外部图片链接（同目录 assets 判定）
    imgs, e, w = check_page("t", page("![外链图](https://e.com/a.png)"))
    cases.append(("外链 png 也计入", len(imgs) == 1))

    ok = 0
    for name, passed in cases:
        print(("PASS " if passed else "FAIL ") + name)
        ok += 1 if passed else 0
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
