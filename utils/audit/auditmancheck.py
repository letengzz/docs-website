#!/usr/bin/env python3
"""巡检台账 ⇄ 脚本实物对账（第 70 项巡检）

存在的理由：本仓最反复出现的缺陷形态是**「台账 ≠ 实物」**——`DOCS_PLAN.md` 的存量整理清单里
写着「第 N 项巡检 `xxx.py` 新立并结清」，而那个脚本在仓库里、在脚本目录里**都不存在**。
这类缺陷最恶劣的地方在于它是**反向**的：读者看到「已结清」会以为那道门禁已经关上，
于是不再人工检查；而它其实从来没跑过。历史上第 49/50 项就是这么消失的。

既有的 `plancheck.py`（历史名，已不在本仓）的 `E2 REGISTERED_NOT_EXISTS` 只查「台账里写了路径的**文件**是否存在」，
判据是路径字符串；本脚本查的是**结构化对账**：
  ① 项号 ⇄ 脚本名 的映射是否一对一；
  ② 每个被声称「已结清」的脚本是否真的能在某个脚本家里找到；
  ③ 脚本家里有没有从未被登记的脚本（有门禁没账）。

判据：
  E0 ROOT_NOT_FOUND         既没有 DOCS_PLAN.md 也没有 docs/
  E1 NO_CLAIMS              一条台账声明都没解析到（拒绝判定）
  E2 SCRIPT_MISSING         「已结清」声明的脚本在所有脚本家里都找不到
  E3 NUMBER_CONFLICT        同一个项号被分配给两个以上不同脚本（同号不同物）
  W1 SCRIPT_MULTI_NUMBER    同一个脚本被登记了两个以上项号（历史重编号，可解释）
  W2 NUMBER_GAP             项号序列有缺口（**仅当解析覆盖完整时才判**，见下）
  W3 UNREGISTERED_SCRIPT    脚本家里存在、台账里从未出现的脚本
  N0 PARTIAL_COVERAGE       带脚本名的声明占比过低 → 项号缺口是解析残缺造成的假象，不出 W2

「脚本家」有四个来源，缺一不可——这是本脚本第一版最容易犯错的地方：
  ① 仓库内 `utils/audit/`（本仓自有的 13 个巡检）；
  ② 仓库内 `utils/`（侧边栏生成器等 3 个 `.mjs`）；
  ③ 外部技能脚本家 `~/.workbuddy/skills/docs-website-doc-ops/scripts/`（**本仓 37 个巡检
     的真身长期在这里**，台账里反复写的就是 `~/.workbuddy/skills/.../scripts/xxx.py`）；
     可用环境变量 `DOCS_SKILL_SCRIPTS` 或 `--extra-scripts` 覆盖/追加。
  ④ 只扫 ①② 会造出一批**误报**：`judgerefcheck.py`（第 39 项，历史名）、`judgecountcheck.py`（第 45 项，历史名）
     （第 45 项）明明在技能家里，却被判「找不到」——第一版就是这样把 2 处误报混进 E 里的。

判据间的正确读法（覆盖率的教训）：
  `parse_claims` 只认「第 N 项」与脚本名**相邻**（80 字符内）的写法，因此 107 条声明里只有
  18 条带脚本名（16.8%）。**项号缺口的真伪完全取决于覆盖率**：台账 69 个项号里只有 16 个
  被解析到，剩下 53 个「缺口」全是解析残缺的产物、不是台账真的丢了 53 项。故 W2 设一条
  闸门——覆盖率 < 90% 时只出 N0，不出 W2。**「数据不完整时不下结论」比「多报一条」重要。**

豁免（登记式，不是静默放过）：
  - 段落里含「未落盘 / 不存在 / 已丢失 / 待补 / 已归档」的**不是声明**，是如实披露，
    不计入 E2 / E3 / W1（披露本身即处置；本脚本抓的是**未被披露**的漂移）。
  - `_` 开头的脚本与 `svgkit_template.py`（历史名；模板，不是巡检，已不在本仓）不计入 W3。
  - 侧边栏生成器（`auto_sidebar.mjs` / `auto-gen-sidebar.mjs` / `gen_sidebar.mjs`）不是门禁，
    不计入 W3——**W3 问的是「有门禁没账」，不是「有脚本没账」**。

用法：
  python3 utils/audit/auditmancheck.py --root . [--extra-scripts DIR]... [--list] [--selftest] [--mutate]
退出码：0 = 无 E；1 = 有 E；2 = 用法/环境错误
"""
import os
import re
import sys
import tempfile

