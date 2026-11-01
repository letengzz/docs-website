#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cmdtargetcheck.py —— 「验证命令里引用的实物在不在」巡检（第 234 天新立，第一百一十六项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

本仓关于「验证」的门已经有四道，各看一层：

  * `tailcheck.py`         —— 有没有 `## 验证方式` 这一节；
  * `verifyevidencecheck.py` —— 节里有没有可执行物（围栏 / 命令式行内代码）；
  * `expectcheck.py`       —— 命令后面有没有「期望值」；
  * `sectionordercheck.py` —— 这一节在不在参考资料之前。

四道全绿，仍然可以写出这样的验证节：

    python3 utils/audit/tablesumcheck.py --selftest

而 `utils/audit/tablesumcheck.py` 可能已经被改名、合并或删除——读者照着敲，得到
`can't open file`，然后**不知道该信文档还是信自己**。这类缺陷与第 94 项（占位词）
同族：**结构完整、期望明确、命令跑不起来**。

四道门全在问「这一节写得像不像验证」，**没有一道问「这条命令指向的东西还在不在」**。

## 判据（E = 错误，必须修；W = 提示，登记长尾）

  E0 ROOT_NOT_FOUND      仓库根不存在（活性判据）
  E1 NO_BLOCKS           一个 shell 围栏都没扫到（活性判据：拒绝在空集上给全绿）
  E2 MISSING_SCRIPT      命令里引用的 `utils/**.py|mjs|ts` 文件不存在
  W1 MISSING_PATH        命令里引用的仓内相对路径（docs/… / project/…）不存在
  W2 MISSING_PKG_SCRIPT  `pnpm <x>` / `npm run <x>` 里 x 不在 package.json scripts 中
  N1 BLOCKS / N2 COMMANDS / N3 TARGETS  只计数

## 口径（四条，都是被真实语料逼出来的）

1. **只扫 shell 类围栏**（`shell` / `bash` / `sh` / `zsh` / `console`）。正文里
   提到 `utils/audit/x.py` 是叙述，不是命令；把它算进来会立刻造出上百条噪声。
2. **带占位符的路径一律跳过**：`<root>`、`$VAR`、`{period}`、`...`、`xxx`、
   `*` 都是「读者自己填」的位置，判它不存在是错的。
3. **`utils/` 下的脚本判 E，其它路径判 W**：脚本是本仓自有的可执行物，缺了
   命令必然失败；而 `docs/xxx.md` 这种路径可能出现在「跑完会生成」的语境里，
   只能提示。
4. **`pnpm install` 不是脚本**：包管理器的内置子命令必须先排除，否则每条
   `pnpm install` 都会被判成「package.json 里没有 install」。
5. **路径要带本仓分类前缀才判**：`docs/Backend/…` 是本仓，`docs/api/openapi.yaml`
   是读者自己工程里的 `docs/`——同形而不同义，只认前者（后者记 `N4`）。
6. **只判本仓自有脚本前缀**（`docs:*` / `lint*`）：`pnpm dev` / `pnpm build` 在
   教程语境里指读者的工程，本仓没有这两个脚本也不该报红。

## 纪律

