#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""anchortextcheck.py — 「链接文字与目标页标题是否同一件事」巡检 · 第 95 项

为什么立这一项
--------------
本库关于「链接」已有三道门，各管一段，**没有一道问「链接文字说的是不是那一页」**：

* `linkexistcheck`   —— 目标文件在不在（`E2 BROKEN_MD` / `E3 BROKEN_ASSET`）；
* `linkformcheck`    —— 链接语法形态对不对（绝对路径、缺扩展名）；
* `titlematchcheck`  —— **侧边栏** `text` 与目标页 H1 是否一致。

第三个门管的是「菜单」，而正文里的链接文字是**第三个地方**：读者点进正文链接时，
先把链接文字当成那一页的摘要。页面改过名、链接没跟着改，文字就会指向一件已经
不存在的事——而前三道门全绿，因为它确实「存在」，只是不叫这个名字了。

这类漂移的伤害不在于点不开，而在于**点开后发现「不是我想要的」**：目录页写
「事件溯源与 CQRS 落地」，点进去标题是「事件溯源与 CQRS 落地工程」还能接受；写
「消息队列」点进去是「可靠投递与消费幂等」，读者会怀疑自己点错了。

**范围收窄（首版翻车记录，如实写下来）**：首版扫了**全部**正文内链，一次跑出
`links=16,547 W1=2,109 W2=6,448`——那不是 2,109 个缺陷，而是 2,109 条「写作风格」。
正文里的链接文字天然是句子成分（「见[会话复用器](...)」），它**不必**等于目标页标题；
把它们判成漂移，等于要求全库所有链接都写成标题，这是把「风格」当「缺陷」。
于是范围收窄为**目录式条目**：整行只有一个链接的列表项（`- [文字](目标.md)`）。
这种写法在本库的语义就是「这一页的名字」，与 H1 天然应当一致。收窄后同一套判据变成
`1,574 一致 / 88 W1 / 213 W2 / 7 目标缺失`——**88 条是可以逐日消化的欠账**。

判据
----
E0 ROOT_NOT_FOUND     仓库根找不到（既没有 docs/ 也没有 project/）
E1 NO_LINKS           一条正文内链都没解析到（活性判据：拒绝在空集上给「全绿」）
E2 NO_H1              目标页没有 `#` 一级标题（无法比较，单独报，不混进 W1）
W1 ITEM_DIFF          归一化 + 软归一化后条目文字与 H1 仍互不包含（真漂移）
W2 ITEM_SHORT         一方是另一方的子串，或仅差大小写/点号/连字符（短名与写法风格）
W3 GENERIC            条目文字是「这里 / 详见 / 参考资料」这类泛称（不计入 W1/W2）

口径（六条，全部来自本库语料的打磨）
------------------------------------
1. **只查目录式条目**：整行只有一个链接的列表项（`- [文字](目标.md)`）。正文句子
   里的链接（「见[某某](...)」）不查——它的文字是句子成分，不是页面名。外链
   （`http`）、图片（`![`）、纯锚点（`#xxx`）同样跳过。
2. **围栏与行内代码必须跳过**：复用第 88 项的共享底座 `fenceutil.scan()`，本项
   不写第五份围栏正则（上一批巡检的教训就是不共用底座会各自栽跟头）。
3. **`index.md` 与目录式链接都认**：`X/index.md`、`X/` 都能解析到 `X/index.md`；
   解析不到的目标**不报 E**，交给 `linkexistcheck`（避免两道门报同一个缺陷）。
4. **泛称单独算 `W3`**：本库大量写「见[这里](...)」「详见[参考资料](...)」，
   这是写作风格，不是漂移；报 `W1` 会让几百条合规链接变红（永久红 = 没人看）。
5. **归一化只做四件事**：去掉尾部成对括号组、全角括号与冒号转半角、压缩空白、
   去尾部标点。**不去数字、不去汉字**——「第 4 周第 4 步」与「第 5 步」必须判不同。
6. **链接文字前缀词剥掉**：`见` / `参见` / `详见` / `关于` 这些是句子成分，不是标题
   的一部分，比较前剥掉（否则「见总览」与「总览」会被判成漂移）。

与 `titlematchcheck` 的关系：**同一条规则、第三个位置**。侧边栏管「菜单准不准」，
本项管「正文引用准不准」；两者共用同一套归一化思路，但各自独立实现（归一化只有
四步，重复的代价远低于把两个不同来源的字符串混进一个函数）。
若日后合并，删本项、把「正文链接文字」作为第三种来源并进 `titlematchcheck` 即可。

纪律
----
* **只读**：不改链接文字、不改标题，只报告。
* `--selftest` 的夹具走 `tempfile.mkdtemp()`，绝不落进仓库。

用法
----
    python3 utils/audit/anchortextcheck.py
    python3 utils/audit/anchortextcheck.py --root . --limit 40
    python3 utils/audit/anchortextcheck.py --selftest