CLAIM_RE = re.compile(r"第\s*(\d{1,3})\s*项")
SCRIPT_RE = re.compile(r"([A-Za-z0-9_\-]+\.(?:py|mjs))")
DISCLOSE = ("未落盘", "不存在", "已丢失", "待补", "已归档")
CLAIM_WORDS = ("结清", "落盘", "新立")
IGNORE_SCRIPTS = {"svgkit_template.py", "auto_sidebar.mjs",   # 前者为历史名，仅为忽略名单保留
                  "auto-gen-sidebar.mjs", "gen_sidebar.mjs"}
DEFAULT_DIRS = ("utils/audit", "utils")
SKILL_ENV = "DOCS_SKILL_SCRIPTS"
SKILL_DEFAULT = "~/.workbuddy/skills/docs-website-doc-ops/scripts"
COVERAGE_FLOOR = 0.90


def parse_claims(text):
    """从 DOCS_PLAN 正文里抽 (项号, 脚本名, 是否披露式) —— 一行可能有多条声明。"""
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        if "项" not in line:
            continue
        for m in CLAIM_RE.finditer(line):
            num = int(m.group(1))
            tail = line[m.end(): m.end() + 80]
            sm = SCRIPT_RE.search(tail)
            seg = line[max(0, m.start() - 30): m.end() + 80]
            disclosed = any(w in seg for w in DISCLOSE)
            claimed = any(w in seg for w in CLAIM_WORDS)
            out.append({"num": num, "script": sm.group(1) if sm else None,
                        "line": lineno, "disclosed": disclosed, "claimed": claimed})
    return out


def scan_scripts(dirs):
    found = {}
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            p = os.path.join(d, fn)
            if os.path.isfile(p) and (fn.endswith(".py") or fn.endswith(".mjs")):
                found.setdefault(fn, []).append(d)
    return found


def external_dirs():
    """外部技能脚本家（本仓 37 个巡检的真身所在），可用环境变量覆盖。"""
    raw = os.environ.get(SKILL_ENV) or SKILL_DEFAULT
    return [os.path.expanduser(p) for p in raw.replace(";", os.pathsep).split(os.pathsep) if p.strip()]


