#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""jsonfencecheck.py —— 代码块声明的语言 ⇄ 内容能否被 JSON 解析（第 97 项巡检）。

## 动机：第九次「某个维度整体没人看」

本库对代码块已有四道门，各管一段：

  * `fencecheck`（第 62 项）—— 语言标注是否有 shiki 注册（`json` 可用吗）；
  * `fenceparitycheck`（第 88 项）—— 围栏是否成对、有没有未闭合；
  * `fencepathcheck` —— 围栏标题里的文件路径是否存在；
  * `langmatchcheck` —— 围栏标注与内容的语言是否明显不符。

四道门全部通过，仍然可能发生这件事：**围栏写着 `json`，内容却不是合法 JSON**。

```json
{
  // 端口
  "port": 8080,
}
```

上面这段在页面上高亮得漂漂亮亮，读者复制到 `package.json` 里立刻报错；而
`JSON.parse` / CI / 构建器全都会在读者那边而不是在仓库这边失败。本库 400+ 个
`json` 围栏里，这类「看起来是 JSON、实际不是」的内容一直是**零门禁区**。

## 判据（E = 错误，W = 提示）

  E0 ROOT_NOT_FOUND     给定根目录不存在
  E1 NO_FENCES          一个 json/jsonc 围栏都没扫到（活性：拒绝在空集上给全绿）
  W1 INVALID_JSON       标 `json`，去掉注释与尾逗号后仍然解析失败（语法真的错）
  W2 COMMENT_OR_TRAILING 标 `json`，但内容含注释或尾逗号（去掉后可解析）→ 应标 `jsonc`
  W3 ELLIPSIS           标 `json`，且含 `...` / `…` 占位省略（片段写法）→ 应标 `jsonc`
  W4 JSONC_INVALID      标 `jsonc`，去掉注释与尾逗号后仍解析失败
  W5 MULTI_DOC          一个围栏里放了多个 JSON 文档（片段集合）→ 应标 `jsonc` 或拆块
  W6 HYBRID             围栏里混了「请求行 / 说明文字」，只有后半段是 JSON → 应标 `http`
  W7 FRAGMENT           只有 JSON 片段（缺外层 `{` `}`），补上即可解析 → 应标 `jsonc`

## 为什么 W1/W4 是错误、W2/W3 只是提示

`jsonc`（JSON with Comments）在 VS Code 生态里是合法标注，本库大量配置片段本来
就该用它。所以「标了 json 但内容带注释」不是内容错，是**标注错**：改一个词就好，
属于提示级欠账（W2/W3）。而 W1/W4 是内容真的解析不了——多半是漏了逗号、括号
不配对、或者把 YAML 写成了 JSON，这类读者复制即失败，按错误处理。

## 三条口径（都被真实语料打出来过）

1. **注释识别必须跳过字符串**。`"url": "https://a.b"` 里的 `//` 不是注释；
   用逐字符状态机（in_string / escape）而不是 `re.sub(r"//.*")`。首版用正则，
   一次误报 9 条（全是 URL）。
2. **尾逗号只在 `}` / `]` 之前**。`,` 后跟字符串是正常分隔，不能动；只把
   `,(\s*[}\]])` 收成一个 `\1`。
3. **`...` 必须独立成记号**。`"glob": "**/*.ts"` 里没有 `...`，但
   `"items": [1, 2, ...]` 是片段写法；按「`...` 前后是空白/逗号/括号」判。

## 不做的事

W5~W7 是「标注与写法不匹配」的三类常见形态：一个围栏塞多份文档、请求行与
JSON 混写、只有片段没有外层括号。它们都能靠改一个标注词或补一对括号解决。

