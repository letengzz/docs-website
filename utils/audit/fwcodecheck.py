#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''fwcodecheck.py — 代码围栏里的全角标点巡检 · 第 117 项

为什么立这一项
--------------
本库已有四道门在看「代码块」：`fencecheck`（语言在不在白名单）、`tickscheck`（围栏闭没闭）、
`langmatchcheck`（标着 sql 的块里是不是 sql）、`jsonfencecheck`（json 能不能解析）。四道全绿
仍然可以写出**复制即报错**的一段代码：

```python
for row in rows：
    print（row）
```

读者复制到编辑器里，`invalid character '：' (U+FF1A)`——而文档在构建、预览、高亮三处都
显示正常，因为 Markdown 渲染器只认围栏，不管内容。中文写作时输入法默认全角，标点几乎
一定会被顺手带进代码里；这类缺陷**只在读者动手那一刻爆炸**，而读者往往以为是自己抄错了。

它与 `punctspacecheck`（第 108 项）方向相反：那一项判**正文里**中英混排的空格，这一项判
**代码里**混进来的全角标点，两者不重叠。

判据
----
E0 ROOT_NOT_FOUND   仓库根找不到
E1 NO_BLOCKS        一个代码块都没扫到（活性判据：扫不到就拒绝给全绿）
E2 FW_PUNCT         语法区出现全角标点，且该语言里它**一定**是语法错误（python/sql/json/js/ts/go/java/rust）
E3 FW_SPACE         语法区出现全角空格 U+3000（不可见，任何语言都算缺陷）
W1 FW_PUNCT_SOFT    语法区出现全角标点，但该语言里**可能合法**（shell/yaml/dockerfile/text…）
N1 BLOCKS / N2 LINES / N3 BY_LANG 只计数

口径（四轮收敛的结论，写在这里防止后人重踩）
--------------------------------------------
1. **注释与字符串是安全区**。`# 期望：0`、`print("你好，世界")` 里的全角标点是内容，不是
   语法。不做剥离的话本库首轮会报出 2,000 条以上的假 E2（本库有大量中文注释与中文提示语）。
2. **按语言分两级**。shell 里 `echo 你好，世界` 完全合法（未加引号的参数就是那一串字符），
   python 里同样的写法直接 SyntaxError。一刀切判 E 会让「shell 教学块」全部变红，而它们
   一个字符都没写错。
3. **只剥三种注释符**：`#`、`//`、`--`，并按语言取子集。`#` 在 shell/python/yaml 是注释，
   在 css 里是颜色值；`--` 在 sql 里是注释，在 css 里是自定义属性。取子集比写通用词法器便宜
   得多，且不会错。
4. **跨行字符串要带状态**：python 的三引号、js 的模板字符串都能跨行。首版逐行独立剥离，
   `docs/` 里三处多行 `"""` 的中文段落被整段判 E2；加 `state` 后归零。

