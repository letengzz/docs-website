#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""judgeghostcheck.py —— 「判据编号被引用但全库没有定义」巡检（第 259 天新立，第一百四十一项巡检）

为什么立这一项
--------------
本仓的判据编号（`FTO-A`、`LNW-H` 这类）是**跨页面的引用坐标**：正文写「见 `DGD-F`」、
目录页写「十页共 80 条」、项目章节写「与 `MKI-C` 同一口径」。读者会顺着这个编号去找定义。

既有的三项巡检各管一段，但都不回答「这个编号到底存不存在」：

* `judgeidcheck`：同一编号是否被**两个页面同时定义**（重复）；
* `judgecovercheck`：单页的「声明 8 条」与「表里 8 行」是否一致（页内）；
* `judgesumcheck`：专题目录页的总条数与各页声明之和是否一致（数量）。

三者全绿，仍然可以出现这种页面：

    这一条与 `QRX-C` 是同一个坑。

而全库从来没有人定义过 `QRX-C`。**构建不报错、目录页总数也对、读者点不过去**——
因为 `QRX-C` 根本不是链接，只是一段等宽文本。这就是「幽灵判据」。

判据
----
E0 ROOT_NOT_FOUND      扫描根不存在
E1 NO_PAGES            一个 Markdown 都没枚举到（活性：拒绝在空样本上给全绿）
E2 REF_UNDEFINED       正文引用了 `ABC-X`，但全库没有任何一页把它写在判据表首列
E3 BAD_LETTER          字母落在 A~H 之外（`ABC-I`、`ABC-Z` 一类手误）
W1 FAMILY_GAP          某页定义了某族，但字母不连续（缺 A、B 之类）
W2 SELF_ONLY           某编号只在本页出现、从未被任何页面引用（可能是写完就忘了用）
W3 PREFIX_SHAPE        前缀不是 3 个大写字母（只计数，用于发现 `AB-A` 这类短前缀）

口径说明
--------
* **定义** = 表格数据行的**首格**，去掉粗体与反引号后**恰好**是编号（形如表格行首格写
  `ABC-A`、`` **`ABC-A`** ``、`**ABC-A**`、裸写 `ABC-A` 四种写法本库都有）。
  只认首格，是因为本库的判据表一律「编号在第一列」，别的列出现编号是引用。
* 首格四种写法都认，是**本项最重要的一条口径收敛**：首版只认「反引号 + 紧跟竖线」，
  把 `project/Complete/TeamBoard`（`| **`BR-A`** |`）与 `project/Complete/MonitoringDashboard`
  （`| **AR-A** |`）、`docs/DB/VectorDatabase/Practice`（`| VD-A |`）三批**真定义**判成
  「未定义引用」，全库 `E=275`；改为「首格归一化后比对」后降到 **57**。
