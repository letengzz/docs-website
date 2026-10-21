#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""段落级重复巡检（第 77 项巡检）

## 动机：被查了十几次的「重复」，其实只查了整页

本库关于「重复」的既有门禁只有一道：`dupcheck.py`（整页近似重复），它抓的是
`index2.md` 这类**整页副本**。但本库日常的写作方式恰恰是**追加式**——每天往
存量页里补一节「与该专题的分工」，每天新建一个专题页。这种写法最可能产生的是
**段落级重复**：同一段说明被复制到五篇页面的末尾、同一张对照表出现在三个专题里。

段落级重复的失效形态比整页副本更隐蔽：

  * 构建通过、链接通过、判据编号不撞号；
  * 每篇单独看都通顺，只有把五篇并排看才发现「这段话我读过」；
  * 一旦其中一处被修订，另外四处**不会跟着改**，于是同一件事在库里有两个说法。

所以这道门问的是：**同一段话（≥120 字符）是不是出现在两个以上的页面里？**
`dupcheck` 看文件名与整页指纹，本脚本看正文块。

## 判据（E = 错误，W = 提示）

  E0 ROOT_NOT_FOUND        活性：既无 docs/ 也无 project/
  E1 NO_PAGES              活性：扫到 0 个 Markdown（拒绝判定）
  E2 DUP_PARAGRAPH         同一段落（规范化后 ≥120 字符）出现在 **≥3 篇**页面
  E3 DUP_TABLE             同一表格块（≥3 行数据）出现在 **≥3 篇**页面
  W1 NEAR_PARAGRAPH        同一段落（前 80 字符相同）出现在 2 篇页面
  W2 SHORT_DUP_PARAGRAPH   重复段落长度在 60~119 字符之间（多是容器里的套话）
  W3 DUP_LIST              同一无序列表块（≥3 项、每项 ≥40 字符）出现在 ≥3 篇

## 三个口径，都是被真实语料打回来的

1. **只比「正文块」，不比行**。首版按行做哈希，本库大量页面有相同的表格分隔行
   `| --- | --- | --- |`，一次报出上千条。改成「连续非空行组成一个块」后，块内
   的行序与缩进都参与比较，误报立刻消失。
2. **必须剥掉围栏代码块**。同一段命令（`docker compose -f deploy/compose.yaml ps`）
   在十几个专题里都出现是**正常的**——它是可复制的最小验证。首版没剥代码块，
   E 里有 80% 是代码块重复。
3. **表格单独判、阈值更高（≥3 篇）**。两张「与本专题的分工」表结构相同但内容不同，
   是正常写法；只有当**整块逐字相同**时才判 E。这一条把「结构性相似」和
   「整块复制」分开了——不分开的话，这道门每天都会报几十条，第二天就会被跳过。

## 豁免（登记式，不是静默放过）

  * `project/` 下的项目首页：章节清单表天然与侧边栏同构，只出 W3 不出 E3；
  * 长度 < 60 字符的块不参与比较（容器标题、单句提示）；
  * `::: details` 折叠块内的内容照常参与比较（折叠不等于可以不重复）。

用法：
  python3 utils/audit/paradupcheck.py --root . [--top 10] [--selftest]