不改文档、不改标注、不猜意图。「这段该标 jsonc 还是该删掉注释」是写作决定，
本项只负责把「哪个文件的第几行、因为什么原因、解析器报了什么」列出来。
"""

import argparse
import json
import os
import re
import sys
import tempfile

import fenceutil

LANGS = ("json", "jsonc")
ELLIPSIS_RE = re.compile(r"(^|[\s,\[\(\{])\.\.\.([\s,\}\]\)]|$)|…")


def strip_jsonc(text: str):
    """去掉 `//`、`/* */` 注释与尾逗号；返回 (新文本, 是否动过)。"""
    out = []
    i, n = 0, len(text)
    in_str = False
    esc = False
    changed = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            changed = True
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            changed = True
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    body = "".join(out)
    body2, k = re.subn(r",(\s*[}\]])", r"\1", body)
    if k:
        changed = True
    return body2, changed


def parse_stream(text: str):
    """按「连续多个 JSON 值」解析；返回成功解析的个数（0 表示不是流）。"""
    dec = json.JSONDecoder()
    i, n, count = 0, len(text), 0
    while i < n:
        while i < n and text[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        try:
            _, end = dec.raw_decode(text, i)
        except Exception:  # noqa: BLE001
            return 0
        count += 1
        i = end
    return count


def drop_prefix(text: str):
    """去掉 JSON 之前的非 JSON 前缀行（请求行、说明），返回剩余文本或 None。"""
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        t = line.strip()
        if not t:
            continue
        if t[0] in "{[\"" or t[0].isdigit() or t in ("true", "false", "null"):
            return "\n".join(lines[idx:])
        continue
    return None


def classify(lang: str, body: str):
    """返回 (level, reason)；level 为 None 表示通过。"""
    try:
        json.loads(body)
        return None, None
    except Exception as exc:  # noqa: BLE001 - 需要任意解析错误的文本
        first_error = f"{type(exc).__name__}: {exc}"
    stripped, changed = strip_jsonc(body)
    try:
        json.loads(stripped)
        if lang == "jsonc":
            return None, None
        return "W2", "JSON 内含注释或尾逗号（去掉后可解析），标注应为 jsonc"
    except Exception:  # noqa: BLE001
        pass
    if parse_stream(stripped) >= 2:
        return "W5", f"一个围栏里放了 {parse_stream(stripped)} 个 JSON 文档（片段集合），应标 jsonc 或拆块"
    tail = drop_prefix(stripped)
    if tail is not None and tail != stripped:
        try:
            json.loads(tail)
            return "W6", "围栏前半段是请求行/说明文字，只有后半段是 JSON，应标 http 或拆块"
        except Exception:  # noqa: BLE001
            if parse_stream(tail) >= 2:
                return "W6", "围栏前半段是请求行/说明文字，后半段是多个 JSON 文档，应标 http 或拆块"
    for cand in ("{" + stripped + "}", "[" + stripped + "]"):
        try:
            json.loads(cand)
            return "W7", "只有 JSON 片段（缺外层括号），补上即可解析，应标 jsonc 或补全"
        except Exception:  # noqa: BLE001
            pass
    if lang == "jsonc":
        return "W4", "标为 jsonc，去掉注释与尾逗号后仍无法解析"
    if ELLIPSIS_RE.search(body):
        return "W3", "JSON 内含 ... / … 占位省略（片段写法），标注应为 jsonc"
    return "W1", f"JSON 语法错误：{first_error}"


def scan_text(text: str):
    mask, blocks, _ = fenceutil.scan(text)
    lines = text.split("\n")
    out = []
    for start, end, info in blocks:
        lang = (info.split()[0].lower() if info.strip() else "")
        if lang not in LANGS:
            continue
        body = "\n".join(lines[start + 1:end])
        level, reason = classify(lang, body)
        out.append((start + 1, lang, level, reason))
    return out


def check(root: str, verbose: bool = False):
    docs, project = os.path.join(root, "docs"), os.path.join(root, "project")
    if not (os.path.isdir(docs) or os.path.isdir(project)):
        return None
    counts = {"W1": 0, "W2": 0, "W3": 0, "W4": 0, "W5": 0, "W6": 0, "W7": 0}
    issues = []
    fences = 0
    for base in (docs, project):
        if not os.path.isdir(base):
            continue
        for dirpath, _, names in os.walk(base):
            for name in sorted(names):
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                for lineno, lang, level, reason in scan_text(text):
                    fences += 1
                    if level is None:
                        continue
                    counts[level] += 1
                    if verbose or level in ("W1", "W4"):
                        issues.append((level, rel, lineno, lang, reason))
    return counts, issues, fences


def selftest():
    cases = []

    def build(files):
        root = tempfile.mkdtemp(prefix="jsonfence-")
        for rel, content in files.items():
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
        return root

    # 1. 合法 JSON 通过
    r = build({"docs/a.md": '```json\n{"port": 8080}\n```\n'})
    counts, issues, fences = check(r)
    cases.append(("合法 JSON 通过", counts["W1"] == 0 and fences == 1))

    # 2. 带行注释 → W2
    r = build({"docs/a.md": '```json\n{\n  // 端口\n  "port": 1\n}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("行注释判 W2", counts["W2"] == 1))

    # 3. 带块注释 → W2
    r = build({"docs/a.md": '```json\n{ /* x */ "a": 1 }\n```\n'})
    counts, _, _ = check(r)
    cases.append(("块注释判 W2", counts["W2"] == 1))

    # 4. 尾逗号 → W2
    r = build({"docs/a.md": '```json\n{"a": 1,}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("尾逗号判 W2", counts["W2"] == 1))

    # 5. 字符串里的 // 不是注释（不许误报）
    r = build({"docs/a.md": '```json\n{"url": "https://a.b/c"}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("URL 不误报", counts["W2"] == 0 and counts["W1"] == 0))

    # 6. 字符串里的尾逗号样式不误伤
    r = build({"docs/a.md": '```json\n{"a": "x,}"}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("字符串内逗号不误报", counts["W1"] == 0 and counts["W2"] == 0))

    # 7. 真语法错 → W1
    r = build({"docs/a.md": '```json\n{"a": 1 "b": 2}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("缺逗号判 W1", counts["W1"] == 1))

    # 8. 省略号片段 → W3
    r = build({"docs/a.md": '```json\n{"items": [1, 2, ...]}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("省略号判 W3", counts["W3"] == 1))

    # 9. jsonc 标注且合法 → 通过
    r = build({"docs/a.md": '```jsonc\n{ // x\n  "a": 1,\n}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("jsonc 合法通过", sum(counts.values()) == 0))

    # 10. jsonc 标注但内容坏 → W4
    r = build({"docs/a.md": '```jsonc\n{"a": 1 "b": 2}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("jsonc 内容坏判 W4", counts["W4"] == 1))

    # 11. 带标题的围栏（info 里有路径）仍识别
    r = build({"docs/a.md": '```json [package.json]\n{"a": 1}\n```\n'})
    counts, _, fences = check(r)
    cases.append(("围栏标题不影响识别", fences == 1 and counts["W1"] == 0))

    # 12. 非 json 围栏不扫
    r = build({"docs/a.md": '```yaml\na: 1\n```\n```shell\nls\n```\n'})
    counts, _, fences = check(r)
    cases.append(("非 json 不扫", fences == 0))

    # 14. 一个围栏多个 JSON 文档 → W5
    r = build({"docs/a.md": '```json\n{"a": 1}\n{"b": 2}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("多文档判 W5", counts["W5"] == 1))

    # 15. 请求行 + JSON → W6
    r = build({"docs/a.md": '```json\nPOST /api/x\n{"a": 1}\n```\n'})
    counts, _, _ = check(r)
    cases.append(("请求行判 W6", counts["W6"] == 1))

    # 16. 缺外层括号的片段 → W7
    r = build({"docs/a.md": '```json\n"a": 1\n```\n'})
    counts, _, _ = check(r)
    cases.append(("片段判 W7", counts["W7"] == 1))

    # 13. 缺 docs/project → None
    r = tempfile.mkdtemp(prefix="jsonfence-")
    cases.append(("缺目录返回 None", check(r) is None))

    ok = 0
    for name, passed in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok += 1 if passed else 0
    print(f"selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description="json/jsonc 围栏内容可解析性（第 97 项）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true", help="把 W2/W3 也逐条打印")
    ap.add_argument("--summary", action="store_true", help="只打印汇总行")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    got = check(root, verbose=args.verbose)
    if got is None:
        print("E0 ROOT_NOT_FOUND（既无 docs/ 也无 project/）")
        return 2
    counts, issues, fences = got
    if not args.summary:
        for level, rel, lineno, lang, reason in issues:
            print(f"{level}\t{rel}:{lineno}\t{lang}\t{reason}")
    e1 = 1 if fences == 0 else 0
    if e1 and not args.summary:
        print("E1 NO_FENCES（一个 json/jsonc 围栏都没扫到，路径或口径可能错了）")
    print(
        "jsonfencecheck: fences={} E={} W1={} W2={} W3={} W4={} W5={} W6={} W7={}".format(
            fences, e1, counts["W1"], counts["W2"], counts["W3"], counts["W4"], counts["W5"], counts["W6"], counts["W7"]
        )
    )
    return 0 if (e1 == 0 and counts["W1"] == 0 and counts["W4"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
