#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""homepathcheck.py —— 文档示例里的「本机绝对路径与用户名」巡检（第 248 天新立，第一百三十项巡检）。

## 为什么立这一项

本库的 129 项巡检里，管路径的有四道：`linkexistcheck` 管 Markdown 链接、`inlinepathcheck`
（第 129 项）管散文里反引号写出的**本仓库**路径、`fencepathcheck` 管代码块标题、
`cmdtargetcheck` 管 shell 命令里的脚本是否存在。**没有一道管「读者机器上的路径」**——也就是
示例里写出来的 `/Users/cuifendemac/...`、`/home/alice/...`、`C:\\Users\\Albert han\\...`。

这类写法有三个具体危害：

1. **泄露**：作者的本机用户名进了公开仓库（本库确实出现过，见本轮修掉的 4 处）；
2. **不可复现**：读者复制命令必然失败，而失败信息（`No such file or directory`）看起来像
   「文档写错了」，实际是「路径是你的机器上的、不是我的」；
3. **不可搜索**：带用户名的路径在别人的机器上永远搜不到，等于把一句可执行的说明变成了噪音。

它通过了现有全部巡检：不渲染成链接（`linkexistcheck` 不管）、不是本仓路径
（`inlinepathcheck` 只认本仓分类目录前缀）、是合法 shell（`cmdtargetcheck` 只查脚本存在性）。

## 判据

    E0 ROOT_NOT_FOUND     既无 docs/ 也无 project/
    E1 NO_PAGES           扫到 0 个 Markdown（活性，防止路径写错后空跑全绿）
    E2 PRIVATE_HOME       `/Users/<name>/` 或 `/home/<name>/`，且 `<name>` 不是占位符
    E3 WINDOWS_PRIVATE    `C:\\Users\\<name>` 或 `C:/Users/<name>`，同样排除占位符
    W1 PERCENT_ENCODED    路径里含 `%20` 这类百分号编码（能读，但复制不可用）
    W2 TEMP_ARTIFACT      指向 `/tmp` 下的具体文件（**只计数、不逐条打印**：全库 653 处，
                          `/tmp` 本身是合法的临时目录，逐条打印会把真缺陷淹掉）
    N1 PAGES / N2 HITS / N3 PLACEHOLDERS   只计数

## 口径（三轮才收敛，记在这里免得下次重犯）

1. **占位符白名单**：`<username>`、`{user}`、`$USER`、`%USERNAME%`、`you`、`your`、`user`、
   `username`、`你的用户名`、`xxx`、`...`（省略号写法）、`~`。白名单是**登记式**的：新增
   写法必须加进 `PLACEHOLDERS` 并补一条自测。
2. **正则语境豁免**：教学页面会写 `grep -nE '([A-Za-z]:\\\\|/Users/|/home/)'` 这类**用来查
   绝对路径的正则**。这类行里 `/Users/` 后面不跟用户名，天然不匹配；但为稳妥，含
   `[A-Za-z]:` 或 `|/Users/|` 的行整行跳过——**判据不能惩罚「教别人怎么查」**。
3. **只认「路径形状」**：必须 `/Users/<token>/`（结尾带斜杠）或 `C:\\Users\\<token>`。
   光写 `/Users/` 不算，`/Users/...` 因为 `...` 在白名单里也不算。

## 用法

    python3 utils/audit/homepathcheck.py               # 全库
    python3 utils/audit/homepathcheck.py --selftest    # 自测（临时目录里的夹具）
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

ROOTS = ("docs", "project")

PLACEHOLDERS = {
    "username", "user", "users", "you", "your", "yourname", "your-name",
    "name", "xxx", "xxx-user", "...", "…", "me", "alice-placeholder",
    "你的用户名", "用户名", "用户", "某人",
}

