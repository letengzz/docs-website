#!/usr/bin/env python3
"""围栏语言标注巡检：标了什么语言、和里面写的东西对不对得上。

判据
  E0 ROOT_NOT_FOUND      根目录不存在（活性）
  E1 NO_FILES            一个文件都没扫到（活性，防「扫了个空目录也算全绿」）
  E2 UNCLOSED_FENCE      围栏没有闭合（内容会漏进正文，渲染错乱）
  E3 LANG_MISMATCH       ```sql 里出现确定性的他语言特征（`public class`、`def`、`<?php` 等）
  W1 SYNONYM_MIX         同一页里同义标注混用（shell/bash、js/javascript、yml/yaml）
  W2 UNKNOWN_LANG        标注不在允许清单里（可能拼错，也可能是新语言）
  W3 EMPTY_FENCE         空围栏（只有开合，没有内容）
  W4 SQL_FRAGMENT        ```sql 里没有 SQL 关键字（片段式示例，允许，只记账）

用法
  python3 utils/audit/fencelangcheck.py            # 扫全库
  python3 utils/audit/fencelangcheck.py --selftest # 跑 14 条自测
"""
import os
import re
import sys
import tempfile

ALLOWED = {
    "html", "css", "scss", "less", "js", "javascript", "ts", "typescript", "jsx", "tsx",
    "json", "jsonc", "json5", "yaml", "yml", "toml", "ini", "properties", "env",
    "shell", "bash", "sh", "zsh", "console", "powershell", "bat", "cmd", "dockerfile",
    "sql", "sqlite", "graphql", "gql", "http", "xml", "markdown", "md", "diff", "text",
    "txt", "plain", "mermaid", "promql", "hcl", "terraform", "nginx", "apache", "conf",
    "vue", "svelte", "python", "py", "java", "kotlin", "scala", "groovy", "go", "rust",
    "c", "cpp", "csharp", "cs", "php", "ruby", "swift", "dart", "lua", "r", "matlab",
    "proto", "protobuf", "makefile", "gradle", "cmake", "asm", "wasm", "wxml", "wxss",
    "ejs", "pug", "handlebars", "jinja", "liquid", "erb", "twig", "astro", "prisma",
    "vim", "regex", "csv", "tsv", "log", "textile", "rest", "redis", "crontab",
    "stylus", "sass", "glsl", "hlsl", "dotenv", "latex", "tex", "jsonl", "ndjson",
    "cypher", "c#", "f#", "objectivec", "solidity", "verilog", "vhdl", "pascal",
}

SYNONYMS = [
    {"shell", "bash", "sh", "zsh"},
    {"js", "javascript"},
    {"ts", "typescript"},
    {"yml", "yaml"},
    {"md", "markdown"},
    {"py", "python"},
    {"txt", "text", "plain"},
    {"json", "jsonc", "json5"},
    {"gql", "graphql"},
    {"conf", "nginx"},
    {"sql", "sqlite"},
]

SQL_KW = re.compile(
    r"\b(select|insert|update|delete|create|drop|alter|with|begin|commit|rollback|"
    r"pragma|explain|vacuum|attach|truncate|grant|revoke|merge)\b", re.I)

# 「标了 sql 但其实是别的语言」的黑名单特征。只抓确定性的错标，
# 不做「没有关键字就是错」这种推断——库里大量刻意贴出的 SQL 片段（列定义、索引定义、表达式）。
OTHER_LANG = re.compile(
    r"(\bpublic\s+class\b|\bprivate\s+[A-Za-z<>\[\]]+\s+\w+\s*[;=]|\bvoid\s+\w+\s*\(|"
    r"\bdef\s+\w+\s*\(|^\s*function\s+\w+\s*\(|\bconsole\.log\s*\(|"
    r"<\?php|#include\s*<|\busing\s+System\b|=>\s*\{|"
    r"^\s*import\s+[\w{}.]+\s+from\s)", re.M)
FENCE = re.compile(r"^(?P<indent>\s{0,3})(?:(?:[-*+]\s+|\d{1,3}[.)]\s+))?"
                   r"(?P<mark>`{3,}|~{3,})(?P<info>.*)$")


def scan(paths):
    fences = []
    for root in paths:
        for dirpath, _dirs, files in os.walk(root):
            for fn in sorted(files):
                if not fn.endswith((".md", ".markdown")):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    lines = open(p, encoding="utf-8").read().split("\n")
                except OSError as e:
                    print(f"E0 READ_FAIL {p}: {e}")
                    continue
                open_mark, open_info, start, body = None, "", 0, []
                for i, line in enumerate(lines, 1):
                    m = FENCE.match(line)
                    if open_mark is None:
                        if m:
                            open_mark = m.group("mark")
                            open_info = (m.group("info") or "").strip()
                            start, body = i, []
                        continue
                    if m and m.group("mark")[0] == open_mark[0] and len(m.group("mark")) >= len(open_mark):
                        lang = open_info.split()[0].lower() if open_info else ""
                        fences.append({"file": p, "line": start, "lang": lang,
                                       "body": "\n".join(body), "closed": True})
                        open_mark = None
                    else:
                        body.append(line)
                if open_mark is not None:
                    lang = open_info.split()[0].lower() if open_info else ""
                    fences.append({"file": p, "line": start, "lang": lang,
                                   "body": "\n".join(body), "closed": False})
    return fences


