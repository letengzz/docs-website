#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""langmatchcheck.py — 代码块「标注语言 ⇄ 实际内容」一致性巡检 · 第 78 项

为什么立这一项
--------------
第 72 项 `fencecheck` 补齐了「围栏有没有 info string、语言在不在白名单、text 块是不是
在画图」，但它**只读围栏后面那几个字符，从不读块里的内容**。于是这一类债全库静默：

* 标着 `sql` 的块里其实是 `docker exec ... psql -c "..."`——读者复制到客户端里，第一条
  命令就是 `docker`，报错；构建照样成功，shiki 照着 `sql` 高亮，看起来还挺像。
* 标着 `shell` 的块里是纯 SQL——同理，复制到终端里整段失败。
* 标着 `json` 的块少了半个括号——读者复制配置时才发现，文档本身没有任何提示。
* 标着 `yaml` 的块里是 `key=value`——那其实是 `properties`/`ini`。

这四种都属于「**文档看起来对、复制就错**」，而它们恰好是 `fencecheck`（语言存在性）、
`tickscheck`（围栏闭合）、`tablecheck`（表格结构）三者的共同盲区：三张网之间有一个
洞，洞的形状正是「语言标注与内容不匹配」。

判据
----
E0 ROOT_NOT_FOUND   仓库根找不到
E1 NO_FENCES        一个代码块都没扫到（活性判据）
E2 SHELL_IN_SQL     `sql` 块里出现行首 shell 命令（docker/kubectl/npm/git/curl/$ ...）
E3 JSON_INVALID     严格 `json` 块无法被 `json.loads` 解析（jsonc/json5 不参与）
W1 SQL_IN_SHELL     `shell` 块里出现 DML/DDL 行，且整块没有任何 psql/mysql 调用
W2 KEYVAL_IN_YAML   `yaml` 块里过半非空行是 `key=value`（其实是 properties）
W3 DOCKERFILE_IN_SHELL  `shell` 块首行是 `FROM ...`（其实是 Dockerfile）

纪律
----
* **只读**：不写文件、不改台账、不给修复建议的自动执行。
* **宁可漏报不误报**：`sql` 块里出现 `docker` 也可能是注释说明，所以 `E2` 只认**行首**
  命令词，且跳过以 `--`/`#` 开头的行；`W1` 要求整块没有 `psql`/`mysql` 作为反证。
