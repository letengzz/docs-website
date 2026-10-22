#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""casecheck.py —— 路径大小写一致性巡检（第 84 项）。

为什么要有这一项
----------------
本库跑在 macOS 上（HFS+/APFS 默认**大小写不敏感**），而 GitHub Actions 的构建机是 Linux
（**大小写敏感**）。这两个事实组合出一个只在「推送之后」才会暴露的缺陷：

  * 页面上写着 `[表格](../Table/index.md)`，磁盘上是 `table/index.md`；
  * 本地 `pnpm docs:dev` 一切正常——因为 macOS 把 `Table` 和 `table` 当成同一个目录；
  * `git push` 之后 Actions 构建失败：`Could not resolve ...`；
  * 更糟的一种：构建**不失败**但页面 404，因为 VitePress 生成了两份路由。

已有的链接类巡检都解决不了它：

  * `linkcheck` 判「文件在不在」——在 macOS 上**它认为在**；
  * `linkformcheck` 判「是不是一个合法链接」——语法没问题；
  * `sidebarcheck` 判「侧边栏路径有没有文件」——同样被文件系统的宽容骗过。

本项补的就是这个盲区：**不按文件系统的宽容去判断，而是逐段比对目录项的真实拼写**。

判据
----
E0 ROOT_NOT_FOUND     根目录不存在
E1 NO_PAGES           没扫到任何 Markdown（活性判据：拒绝在空集上给出全绿）
E2 CASE_MISMATCH      Markdown 链接的目标，在磁盘上存在但大小写与写法不一致
E3 SIDEBAR_CASE       `.vitepress/*.ts` 里侧边栏 `link` 指向的路径大小写不一致
W1 ABS_PATH           以 `/` 开头的站内绝对路径（站点 `base` 为 `/docs-website/`，极可能失效）
W2 NO_TARGET          链接目标既不是文件也不是目录（交给 linkcheck 兜底，这里只做交叉验证）

刻意不查的
----------
* `http(s)://`、`mailto:`、`#fragment`；
* 代码围栏与行内代码里的路径（那里是示例文本，不是链接）；
* `public/` 下的全局资源（不经 Markdown 引用）。

用法
----
    python3 utils/audit/casecheck.py [根目录] [--quiet]
    python3 utils/audit/casecheck.py --selftest