"""

import argparse
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fenceutil  # noqa: E402

# 目录式条目：整行只有一个链接的列表项（允许缩进、允许 1. 有序列表）
PURE_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(?<!!)\[([^\]\n]{1,120})\]\(([^)\s]+)\)\s*$")
PAREN_TAIL_RE = re.compile(r"[（(][^（()）]*[）)]\s*$")
GENERIC = {
    "这里", "此处", "详见", "见", "参见", "点击", "链接", "文档", "页面",
    "上一页", "下一页", "参考资料", "相关页面", "详情", "更多", "本页", "该页",
}
PREFIX_RE = re.compile(r"^(?:详见|参见|见|关于|阅读)\s*")
TAIL_PUNCT = "：:。．.，,、；;》」】)）"


def normalize(text: str) -> str:
    s = text.strip()
    s = PREFIX_RE.sub("", s)
    while True:
        stripped = PAREN_TAIL_RE.sub("", s).strip()
        if stripped == s or not stripped:
            break
        s = stripped
    s = s.replace("（", "(").replace("）", ")").replace("：", ":")
    s = re.sub(r"\s+", "", s)
    return s.rstrip(TAIL_PUNCT).casefold()


SOFT_STRIP_RE = re.compile(r"[.\-·—'\"`]")


def soft(text: str) -> str:
    """软归一化：只抹掉「写法差异」，不抹掉语义差异（大小写、点号、连字符、中点）。"""
    return SOFT_STRIP_RE.sub("", text)


def read_h1(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    return line[2:].strip()
    except OSError:
        return None
    return None


def iter_pages(root: str):
    for base in ("docs", "project"):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for dirpath, _dirnames, filenames in os.walk(top):
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def resolve(src: str, target: str, root: str):
    """把相对的 md 链接解析成绝对路径；外链/图片/锚点返回 None。"""
    if target.startswith(("http://", "https://", "mailto:", "#", "//")):
        return None
    t = target.split("#", 1)[0]
    if not t:
        return None
    if not t.endswith(".md"):
        if t.endswith("/"):
            t = t + "index.md"
        else:
            return None
    p = os.path.normpath(os.path.join(os.path.dirname(src), t))
    if not p.startswith(os.path.join(root, "")):
        return None
    return p


def check(root: str, limit: int = 0, quiet: bool = False):
    result = {"E1": 0, "E2": 0, "W1": 0, "W2": 0, "W3": 0}
    issues = []
    checked = 0
    missing = 0
    for page in iter_pages(root):
        try:
            text = open(page, encoding="utf-8").read()
        except OSError:
            continue
        mask, _, _ = fenceutil.scan(text)
        rel_page = os.path.relpath(page, root)
        for idx, line in enumerate(text.split("\n")):
            if idx in mask:
                continue
            m = PURE_ITEM_RE.match(line)
            if not m:
                continue
            if True:
                anchor, target = m.group(1).strip(), m.group(2).strip()
                tgt = resolve(page, target, root)
                if tgt is None:
                    continue
                na = normalize(anchor)
                if not na or na in GENERIC:
                    result["W3"] += 1
                    continue
                if not os.path.isfile(tgt):
                    missing += 1
                    continue
                h1 = read_h1(tgt)
                if not h1:
                    result["E2"] += 1
                    if not quiet and (not limit or len(issues) < limit):
                        issues.append(("E2 NO_H1", rel_page, f"{target} <- {anchor}"))
                    continue
                checked += 1
                nh = normalize(h1)
                if na == nh:
                    continue
                if na in nh or nh in na or soft(na) == soft(nh):
                    result["W2"] += 1
                    if not quiet and (not limit or len(issues) < limit):
                        issues.append(("W2 ITEM_SHORT", rel_page, f"item={anchor} | h1={h1}"))
                    continue
                result["W1"] += 1
                if not quiet and (not limit or len(issues) < limit):
                    issues.append(("W1 ITEM_DIFF", rel_page, f"item={anchor} | h1={h1}"))
    if checked == 0 and result["E2"] == 0:
        result["E1"] = 1
    return result, issues, checked, missing


def selftest() -> int:
    cases = []

    def build(files):
        d = tempfile.mkdtemp()
        for rel, content in files.items():
            p = os.path.join(d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
        return d

    # 1. 目录式条目与 H1 完全一致：不报
    d = build({"docs/A/index.md": "# A\n\n- [计价链路](B/index.md)\n",
               "docs/A/B/index.md": "# 计价链路\n"})
    r, _, _, _ = check(d)
    cases.append(("一致不报", r["W1"] == 0 and r["W2"] == 0))

    # 2. 短名：W2
    d = build({"docs/A/index.md": "# A\n\n- [总览](B/index.md)\n",
               "docs/A/B/index.md": "# 总览：七段链\n"})
    r, _, _, _ = check(d)
    cases.append(("短名 W2", r["W2"] == 1 and r["W1"] == 0))

    # 3. 互不包含：W1
    d = build({"docs/A/index.md": "# A\n\n- [消息队列](B/index.md)\n",
               "docs/A/B/index.md": "# 可靠投递与消费幂等\n"})
    r, _, _, _ = check(d)
    cases.append(("漂移 W1", r["W1"] == 1))

    # 4. 泛称：W3，不计 W1/W2
    d = build({"docs/A/index.md": "# A\n\n- [这里](B/index.md)\n",
               "docs/A/B/index.md": "# 完全不同的标题\n"})
    r, _, _, _ = check(d)
    cases.append(("泛称 W3", r["W3"] == 1 and r["W1"] == 0))

    # 5. 围栏里的条目不算
    d = build({"docs/A/index.md": "# A\n\n```md\n- [消息队列](B/index.md)\n```\n",
               "docs/A/B/index.md": "# 别的标题\n"})
    r, _, _, _ = check(d)
    cases.append(("围栏跳过", r["W1"] == 0 and r["W3"] == 0))

    # 6. 图片引用不算
    d = build({"docs/A/index.md": "# A\n\n- ![消息队列](B/index.md)\n",
               "docs/A/B/index.md": "# 别的标题\n"})
    r, _, _, _ = check(d)
    cases.append(("图片跳过", r["W1"] == 0))

    # 7. 正文句子里的链接不算（收窄的核心口径）
    d = build({"docs/A/index.md": "# A\n\n详见[消息队列](B/index.md) 那一页。\n",
               "docs/A/B/index.md": "# 完全不同的标题\n"})
    r, _, _, _ = check(d)
    cases.append(("正文链接跳过", r["W1"] == 0 and r["W3"] == 0))

    # 8. 目标缺失不报 E（交给 linkexistcheck）
    d = build({"docs/A/index.md": "# A\n\n- [不存在的页](Nope/index.md)\n"})
    r, _, _, missing = check(d)
    cases.append(("缺失不报 E", missing == 1 and r["E2"] == 0))

    # 9. 目标无 H1：E2
    d = build({"docs/A/index.md": "# A\n\n- [某页](B/index.md)\n",
               "docs/A/B/index.md": "## 只有二级\n"})
    r, _, _, _ = check(d)
    cases.append(("无 H1 E2", r["E2"] == 1))

    # 10. 空集合：E1（拒绝在空集上给全绿）
    d = build({"docs/A/index.md": "# A\n\n没有条目。\n"})
    r, _, _, _ = check(d)
    cases.append(("空集合 E1", r["E1"] == 1))

    # 11. 前缀词剥离：「参见总览」vs「总览」
    d = build({"docs/A/index.md": "# A\n\n- [参见总览](B/index.md)\n",
               "docs/A/B/index.md": "# 总览\n"})
    r, _, _, _ = check(d)
    cases.append(("前缀词剥离", r["W1"] == 0))

    # 12. 数字差异不被吞
    d = build({"docs/A/index.md": "# A\n\n- [第 4 周第 4 步](B/index.md)\n",
               "docs/A/B/index.md": "# 第 4 周第 5 步\n"})
    r, _, _, _ = check(d)
    cases.append(("数字不吞", r["W1"] == 1))

    # 13. 目录式目标（`B/`）自动补 index.md
    d = build({"docs/A/index.md": "# A\n\n- [计价链路](B/)\n",
               "docs/A/B/index.md": "# 计价链路\n"})
    r, _, _, _ = check(d)
    cases.append(("目录式目标", r["W1"] == 0 and r["E2"] == 0))

    # 14. 只差大小写/点号：软归一化判 W2，不判 W1
    d = build({"docs/A/index.md": "# A\n\n- [NodeJs](B/index.md)\n",
               "docs/A/B/index.md": "# Node.js\n"})
    r, _, _, _ = check(d)
    cases.append(("软归一化 W2", r["W2"] == 1 and r["W1"] == 0))

    # 15. 有序列表也算目录式条目
    d = build({"docs/A/index.md": "# A\n\n1. [计价链路](B/index.md)\n",
               "docs/A/B/index.md": "# 计价链路\n"})
    r, _, _, _ = check(d)
    cases.append(("有序列表", r["W1"] == 0 and r["W2"] == 0))

    ok = 0
    for name, passed in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok += 1 if passed else 0
    print(f"selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="正文链接文字与目标页 H1 一致性巡检（第 95 项）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "docs")):
        print("E0 ROOT_NOT_FOUND（找不到 docs/）")
        return 2
    result, issues, checked, missing = check(root, limit=args.limit, quiet=args.quiet)
    for kind, path, detail in issues:
        print(f"{kind}\t{path}\t{detail}")
    print(
        "anchortextcheck: links={} missingTarget={} E={} W1={} W2={} W3={}".format(
            checked, missing, result["E1"] + result["E2"],
            result["W1"], result["W2"], result["W3"],
        )
    )
    return 0 if result["E1"] + result["E2"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
