#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""secretleakcheck.py —— 「文档示例里的疑似真实凭证」巡检（第 257 天新立，第 138 项巡检）

背景
----
本库 3,100+ 页技术文档里有 17,000 多个代码围栏。为了让示例「能照着跑」，作者会写
`password = "..."`、`Authorization: Bearer ...`、`AWS_ACCESS_KEY_ID=...` 这类行。
绝大多数写的是占位符，但有三种情况会把**真实值**带进仓库：

1. 从本地配置文件里复制一段「能跑」的样例，忘了替换；
2. 从线上日志里贴一段请求头，里面带着真实 token；
3. 生成一段「随机串」当示例，长度与字符集恰好与真实密钥同构——**它不可用，但扫描器
   与代码评审都会当成泄露**，于是每次安全扫描都要人工判一次。

既有的 137 项巡检没有一项看这件事：`placeholdercheck` 管的是「待补充 / TODO」这类
**占位词**，`invisiblecheck` 管不可见字符，`htmltagcheck` 管行内标签，`fwcodecheck`
管围栏内的全角标点——都在管「写法」，没有一项管「这里是不是不该出现的值」。

判据（E = 错误，必须修；W = 提示，登记长尾）
--------------------------------------------
  E0 ROOT_NOT_FOUND       根目录不存在
  E1 NO_PAGES             一个 index.md 都没扫到（活性）
  E2 NO_FENCE             全库一个代码围栏都没扫到（活性，防解析器整体失效）
  E3 PEM_PRIVATE_KEY      `-----BEGIN ... PRIVATE KEY-----` 私钥块
  E4 CLOUD_ACCESS_KEY     `AKIA` / `ASIA` / `LTAI` / `AKID` 开头的 16~20 位访问密钥
  E5 API_TOKEN            `sk-` / `ghp_` / `xox?-` / `AIza` 实值
  W5 JWT_LITERAL          `eyJhbGciOi` 开头的三段式 JWT
  W1 HARD_CODED_PASSWORD  `password/passwd/pwd` 赋了非占位符的值
  W2 PRIVATE_IP           10./172.16-31./192.168. 内网地址
  W3 INTERNAL_HOST        `.internal` / `.local` / `.corp` / `.intra` 结尾的主机名
  W4 HIGH_ENTROPY         引号内 ≥32 位、大小写+数字混合的可疑长串

为什么凭证类判 E、环境类判 W
----------------------------
私钥与云厂商访问密钥**一旦是真值就是事故**，没有「示例豁免」这一说（示例应当用
`AKIAIOSFODNN7EXAMPLE` 这种官方示例值）。而内网 IP 与 `.local` 域名在示例里非常常见
（「连到 192.168.1.10 上的 Redis」），判 E 会产生几百条假阳性，只能判 W 供人抽看。

JWT 单列为 W5 也是同一条理由：全库第一轮跑出来的唯一一条 E5 是
`project/Complete/BlogPlatform/AuthRoles` 里的教学样例——`{"sub":"admin"}` 加一段
截断的签名，三段结构本身就是那一节的讲解重点。JWT 在文档里几乎总是示例，判 E 只会
训练读者「忽略这条告警」。

口径
----
- **只扫围栏内**（`fenceutil.scan`）。正文里提到「password」是叙述，不是可复制的值。
- 占位符白名单命中即跳过：`xxxx` `***` `your_` `your-` `<...>` `${...}` `{{...}}`
  `changeme` `example` `placeholder` `dummy` `mock` `fake` `test` `sample`
  `123456` `secret`（字面） `TODO` `...`。
- 注释行同样扫：`# password=真实值` 也是泄露。
- 语言不限：yaml / shell / json / ts / java 都可能带凭证。

用法
----
  python3 utils/audit/secretleakcheck.py [--root docs project] [--selftest]
  python3 utils/audit/secretleakcheck.py --root docs/Backend/LodgingOps

退出码：0 = 无 E；1 = 有 E 或活性失败；2 = 用法错误
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fenceutil import scan as fence_scan  # noqa: E402

PEM = re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")
CLOUD_KEY = re.compile(r"\b(?:AKIA|ASIA|LTAI|AKID)[0-9A-Za-z]{12,20}\b")
TOKEN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_\-]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|gho_[A-Za-z0-9]{20,}"
    r"|xox[abprs]-[A-Za-z0-9\-]{10,}"
    r"|AIza[0-9A-Za-z_\-]{30,})"
)
JWT = re.compile(r"\beyJhbGciOi[A-Za-z0-9_\-\.]{20,}")
PASSWORD = re.compile(
    r"(?i)\b(?:password|passwd|pwd|secret_key|access_key_secret)\b\s*[:=]\s*"
    r"[\"']?([^\s\"',;]{3,})"
)
PRIVATE_IP = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3})\b"
)
INTERNAL_HOST = re.compile(
    r"\b[a-z0-9][a-z0-9\-]*(?:\.[a-z0-9\-]+)*\.(?:internal|local|corp|intra)\b", re.I
)
QUOTED = re.compile(r"[\"']([^\"'\s]{32,})[\"']")

