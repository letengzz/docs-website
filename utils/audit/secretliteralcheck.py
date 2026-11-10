#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""secretliteralcheck.py —— 文档示例里「疑似真实凭据字面量」巡检（第一百四十五项巡检）

## 动机（又一个「内容维度整体没人看」）

本库有大量讲密钥、凭据、签名的页面，示例代码里常出现 `AKIA…` / `sk-…` /
PEM 私钥头 / 长 hex / 明文口令。既有巡检各管一段，都不看**示例里的字符串长得像不像真凭据**：

  * `fencecheck` —— 围栏开闭与语言标注是否合法；
  * `tickscheck` —— 反引号游程是否越界；
  * `fencelangcheck` / `langmatchcheck` —— 语言标注对不对；
  * `placeholdercheck` —— 有没有留 `TODO` / `待补` 这类占位文字。

写得像真值，读者可能直接复制误用；更糟的是把真实值贴进文档。这一项只读
`*.md`，逐行找「凭据形态」，再看有没有占位标注，最后分级。

## 判据（分级 = 修法不同）

  E1 疑似真实凭据字面量，且同一行 / 相邻一行**没有任何示例标注**（必须修）
  W1 占位符写法不规范：用了示例词，但字面量形态仍像真值（非口令族）
  W2 示例口令未脱敏：口令族的值仍在以「像口令的字符串」示人（含弱演示口令）

  E0 ROOT_NOT_FOUND  扫描根不存在（退出码 2）

## 六类形态

  AWS_KEY        `AKIA|ASIA` + 16 位大写字母数字
  GITHUB_TOKEN   `ghp_|gho_|github_pat_` 前缀
  SK_KEY         `sk-` + ≥20 位字母数字
  PEM_HEADER     `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`
  HEX40          ≥40 位连续 hex
  PLAIN_PASSWORD `password|passwd|secret|token` + `[:=]` + ≥8 位引号字符串

## 白名单（同一行或相邻一行判定）

含 `EXAMPLE` / `示例` / `占位` / `假` / `fake` / `dummy` / `placeholder` /
`your-` / `xxx` / `<...>` / 全 0 / 全 X。字面量**自身**带强占位形态
（`<...>`、`your-`、`xxx`、`placeholder`、`dummy`、`示例`、`占位`、
`change-me`、全 0、全 X）直接跳过；只在旁边写字而字面量仍像真值的，记 W1/W2。

**明确在讲解检测规则本身的页面**用 `--allow <path>` 传入，脚本不硬编码任何路径豁免。

## 口径（被真实语料打出来的，见 /tmp/sr_audit_summary.md 的返工记录）

1. **长 hex 不能裸判**：本库大量 `sha256sum` 校验和、git commit、镜像 digest、
   资源文件名、EVALSHA 都是 ≥40 位 hex，全不是凭据。首版「见 ≥40 hex 就报」一次造出
   上百条假 E1。改为**只认被赋给凭据槽位的 hex**（见 `CRED_SLOT_RE`），这是把判据从
   「长得像」改成「被当成凭据用」，不是给某几个文件加豁免。
2. **字面量必须是字面量**：`"$POSTGRES_PASSWORD"`、`${VAR:?msg}`、`$(openssl rand …)`、
   psql 的 `:'owner_pw'` 都是变量 / 命令替换，不是明文值。
3. **口令族按熵分流**：`admin123` / `abcd1234` 这类弱演示口令不是「疑似真实凭据」，
   但确实没脱敏 → `W2`；只有「大小写+数字+符号、长度 ≥10」的高熵值才够格进 `E1`。
4. **凭据字面量须落在 ASCII 凭据字符集**：全文检索例句 `token='在线协作任务看板'` 里的
   `token` 是分词结果不是凭据。要求值至少含 1 个 ASCII 字母/数字且不含非 ASCII 字符，
   中文自然语言字符串一律不进结论（不是给某个文件开豁免，是把「凭据字面量」定义清楚）。

## 用法

    python3 utils/audit/secretliteralcheck.py                       # 扫 docs 与 project
    python3 utils/audit/secretliteralcheck.py --root docs --root project
    python3 utils/audit/secretliteralcheck.py --allow docs/Tools/DevEnvironment/Secrets/index.md
    python3 utils/audit/secretliteralcheck.py --selftest
    python3 utils/audit/secretliteralcheck.py --json

退出码：0 = 无 E1（W 不影响退出码）；1 = 存在 E1；2 = 参数 / 根目录错误。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