纪律
----
只读不改正文。E2/E3 是真缺陷，按日修；W1 是「可能合法」的欠账，登记不催。
'''

import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

FW = "，。；：！？（）【】《》“”‘’、·～"
FW_SPACE = "\u3000"

HARD_LANGS = {"python", "py", "python3", "sql", "json", "js", "javascript", "ts", "typescript",
              "go", "java", "rust", "kotlin", "scala", "c", "cpp", "csharp", "php", "ruby"}
SOFT_LANGS = {"shell", "sh", "bash", "zsh", "console", "dockerfile", "yaml", "yml", "ini",
              "properties", "text", "txt", "toml", "http", "diff", "makefile", "conf"}
SKIP_LANGS = {"html", "css", "scss", "xml", "md", "markdown", "vue", "svg", "plain"}

COMMENT = {
    "python": ("#",), "py": ("#",), "python3": ("#",), "shell": ("#",), "sh": ("#",),
    "bash": ("#",), "zsh": ("#",), "yaml": ("#",), "yml": ("#",), "dockerfile": ("#",),
    "ruby": ("#",), "makefile": ("#",), "conf": ("#",), "ini": ("#", ";"), "properties": ("#", "!"),
    "toml": ("#",), "js": ("//",), "javascript": ("//",), "ts": ("//",), "typescript": ("//",),
    "go": ("//",), "java": ("//",), "rust": ("//",), "kotlin": ("//",), "scala": ("//",),
    "c": ("//",), "cpp": ("//",), "csharp": ("//",), "php": ("//", "#"), "sql": ("--",),
    "http": ("#",), "diff": (), "text": (), "txt": (), "console": ("#",),
    "json": ("//",),           # jsonc 容忍
}
BLOCK_QUOTE = {
    "python": ('"""', "'''"), "py": ('"""', "'''"), "python3": ('"""', "'''"),
    # Java 文本块与 C# 原始字符串：三引号跨行，里面写的就是中文提示词
    "java": ('"""',), "kotlin": ('"""',), "scala": ('"""',), "csharp": ('"""',),
}
# 反引号单独处理：js 的模板串可以嵌模板串（`${a ? `x：y` : ''}`），
# 当成普通块定界符会在内层反引号处提前闭合，把中文露成语法
BACKTICK_LANGS = {"js", "javascript", "ts", "typescript"}
# 行首即注释的行整行豁免：`* 续行`、`// 说明`、`<!-- 注释 -->` 都是「说明」不是语法
LEAD_MARKERS = ("//", "#", "--", "<!--", "*", "%", ";;")
# 块注释 /* … */：JSDoc 里全是中文，不认它首轮会造出 500+ 条假 E2
BLOCK_COMMENT = {
    "js": ("*/",), "javascript": ("*/",), "ts": ("*/",), "typescript": ("*/",),
    "java": ("*/",), "go": ("*/",), "rust": ("*/",), "kotlin": ("*/",), "scala": ("*/",),
    "c": ("*/",), "cpp": ("*/",), "csharp": ("*/",), "php": ("*/",),
    "json": ("*/",),          # jsonc 容忍
    "sql": ("*/",),
}
PROSE_LANGS = {"text", "txt", "diff"}   # 围栏里本来就是画图/贴输出，中文属内容
LINE_QUOTE = {"'": "'", '"': '"'}


def lang_of(info: str) -> str:
    tok = (info or "").strip().split()
    if not tok:
        return ""
    return tok[0].strip("{}").lower()


def _js_backtick(line: str, lang: str, state):
    """js/ts 的模板串：支持同线嵌套，支持跨行。返回 (剩余待扫文本, 新状态) 或 None。"""
    if lang not in BACKTICK_LANGS:
        return None
    if state and state[0] == "str" and state[1] == "`":
        k = line.find("`")
        if k == -1:
            return "", state
        return line[k + 1:], None
    if line.count("`") == 0:
        return None
    if line.count("`") % 2 == 1:
        k = line.find("`")
        return line[:k], ("str", "`")
    first, last = line.find("`"), line.rfind("`")
    return line[:first] + line[last + 1:], None


def strip_line(line: str, lang: str, state):
    """剥掉注释与字符串，返回 (语法区, 新状态)。

    state 为（种类, 定界符）：`('str', '\"\"\"')` / `('str', '`')` / `('cmt', '*/')`；
    None 表示当前行不在任何块内。
    """
    r = _js_backtick(line, lang, state)
    if r is not None:
        line, state = r
        if not line.strip():
            return "", state
    out = []
    i, n = 0, len(line)
    bq = BLOCK_QUOTE.get(lang, ())
    bc = BLOCK_COMMENT.get(lang, ())
    if not state and line.lstrip().startswith(LEAD_MARKERS):
        return "", None
    while i < n:
        if state:
            kind, delim = state
            if line.startswith(delim, i):
                i += len(delim)
                state = None
            else:
                i += 1
            continue
        ch = line[i]
        if bc and line.startswith("/*", i):
            state = ("cmt", "*/")
            i += 2
            continue
        if bq and any(line.startswith(q, i) for q in bq):
            q = next(q for q in bq if line.startswith(q, i))
            state = ("str", q)
            i += len(q)
            continue
        if ch in LINE_QUOTE:
            q = ch
            i += 1
            while i < n:
                if line[i] == "\\":
                    i += 2
                    continue
                if line[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if lang in ("js", "javascript", "ts", "typescript") and ch == "`":
            i += 1
            while i < n:
                if line[i] == "\\":
                    i += 2
                    continue
                if line[i] == "`":
                    i += 1
                    break
                i += 1
            continue
        hit = next((c for c in COMMENT.get(lang, ()) if line.startswith(c, i)), None)
        if hit:
            break
        out.append(ch)
        i += 1
    return "".join(out), state


def scan_code(code: str, lang: str):
    """返回 [(相对行号, 字符, 是否空格)]"""
    hits = []
    state = None
    for idx, line in enumerate(code.split("\n")):
        rest, state = strip_line(line, lang, state)
        for ch in rest:
            if ch in FW or ch == FW_SPACE:
                hits.append((idx, ch, ch == FW_SPACE))
    return hits


def walk(root):
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in
                       {".git", "node_modules", ".vitepress", "dist", ".workbuddy", "assets"}]
        for nm in names:
            if nm.endswith(".md"):
                yield os.path.join(dirpath, nm)


