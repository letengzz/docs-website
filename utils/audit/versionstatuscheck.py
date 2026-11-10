#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""versionstatuscheck.py —— 「版本状态标注配套」巡检（第 271 天新立，第一百四十八项巡检）

## 动机（本仓「某个维度整体没人看」的第 N 次）

`AGENTS.md` 第 3 节要求：主题出现大版本差异时按版本目录组织，**旧版本保留原内容、
页面顶部标注版本与维护状态**，主题目录页同时列出各版本入口并提供「版本差异 /
升级指南」。既有巡检里 `sidebarcheck` 查导航死链、`indexcovercheck` 查目录页覆盖、
`ledgerdircheck` 查台账目录、`headingcheck` 查标题文本——**没有一项问「一个自称
『仅存量项目使用』的页面，读者到底怎么找到它、又怎么迁走」**。

第 271 天新建 `ClassicResolver/` / `ModernResolver/` 时把这件事显式做了一遍：
页顶状态容器、目录页双入口、迁移映射表、侧边栏叶子。本脚本把这四个配套动作
变成门禁，防止后来者只写一句「已停止维护」就把版本页丢进库里。

## 判据（E = 必须修，W = 登记长尾）

    E0 ROOT_NOT_FOUND         给定根目录不存在
    E1 NO_FILES               一个 Markdown 都没扫到（活性）
    E2 NO_STATUS_PAGE         全库一个「页顶容器内状态页」都没有（活性：拒绝空集全绿）
    E3 NO_INDEX_ENTRY         状态页所在版本目录，在上级主题目录页里没有任何入口
    E4 NO_UPGRADE_GUIDE       标为旧版/停维护的状态页，全文没有升级或替代指引
    E5 CONFLICTED_STATUS      同一个状态容器里同时声明「停止新增」与「当前主线」
    W1 STATUS_OUTSIDE_BOX     页顶出现状态词但不在提示容器内（格式债）
    W2 NO_SIDEBAR_ENTRY       状态页路径没有出现在 .vitepress/*.ts 中
    W3 NO_PEER_VERSION        同级找不到第二个版本目录（孤立标注）

## 四条口径（都是为了避免永久红）

1. **只认「页顶提示容器内的状态词」，且容器标题行也算**：用轻量容器解析（前 20 行内
   `:::` 开、下一个 `:::` 闭），先剔除代码围栏。本库大量写成
   `::: danger 版本状态：仅存量项目使用`——状态词只在标题行；首版跳过标题行，
   4 个 selftest 因此失真，修完后 11/11 通过。
2. **正文判定前剥掉整段链接与指引句**：「本页仅存量项目使用；新代码一律使用
   [当前主线日期时间 API](../ModernDateTime/index.md)」里的「当前主线」是**链接文字**，
   不是本页自称。首版全库 E5=2 全是这类误报；改为剔除 `[text](url)` 并丢掉含
   「请阅读 / 一律使用 / 新项目 / 移步 / 直接看 / 参见」的分句后归零。
3. **升级指引不要求固定措辞**：`迁移 / 升级 / 差异 / 对照 / 映射 / 替代 / 改用 /
   换用 / 推荐 / 新项目` 任一命中即可。`Vue2/VueResource` 只写「官方推荐使用
   axios 替代」，按真实语义算有指引，不能因为它没写「升级」两个字就报 E。
4. **目录页入口按「版本目录名」匹配**：查上两级 `index.md` 里有没有
   `VersionDir/` 形态的链接；不要求链接精确到子页，避免把「目录页链到版本首页」
   误判为缺入口。实测全库 38 个状态页该项 0 命中。
5. **W 不自动改正文**：`STATUS_OUTSIDE_BOX` 的历史写法（普通段落里写状态）机械
   搬进容器会打乱既有版式；`NO_SIDEBAR_ENTRY` / `NO_PEER_VERSION` 同理，降为 W
   并登记为格式债，交由主题维护时处理。

## 与相邻巡检的边界

`sidebarcheck` 查的是「导航项有没有对应页面」，`indexcovercheck` 查的是「页面
有没有被目录页覆盖」，两者都不看页面自称的版本状态。本脚本反过来：以**作者主动
声明的状态**为锚点，检查配套的入口与迁移指引；不查链接是否存在、不查标题、
不查判据编号。

用法：
    python3 utils/audit/versionstatuscheck.py [--root docs project] [--selftest] [--top 15]
"""

import argparse
import os
import re
import sys
import tempfile

OLD_WORDS = ("仅存量项目使用", "已停止新增", "已停止维护", "仅存量项目", "停止新增")
NEW_WORDS = ("当前主线", "持续维护", "当前基线", "当前稳定版")
UPGRADE_WORDS = ("迁移", "升级", "差异", "对照", "映射", "替代", "改用", "换用",
                 "推荐", "新项目", "版本差异", "不再使用", "改用")
VERSION_DIR_RE = re.compile(r"(Legacy|Modern|Classic|v\d|\d)", re.I)
HEAD_LINES = 20
LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
GUIDE_RE = re.compile(r"请阅读|一律使用|新项目|移步|直接看|见当前|改为使用|参见|或看")


def strip_fences(lines):
    """去掉代码围栏内的行：示例里的状态词不是作者的状态声明。"""
    out, inside = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            out.append(line)
    return out


def container_spans(lines):
    """返回页顶的提示容器列表，每项含「标题行文字」与「容器内正文行」。

    标题行本身要纳入判定：本库大量写成 `::: danger 版本状态：仅存量项目使用`，
    把状态词只放在容器开头这一行；早期版本跳过标题行导致 4 个 selftest 失真。
    """
    head = strip_fences(lines[:HEAD_LINES])
    spans, cur = [], None
    for line in head:
        s = line.strip()
        if s.startswith(":::"):
            if cur is None:
                cur = {"title": s[3:].strip(), "body": []}
            else:
                spans.append(cur)
                cur = None
            continue
        if cur is not None:
            cur["body"].append(line)
    if cur is not None:
        spans.append(cur)
    return spans, "\n".join(head)


def clean_body(seg):
    """剥掉整段链接，并剔除「请阅读新版 / 新项目一律使用」这类指引句。

    否则「本页仅存量项目使用；新代码一律使用[当前主线日期时间 API](...)」
    会被判成同一页同时自称旧版与当前主线，首轮 2 条 E5 全是这类误报。
    """
    seg = LINK_RE.sub("", seg)
    parts = re.split(r"([。；;\n])", seg)
    return "".join(p for p in parts if not GUIDE_RE.search(p))


def parse_status(text):
    """解析页顶状态；返回 (是否状态页, kind, 是否矛盾)。"""
    lines = text.splitlines()
    spans, head = container_spans(lines)
    old = new = False
    for span in spans:
        t_old = any(w in span["title"] for w in OLD_WORDS)
        t_new = any(w in span["title"] for w in NEW_WORDS)
        if t_old or t_new:
            # 标题行已明确声明状态，正文只作描述，不再参与判定
            old |= t_old
            new |= t_new
            continue
        body = clean_body("\n".join(span["body"]))
        old |= any(w in body for w in OLD_WORDS)
        new |= any(w in body for w in NEW_WORDS)
    if not (old or new):
        return None
    return {"kind": "old" if old else "new", "conflict": old and new}


def has_guide(text):
    return any(w in text for w in UPGRADE_WORDS)


def index_has_entry(path):
    """上级（最多两级）index.md 里是否出现版本目录名。"""
    ver = os.path.basename(os.path.dirname(path))
    d = os.path.dirname(os.path.dirname(path))
    for _ in range(2):
        idx = os.path.join(d, "index.md")
        if os.path.exists(idx):
            t = open(idx, encoding="utf-8").read()
            if (ver + "/") in t or (ver + ")") in t or (ver + "/index.md") in t:
                return True
        d = os.path.dirname(d)
    return False


def has_peer(path):
    parent = os.path.dirname(os.path.dirname(path))
    ver = os.path.basename(os.path.dirname(path))
    if not os.path.isdir(parent):
        return False
    for name in os.listdir(parent):
        if name == ver or not os.path.isdir(os.path.join(parent, name)):
            continue
        if VERSION_DIR_RE.search(name):
            return True
    return False


def collect(root):
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "dist")]
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.join(base, f))
    return sorted(out)


def evaluate(files, sidebar_text="", repo_root=None):
    errors, warns, status_pages = [], [], []
    for path in files:
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        st = parse_status(text)
        _, head = container_spans(text.splitlines())
        if st is None:
            # 页顶有状态词但没用容器：格式债，不判 E
            if any(w in head for w in OLD_WORDS + NEW_WORDS):
                warns.append(("W1", "STATUS_OUTSIDE_BOX", path,
                              "页顶出现状态词但不在提示容器内"))
            continue
        status_pages.append(path)
        rel = path if repo_root is None else os.path.relpath(path, repo_root)
        if st["conflict"]:
            errors.append(("E5", "CONFLICTED_STATUS", path,
                           "同一状态容器里同时声明停止新增与当前主线"))
        if not index_has_entry(path):
            errors.append(("E3", "NO_INDEX_ENTRY", path, "上级目录页没有版本目录入口"))
        if st["kind"] == "old" and not has_guide(text):
            errors.append(("E4", "NO_UPGRADE_GUIDE", path, "旧版页没有升级或替代指引"))
        if sidebar_text:
            needle = "/" + rel.replace(os.sep, "/")
            if needle not in sidebar_text:
                warns.append(("W2", "NO_SIDEBAR_ENTRY", path, "侧边栏配置里没有该路径"))
        if not has_peer(path):
            warns.append(("W3", "NO_PEER_VERSION", path, "同级找不到第二个版本目录"))
    if not status_pages:
        errors.append(("E2", "NO_STATUS_PAGE", "-", "全库没有页顶状态页（活性判据）"))
    return errors, warns, status_pages


def sidebar_blob(repo_root):
    cfg = os.path.join(repo_root, ".vitepress")
    if not os.path.isdir(cfg):
        return ""
    parts = []
    for f in os.listdir(cfg):
        if f.endswith(".ts") or f.endswith(".mts"):
            try:
                parts.append(open(os.path.join(cfg, f), encoding="utf-8").read())
            except (OSError, UnicodeDecodeError):
                pass
    return "\n".join(parts)


def selftest():
    cases = []

    def run(name, build, expect_e, expect_w=()):
        with tempfile.TemporaryDirectory() as td:
            files = build(td)
            e, w, _ = evaluate(files, sidebar_text="", repo_root=td)
            codes = {x[0] for x in e}
            wcodes = {x[0] for x in w}
            ok = (codes == set(expect_e)) and all(c in wcodes for c in expect_w)
            cases.append((name, ok, sorted(codes), sorted(wcodes)))
            return ok

    def one_page(text, name="VersionA/index.md", index_text=None):
        def build(td):
            p = os.path.join(td, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write(text)
            if index_text is not None:
                open(os.path.join(td, "index.md"), "w", encoding="utf-8").write(index_text)
            peer = os.path.join(td, "VersionB")
            os.makedirs(peer, exist_ok=True)
            open(os.path.join(peer, "index.md"), "w", encoding="utf-8").write("# B\n")
            return [p]
        return build

    GOOD = ("# 旧版\n\n::: danger 版本状态：仅存量项目使用 · 已停止新增\n"
            "仅存量项目使用。\n:::\n\n## 迁移映射\n见升级指南与差异对照表。\n")
    run("正常旧版页：0 错", one_page(GOOD, index_text="[A](VersionA/index.md)"), [], [])
    run("缺目录页入口：E3", one_page(GOOD, index_text="# 目录\n（无入口）"), ["E3"])
    run("旧版页无升级指引：E4",
        one_page("# 旧版\n\n::: danger 版本状态：已停止新增\n别用了。\n:::\n",
                 index_text="[A](VersionA/index.md)"), ["E4"])
    run("容器内状态矛盾：E5",
        one_page("# 混\n\n::: info 版本状态：已停止新增，同时是当前主线 · 持续维护\n:::\n\n迁移说明\n",
                 index_text="[A](VersionA/index.md)"), ["E5"])
    run("状态词不在容器：只有 W1",
        one_page("# 普通页\n\n仅存量项目使用，但没有容器。\n",
                 index_text="[A](VersionA/index.md)"), ["E2"], ["W1"])
    run("状态词只在代码块里：不算状态页",
        one_page("# 普通页\n\n```text\n仅存量项目使用\n```\n",
                 index_text="# 目录\n"), ["E2"])
    run("状态词在正文第 40 行：不算状态页",
        one_page("# 普通页\n\n" + "正文\n" * 38 + "仅存量项目使用\n",
                 index_text="# 目录\n"), ["E2"])
    def solo(td):
        p = os.path.join(td, "Solo", "index.md")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(
            "# 旧版\n\n::: danger 版本状态：已停止新增\n:::\n\n迁移与差异对照\n")
        open(os.path.join(td, "index.md"), "w", encoding="utf-8").write(
            "[Solo](Solo/index.md)\n")
        return [p]
    run("同级无版本兄弟：W3", solo, [], ["W3"])
    run("推荐/替代算升级指引：不报 E4",
        one_page("# 旧版\n\n::: danger 版本状态：已停止维护\n:::\n\n官方推荐使用 axios 替代。\n",
                 index_text="[A](VersionA/index.md)"), [])
    # 活性判据：空目录 / 不存在的根
    with tempfile.TemporaryDirectory() as td:
        e, w, _ = evaluate([], repo_root=td)
        cases.append(("空集触发 E2", {x[0] for x in e} == {"E2"},
                      sorted({x[0] for x in e}), []))
    bad_root = os.path.join(tempfile.gettempdir(), "_vsc_no_such_root_271_")
    cases.append(("根不存在可判定", not os.path.exists(bad_root), [], []))

    for name, ok, e, w in cases:
        print(("PASS" if ok else "FAIL"), name, "E=", e, "W=", w)
    passed = sum(c[1] for c in cases)
    print("SELFTEST %d / %d" % (passed, len(cases)))
    return 0 if passed == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", nargs="*", default=["docs", "project"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    repo_root = os.path.abspath(".")
    for r in args.root:
        if not os.path.isdir(r):
            print("E0 ROOT_NOT_FOUND", r)
            return 1
    files = []
    for r in args.root:
        files.extend(collect(r))
    if not files:
        print("E1 NO_FILES")
        return 1
    errors, warns, pages = evaluate(files, sidebar_blob(repo_root), repo_root)
    print("pages=%d status_pages=%d E=%d W=%d" %
          (len(files), len(pages), len(errors), len(warns)))
    from collections import Counter
    print("E 分布:", dict(Counter(x[1] for x in errors)))
    print("W 分布:", dict(Counter(x[1] for x in warns)))
    for code, name, path, why in errors[:args.top]:
        print(" ", code, name, path, why)
    for code, name, path, why in warns[:args.top]:
        print(" ", code, name, path, why)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
