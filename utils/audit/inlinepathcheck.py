#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inlinepathcheck —— 正文行内代码里的「仓库路径」到底在不在。

立这一项的原因：本库有 `linkexistcheck` 管 Markdown 链接、`cmdtargetcheck` 管 shell 命令里
的脚本与目录、`fencepathcheck` 管代码块标题 `[src/main.ts]`、`ghostgatecheck` 管注释里的
兄弟脚本。四道门都在看「结构化引用」，**没有一道管散文里用反引号写出来的仓库路径**：

    规则见 `docs/Backend/UnderwritingPolicy/Overview/index.md`
    巡检脚本在 `utils/audit/containercheck.py`

这类写法不会渲染成链接，因此断链检查扫不到；而读者点不动、也搜不到。它最常见的成因是
「文件改名或移动后，链接改了，散文里那串路径没改」——本库历史上多次发生（目录重构、
专题改名）。它不影响构建、不影响渲染，只影响「照着这句话去找东西的人」。

判据：
  E0 ROOT_NOT_FOUND   根目录不存在
  E1 NO_PAGES         一个页面都没扫到（活性判据）
  E2 MISSING_FILE     以 docs/ project/ utils/ public/ 开头 + 已知扩展名，文件不存在
  E3 MISSING_DIR      以 docs/ project/ utils/ 开头 + 以 / 结尾，目录不存在
  W1 EXTERNALISH      读者工程路径（src/ app/ server/ 等），不在本仓
  W2 AMBIGUOUS        像路径但无扩展名、也不以 / 结尾，无法判定
  W4 HISTORICAL       路径不存在，但同一行写明了「已删除/已改名」——历史引述，不算缺陷
  N1 PATHS / N2 RESOLVED / N3 PAGES

用法：
    python3 utils/audit/inlinepathcheck.py
    python3 utils/audit/inlinepathcheck.py --selftest
    python3 utils/audit/inlinepathcheck.py --path docs/Backend