def run(root, verbose=False):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND", root)
        return 2
    e2 = e3 = w1 = 0
    blocks = lines = 0
    by_lang = Counter()
    soft_by_lang = Counter()
    detail = []
    for path in walk(root):
        try:
            text = open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        _, blks, _ = fenceutil.scan(text)
        src = text.split("\n")
        for (s, e, info) in blks:
            lang = lang_of(info)
            if lang in SKIP_LANGS:
                continue
            body = "\n".join(src[s + 1:e])
            if not body.strip():
                continue
            blocks += 1
            lines += body.count("\n") + 1
            by_lang[lang or "(none)"] += 1
            for rel, ch, is_space in scan_code(body, lang):
                absline = s + 2 + rel
                if is_space:
                    e3 += 1
                    detail.append(("E3", path, absline, ch, lang))
                elif lang in HARD_LANGS:
                    e2 += 1
                    detail.append(("E2", path, absline, ch, lang))
                elif lang in PROSE_LANGS:
                    continue          # text/txt 围栏里本就是画图与中文输出
                else:
                    w1 += 1
                    soft_by_lang[lang or "(none)"] += 1
                    if verbose:
                        detail.append(("W1", path, absline, ch, lang))
    if blocks == 0:
        print("E1 NO_BLOCKS 一个代码块都没扫到，拒绝给全绿")
        return 2
    print(f"pages_root={root} blocks={blocks} lines={lines} "
          f"E2={e2} E3={e3} W1={w1}")
    if detail:
        for lv, path, ln, ch, lang in detail[:40]:
            print(f"  {lv} {path}:{ln} {ch!r} lang={lang or '-'}")
    if soft_by_lang:
        print("  W1 by lang:", dict(soft_by_lang.most_common(8)))
    return 1 if (e2 or e3) else 0


def selftest():
    cases = [
        # (名字, 代码, 语言, 期望 E2, 期望 E3, 期望 W1)
        ("python 全角冒号", "for x in y：\n    pass\n", "python", 1, 0, 0),
        ("python 注释里的全角", "# 期望：0\nprint(1)\n", "python", 0, 0, 0),
        ("python 字符串里的全角", 'print("你好，世界")\n', "python", 0, 0, 0),
        ("python 三引号跨行", 's = """\n中文，段落。\n"""\nx：= 1\n', "python", 1, 0, 0),
        ("sql 全角分号", "SELECT 1；\n", "sql", 1, 0, 0),
        ("sql 注释里的全角", "-- 期望：1 行\nSELECT 1;\n", "sql", 0, 0, 0),
        ("shell 全角逗号算软", "echo 你好，世界\n", "shell", 0, 0, 1),
        ("yaml 全角冒号算软", "name: 值：值\n", "yaml", 0, 0, 1),
        ("js 全角括号", "if (a（b）) {}\n", "js", 2, 0, 0),
        ("全角空格任何语言都算", "x = 1\u3000+ 2\n", "python", 0, 1, 0),
        ("html 整块跳过", "<p>你好，世界</p>\n", "html", 0, 0, 0),
        ("单引号转义不漏", "s = 'it\\'s，ok'\n", "python", 0, 0, 0),
        ("json 字符串合法", '{"k": "值，值"}\n', "json", 0, 0, 0),
        ("js 模板串跨行", "const s = `\n中文，文本\n`;\nlet a：1;\n", "js", 1, 0, 0),
    ]
    ok = 0
    for name, code, lang, want_e2, want_e3, want_w1 in cases:
        hits = scan_code(code, lang)
        e2 = sum(1 for _, _, sp in hits if not sp and lang in HARD_LANGS)
        e3 = sum(1 for _, _, sp in hits if sp)
        w1 = sum(1 for _, _, sp in hits if not sp and lang not in HARD_LANGS) if lang not in SKIP_LANGS else 0
        if lang in SKIP_LANGS:
            e2 = e3 = w1 = 0
        good = (e2, e3, w1) == (want_e2, want_e3, want_w1)
        ok += good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: E2={e2} E3={e3} W1={w1} "
              f"（期望 {want_e2}/{want_e3}/{want_w1}）")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(a.root, a.verbose)


if __name__ == "__main__":
    sys.exit(main())