def check(root, extra_dirs=()):
    findings = []
    plan = os.path.join(root, "DOCS_PLAN.md")
    if not (os.path.isfile(plan) or os.path.isdir(os.path.join(root, "docs"))):
        return [("E0", "ROOT_NOT_FOUND", "既没有 DOCS_PLAN.md 也没有 docs/")]

    text = ""
    if os.path.isfile(plan):
        with open(plan, encoding="utf-8", errors="replace") as f:
            text = f.read()
    claims = parse_claims(text)
    real = [c for c in claims if c["script"]]
    if not real:
        return [("E1", "NO_CLAIMS", "一条带脚本名的台账声明都没解析到")]

    dirs = [os.path.join(root, d) for d in DEFAULT_DIRS] + external_dirs() + list(extra_dirs)
    scripts = scan_scripts(dirs)

    # E2：声称已结清、但脚本找不到
    for c in real:
        if c["disclosed"] or not c["claimed"]:
            continue
        if c["script"] not in scripts:
            findings.append(("E2", "SCRIPT_MISSING",
                             f"第 {c['num']} 项声称结清 `{c['script']}`，但 {c['line']} 行所指脚本在脚本家里找不到"))

    # E3：同一项号 → 两个不同脚本（已披露撞号的条目不计：披露本身即处置）
    by_num = {}
    for c in real:
        by_num.setdefault(c["num"], set())
        if not c["disclosed"]:
            by_num[c["num"]].add(c["script"])
    for num, names in sorted(by_num.items()):
        if len(names) > 1:
            findings.append(("E3", "NUMBER_CONFLICT",
                             f"第 {num} 项被分配给 {len(names)} 个脚本：{', '.join(sorted(names))}"))

    # W1：同一脚本 → 多个项号（同上，披露过的重编号不计）
    by_script = {}
    for c in real:
        if c["disclosed"]:
            continue
        by_script.setdefault(c["script"], set()).add(c["num"])
    for name, nums in sorted(by_script.items()):
        if len(nums) > 1:
            findings.append(("W1", "SCRIPT_MULTI_NUMBER",
                             f"`{name}` 被登记了 {len(nums)} 个项号：{sorted(nums)}"))

    # W2：项号缺口 —— 只在「解析覆盖完整」时才有意义，否则缺口全是解析残缺的产物
    coverage = len(real) / len(claims) if claims else 0.0
    nums = sorted(by_num)
    if coverage >= COVERAGE_FLOOR and nums:
        gaps = [n for n in range(1, nums[-1] + 1) if n not in by_num]
        if gaps:
            findings.append(("W2", "NUMBER_GAP",
                             f"项号缺口 {len(gaps)} 个：{gaps[:12]}{' …' if len(gaps) > 12 else ''}"))
    elif nums:
        findings.append(("N0", "PARTIAL_COVERAGE",
                         f"带脚本名的声明仅 {len(real)}/{len(claims)}（{coverage:.1%}）"
                         f"< {COVERAGE_FLOOR:.0%}，项号缺口不可判，W2 不出"))

    # W3：有门禁没账 —— 只扫仓库内的脚本家（外部技能目录不属于本仓台账范围）；
    #     「台账从未出现」按**全文**判：脚本名只要在 DOCS_PLAN 任何位置出现过就算登记过，
    #     不要求它紧跟在「第 N 项」后面（否则 headingcheck / refjudgecheck 这类
    #     「名字离项号太远」的已登记脚本会被误报成「没账」）。
    local = scan_scripts([os.path.join(root, d) for d in DEFAULT_DIRS])
    mentioned = set(SCRIPT_RE.findall(text))
    for name in sorted(local):
        if name in mentioned or name in IGNORE_SCRIPTS or name.startswith("_"):
            continue
        findings.append(("W3", "UNREGISTERED_SCRIPT",
                         f"`{name}` 在 {local[name][0]} 里，但台账从未登记"))

    return findings