退出码：0 = 无 E 级；1 = 有 E 级；2 = 用法错误。
"""
import os
import re
import sys
import tempfile

LINK = re.compile(r'!?\[[^\]]*\]\(([^)\s]+?)(?:\s+"[^"]*")?\)')
SIDEBAR_LINK = re.compile(r'"?link"?\s*:\s*"([^"]+)"')
FENCE = re.compile(r'^\s*(```|~~~)')


def strip_noise(text):
    """去掉代码围栏与行内代码，避免把示例文本当链接。"""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(re.sub(r'`[^`]*`', "", line))
    return "\n".join(out)


def exact_exists(root, rel_parts):
    """逐段比对真实拼写：任何一段在 os.listdir 里找不到同名项即视为不匹配。"""
    cur = root
    for part in rel_parts:
        if part in ("", "."):
            continue
        if part == "..":
            cur = os.path.dirname(cur)
            continue
        try:
            entries = os.listdir(cur)
        except OSError:
            return False
        if part in entries:
            cur = os.path.join(cur, part)
            continue
        # 磁盘上可能是另一种拼写
        low = {e.lower(): e for e in entries}
        if part.lower() in low:
            return False
        return False
    return True


def resolve(node_dir, target):
    """把相对路径拆成段，返回 (段列表, 是否越界)。"""
    parts = []
    for seg in target.replace("\\", "/").split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(seg)
    return parts


SKIP_DIRS = {"node_modules", "dist", ".git", ".vitepress"}


def check_pages(root):
    errs, warns, pages = [], [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            # 站点页面只收 docs/ 与 project/ 两棵树（含根 index.md）；
            # 仓库根的规划类 Markdown（AGENTS/DOCS_PLAN/README）不参与站点链接判定
            if rel_dir == "." and fn != "index.md":
                continue
            pages += 1
            path = os.path.join(dirpath, fn)
            text = strip_noise(open(path, encoding="utf-8").read())
            base_parts = os.path.relpath(dirpath, root).split(os.sep)
            if base_parts == ["."]:
                base_parts = []
            for m in LINK.finditer(text):
                tgt = m.group(1).strip()
                if tgt.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if tgt.startswith("/"):
                    warns.append(("W1 ABS_PATH", path, tgt))
                    continue
                tgt = tgt.split("#", 1)[0]
                if not tgt:
                    continue
                # 相对于当前页面目录解析
                stack = list(base_parts)
                for seg in tgt.replace("\\", "/").split("/"):
                    if seg in ("", "."):
                        continue
                    if seg == "..":
                        if stack:
                            stack.pop()
                        continue
                    stack.append(seg)
                if exact_exists(root, stack):
                    continue
                # 是大小写不符，还是真的不存在？
                low_stack = [s.lower() for s in stack]
                cur, ok = root, True
                for s in low_stack:
                    try:
                        entries = {e.lower(): e for e in os.listdir(cur)}
                    except OSError:
                        ok = False
                        break
                    if s not in entries:
                        ok = False
                        break
                    cur = os.path.join(cur, entries[s])
                if ok:
                    actual = os.path.relpath(cur, root)
                    errs.append(("E2 CASE_MISMATCH", path, f"{tgt}  →  实际 {actual}"))
                else:
                    warns.append(("W2 NO_TARGET", path, tgt))
    return pages, errs, warns


def check_sidebar(root):
    errs = []
    vp = os.path.join(root, ".vitepress")
    if not os.path.isdir(vp):
        return errs
    for fn in os.listdir(vp):
        if not fn.endswith(".ts"):
            continue
        path = os.path.join(vp, fn)
        for m in SIDEBAR_LINK.finditer(open(path, encoding="utf-8").read()):
            link = m.group(1)
            if not link.startswith("/"):
                continue
            parts = [p for p in link.split("/") if p]
            # 侧边栏路径是站点路径：去掉 base 后对应仓库内路径
            for i in range(len(parts)):
                cand = parts[i:]
                if exact_exists(root, cand):
                    break
                low = [s.lower() for s in cand]
                cur, ok = root, True
                for s in low:
                    try:
                        entries = {e.lower(): e for e in os.listdir(cur)}
                    except OSError:
                        ok = False
                        break
                    if s not in entries:
                        ok = False
                        break
                    cur = os.path.join(cur, entries[s])
                if ok:
                    errs.append(("E3 SIDEBAR_CASE", path,
                                 f"{link}  →  实际 {os.path.relpath(cur, root)}"))
                    break
    return errs


def run(root=".", quiet=False):
    if not os.path.isdir(root):
        print(f"E0 ROOT_NOT_FOUND  {root}")
        return 1
    pages, errs, warns = check_pages(root)
    if pages == 0:
        print("E1 NO_PAGES  没有扫到任何 Markdown")
        return 1
    errs += check_sidebar(root)
    for code, path, detail in errs:
        print(f"{code:16s} {os.path.relpath(path, root)}  {detail}")
    # W 级只计数：W1 的 `/docs/...` 写法会被 VitePress 在构建时补上 base，
    # 属于「风格风险」而非缺陷；W2 与 linkcheck 重叠，只作交叉验证。
    abs_path = sum(1 for w in warns if w[0].startswith("W1"))
    missing = sum(1 for w in warns if w[0].startswith("W2"))
    if not quiet:
        for code, path, detail in warns[:10]:
            if code.startswith("W2"):
                print(f"{code:16s} {os.path.relpath(path, root)}  {detail}")
    print(f"\npages={pages} E={len(errs)} W_ABS={abs_path} W_MISS={missing}")
    return 0 if not errs else 1


def selftest():
    checks = []

    def case(name, cond):
        checks.append((name, bool(cond)))

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs", "Table"))
        os.makedirs(os.path.join(tmp, ".vitepress"))
        open(os.path.join(tmp, "docs", "Table", "index.md"), "w").write("# t\n")
        # 1 正确大小写
        open(os.path.join(tmp, "docs", "ok.md"), "w").write("[t](Table/index.md)\n")
        # 2 大小写不符
        open(os.path.join(tmp, "docs", "bad.md"), "w").write("[t](table/index.md)\n")
        # 3 不存在
        open(os.path.join(tmp, "docs", "miss.md"), "w").write("[t](Nope/index.md)\n")
        # 4 绝对路径
        open(os.path.join(tmp, "docs", "abs.md"), "w").write("![x](/assets/a.svg)\n")
        # 5 侧边栏大小写
        open(os.path.join(tmp, ".vitepress", "s.ts"), "w").write(
            'const a=[{ text:"t", link:"/docs/table/index.md" }];\n')
        pages, errs, warns = check_pages(tmp)
        codes = [e[0] for e in errs]
        wcodes = [w[0] for w in warns]
        sb = [e[0] for e in check_sidebar(tmp)]
        case("pages 计数", pages == 5)
        case("E2 命中大小写不符", codes.count("E2 CASE_MISMATCH") == 1)
        case("正确大小写不报错", "E2 CASE_MISMATCH" not in [c for c, p, _ in errs
                                                          if p.endswith("ok.md")])
        case("W2 命中不存在", "W2 NO_TARGET" in wcodes)
        case("W1 命中绝对路径", "W1 ABS_PATH" in wcodes)
        case("E3 命中侧边栏", sb and sb[0] == "E3 SIDEBAR_CASE")
    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        print(f"{'PASS' if c else 'FAIL'}  {name}")
    print(f"\nselftest {ok}/{len(checks)}")
    return 0 if ok == len(checks) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = "."
    quiet = "--quiet" in argv
    rest = [a for a in argv if not a.startswith("--")]
    if len(rest) > 1:
        root = rest[1]
    elif len(rest) == 1 and rest[0] != argv[0]:
        root = rest[0]
    return run(root, quiet)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