POSIX_RE = re.compile(r"/(?:Users|home)/([^/\s'\"`<>()\[\]{}]+)/")
WIN_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+([^\\/'\"`<>()\[\]{}]+)")
PCT_RE = re.compile(r"%[0-9A-Fa-f]{2}")
TMP_RE = re.compile(r"/tmp/[A-Za-z0-9_.-]+\.(?:py|sh|js|sql|db|csv)")
SKIP_LINE = ("[A-Za-z]:", "|/Users/|", "|/home/")


def is_placeholder(tok: str) -> bool:
    t = tok.strip().strip("\\/").lower()
    if not t:
        return True
    if t.startswith("<") or t.startswith("{") or t.startswith("$") or t.startswith("%"):
        return True
    if set(t) == {"."}:
        return True
    return t in PLACEHOLDERS


def scan_line(line: str):
    """返回 (E2 命中, E3 命中, W1, W2)。"""
    if any(s in line for s in SKIP_LINE):
        return [], [], 0, 0
    e2, e3 = [], []
    for m in POSIX_RE.finditer(line):
        if not is_placeholder(m.group(1)):
            e2.append(m.group(0))
    for m in WIN_RE.finditer(line):
        if not is_placeholder(m.group(1)):
            e3.append(m.group(0))
    w1 = 1 if (e2 or e3) and PCT_RE.search(line) else 0
    w2 = 1 if TMP_RE.search(line) else 0
    return e2, e3, w1, w2


def collect(root: str):
    pages = 0
    hits = []
    for base in ROOTS:
        b = os.path.join(root, base)
        if not os.path.isdir(b):
            continue
        for dirpath, _dirs, files in os.walk(b):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                pages += 1
                p = os.path.join(dirpath, fn)
                try:
                    text = open(p, encoding="utf-8").read()
                except OSError:
                    continue
                for i, line in enumerate(text.splitlines(), 1):
                    e2, e3, w1, w2 = scan_line(line)
                    for h in e2:
                        hits.append(("E2 PRIVATE_HOME", p, i, h, line.strip()[:80]))
                    for h in e3:
                        hits.append(("E3 WINDOWS_PRIVATE", p, i, h, line.strip()[:80]))
                    if w1:
                        hits.append(("W1 PERCENT_ENCODED", p, i, "", line.strip()[:80]))
                    if w2:
                        hits.append(("W2 TEMP_ARTIFACT", p, i, "", line.strip()[:80]))
    return pages, hits


def report(root: str) -> int:
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print("E0 ROOT_NOT_FOUND")
        return 2
    pages, hits = collect(root)
    if pages == 0:
        print("E1 NO_PAGES")
        return 2
    errors = [h for h in hits if h[0].startswith("E")]
    warns = [h for h in hits if h[0].startswith("W")]
    for tag, p, i, frag, ctx in errors + [w for w in warns if w[0].startswith("W1")]:
        rel = os.path.relpath(p, root)
        print(f"{tag} {rel}:{i} {frag or ''} | {ctx}")
    w1 = sum(1 for h in warns if h[0].startswith("W1"))
    w2 = sum(1 for h in warns if h[0].startswith("W2"))
    print(f"pages={pages} E={len(errors)} W1={w1} W2={w2} hits={len(hits)}")
    return 0 if not errors else 1


def selftest() -> int:
    cases = [
        ("/Users/cuifendemac/work/app.py", True, "真实用户名"),
        ("/home/alice/project", True, "Linux 真实用户名"),
        ("C:\\\\Users\\\\Albert han\\\\Desktop", True, "Windows 真实用户名"),
        ("open /Users/<username>/app", False, "占位符尖括号"),
        ("cp -r ~/dotfiles /home/you/", False, "you 是占位符"),
        ("ls /Users/", False, "无用户名"),
        ("ls /Users/.../x", False, "省略号"),
        ("file:///C:/Users/you/a.png", False, "路径占位"),
        ("grep -nE '([A-Za-z]:\\\\\\\\|/Users/|/home/)' f", False, "正则语境"),
        ("图片来自 /Users/bob/Desktop/图 1.png", True, "中文文件名也命中"),
        ("C:/Users/%USERNAME%/AppData", False, "环境变量占位"),
        ("/Users/alice/my%20project", True, "百分号编码仍算 E"),
    ]
    ok = 0
    for line, want, why in cases:
        e2, e3, _w1, _w2 = scan_line(line)
        got = bool(e2 or e3)
        flag = "PASS" if got == want else "FAIL"
        if got == want:
            ok += 1
        print(f"{flag} [{why}] want={want} got={got}")
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return report(a.root)


if __name__ == "__main__":
    sys.exit(main())