只读、不改文档、不执行命令。本项只负责把「哪个文件、第几行、哪条命令、缺什么」列出来。
"""

import argparse
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCAN_DIRS = ("docs", "project")
ASSET_DIRS = ("docs", "project", "utils", ".vitepress")
SHELL_LANGS = {"shell", "bash", "sh", "zsh", "console", "shellscript"}
FENCE = re.compile(r"^(\s*)(```+|~~~+)\s*([\w+-]*)\s*$")
SCRIPT_REF = re.compile(r"(?<![\w/.-])((?:\./)?utils/[\w./-]+\.(?:py|mjs|ts))")
PATH_REF = re.compile(
    r"(?<![\w/.-])((?:docs/(?:Backend|Frontend|DB|Ops|AI|Tools|Others)/|project/(?:Base|Complete)/)"
    r"[\w./-]+\.(?:md|svg|png|jpg|jpeg|json|ya?ml|ts|mjs|py))")
PNPM_REF = re.compile(r"\bpnpm\s+(?:run\s+)?([A-Za-z][\w:.-]*)")
NPM_REF = re.compile(r"\bnpm\s+run\s+([A-Za-z][\w:.-]*)")
PLACEHOLDER = re.compile(r"[<>${}*]|\.\.\.|\bxxx\b|\bXxx\b|<root>")
PNPM_BUILTIN = {
    "install", "i", "add", "remove", "rm", "uninstall", "update", "up", "upgrade",
    "dlx", "exec", "why", "list", "ls", "outdated", "audit", "store", "run",
    "create", "init", "publish", "pack", "link", "import", "deploy", "patch",
    "rebuild", "prune", "root", "bin", "env", "config", "setup", "fetch", "help",
    "workspace", "recursive", "filter", "-r", "-w",
}


def list_pages(root):
    out = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        for dirpath, _dirnames, filenames in os.walk(base):
            if "node_modules" in dirpath or "/assets" in dirpath:
                continue
            for fn in filenames:
                if fn.endswith(".md"):
                    out.append(os.path.join(dirpath, fn))
    return sorted(out)


def shell_blocks(text):
    """返回 [(起始行号, 代码块文本)]；用显式状态位，不能靠 cur 的真值判「在不在块内」"""
    blocks, cur, start, lang, inside = [], [], 0, "", False
    for i, line in enumerate(text.split("\n"), 1):
        m = FENCE.match(line)
        if not inside:
            if m:
                inside, start, lang, cur = True, i, m.group(3).lower(), []
            continue
        if m and m.group(3) == "":
            if lang in SHELL_LANGS:
                blocks.append((start, "\n".join(cur)))
            inside, cur, lang = False, [], ""
            continue
        cur.append(line)
    return blocks


def check_page(text, scripts_exist, pkg_scripts):
    """返回 (issues, counters)；issues = [(code, line, detail)]"""
    issues = []
    n_cmd = n_target = 0
    for start, block in shell_blocks(text):
        for offset, line in enumerate(block.split("\n")):
            lineno = start + offset + 1
            if PLACEHOLDER.search(line):
                continue
            for m in SCRIPT_REF.finditer(line):
                n_target += 1
                n_cmd += 1
                rel = m.group(1).lstrip("./")
                if rel not in scripts_exist:
                    issues.append(("E2", lineno, "脚本不存在：%s" % rel))
            for m in PATH_REF.finditer(line):
                n_target += 1
                if m.group(1) not in scripts_exist:
                    issues.append(("W1", lineno, "路径不存在：%s" % m.group(1)))
            if pkg_scripts is None:
                continue
            for m in PNPM_REF.finditer(line):
                name = m.group(1)
                if name in PNPM_BUILTIN or name.startswith("-"):
                    continue
                n_cmd += 1
                if not (name.startswith("docs:") or name.startswith("lint")):
                    issues.append(("N4", lineno, "外部工程脚本：%s" % name))
                    continue
                if name not in pkg_scripts:
                    issues.append(("W2", lineno, "package.json 无此 script：%s" % name))
            for m in NPM_REF.finditer(line):
                name = m.group(1)
                n_cmd += 1
                if not (name.startswith("docs:") or name.startswith("lint")):
                    issues.append(("N4", lineno, "外部工程脚本：%s" % name))
                    continue
                if name not in pkg_scripts:
                    issues.append(("W2", lineno, "package.json 无此 script：%s" % name))
    return issues, (1, n_cmd, n_target)


def scan(root, verbose=False):
    if not os.path.isdir(root):
        print("E0 ROOT_NOT_FOUND: %s" % root)
        return 1
    all_files = set()
    for d in ASSET_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            if "node_modules" in dirpath:
                continue
            for fn in filenames:
                all_files.add(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    scripts_exist = {p for p in all_files if p.endswith((".py", ".mjs", ".ts"))}
    for extra in ("AGENTS.md", "DOCS_PLAN.md"):
        if os.path.exists(os.path.join(root, extra)):
            all_files.add(extra)
            scripts_exist.add(extra)
    pkg_scripts = set()
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        try:
            pkg_scripts = set(json.load(open(pkg, encoding="utf-8")).get("scripts", {}))
        except Exception:
            pkg_scripts = set()

    tally = {"E2": 0, "W1": 0, "W2": 0, "N4": 0}
    pages = n_blocks = n_cmd = n_target = 0
    for path in list_pages(root):
        text = open(path, encoding="utf-8").read()
        blocks = shell_blocks(text)
        if not blocks:
            continue
        pages += 1
        n_blocks += len(blocks)
        is_repo_page = os.path.relpath(path, root).replace(os.sep, "/").startswith("docs/")
        issues, (_, c, t) = check_page(text, all_files, pkg_scripts if is_repo_page else None)
        n_cmd += c
        n_target += t
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        for code, lineno, detail in issues:
            tally[code] += 1
            if code.startswith("E") or (verbose and code != "N4"):
                print("%s %s:%d  %s" % (code, rel, lineno, detail))
    if n_blocks == 0:
        print("E1 NO_BLOCKS: 一个 shell 围栏都没扫到")
        return 1
    e = tally["E2"]
    w = tally["W1"] + tally["W2"]
    print("pages=%d blocks=%d cmds=%d targets=%d E=%d W=%d  [E2=%d W1=%d W2=%d N4=%d]"
          % (pages, n_blocks, n_cmd, n_target, e, w, tally["E2"], tally["W1"], tally["W2"], tally["N4"]))
    return 0 if e == 0 else 1


MD = "# 页\n\n正文。\n\n## 验证方式\n\n```shell\n%s\n```\n"


def selftest():
    cases = [
        ("正常：脚本存在", "python3 utils/audit/tablecheck.py --root .", 0, 0),
        ("脚本不存在 → E2", "python3 utils/audit/nosuch.py --root .", 1, 0),
        ("占位符路径不算 → 0", "python3 utils/audit/<name>.py", 0, 0),
        ("变量路径不算 → 0", "cat $ROOT/docs/x.md", 0, 0),
        ("仓内路径不存在 → W1", "cat docs/Backend/Ghost/index.md", 0, 1),
        ("仓内路径存在 → 0", "cat docs/Backend/Consolidation/index.md", 0, 0),
        ("外部工程路径不判 → 0", "cat docs/api/openapi.yaml", 0, 0),
        ("pnpm 内置 install 不算 → 0", "pnpm install", 0, 0),
        ("pnpm 未知 script → W2", "pnpm docs:deploy", 0, 1),
        ("pnpm 已知 script → 0", "pnpm docs:build", 0, 0),
        ("npm run 未知 → W2", "npm run lint:none", 0, 1),
        ("非 shell 围栏不扫 → 0", "```js\nconst x = require('utils/audit/nosuch.py')\n```", 0, 0),
        ("shell 围栏里两个缺脚本 → E2×2", "python3 utils/audit/a1.py\npython3 utils/audit/a2.py", 2, 0),
    ]
    ok = 0
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs", "Backend"))
        os.makedirs(os.path.join(tmp, "utils", "audit"))
        os.makedirs(os.path.join(tmp, "docs", "Backend", "Consolidation"))
        open(os.path.join(tmp, "docs", "Backend", "Consolidation", "index.md"), "w").write("# 分类\n")
        open(os.path.join(tmp, "utils", "audit", "tablecheck.py"), "w").write("# x\n")
        json.dump({"scripts": {"docs:build": "vitepress build"}},
                  open(os.path.join(tmp, "package.json"), "w"))
        exist_scripts = {"utils/audit/tablecheck.py", "docs/Backend/Consolidation/index.md"}
        for i, (desc, cmd, want_e, want_w) in enumerate(cases, 1):
            body = cmd if cmd.startswith("```") else MD % cmd
            issues, _ = check_page(body if cmd.startswith("```") is False else body,
                                   exist_scripts, {"docs:build"})
            e = sum(1 for c, _, _ in issues if c == "E2")
            w = sum(1 for c, _, _ in issues if c in ("W1", "W2"))
            good = (e == want_e and w == want_w)
            ok += good
            print("%s %2d. %s: E=%d W=%d（期望 %d/%d）[%s]"
                  % ("PASS" if good else "FAIL", i, desc, e, w, want_e, want_w,
                     ", ".join(c for c, _, _ in issues)))
    print("selftest %d/%d" % (ok, len(cases)))
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser(description="验证命令引用实物 🔍 巡检")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return scan(args.root, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