# ------------------------------------------------------------------ 自测
CASES = {
    "case-01": ("正常：一对一，脚本齐全", [("1", "alpha.py", True)], {"alpha.py": 1}, set()),
    "case-02": ("E2：声称结清但脚本不存在", [("1", "ghost.py", True), ("2", "alpha.py", True)],
                {"alpha.py": 1}, {"E2"}),
    "case-03": ("E3：同一项号两个脚本", [("1", "alpha.py", True), ("1", "beta.py", True)],
                {"alpha.py": 1, "beta.py": 1}, {"E3"}),
    "case-04": ("W1：同一脚本两个项号", [("1", "alpha.py", True), ("2", "alpha.py", True)],
                {"alpha.py": 1}, {"W1"}),
    "case-05": ("如实披露不算声明（豁免）", [("1", "ghost.py", False), ("2", "alpha.py", True)],
                {"alpha.py": 1}, set()),
    "case-06": ("W2：项号缺口", [("1", "alpha.py", True), ("3", "beta.py", True)],
                {"alpha.py": 1, "beta.py": 1}, {"W2"}),
    "case-07": ("W3：有门禁没账", [("1", "alpha.py", True)], {"alpha.py": 1, "stray.py": 1}, {"W3"}),
    "case-08": ("E1：一条声明都没有", [("", "", False)], {"alpha.py": 1}, {"E1"}),
    "case-09": ("两项同号同脚本（不算冲突）",
                [("1", "alpha.py", True), ("1", "alpha.py", True)], {"alpha.py": 1}, set()),
    "case-10": ("E2 + W1 + W3 同时出现",
                [("1", "ghost.py", True), ("2", "gamma.py", True), ("3", "gamma.py", True)],
                {"gamma.py": 1, "beta.py": 1}, {"E2", "W1", "W3"}),
    # 下面两条锁定本轮修掉的两个失真点：W2 的门控、W3 的全文口径
    "case-11": ("N0：覆盖率不足时不出 W2（缺口是解析残缺的假象）",
                [("1", "alpha.py", True), ("2", "", True), ("3", "", True)],
                {"alpha.py": 1}, {"N0"}),
    "case-12": ("W3 按全文判「登记过」：名字离项号远也不算没账",
                [("1", "alpha.py", True), ("2", "tau.py", True)],
                {"alpha.py": 1, "tau.py": 1}, set(),
                ["（另见 `tau.py` 的说明——这一行刻意不出现任何项号）"]),
}


def _mk_sandbox(base):
    os.makedirs(base, exist_ok=True)
    return base