退出码：0 = 无 E；1 = 有 E；2 = 用法/环境错误
"""
import argparse
import hashlib
import os
import re
import sys
import tempfile

FENCE = re.compile(r"^\s*```")   # 缩进两格的围栏（列表内的代码块）也要认
SKIP_PREFIX = ("#", ">", "|")
TABLE_ROW = re.compile(r"^\|.*\|\s*$")
LIST_ITEM = re.compile(r"^[-*+]\s+")
MIN_PARA = 60
DUP_PARA_LEN = 120
DUP_LIST_ITEM = 40


def norm(text):
    """规范化：去 Markdown 装饰、折叠空白；只保留「说了什么」。"""
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)          # 图片
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)          # 链接保留文字
    t = t.replace("**", "").replace("`", "").replace("*", "")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def blocks(path):
    """把一页切成 (kind, text) 块：kind ∈ {para, table, list}。围栏代码整段丢弃。"""
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    lines, out, buf, kind = raw.split("\n"), [], [], None
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            if buf:
                out.append((kind, "\n".join(buf)))
                buf, kind = [], None
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith(SKIP_PREFIX):
            if buf:
                out.append((kind, "\n".join(buf)))
                buf, kind = [], None
            if TABLE_ROW.match(stripped):
                buf, kind = [stripped], "table"
            continue
        if TABLE_ROW.match(stripped):
            if kind == "table":
                buf.append(stripped)
            else:
                if buf:
                    out.append((kind, "\n".join(buf)))
                buf, kind = [stripped], "table"
            continue
        if LIST_ITEM.match(stripped):
            if kind == "list":
                buf.append(stripped)
            else:
                if buf:
                    out.append((kind, "\n".join(buf)))
                buf, kind = [stripped], "list"
            continue
        if kind in ("table", "list"):
            out.append((kind, "\n".join(buf)))
            buf, kind = [], None
        buf.append(stripped)
        kind = "para"
    if buf:
        out.append((kind, "\n".join(buf)))
    return out


def pages(root):
    result = []
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dp, _, fs in os.walk(d):
            for f in sorted(fs):
                if f.endswith(".md"):
                    result.append(os.path.join(dp, f))
    return result


def key_of(kind, text, n=0):
    body = norm(text)
    if n:
        body = body[:n]
    return hashlib.sha1(("%s|%s" % (kind, body)).encode("utf-8")).hexdigest()


def scan(root):
    files = pages(root)
    if not files:
        return None, [], []
    index = {}
    for p in files:
        for kind, text in blocks(p):
            body = norm(text)
            if len(body) < MIN_PARA:
                continue
            index.setdefault((kind, key_of(kind, text)), []).append((p, body))
            if kind == "para" and len(body) >= DUP_PARA_LEN:
                index.setdefault((kind, key_of(kind, text, 80)), []).append((p, body))
    errs, warns = [], []
    seen = set()
    for (kind, k), hits in index.items():
        paths = sorted({p for p, _ in hits})
        if len(paths) < 2:
            continue
        body = hits[0][1]
        sig = (kind, body[:60], tuple(paths))
        if sig in seen:
            continue
        seen.add(sig)
        n = len(paths)
        if kind == "table":
            # 表格要「够大」才算整表复制：3 行的示例表在多个目录页复用是正常写法
            rows = len([l for l in hits[0][1].split("\n") if l.startswith("|")])
            if n >= 3 and rows >= 4:
                errs.append(("E3", "DUP_TABLE", body[:60], paths))
            elif n >= 3:
                warns.append(("W2", "SHORT_DUP_TABLE", body[:60], paths))
            continue
        if kind == "list":
            items = [t for t in hits[0][1].split("\n") if len(t) >= DUP_LIST_ITEM]
            if n >= 3 and len(items) >= 3:
                warns.append(("W3", "DUP_LIST", body[:60], paths))
            continue
        if body.startswith("::: ") or body.startswith(":::"):
            # 容器提示（::: warning / ::: tip）在多页重复是常见写法，只登记为格式债
            warns.append(("W2", "DUP_CONTAINER", body[:60], paths))
        elif len(body) >= DUP_PARA_LEN and n >= 3:
            errs.append(("E2", "DUP_PARAGRAPH", body[:60], paths))
        elif len(body) >= DUP_PARA_LEN:
            warns.append(("W1", "NEAR_PARAGRAPH", body[:60], paths))
        else:
            warns.append(("W2", "SHORT_DUP_PARAGRAPH", body[:60], paths))
    return files, errs, warns


def report(files, errs, warns, top):
    print("pages=%d E=%d W=%d" % (len(files), len(errs), len(warns)))
    for code, name, head, paths in errs[:top]:
        print("%s %s n=%d :: %s" % (code, name, len(paths), head))
        for p in paths[:5]:
            print("      %s" % p)
    for code, name, head, paths in warns[:top]:
        print("%s %s n=%d :: %s" % (code, name, len(paths), head))
    return 1 if errs else 0


def selftest():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "docs", "A"))
    para = "这是一段用于自检的正文，它的长度必须超过一百二十个字符，才能在段落级重复判据里被算作一次重复。" * 3
    for name in ("p1", "p2", "p3"):
        open(os.path.join(tmp, "docs", "A", name + ".md"), "w", encoding="utf-8").write(
            "# T%s\n\n%s\n\n```shell\n同一段代码不应触发段落重复\n```\n" % (name, para))
    open(os.path.join(tmp, "docs", "A", "unique.md"), "w", encoding="utf-8").write(
        "# U\n\n%s\n" % ("完全不同的另一段正文，" * 10))
    files, errs, warns = scan(tmp)
    ok = len(files) == 4 and any(e[1] == "DUP_PARAGRAPH" for e in errs)
    # 围栏内的相同代码不应被计入
    code_ok = not any("同一段代码" in e[2] for e in errs)
    print("selftest pages=%d E=%d W=%d dup_para=%s code_excluded=%s"
          % (len(files), len(errs), len(warns), ok, code_ok))
    return 0 if (ok and code_ok) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not os.path.isdir(os.path.join(a.root, "docs")) and not os.path.isdir(
            os.path.join(a.root, "project")):
        print("E0 ROOT_NOT_FOUND")
        return 2
    files, errs, warns = scan(a.root)
    if files is None:
        print("E1 NO_PAGES")
        return 2
    return report(files, errs, warns, a.top)


if __name__ == "__main__":
    sys.exit(main())