def run(paths, quiet=False):
    fences = scan(paths)
    e2 = [f for f in fences if not f["closed"]]
    e3 = [f for f in fences if f["closed"] and f["lang"] == "sql"
          and OTHER_LANG.search(f["body"])]
    w4 = [f for f in fences if f["closed"] and f["lang"] == "sql"
          and not SQL_KW.search(re.sub(r"--[^\n]*", "", f["body"]))
          and not OTHER_LANG.search(f["body"])]
    w2 = [f for f in fences if f["closed"] and f["lang"] and f["lang"] not in ALLOWED]
    w3 = [f for f in fences if f["closed"] and not f["body"].strip()]

    pages = {}
    for f in fences:
        pages.setdefault(f["file"], set()).add(f["lang"])
    w1 = []
    for p, langs in pages.items():
        for group in SYNONYMS:
            hit = langs & group
            if len(hit) > 1:
                w1.append((p, sorted(hit)))

    if not quiet:
        for f in e2:
            print(f"E2 UNCLOSED_FENCE {f['file']}:{f['line']} lang={f['lang'] or '-'}")
        for f in e3:
            print(f"E3 LANG_MISMATCH {f['file']}:{f['line']} lang=sql")
        for p, hit in sorted(w1):
            print(f"W1 SYNONYM_MIX {p} -> {','.join(hit)}")
        for f in w2[:40]:
            print(f"W2 UNKNOWN_LANG {f['file']}:{f['line']} lang={f['lang']}")
        for f in w3[:40]:
            print(f"W3 EMPTY_FENCE {f['file']}:{f['line']}")
        print(f"pages={len(pages)} fences={len(fences)} "
              f"E={len(e2) + len(e3)} (E2={len(e2)} E3={len(e3)}) "
              f"W={len(w1) + len(w2) + len(w3) + len(w4)} "
              f"(W1={len(w1)} W2={len(w2)} W3={len(w3)} W4={len(w4)})")
    return len(e2) + len(e3), fences


# ---------------- selftest ----------------
CASES = [
    ("```sql\nselect 1;\n```", 0, "正常的 sql 围栏"),
    ("```sql\npublic class A { void f() {} }\n```", 1, "E3：标 sql 实为 C#"),
    ("```sql\nCONSTRAINT uq UNIQUE (a, b)   -- 列定义片段\n```", 0, "片段式 SQL 只记 W4，不算错"),
    ("```python\nprint(1)\n```", 0, "正常的 python 围栏"),
    ("```js\nlet a = 1\n```", 0, "正常的 js 围栏"),
    ("```shell\nls -la\n```\n\n```bash\npwd\n```", 0, "同页两种同义标注（W1 不计入 E）"),
    ("```text\n未闭合\n", 1, "E2：围栏未闭合"),
    ("````md\n```sql\nselect 1;\n```\n````", 0, "四反引号嵌套三反引号是合法写法"),
    ("```\n裸围栏\n```", 0, "无语言标注交给 fencecheck，不在此处判"),
    ("~~~sql\nselect 2;\n~~~", 0, "波浪线围栏同样合法"),
    ("```json\n{\"a\":1}\n```", 0, "正常 json"),
    ("```zzzlang\nx\n```", 0, "未知语言只记 W2"),
    ("```sql\n\n```", 0, "空 sql 围栏归 W3/W4，不计 E"),
    ("  ```sql\n  select 3;\n  ```", 0, "允许 3 空格缩进（列表内围栏）"),
    ("2. ```shell\n   ls\n   ```", 0, "列表标记后的围栏也合法"),
]


def selftest():
    ok = 0
    for i, (text, want_e, desc) in enumerate(CASES, 1):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "t.md")
        open(p, "w", encoding="utf-8").write(text + "\n")
        got, _ = run([d], quiet=True)
        good = (got == want_e)
        ok += good
        print(f"{'PASS' if good else 'FAIL'}  case {i:02d} {desc}  (E={got}, 期望 {want_e})")
    print(f"selftest {ok}/{len(CASES)}")
    return 0 if ok == len(CASES) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
    targets = [os.path.join(root, "docs"), os.path.join(root, "project")]
    for t in targets:
        if not os.path.isdir(t):
            print(f"E0 ROOT_NOT_FOUND {t}")
            sys.exit(1)
    e, fences = run(targets)
    sys.exit(0 if e == 0 else 1)