# `.env.local`、`vite.config.local` 这类是**文件名**不是主机名（第 257 天首轮 141 条 W3
# 里排第一的就是它），按首段排除。
CONFIG_STEM = {"env", "tsconfig", "vite", "next", "nuxt", "config", "app", "web"}

# 强标记：命中即判定为占位符，与长度无关
PLACEHOLDER_STRONG = (
    "xxxx", "***", "your_", "your-", "yourkey", "<", "${", "{{", "changeme",
    "example", "placeholder", "redacted",
)
# 弱标记：只在短值（< 24 字符）上生效
# 为什么要分两级：长 token 里出现 "123456" 或 "test" 是随机字符的正常结果，
# 用弱标记判长串会把「真泄露」全部放过（第 257 天自测第 8 例就是被 123456 吃掉的）。
PLACEHOLDER_WEAK = (
    "dummy", "mock", "fake", "test", "sample", "123456", "secret", "todo",
    "...", "none", "null",
)


def is_placeholder(val: str) -> bool:
    low = val.lower().strip("\"'")
    if any(p in low for p in PLACEHOLDER_STRONG):
        return True
    return len(low) < 24 and any(p in low for p in PLACEHOLDER_WEAK)


def entropy_like(val: str) -> bool:
    """≥32 位、同时有大小写与数字，且不是纯单词/纯路径。"""
    if len(val) < 32:
        return False
    has_low = any(c.islower() for c in val)
    has_up = any(c.isupper() for c in val)
    has_dig = any(c.isdigit() for c in val)
    if not (has_low and has_up and has_dig):
        return False
    if val.count("/") >= 2 or val.count("-") >= 4:
        return False
    return True


def analyze_line(line: str):
    """纯函数：一行 → [(code, detail)]。注释行同样处理。"""
    out = []
    if PEM.search(line):
        out.append(("E3", "PEM_PRIVATE_KEY"))
    for m in CLOUD_KEY.finditer(line):
        if not is_placeholder(m.group(0)):
            out.append(("E4", f"CLOUD_ACCESS_KEY {m.group(0)[:6]}…"))
            break
    for m in TOKEN.finditer(line):
        if not is_placeholder(m.group(0)):
            out.append(("E5", f"API_TOKEN {m.group(0)[:8]}…"))
            break
    for m in PASSWORD.finditer(line):
        val = m.group(1).rstrip("\\")
        if val and not is_placeholder(val) and not val.startswith("$"):
            out.append(("W1", f"HARD_CODED_PASSWORD {val[:4]}…"))
            break
    m = PRIVATE_IP.search(line)
    if m:
        out.append(("W2", f"PRIVATE_IP {m.group(0)}"))
    m = INTERNAL_HOST.search(line)
    if m and m.group(0).split(".")[0].lower() not in CONFIG_STEM:
        out.append(("W3", f"INTERNAL_HOST {m.group(0)}"))
    for m in JWT.finditer(line):
        if not is_placeholder(m.group(0)):
            out.append(("W5", f"JWT_LITERAL {m.group(0)[:8]}…"))
            break
    for m in QUOTED.finditer(line):
        if entropy_like(m.group(1)) and not is_placeholder(m.group(1)):
            out.append(("W4", f"HIGH_ENTROPY {m.group(1)[:6]}…"))
            break
    return out


def analyze_text(text: str):
    """纯函数：整页文本 → (findings, fences)。findings = [(code, lineno, detail)]。"""
    lines = text.split("\n")
    mask, blocks, _unclosed = fence_scan(text)
    findings = []
    if not blocks:
        return findings, 0
    inside = set()
    for start, end, _info in blocks:
        for ln in range(start + 1, end):
            inside.add(ln)
    for ln in sorted(inside):
        for code, detail in analyze_line(lines[ln]):
            findings.append((code, ln + 1, detail))
    return findings, len(blocks)


def walk(roots):
    for root in roots:
        for dirpath, _dn, fns in os.walk(root):
            if "index.md" in fns:
                yield os.path.join(dirpath, "index.md")