"""
import argparse
import os
import re
import sys

ROOT_DEFAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 行内代码
INLINE_RE = re.compile(r"`([^`\n]+)`")
# 只认「本仓已知分类目录」开头的路径。
# 为什么不用裸 `docs/`：读者自己的工程里也常有一个叫 docs/ 的目录（`docs/deploy.md`），
# 用裸前缀会把它全部判成断路径——第 247 天首版正是这样报出 58 条假 E。
REPO_PREFIX = ()   # 运行时按仓库实际分类目录填充，见 known_prefixes()
EXT_OK = {".md", ".py", ".mjs", ".ts", ".svg", ".png", ".jpg", ".json", ".yaml", ".yml", ".sh"}
# 读者自己工程里的路径前缀
FOREIGN_PREFIX = ("src/", "app/", "server/", "client/", "packages/", "web/", "api/",
                  "cmd/", "internal/", "test/", "tests/", "scripts/", "config/", "deploy/",
                  "migrations/", "dist/", "build/", "node_modules/")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def known_prefixes(root):
    """本仓真实存在的分类目录前缀，例如 docs/Backend/、project/Complete/、utils/。"""
    got = {"utils/"}
    ddir = os.path.join(root, "docs")
    if os.path.isdir(ddir):
        for n in os.listdir(ddir):
            if os.path.isdir(os.path.join(ddir, n)) and not n.startswith("."):
                got.add(f"docs/{n}/")
    for base in ("Base", "Complete"):
        if os.path.isdir(os.path.join(root, "project", base)):
            got.add(f"project/{base}/")
    return tuple(sorted(got))


def strip_fences(lines):
    out, fence = [], None
    for ln in lines:
        m = FENCE_RE.match(ln)
        if fence is None and m:
            fence = m.group(1)[0] * len(m.group(1))
            out.append("")
            continue
        if fence is not None:
            if m and m.group(1)[0] * len(m.group(1)) == fence:
                fence = None
            out.append("")
            continue
        out.append(ln)
    return out


def classify(token, root, prefixes):
    """返回 (kind, path)。kind ∈ FILE / DIR / FOREIGN / AMBIG / SKIP"""
    t = token.strip()
    if not t or " " in t or t.startswith("-") or t.startswith("$"):
        return ("SKIP", t)
    if any(ch in t for ch in "<>…*{}[]"):
        return ("SKIP", t)          # 占位符写法，不是真路径
    if t.startswith("/") or t.startswith("~"):
        return ("SKIP", t)          # 系统绝对路径
    if t.startswith(FOREIGN_PREFIX):
        # 读者工程里的路径：只有带已知扩展名才算「一个具体文件」，否则多半是接口/命令
        return ("FOREIGN", t) if os.path.splitext(t)[1].lower() in EXT_OK else ("SKIP", t)
    if not t.startswith(prefixes) or len(t.rstrip("/").split("/")) < 3:
        return ("SKIP", t)
    t = t.split("#")[0].split("?")[0].rstrip()
    if not t:
        return ("SKIP", t)
    if t.endswith("/"):
        return ("DIR", t.rstrip("/"))
    ext = os.path.splitext(t)[1].lower()
    if ext in EXT_OK:
        return ("FILE", t)
    if ext:
        return ("SKIP", t)
    # 无扩展名：能落到目录上就放过；落不到就当「歧义」提示，不判 E
    # （散文里的 `docs/perf` 多半是读者自己工程里的目录名，不是本仓路径）
    if os.path.isdir(os.path.join(root, t)):
        return ("DIR", t)
    return ("AMBIG", t)


def check_file(path, rel, root, prefixes):
    issues = []
    with open(path, encoding="utf-8") as f:
        lines = strip_fences(f.read().splitlines())
    n_paths = n_ok = 0
    for i, ln in enumerate(lines, 1):
        for m in INLINE_RE.finditer(ln):
            kind, t = classify(m.group(1), root, prefixes)
            if kind == "SKIP":
                continue
            n_paths += 1
            if kind == "FOREIGN":
                issues.append(("W1", rel, i, t))
                continue
            if kind == "AMBIG":
                issues.append(("W2", rel, i, t))
                continue
            full = os.path.join(root, t)
            HIST = ("已删除", "已移除", "已废弃", "不再提供", "历史路径", "已改名")
            hist = any(k in ln for k in HIST)
            if kind == "FILE":
                if os.path.isfile(full):
                    n_ok += 1
                else:
                    issues.append((("W4" if hist else "E2"), rel, i, t))
            else:
                if os.path.isdir(full):
                    n_ok += 1
                else:
                    issues.append((("W4" if hist else "E3"), rel, i, t))
    return issues, n_paths, n_ok


def walk(root, sub):
    files = []
    for base in sub:
        start = os.path.join(root, base)
        for dirpath, _d, names in os.walk(start):
            if "node_modules" in dirpath or "/.vitepress" in dirpath:
                continue
            for n in names:
                if n.endswith(".md"):
                    p = os.path.join(dirpath, n)
                    files.append((p, os.path.relpath(p, root)))
    return sorted(files)


SELFTEST = [
    ("存在的文件", "见 `docs/Backend/Overview.md`\n", []),
    ("不存在的文件", "见 `docs/Backend/Nope/index.md`\n", ["E2"]),
    ("存在的目录", "见 `docs/Backend`\n", []),
    ("不存在的目录", "见 `docs/Backend/Nope/`\n", ["E3"]),
    ("读者工程路径", "放在 `src/main.ts`\n", ["W1"]),
    ("绝对路径忽略", "配置在 `/etc/nginx/nginx.conf`\n", []),
    ("围栏内不算", "```shell\ncat docs/Nope/index.md\n```\n", []),
    ("无引号不算", "见 docs/Backend/Nope/index.md\n", []),
    ("带锚点", "见 `docs/Backend/Overview.md#x`\n", []),
    ("带锚点且不存在", "见 `docs/Backend/Nope/index.md#x`\n", ["E2"]),
    ("无扩展名", "见 `docs/Backend/SomeTopic`\n", ["W2"]),
    ("多个反引号混排", "a `docs/Backend` b `utils/audit` c\n", []),
]


def selftest(_root):
    ok = 0
    import tempfile
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "vault")
    os.makedirs(os.path.join(root, "docs", "Backend"), exist_ok=True)
    os.makedirs(os.path.join(root, "utils", "audit"), exist_ok=True)
    with open(os.path.join(root, "docs", "Backend", "Overview.md"), "w", encoding="utf-8") as f:
        f.write("# x\n")
    for idx, (name, body, expect) in enumerate(SELFTEST, 1):
        p = os.path.join(tmp, f"_t{idx}.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        issues, _n, _ok = check_file(p, f"_t{idx}.md", root, known_prefixes(root))
        got = sorted({x[0] for x in issues})
        good = got == sorted(expect)
        print(f"{'PASS' if good else 'FAIL'} {idx:>2}. {name}: got={got} 期望={sorted(expect)}")
        ok += 1 if good else 0
        os.remove(p)
    print(f"selftest {ok}/{len(SELFTEST)}")
    return 0 if ok == len(SELFTEST) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--path", nargs="*", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest(args.root)
    if not os.path.isdir(args.root):
        print(f"E0 ROOT_NOT_FOUND {args.root}")
        return 2
    files = walk(args.root, args.path)
    if not files:
        print("E1 NO_PAGES")
        return 2

    prefixes = known_prefixes(args.root)
    all_issues, n_paths, n_ok = [], 0, 0
    for p, rel in files:
        issues, np_, no = check_file(p, rel, args.root, prefixes)
        all_issues += issues
        n_paths += np_
        n_ok += no
    errs = [i for i in all_issues if i[0].startswith("E")]
    for code, rel, line, msg in sorted(all_issues)[:80]:
        print(f"{code} {rel}:{line} {msg}")
    if len(all_issues) > 80:
        print(f"... 另有 {len(all_issues) - 80} 条未显示")
    print(f"pages={len(files)} paths={n_paths} resolved={n_ok} E={len(errs)} W={len(all_issues)-len(errs)}")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