* **语言别名一并认**：`sh`/`zsh`/`bash` 同属 shell；`yml` 与 `yaml` 同族。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/langmatchcheck.py [--selftest] [--root .]
"""

import argparse
import json
import os
import re
import sys
import tempfile

EXT = (".md",)
SKIP_DIRS = {".git", "node_modules", ".vitepress", "dist", ".workbuddy", "__pycache__"}

SHELL_LANGS = {"shell", "bash", "sh", "zsh", "fish", "console"}
SQL_LANGS = {"sql", "plsql", "postgresql", "mysql"}
YAML_LANGS = {"yaml", "yml"}
JSON_LANGS = {"json"}          # jsonc/json5 允许注释与尾逗号，不参与解析
DIAGRAM_LANGS = {"text", "plaintext", "txt", "markdown", "md"}

FENCE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)?(```+|~~~+)\s*([^\s`]*)")
# 只收「不可能出现在 SQL 里」的命令词。`cat`/`source`/`cd`/`ls` 一律不收——
# 首轮实测里 `cat VARCHAR(16) NOT NULL`（列名叫 cat）、`source text NOT NULL`
# 会被它们误判成 shell 命令（见「口径被真实语料打回来」那段）。
SHELL_CMD_RE = re.compile(
    r"^\s*(?:\$\s+)?(docker|docker-compose|kubectl|helm|npm|pnpm|yarn|git|curl|wget|"
    r"python3?|pip3?|mvn|gradle|brew|apt-get|apt|yum|systemctl|ssh|scp|sudo|mkdir)\b"
)
DDL_LINE_RE = re.compile(r"(NOT\s+NULL|VARCHAR\(|PRIMARY\s+KEY|REFERENCES\s+\w+\s*\()", re.I)
SQL_LINE_RE = re.compile(
    r"^\s*(select|insert\s+into|update\s+\w|delete\s+from|create\s+(table|index|role|database|schema)"
    r"|alter\s+table|drop\s+(table|index)|with\s+\w+\s+as|truncate)\b",
    re.I,
)
KEYVAL_RE = re.compile(r"^\s*[A-Za-z_][\w.\-]*\s*=\s*\S")
# 裸大写命令词（Redis/DB 的命令清单页常见：DBSIZE / SELECT 1 / SET k v）
COMMAND_LIST_RE = re.compile(r"^[A-Z]{3,}(\s|$)", re.M)
SQL_EVIDENCE_RE = re.compile(
    r"\b(psql|mysql|mariadb|sqlcmd|sqlite3|clickhouse|clickhouse-client|redis-cli|mongosh|cqlsh|duckdb|influx)\b",
    re.I,
)


def strip_fences_cache(root):
    """返回 [(relpath, lang, content, start_line)]，跳过未闭合块（交给 tickscheck 管）。"""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(EXT):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
            except OSError:
                continue
            i = 0
            while i < len(lines):
                m = FENCE_RE.match(lines[i])
                if not m:
                    i += 1
                    continue
                ticker, lang = m.group(1), (m.group(2) or "").lower()
                j = i + 1
                buf = []
                closed = False
                while j < len(lines):
                    m2 = FENCE_RE.match(lines[j])
                    if m2 and m2.group(1)[0] == ticker[0] and len(m2.group(1)) >= len(ticker) \
                            and not (m2.group(2) or "").strip():
                        closed = True
                        break
                    buf.append(lines[j])
                    j += 1
                if closed:
                    out.append((rel, lang, "\n".join(buf), i + 1))
                    i = j + 1
                else:
                    i += 1
    return out


def check_block(lang, content):
    """返回 [(code, detail)]，code 为 E2/E3/W1/W2/W3。"""
    hits = []
    if not lang or not content.strip():
        return hits
    body = [ln for ln in content.split("\n") if ln.strip()]

    if lang in SQL_LANGS:
        for ln in body:
            s = ln.strip()
            if s.startswith("--") or s.startswith("#"):
                continue
            if SHELL_CMD_RE.match(ln) and not DDL_LINE_RE.search(ln):
                hits.append(("E2", s[:70]))
                break

    if lang in JSON_LANGS:
        # 三类「不是完整 JSON」的合法写法，不参与解析：
        #   ① 用 `...` 省略（AGENTS 允许）；② 片段（首字符不是 { 或 [）；
        #   ③ 带 // 或 # 注释（其实是 jsonc，全库常见于 package.json 说明）。
        first = content.lstrip()[:1]
        placeholder = ("..." in content or "…" in content
                       or any(re.fullmatch(r"\s*\.{1,3}\s*", ln) for ln in body))
        commented = any(ln.strip().startswith(("//", "#")) for ln in body[:3])
        # ④ VitePress 的代码注记（`// [!code focus]`）是渲染指令，不是 JSON 内容
        notation = "[!code" in content
        if not placeholder and not commented and not notation and first in "{[":
            try:
                json.loads(content)
            except Exception as e:  # noqa: BLE001 — 报错文本本身就是证据
                hits.append(("E3", str(e)[:70]))

    if lang in SHELL_LANGS:
        if body and re.match(r"^\s*FROM\s+\S+", body[0], re.I) and " AS " in body[0].upper():
            hits.append(("W3", body[0].strip()[:70]))
        elif not SQL_EVIDENCE_RE.search(content) and not COMMAND_LIST_RE.search(content):
            for ln in body:
                s = ln.strip()
                if s.startswith("#") or s.startswith("--"):
                    continue
                if SQL_LINE_RE.match(ln):
                    hits.append(("W1", s[:70]))
                    break

    if lang in YAML_LANGS:
        kv = sum(1 for ln in body if KEYVAL_RE.match(ln))
        if body and kv * 2 > len(body) and not any(ln.strip().startswith("-") for ln in body):
            hits.append(("W2", f"{kv}/{len(body)} 行是 key=value"))

    return hits


def scan(root):
    blocks = strip_fences_cache(root)
    errors, warns = [], []
    for rel, lang, content, line in blocks:
        for code, detail in check_block(lang, content):
            item = (rel, line, code, detail)
            (errors if code.startswith("E") else warns).append(item)
    return blocks, errors, warns


def report(root="."):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND", root)
        return 1
    blocks, errors, warns = scan(root)
    print(f"fences={len(blocks)} errors={len(errors)} warns={len(warns)}")
    for rel, line, code, detail in errors + warns:
        print(f"{code}\t{rel}:{line}\t{detail}")
    if not blocks:
        print("E1 NO_FENCES 一个代码块都没扫到")
        return 1
    return 1 if errors else 0


# --------------------------------------------------------------------------- selftest
GOOD = """# 混合夹具