# ------------------------------------------------------------------ 形态正则
PATTERNS = [
    ("AWS_KEY", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GITHUB_TOKEN", re.compile(r"\b(?:ghp_|gho_|github_pat_)[A-Za-z0-9_]{16,}\b")),
    ("SK_KEY", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("PEM_HEADER", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("HEX40", re.compile(r"\b[0-9a-fA-F]{40,}\b")),
    ("PLAIN_PASSWORD", re.compile(
        r"(?<![A-Za-z])(?:password|passwd|secret|token)\s*(?::\s+|=\s*)[\"']([^\"']{8,})[\"']",
        re.I)),
]

# 凭据槽位：hex 只有被赋给这些名字时才算「被当成凭据用」
CRED_SLOT_RE = re.compile(
    r"\b(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|"
    r"secret[_-]?key|private[_-]?key|client[_-]?secret|client[_-]?id|"
    r"signing[_-]?key|credential|ak|sk|key)\b\s*[:=]", re.I)

# 示例标注（同一行 / 相邻一行）
MARK_RE = re.compile(
    r"EXAMPLE|示例|占位|假(?!如|设|使|若|想|象|冒|装|定|期|以|话)|"
    r"fake|dummy|placeholder|your-|xxx|<[^>]{1,60}>|0{8,}|[Xx]{6,}", re.I)

# 字面量自带的强占位形态：直接跳过，不进分级
STRONG_PLACEHOLDER = re.compile(
    r"<[^>]*>|your-|xxx|placeholder|dummy|示例|占位|change[-_]?me|"
    r"0{8,}|[Xx]{6,}", re.I)

# 变量引用 / 命令替换：不是明文值
VAR_VALUE = re.compile(r"^\$|^\$\{|\$\(|\$\{")


def looks_like_placeholder(lit: str) -> bool:
    return bool(STRONG_PLACEHOLDER.search(lit))


def high_entropy(v: str) -> bool:
    """口令值是否像一条随机生成的真凭据。"""
    classes = sum(bool(re.search(p, v)) for p in (r"[a-z]", r"[A-Z]", r"[0-9]", r"[^\w\s]"))
    return (len(v) >= 10 and classes >= 3) or (len(v) >= 24 and bool(re.fullmatch(r"[A-Za-z0-9+/=_-]+", v)))


def find_literals(line: str):
    """返回 [(kind, literal)]，同一字面量只报一次。"""
    out, seen = [], set()
    for kind, rx in PATTERNS:
        for m in rx.finditer(line):
            lit = m.group(1) if kind == "PLAIN_PASSWORD" else m.group(0)
            if kind == "HEX40":
                # 口径 1：长 hex 必须是「被赋给凭据槽位」的值，否则按摘要 / 校验和 / 提交号跳过
                if not CRED_SLOT_RE.search(line):
                    continue
            if kind == "PLAIN_PASSWORD":
                # 口径 2：变量 / 命令替换不是明文值；口径 4：中文自然语言不是凭据字面量
                if VAR_VALUE.search(lit) or not re.search(r"[A-Za-z0-9]", lit) \
                        or re.search(r"[^\x00-\x7f]", lit):
                    continue
            key = (kind, lit)
            if key in seen:
                continue
            seen.add(key)
            out.append(key)
    return out


def check_text(text: str, allowed: bool = False):
    """返回 [(level, kind, lineno, literal)]。"""
    if allowed:
        return []
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        ctx = "\n".join(lines[max(0, i - 1): i + 2])
        marked = bool(MARK_RE.search(ctx))
        for kind, lit in find_literals(line):
            if looks_like_placeholder(lit):
                continue
            if kind == "PLAIN_PASSWORD":
                # 口令族：只有「无标注 + 高熵」才够格进 E1；其余一律 W2（示例口令未脱敏）
                level = "E1" if (not marked and high_entropy(lit)) else "W2"
            else:
                level = "W1" if marked else "E1"
            out.append((level, kind, i + 1, lit))
    return out


def snippet(lit: str, limit: int = 48) -> str:
    return lit if len(lit) <= limit else lit[:limit - 1] + "…"


def iter_md(roots):
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for fn in sorted(files):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def run(roots, allow, as_json=False):
    allow_abs = {os.path.abspath(p) for p in allow}
    findings, files = [], 0
    for path in iter_md(roots):
        files += 1
        rel = os.path.relpath(path)
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        for level, kind, ln, lit in check_text(text, os.path.abspath(path) in allow_abs):
            findings.append((level, rel, ln, kind, snippet(lit)))
    e = sum(1 for f in findings if f[0].startswith("E"))
    w = len(findings) - e
    if as_json:
        print(json.dumps({
            "files": files, "matches": len(findings), "E": e, "W": w,
            "findings": [{"level": a, "file": b, "line": c, "kind": d, "snippet": s}
                         for a, b, c, d, s in findings],
        }, ensure_ascii=False))
    else:
        for level, rel, ln, kind, snip in findings:
            print(f"{level} {rel}:{ln} {kind} {snip}")
        print(f"files={files} matches={len(findings)} E={e} W={w}")
    return 1 if e else 0


# ---------------------------------------------------------------- selftest
# (名称, markdown, 期望级别集合)
CASES = [
    ("AWS 裸值", "key = AKIAQWERTYUIOPASDF12\n", {"E1"}),
    ("GitHub token 裸值", "TOKEN=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n", {"E1"}),
    ("sk- 裸值", "Authorization: Bearer sk-live1234567890abcdefghijklmn\n", {"E1"}),
    ("PEM 私钥头", "-----BEGIN RSA PRIVATE KEY-----\n", {"E1"}),
    ("凭据槽位里的长 hex", "client-secret: 65069dcfd21288d79730613b6a93ebf4f84780ae\n", {"E1"}),
    ("高熵明文口令无标注", 'DB_PASSWORD="S3cr3t-Token-9f2a"\n', {"E1"}),
    ("尖括号占位", "AKIA<YOUR_KEY_ID>\n", set()),
    ("EXAMPLEPLACEHOLDER 形态", "AKIAEXAMPLEPLACEHOLDER\n", set()),
    ("全 0 占位", "secret = '0000000000000000'\n", set()),
    ("全 X 占位", "token: 'XXXXXXXXXXXXXXXX'\n", set()),
    ("your- 占位", "secret: 'your-secret-key'\n", set()),
    ("同行示例标注", "AWS_KEY=AKIAQWERTYUIOPASDF12  # 示例值\n", {"W1"}),
    ("相邻行示例标注（跨行）", "下面这行是示例：\nAKIAQWERTYUIOPASDF12\n", {"W1"}),
    ("AWS 官方示例键形态仍像真值", "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n", {"W1"}),
    ("示例口令未脱敏", 'password="S3cr3t-Token-9f2a"  # 示例\n', {"W2"}),
    ("代码块内", "```shell\nexport AKIAKEY=AKIAQWERTYUIOPASDF12\n```\n", {"E1"}),
    ("容器内", "::: tip 说明\nAKIAQWERTYUIOPASDF12\n:::\n", {"E1"}),
    ("sha256sum 校验和不是凭据", "b4143947ffa03381e83438998b61f80697b7c75a7596f917b6d801cbc578163f  d1.dump\n", set()),
    ("git commit 不是凭据", "commit f0f13a3a08b2757997410f3a1c38bdc22973c525（2020-10-12）\n", set()),
    ("镜像 digest 不是凭据", "FROM nginx@sha256:3dd08163706a0e9de2ce8b9b3b1f5d3a5e8f6b1c2d3e4f5a6b7c8d9e0f1a2b3c\n", set()),
    ("检测规则正则示例", "grep -nE 'sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}' .\n", set()),
    ("全文检索 token 不是凭据", "-- 期望：只有一行 alias=word，token='在线协作任务看板'\n", set()),
    ("变量引用不是明文", 'POSTGRES_PASSWORD: "${POSTGRES_PASSWORD:?must be set}"\n', set()),
    ("psql 变量不是明文", "create role app_owner login password :'owner_pw';\n", set()),
    ("弱演示口令记 W2", "admin: { password: 'admin123', name: '管理员' }\n", {"W2"}),
    ("--allow 检测规则页", "AKIAQWERTYUIOPASDF12\n", set()),
]


def selftest() -> int:
    ok = 0
    for idx, (name, md, want) in enumerate(CASES, 1):
        got = {f[0] for f in check_text(md, allowed=(name.startswith("--allow")))}
        good = got == want
        ok += bool(good)
        print(f"  [{'PASS' if good else 'FAIL'}] {idx:02d} {name}: 得到 {sorted(got)} 期望 {sorted(want)}")
    print(f"SELFTEST {ok}/{len(CASES)} PASS")
    return 0 if ok == len(CASES) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="文档示例里疑似真实凭据字面量巡检")
    ap.add_argument("--root", action="append", nargs="+", default=None,
                    help="扫描根，可重复；默认 docs 与 project")
    ap.add_argument("--allow", action="append", default=[], metavar="PATH",
                    help="讲解检测规则本身的页面，整页跳过（不硬编码豁免）")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    roots = [r for grp in args.root for r in grp] if args.root else ["docs", "project"]
    for r in roots:
        if not os.path.isdir(r):
            print(f"E0 ROOT_NOT_FOUND {r}")
            return 2
    return run(roots, args.allow, args.json)


if __name__ == "__main__":
    sys.exit(main())