def run_case(name, spec, base, checker=None):
    desc, claims, scripts, expect = spec[:4]
    extra_lines = spec[4] if len(spec) > 4 else ()
    d = _mk_sandbox(os.path.join(base, name))
    sd = os.path.join(d, "utils", "audit")
    os.makedirs(sd, exist_ok=True)
    os.makedirs(os.path.join(d, "docs"), exist_ok=True)
    lines = ["# DOCS_PLAN", ""]
    for num, script, claimed in claims:
        if not num:
            lines.append("（本用例没有任何带脚本名的声明）")
            continue
        verb = "新立并结清" if claimed else "未落盘"
        if script:
            lines.append(f"- [x] 存量整理任务：**第 {num} 项巡检** `{script}` {verb}（用例 {name}）")
        else:
            lines.append(f"- [x] 存量整理任务：**第 {num} 项** {verb}（用例 {name}，本行无脚本名）")
    lines.extend(extra_lines)
    with open(os.path.join(d, "DOCS_PLAN.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    for fn, n in scripts.items():
        for i in range(n):
            with open(os.path.join(sd, fn), "w", encoding="utf-8", newline="\n") as f:
                f.write(f"# fixture {fn} {i}\n")
    checker = checker or check
    got = {f[0] for f in checker(d)}
    ok = got == expect
    return desc, sorted(expect), sorted(got), ok


def case_external(base):
    """外部脚本家用例：脚本只在仓库外时必须**不算缺失**，且去掉该目录后必须**立刻报 E2**。

    这一条锁定的是第一版最大的失真：只扫 `utils/audit` + `utils` 时，
    `judgerefcheck.py`（第 39 项，历史名）、`judgecountcheck.py`（第 45 项，历史名）明明在技能家里
    却被判「找不到」——**误报会把真缺陷淹掉**，所以必须双向断言。
    """
    name = "case-13-external"
    d = _mk_sandbox(os.path.join(base, name))
    os.makedirs(os.path.join(d, "utils", "audit"), exist_ok=True)
    os.makedirs(os.path.join(d, "docs"), exist_ok=True)
    with open(os.path.join(d, "DOCS_PLAN.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# DOCS_PLAN\n\n- [x] 存量整理任务：**第 1 项巡检** `omega.py` 新立并结清\n")
    ext = os.path.join(base, name + "-skills")
    os.makedirs(ext, exist_ok=True)
    with open(os.path.join(ext, "omega.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# fixture omega.py\n")
    with_ext = {f[0] for f in check(d, [ext])}
    without = {f[0] for f in check(d)}
    ok = with_ext == set() and "E2" in without
    print(f"{'PASS' if ok else 'FAIL'} {name}: 外部脚本家计入脚本家  计入={sorted(with_ext)} 不计入={sorted(without)}")
    return 1 if ok else 0


def selftest():
    # 沙箱放系统临时目录：写进 `utils/audit/` 会污染工作区（一堆未跟踪目录），
    # 也会让 `git status` 分不清「真新增」与「自测残留」。
    base = tempfile.mkdtemp(prefix="auditman_cases_")
    passed = 0
    for name in sorted(CASES):
        desc, expect, got, ok = run_case(name, CASES[name], base)
        print(f"{'PASS' if ok else 'FAIL'} {name}: {desc}  期望={expect} 实际={got}")
        passed += 1 if ok else 0
    passed += case_external(base)
    total = len(CASES) + 1
    print(f"selftest {passed}/{total}")
    return 0 if passed == total else 1


MUTANTS = [
    ("M1 关掉 E2（脚本存在性不判）", "E2", {"case-02", "case-10"}),
    ("M2 关掉 E3（同号冲突不判）", "E3", {"case-03"}),
    ("M3 关掉 W1（多号登记不判）", "W1", {"case-04", "case-10"}),
    ("M4 关掉 W2（缺口不判）", "W2", {"case-06"}),
    ("M5 关掉 W3（未登记脚本不判）", "W3", {"case-07", "case-10"}),
    ("M6 关掉 E1（活性判据不判）", "E1", {"case-08"}),
    ("M7 关掉 N0（覆盖率门控不判，W2 就会在残缺数据上乱报）", "N0", {"case-11"}),
]


def mutate():
    """逐个关掉一条判据，期望「失败用例集合恰好等于该判据的用例集合」。"""
    import types
    base = tempfile.mkdtemp(prefix="auditman_mut_")
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    src = src.split("# ------------------------------------------------------------------ 自测")[0]
    fails = 0
    for label, code, expect in MUTANTS:
        mod = types.ModuleType("mut")
        exec(compile(src, "mut", "exec"), mod.__dict__)
        orig = mod.check

        def patched(root, extra_dirs=(), _code=code, _orig=orig):
            return [f for f in _orig(root, extra_dirs) if f[0] != _code]

        mod.check = patched
        failed = set()
        for name in sorted(CASES):
            desc, exp, got, ok = run_case(name, CASES[name], os.path.join(base, code), mod.check)
            if not ok:
                failed.add(name)
        good = failed == expect
        print(f"{'OK  ' if good else 'FAIL'} {label} → 失败集合={sorted(failed)} 期望={sorted(expect)}")
        fails += 0 if good else 1
    print(f"mutate {len(MUTANTS) - fails}/{len(MUTANTS)}")
    return 0 if fails == 0 else 1


def main(argv):
    root = "."
    extra = []
    show = False
    it = iter(argv)
    for a in it:
        if a == "--root":
            root = next(it, ".")
        elif a == "--extra-scripts":
            extra.append(next(it, ""))
        elif a == "--list":
            show = True
        elif a == "--selftest":
            return selftest()
        elif a == "--mutate":
            return mutate()
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print(f"unknown arg: {a}", file=sys.stderr)
            return 2

    findings = check(root, extra)
    e = [f for f in findings if f[0].startswith("E")]
    w = [f for f in findings if f[0].startswith("W")]
    n = [f for f in findings if f[0].startswith("N")]
    print(f"root={os.path.abspath(root)}")
    print(f"E={len(e)} W={len(w)} N={len(n)}")
    if show:
        for code, kind, msg in findings:
            print(f"  {code} {kind}: {msg}")
    else:
        for code, kind, msg in e[:10]:
            print(f"  {code} {kind}: {msg}")
    for code, kind, msg in n:
        print(f"  注 {code} {kind}: {msg}")
    print("RESULT:", "FAIL" if e else "PASS")
    return 1 if e else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