```sql
-- 正常 SQL
select id, status from orders where id = 1;
```

```shell
# 正常 shell
docker compose ps
```

```json
{"a": 1, "b": [2, 3]}
```

```yaml
server:
  port: 8080
```
"""

BAD = """# 坏夹具

```sql
docker exec eoh-pg psql -U postgres -c "select 1"
```

```json
{"a": 1, "b": [2, 3}
```

```shell
select id from orders where status = 'PAID';
```

```yaml
spring.datasource.url=jdbc:postgresql://localhost:5432/eoh
spring.datasource.username=eoh
```

```shell
FROM eclipse-temurin:25 AS build
```
"""

TRICKY = """# 干扰夹具

```sql
-- docker exec 只是注释，不算错
select 1;
```

```shell
# 调 psql 的 shell 块，里面的 SQL 不算错标
psql -h localhost -U postgres -c "select 1"
```

```text
select * from orders -- 这是示意图，不是可执行代码
```

```jsonc
// jsonc 允许注释，不参与解析
{"a": 1,}
```
"""


def selftest():
    root = tempfile.mkdtemp(prefix="langmatch-")
    for name, text in (("good.md", GOOD), ("bad.md", BAD), ("tricky.md", TRICKY)):
        with open(os.path.join(root, name), "w", encoding="utf-8") as f:
            f.write(text)

    blocks, errors, warns = scan(root)
    ecodes = {c for _, _, c, _ in errors}
    wcodes = {c for _, _, c, _ in warns}
    def has(path_suffix, code):
        return any(p.endswith(path_suffix) and c == code for p, _, c, _ in errors + warns)

    cases = [
        ("E1-activity", len(blocks) == 13),
        ("good-clean", not any(p.endswith("good.md") for p, _, _, _ in errors + warns)),
        ("E2-shell-in-sql", has("bad.md", "E2")),
        ("E3-json-invalid", has("bad.md", "E3")),
        ("W1-sql-in-shell", has("bad.md", "W1")),
        ("W2-keyval-in-yaml", has("bad.md", "W2")),
        ("W3-dockerfile", has("bad.md", "W3")),
        ("tricky-comment-ok", not any(p.endswith("tricky.md") and c == "E2"
                                      for p, _, c, _ in errors)),
        ("tricky-psql-ok", not any(p.endswith("tricky.md") and c == "W1"
                                   for p, _, c, _ in errors + warns)),
        ("tricky-jsonc-ok", not any(p.endswith("tricky.md") and c == "E3"
                                    for p, _, c, _ in errors)),
        ("tricky-text-ok", not any(p.endswith("tricky.md") and c == "W1"
                                   for p, _, c, _ in errors + warns)),
        ("codes-shape", ecodes <= {"E2", "E3"} and wcodes <= {"W1", "W2", "W3"}),
    ]
    ok = 0
    for name, cond in cases:
        print(("PASS " if cond else "FAIL ") + name)
        ok += 1 if cond else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return report(a.root)


if __name__ == "__main__":
    sys.exit(main())