def selftest():
    """14 条纯函数自测，全部走 analyze_text（含围栏切分）。"""
    cases = [
        ("普通示例无告警",
         "# T\n\n```js\nconst a = 1;\n```\n", []),
        ("shell 占位符密码不算",
         "# T\n\n```shell\nexport DB_PASSWORD=your_password_here\n```\n", []),
        ("yaml 真值密码 → W1",
         "# T\n\n```yaml\npassword: Hunter2Prod\n```\n", ["W1"]),
        ("注释里的密码也算",
         "# T\n\n```shell\n# password=Abc123Xyz\necho hi\n```\n", ["W1"]),
        ("AWS 示例键（官方 EXAMPLE）→ E4? 否（含 example）",
         "# T\n\n```shell\nexport AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\n```\n", []),
        ("AWS 形似真键 → E4",
         "# T\n\n```shell\nexport AWS_ACCESS_KEY_ID=AKIA3XQ7ZR2LMNOPQR4T\n```\n", ["E4"]),
        ("PEM 私钥块 → E3",
         "# T\n\n```text\n-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n```\n", ["E3"]),
        ("GitHub token → E5",
         "# T\n\n```shell\ncurl -H 'Authorization: Bearer ghp_abcdefghijklmnopqrstuvwxyz0123456789'\n```\n",
         ["E5"]),
        ("内网 IP → W2",
         "# T\n\n```shell\nredis-cli -h 192.168.1.10\n```\n", ["W2"]),
        ("172.20 段 → W2",
         "# T\n\n```yaml\nhost: 172.20.3.4\n```\n", ["W2"]),
        ("172.40 不是内网 → 无",
         "# T\n\n```yaml\nhost: 172.40.3.4\n```\n", []),
        (".internal 域名 → W3",
         "# T\n\n```yaml\nurl: http://api.pay.internal/v1\n```\n", ["W3"]),
        ("正文里的 password 不算（围栏外）",
         "# T\n\n这里讨论 password 该怎么存。\n", []),
        ("教学用 JWT → W5（不是 E）",
         "# T\n\n```text\neyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.abc123\n```\n",
         ["W5"]),
        ("配置文件 env.local 不算主机名",
         "# T\n\n```shell\ncp .env.example .env.local\n```\n", []),
        ("高熵串 → W4，短串不算",
         "# T\n\n```js\nconst k = \"Zm9vYmFyQmF6UXV4MTIzNDU2Nzg5MEFCQ0RFRg\";\nconst s = \"abc\";\n```\n",
         ["W4"]),
    ]
    ok = 0
    for name, text, want in cases:
        got, _ = analyze_text(text)
        codes = sorted({c for c, _, _ in got})
        if codes == sorted(want):
            ok += 1
        else:
            print(f"  FAIL {name}: want {want} got {codes}")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()

    roots, i = ["docs", "project"], 1
    while i < len(argv):
        if argv[i] == "--root":
            roots, i = [], i + 1
            while i < len(argv) and not argv[i].startswith("--"):
                roots.append(argv[i])
                i += 1
        else:
            i += 1

    missing = [r for r in roots if not os.path.isdir(r)]
    if missing:
        print(f"E0 ROOT_NOT_FOUND {' '.join(missing)}")
        return 1

    pages = 0
    fences = 0
    all_findings = []
    for page in walk(roots):
        pages += 1
        try:
            text = open(page, encoding="utf-8").read()
        except OSError:
            continue
        found, nf = analyze_text(text)
        fences += nf
        for code, lineno, detail in found:
            all_findings.append((code, page.replace(os.sep, "/"), lineno, detail))

    if pages == 0:
        print("E1 NO_PAGES 没有扫到任何 index.md")
        return 1
    if fences == 0:
        print("E2 NO_FENCE 一个代码围栏都没扫到（解析器可能整体失效）")
        return 1

    for code, page, lineno, detail in all_findings:
        print(f"{code} {page}:{lineno} {detail}")

    cnt = {}
    for code, *_ in all_findings:
        cnt[code] = cnt.get(code, 0) + 1
    e_cnt = sum(v for k, v in cnt.items() if k.startswith("E"))
    w_cnt = sum(v for k, v in cnt.items() if k.startswith("W"))
    print(f"\npages={pages} fences={fences} findings={len(all_findings)}")
    print("分项：" + " ".join(f"{k}={cnt.get(k, 0)}"
                             for k in ("E3", "E4", "E5", "W1", "W2", "W3", "W4", "W5")))
    print(f"合计 E={e_cnt} W={w_cnt}")
    print("RESULT", "OK" if e_cnt == 0 else "FAIL")
    return 0 if e_cnt == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