* **引用** = 除定义行以外的任何出现（含正文、表格单元格、代码围栏外）。
* 围栏内的编号不计引用：代码块里写判据编号是举例，不是承诺。
* 本项只做「存在性」，不做「引用得对不对」——那需要语义判断，交给人工。
"""
import os
import re
import sys

ID_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z]{2,4})-([A-Z])(?![A-Za-z0-9])")
CELL_RE = re.compile(r"^\|([^|]*)\|")
CELL_ID_RE = re.compile(r"^([A-Z]{2,4})-([A-H])(?![A-Za-z0-9])")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def def_id(line):
    """表格行首格**以**判据编号开头则为定义；返回 (前缀, 字母)。

    首格允许「编号 + 一句话声明」同格（`| **`CB-A`** 收敛四项… |` 这种写法早期章节很多），
    所以是前缀匹配而不是整格相等。
    """
    m = CELL_RE.match(line.strip())
    if not m:
        return None
    cell = m.group(1).replace("*", "").replace("`", "").strip()
    m2 = CELL_ID_RE.match(cell)
    return (m2.group(1), m2.group(2)) if m2 else None


def iter_md(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in
                   {"node_modules", ".git", "dist", ".vitepress", "__pycache__"}]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(base, f)


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        return open(path, encoding="utf-8", errors="replace").read()


def scan(pages):
    """pages: [(path, text)] -> (defs, refs, issues)"""
    defs = {}          # (prefix, letter) -> [paths]
    refs = {}          # (prefix, letter) -> [paths]
    issues = []
    for path, text in pages:
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), 1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            hit = def_id(line)
            if hit:
                defs.setdefault(hit, []).append(path)
                # 定义行本身也可能在同一行引用别处，但首格已消费，跳过本行
                continue
            for mm in ID_RE.finditer(line):
                key = (mm.group(1), mm.group(2))
                refs.setdefault(key, []).append(f"{path}:{lineno}")
    return defs, refs, issues


def analyze(root="."):
    """返回 (pages, defs, refs, out)；out 为全部发现项"""
    docs = os.path.join(root, "docs")
    proj = os.path.join(root, "project")
    if not os.path.isdir(docs) and not os.path.isdir(proj):
        return None, None, None, [("E0 ROOT_NOT_FOUND", root, "", "")]
    paths = []
    for base in (docs, proj):
        if os.path.isdir(base):
            paths.extend(iter_md(base))
    paths.sort()
    if not paths:
        return None, None, None, [("E1 NO_PAGES", "", "", "")]

    pages = [(p, read(p)) for p in paths]
    defs, refs, _ = scan(pages)

    out = []
    # E2 / E3
    for key in sorted(refs):
        prefix, letter = key
        if key not in defs:
            kind = "E3 BAD_LETTER" if letter not in "ABCDEFGH" else "E2 REF_UNDEFINED"
            out.append((kind, f"{prefix}-{letter}", refs[key][0], f"{len(refs[key])} 处引用"))
    # W1 族内缺字母
    fam = {}
    for (prefix, letter) in defs:
        fam.setdefault(prefix, set()).add(letter)
    for prefix in sorted(fam):
        letters = fam[prefix]
        expect = [chr(ord("A") + i) for i in range(len(letters))]
        if sorted(letters) != expect:
            missing = [c for c in "ABCDEFGH" if c not in letters]
            out.append(("W1 FAMILY_GAP", prefix, defs[(prefix, sorted(letters)[0])][0],
                        "缺 " + ",".join(missing)))
    # W2 定义了但全库无人引用
    for key in sorted(defs):
        if key not in refs:
            out.append(("W2 SELF_ONLY", f"{key[0]}-{key[1]}", defs[key][0], "全库无引用"))
    # W3 前缀形状
    for key in sorted(defs):
        if len(key[0]) != 3:
            out.append(("W3 PREFIX_SHAPE", f"{key[0]}-{key[1]}", defs[key][0], "前缀非 3 字母"))

    return pages, defs, refs, out


def run(root=".", quiet=False):
    pages, defs, refs, out = analyze(root)
    if pages is None:
        print(out[0][0], out[0][1])
        return 2
    counts = {}
    for kind, *_ in out:
        counts[kind.split()[0]] = counts.get(kind.split()[0], 0) + 1
    if not quiet:
        for item in out:
            print(f"{item[0]:20s} {item[1]:10s} {item[2]}  ({item[3]})")
    print(f"pages={len(pages)} defs={len(defs)} refs={len(refs)} "
          f"E={counts.get('E2', 0) + counts.get('E3', 0)} "
          f"W1={counts.get('W1', 0)} W2={counts.get('W2', 0)} W3={counts.get('W3', 0)}")
    return 0 if counts.get("E2", 0) + counts.get("E3", 0) == 0 else 1


def selftest():
    import tempfile
    checks = []
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "docs"))
        def w(name, body):
            p = os.path.join(d, "docs", name)
            open(p, "w", encoding="utf-8").write(body)
            return p

        w("a.md", "# A\n\n本页判据族 `ABC-A` ~ `ABC-B`，共 2 条。\n\n"
                  "| 编号 | 判据 |\n| --- | --- |\n| `ABC-A` | 甲 |\n| `ABC-B` | 乙 |\n\n"
                  "见 `ABC-B` 与 `XYZ-C`。\n")
        w("b.md", "# B\n\n| 编号 | 判据 |\n| --- | --- |\n| `DEF-A` | 丙 |\n\n"
                  "与 `ABC-A` 同一口径。\n")
        w("c.md", "# C\n\n| 编号 | 判据 |\n| --- | --- |\n| `GHI-A` | 丁 |\n\n"
                  "手误写成 `GHI-I`。\n")
        w("e.md", "# E\n\n```text\n例如 `JKL-B` 这种写法\n```\n")
        w("f.md", "# F\n\n| 编号 | 判据 |\n| --- | --- |\n| `MNO-A` | 戊 |\n| `MNO-C` | 己 |\n\n"
                  "见 `MNO-C`。\n")

        pages, defs, refs, out = analyze(d)
        kinds = [k for k, *_ in out]
        ids = [i for _, i, *_ in out]

        checks.append(("定义能认出 6 条", len(defs) == 6))
        checks.append(("同页引用计入 refs", ("ABC", "B") in refs))
        checks.append(("跨页引用计入 refs", ("ABC", "A") in refs))
        checks.append(("未定义引用计入 refs", ("XYZ", "C") in refs))
        checks.append(("围栏内不计引用", ("JKL", "B") not in refs))
        checks.append(("坏字母计入 refs", ("GHI", "I") in refs))

        checks.append(("未定义报 E2", "E2 REF_UNDEFINED" in kinds and "XYZ-C" in ids))
        checks.append(("坏字母报 E3", "E3 BAD_LETTER" in kinds and "GHI-I" in ids))
        checks.append(("E2/E3 各恰好 1 条",
                       kinds.count("E2 REF_UNDEFINED") == 1 and kinds.count("E3 BAD_LETTER") == 1))
        checks.append(("缺字母报 W1", "W1 FAMILY_GAP" in kinds and "MNO" in ids))
        checks.append(("定义了没人用报 W2", "W2 SELF_ONLY" in kinds and "DEF-A" in ids))
        checks.append(("有 E 时返回 1", run(d, quiet=True) == 1))

    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "docs"))
        open(os.path.join(d, "docs", "ok.md"), "w", encoding="utf-8").write(
            "# ok\n\n| 编号 | 判据 |\n| --- | --- |\n| `ABC-A` | 甲 |\n\n"
            "见 `ABC-A` 与 `ABC-B`。\n")
        open(os.path.join(d, "docs", "ok2.md"), "w", encoding="utf-8").write(
            "# ok2\n\n| 编号 | 判据 |\n| --- | --- |\n| `ABC-B` | 乙 |\n")
        checks.append(("干净样本返回 0", run(d, quiet=True) == 0))

    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "docs"))
        open(os.path.join(d, "docs", "bold.md"), "w", encoding="utf-8").write(
            "# bold\n\n| 判据 | 一句话声明 |\n| --- | --- |\n"
            "| **`PQR-A`** | 甲 |\n| **`PQR-B`** | 乙 |\n| VWX-A | 丙 |\n"
            "| **`RST-A`** 编号与声明同格 | 丁 |\n\n"
            "正文引用 `PQR-A` 与 `PQR-B`，另有 `STU-B` 未定义。\n"
            "\n```text\n| YZA-A | 围栏里的表格不是定义 |\n```\n")
        _, defs, _, out = analyze(d)
        kinds = [k for k, *_ in out]
        ids = [i for _, i, *_ in out]
        checks.append(("粗体首格算定义", ("PQR", "A") in defs and ("PQR", "B") in defs))
        checks.append(("裸首格也算定义", ("VWX", "A") in defs))
        checks.append(("编号与声明同格也算定义", ("RST", "A") in defs))
        checks.append(("围栏里的表格不算定义", ("YZA", "A") not in defs))
        checks.append(("粗体定义不报 E2", "PQR-A" not in ids and "PQR-B" not in ids))
        checks.append(("粗体样本只剩 1 条 E2",
                       kinds.count("E2 REF_UNDEFINED") == 1 and "STU-B" in ids))

    with tempfile.TemporaryDirectory() as d:
        checks.append(("空根报 E0", run(d, quiet=True) == 2))

    ok = all(o for _, o in checks)
    for name, o in checks:
        if not o:
            print("FAIL:", name)
    print(f"selftest {sum(1 for _, o in checks if o)}/{len(checks)}",
          "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(selftest())
    if len(args) > 1:
        print("usage: judgeghostcheck.py [root] | --selftest")
        sys.exit(2)
    sys.exit(run(args[0] if args else "."))
