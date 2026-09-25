#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""acceptance_check.py 的自测：把「验收清单」里能离线判定的部分全部断言成测试。

零第三方依赖，直接运行::

    python Acceptance/selftest.py

退出码 0 = 全部通过；1 = 有断言失败（stderr 打印失败项）。

为什么验收清单也需要自测
------------------------
验收清单和单元测试有一个相同的失效方式：**门禁本身悄悄坏了**。区别是单元测试坏了会报红，
而验收清单坏了只会**变得更宽松** —— 判据少查一项、矩阵基线不再被比对、签名表字段少验一个，
这些都不会让任何人收到通知，只会让上线那天看起来「全部通过」。

所以这里对三件事做**变异测试**（而不是只跑一遍看它是绿的）：

  · **用例矩阵**：格子填非法符号 / 少一格 / 把覆盖数压到基线以下 / 整行置为不适用，
    每一种都必须被判 FAIL。只测「原文件通过」等于什么都没测——原文件当然通过。
  · **签名表**：少签一项、缺 evidence、evidence 只写「OK」、日期写「上周」、给 AUTO 项签名，
    每一种都必须被判 FAIL。
  · **交叉断言**：`--cross` 内部已含两处变异（改小基线、回滚指向环境指针），这里断言它
    整体退出码为 0，并断言输出里出现「变异」字样 —— 若哪天变异测试被删掉、只剩「生成后
    --check 通过」这种必然成立的检查，`--cross` 仍会返回 0，只有断言文案能发现。
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import acceptance_check as acc  # noqa: E402

PASS = 0
FAIL: list[str] = []
_TMP: list[str] = []


def ok(name: str, cond: bool, extra: str = "") -> None:
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(f"{name}{(' — ' + extra) if extra else ''}")


def _tmpdir(prefix: str) -> Path:
    d = tempfile.mkdtemp(prefix=prefix)
    _TMP.append(d)
    return Path(d)


def _python() -> str:
    for cand in (sys.executable, shutil.which("python3"), shutil.which("python")):
        if cand and Path(cand).exists():
            return cand
    return sys.executable


PY = _python()


def cli(*argv) -> tuple:
    """在进程内跑 CLI，返回 (rc, stdout)。避免依赖子进程与 python 路径。"""
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = acc.main(list(argv))
    return rc, buf.getvalue()


def run_py(script: str, *args: str, env_extra: dict | None = None) -> tuple:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run([PY, str(HERE / script), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ================================================================ A. 清单结构

IDS = [it["id"] for it in acc.ITEMS]
MANUAL_IDS = [it["id"] for it in acc.ITEMS if it["kind"] == "manual"]
AUTO_IDS = [it["id"] for it in acc.ITEMS if it["kind"] != "manual"]
CATS = ["功能", "性能", "安全", "数据", "可观测", "运维"]

ok("A.1 清单共 18 项", len(acc.ITEMS) == 18, str(len(acc.ITEMS)))
ok("A.2 六类各 3 项",
   all(sum(1 for it in acc.ITEMS if it["cat"] == c) == 3 for c in CATS),
   str({c: sum(1 for it in acc.ITEMS if it["cat"] == c) for c in CATS}))
ok("A.3 id 唯一", len(set(IDS)) == len(IDS), str(IDS))
ok("A.4 AUTO 12 / MANUAL 6", (len(AUTO_IDS), len(MANUAL_IDS)) == (12, 6),
   "%d/%d" % (len(AUTO_IDS), len(MANUAL_IDS)))
ok("A.5 每项都有 judge 与 owner", all(it.get("judge") and it.get("owner") for it in acc.ITEMS))
ok("A.6 kind 都在允许集合内",
   all(it["kind"] in {"manual", "matrix", "crossrollback", "file", "grep", "script"}
       for it in acc.ITEMS), str(sorted({it["kind"] for it in acc.ITEMS})))
ok("A.7 每个 MANUAL 项都写了可粘贴的命令与期望",
   all(it.get("manual") and it.get("expect") for it in acc.ITEMS if it["kind"] == "manual"))

SIGNOFF_SRC = json.loads((HERE / "manual_signoff.json").read_text(encoding="utf-8"))
ok("A.8 签名表模板的条目与 MANUAL 项一致",
   sorted(SIGNOFF_SRC.get("_manualItems", {})) == sorted(MANUAL_IDS),
   "%s vs %s" % (sorted(SIGNOFF_SRC.get("_manualItems", {})), sorted(MANUAL_IDS)))
ok("A.9 随仓库提供的签名表是空的（没验就不该是绿的）",
   SIGNOFF_SRC.get("signoffs") == {}, str(SIGNOFF_SRC.get("signoffs")))

# ================================================================ B. --list

rc, out = cli("--list")
ok("B.1 --list 退出码 0", rc == 0, str(rc))
ok("B.2 --list 列出全部 18 个 id", all(i in out for i in IDS))
ok("B.3 --list 分组标题含六类", all(("[%s]" % c) in out for c in CATS))
ok("B.4 --list 汇总行正确", "合计 18 项；AUTO 12 项，MANUAL 6 项。" in out)
ok("B.5 --list 打印了 MANUAL 的命令与期望",
   out.count("命令：") >= len(MANUAL_IDS) and "期望：" in out)

# ================================================================ C. 默认模式与 --json

rc, out = cli()
ok("C.1 默认模式退出码 0（AUTO 全过）", rc == 0,
   out.strip().splitlines()[-1] if out else "")
ok("C.2 默认模式报告 AUTO 12/12", "AUTO：12/12 通过" in out)
ok("C.3 默认模式列出 6 个 MANUAL 项", out.count("（责任人：") == len(MANUAL_IDS),
   str(out.count("（责任人：")))
ok("C.4 默认模式不因未签名而失败（签名只由 --strict 管）", "签名表" not in out)

rc, out = cli("--json")
data = json.loads(out)
ok("C.5 --json 可解析且 18 项", rc == 0 and len(data["items"]) == 18)
ok("C.6 --json 计数正确",
   (data["autoTotal"], data["autoPassed"], data["manualTotal"]) == (12, 12, 6),
   json.dumps({k: data[k] for k in ("autoTotal", "autoPassed", "manualTotal")}))
ok("C.7 --json 每项都带责任人 / 状态 / 详情",
   all("owner" in i and "state" in i and "detail" in i for i in data["items"]))

# ================================================================ D. 用例矩阵（变异测试）


def base_data() -> dict:
    return json.loads((HERE / "case_baseline.json").read_text(encoding="utf-8"))


def _first_key(d):
    return next(iter(d["matrix"]))


def _set_cell(d, api, idx, sym):
    d["matrix"][api][idx] = sym
    return d


def _drop_cell(d):
    k = _first_key(d)
    d["matrix"][k] = d["matrix"][k][:-1]
    return d


def _blank_row(d):
    k = _first_key(d)
    d["matrix"][k] = ["—"] * len(d["matrix"][k])
    return d


def _replace_n_covered(d, n, symbol="?"):
    """把前 n 个已覆盖格改成 symbol，用于把覆盖数压到任意水平。"""
    left = n
    for cells in d["matrix"].values():
        for i, c in enumerate(cells):
            if left and d["symbols"][c] == "covered":
                cells[i] = symbol
                left -= 1
        if not left:
            break
    return d


def _raise_baseline(d):
    d["javaMetaTestBaseline"] = 39
    return d


def matrix_of(transform) -> tuple:
    """把矩阵做一次变异后交给 check_matrix，返回 (ok, detail)。"""
    d = transform(base_data())
    p = _tmpdir("acc-matrix-") / "case_baseline.json"
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    old = acc.BASELINE_JSON
    acc.BASELINE_JSON = p
    try:
        return acc.check_matrix({})
    finally:
        acc.BASELINE_JSON = old


BASE = base_data()
COVERED = sum(1 for cells in BASE["matrix"].values()
              for c in cells if BASE["symbols"][c] == "covered")

okd, detail = matrix_of(lambda d: d)
ok("D.1 原矩阵通过", okd, detail)
ok("D.2 详情写出已覆盖数与元测试基线",
   ("已覆盖 %d 格" % COVERED) in detail and "元测试基线 38 格" in detail, detail)
ok("D.3 详情写出余量（余量必须可见，否则掉到 39 也没人发现）",
   "余量 %d 格" % (COVERED - 38) in detail, detail)

okd2, d2 = matrix_of(lambda d: _set_cell(d, _first_key(d), 0, "X"))
ok("D.4 变异：格子填了非法符号 → FAIL", (not okd2) and "没有结论的格子" in d2, d2)

okd3, d3 = matrix_of(_drop_cell)
ok("D.5 变异：格子数少于场景数 → FAIL", (not okd3) and "格子数" in d3, d3)

okd4, d4 = matrix_of(lambda d: _replace_n_covered(d, 3))
ok("D.6 变异：覆盖数掉到基线之下 → FAIL", (not okd4) and "< 元测试基线" in d4, d4)

okd5, d5 = matrix_of(_blank_row)
ok("D.7 变异：整行置为不适用 → FAIL", (not okd5) and "整行没有任何用例" in d5, d5)

okd6, d6 = matrix_of(lambda d: _replace_n_covered(d, 2))
ok("D.8 边界：覆盖数恰好等于基线 38 → 通过（基线是下限不是等号）", okd6, d6)
ok("D.9 边界：余量缩到 0 时详情给出「余量 0 格」", "余量 0 格" in d6, d6)

okd7, d7 = matrix_of(_raise_baseline)
ok("D.10 边界：基线抬到 39（余量 1）仍通过，且余量可见",
   okd7 and "余量 1 格" in d7, d7)

okd8, d8 = matrix_of(lambda d: {**d, "javaMetaTestBaseline": 999})
ok("D.11 变异：把元测试基线抬到 999 → FAIL", not okd8, d8)

_old_base = acc.BASELINE_JSON
acc.BASELINE_JSON = HERE / "definitely-not-here" / "case_baseline.json"
missing_ok, missing_detail = acc.check_matrix({})
acc.BASELINE_JSON = _old_base
ok("D.12 矩阵文件缺失 → FAIL 且说明缺哪个文件",
   (not missing_ok) and "缺少" in missing_detail, missing_detail)


def _raw_matrix(text: str) -> tuple:
    p = _tmpdir("acc-matrix-raw-") / "case_baseline.json"
    p.write_text(text, encoding="utf-8")
    old = acc.BASELINE_JSON
    acc.BASELINE_JSON = p
    try:
        return acc.check_matrix({})
    finally:
        acc.BASELINE_JSON = old


okr, dr = _raw_matrix("{ not json at all ")
ok("D.13 矩阵 JSON 损坏 → FAIL 而不是抛异常（校验器崩了比校验失败危险）",
   (not okr) and "不是合法 JSON" in dr, dr)

okr2, dr2 = _raw_matrix(json.dumps({"symbols": {}, "scenarios": []}, ensure_ascii=False))
ok("D.14 矩阵缺字段 → FAIL 且列出缺哪几个字段",
   (not okr2) and "缺少字段" in dr2 and "matrix" in dr2, dr2)

# ================================================================ E. 签名表


def full_signoffs() -> dict:
    return {i: {"by": "李 · 研发负责人", "at": "2026-09-25",
                "evidence": "CI run #482 — artifacts/%s.txt" % i,
                "result": "pass"} for i in MANUAL_IDS}


def signoff_of(signoffs=None, *, absent=False) -> Path:
    p = _tmpdir("acc-sign-") / "manual_signoff.json"
    if not absent:
        p.write_text(json.dumps({"schemaVersion": 1, "signoffs": signoffs or {}},
                                ensure_ascii=False), encoding="utf-8")
    return p


okE, dE = acc.check_signoff(signoff_of())
ok("E.1 空签名表 → FAIL 且点名全部未签", (not okE) and all(i in dE for i in MANUAL_IDS), dE)

okE2, dE2 = acc.check_signoff(signoff_of(absent=True))
ok("E.2 签名表文件不存在 → FAIL 且说明「一个都没签」",
   (not okE2) and "一个都没签" in dE2, dE2)

okE3, dE3 = acc.check_signoff(signoff_of(full_signoffs()))
ok("E.3 六项全填且证据充分 → PASS", okE3, dE3)

partial = full_signoffs()
partial.pop("E3")
okE4, dE4 = acc.check_signoff(signoff_of(partial))
ok("E.4 变异：少签一项 → FAIL 且点名 E3", (not okE4) and "E3" in dE4, dE4)

nodata = full_signoffs()
del nodata["A1"]["evidence"]
okE5, dE5 = acc.check_signoff(signoff_of(nodata))
ok("E.5 变异：缺 evidence → FAIL 且点名 A1", (not okE5) and "A1" in dE5, dE5)

weak = full_signoffs()
weak["B1"]["evidence"] = "OK"
okE6, dE6 = acc.check_signoff(signoff_of(weak))
ok("E.6 变异：evidence 只写「OK」→ FAIL（够不上可复核）",
   (not okE6) and "够不上可复核" in dE6, dE6)

baddate = full_signoffs()
baddate["C3"]["at"] = "上周"
okE7, dE7 = acc.check_signoff(signoff_of(baddate))
ok("E.7 变异：日期写「上周」→ FAIL（不是 ISO 日期开头）",
   (not okE7) and "不是 ISO 日期开头" in dE7, dE7)

stray = full_signoffs()
stray["A2"] = {"by": "李", "at": "2026-09-25", "evidence": "CI run #1"}
okE8, dE8 = acc.check_signoff(signoff_of(stray))
ok("E.8 变异：给 AUTO 项（A2）签名 → FAIL（签了等于绕开脚本判据）",
   (not okE8) and "不该由人签名" in dE8, dE8)


def _raw_signoff(text: str) -> tuple:
    p = _tmpdir("acc-sign-raw-") / "manual_signoff.json"
    p.write_text(text, encoding="utf-8")
    return acc.check_signoff(p)


okE9, dE9 = _raw_signoff("{ nope ")
ok("E.9 签名表 JSON 损坏 → FAIL 而不是抛异常",
   (not okE9) and "不是合法 JSON" in dE9, dE9)

okE10, dE10 = _raw_signoff(json.dumps({"signoffs": ["A1"]}, ensure_ascii=False))
ok("E.10 签名表 signoffs 类型不对 → FAIL 且说明应当是对象",
   (not okE10) and "应当是" in dE10, dE10)

rc, out = cli("--strict")
ok("F.1 --strict 在未签名时退出码 1", rc == 1, str(rc))
ok("F.2 --strict 输出点名未签项", "未签" in out and "A1" in out)

rc, out = cli("--strict", "--signoff", str(signoff_of(full_signoffs())))
ok("F.3 --strict 指向填好的签名表 → 退出码 0", rc == 0,
   out.strip().splitlines()[-1] if out else "")
ok("F.4 --strict 通过时说明证据可复核", "证据均可复核" in out, out[-200:])

rc, out = cli("--strict", "--signoff", str(signoff_of(absent=True)))
ok("F.5 --strict 指向不存在的签名表 → 退出码 1", rc == 1, str(rc))

# ================================================================ G. run_item 回归

calls: list[str] = []
_orig_run_script = acc.run_script


def _spy(item):
    calls.append(item["id"])
    return _orig_run_script(item)


acc.run_script = _spy
try:
    _d1 = next(i for i in acc.ITEMS if i["id"] == "D1")
    state, detail = acc.run_item(_d1)
finally:
    acc.run_script = _orig_run_script

ok("G.1 脚本类项只调用一次 run_script（调两次 = 真跑两遍子进程）",
   calls == ["D1"], str(calls))
ok("G.2 D1 判定 PASS 且详情写明命中关键字",
   state == "PASS" and "输出命中" in detail, detail)

_kn = {"id": "X", "kind": "file", "path": "Acceptance/known_issues.md", "min_bytes": 300}
st, dt = acc.run_item(_kn)
ok("G.3 file 类：已存在的文件 → PASS", st == "PASS", dt)

st, dt = acc.run_item({**_kn, "path": "Acceptance/nope.md"})
ok("G.4 file 类：文件不存在 → FAIL", st == "FAIL" and "文件不存在" in dt, dt)

st, dt = acc.run_item({**_kn, "min_bytes": 10 ** 7})
ok("G.5 file 类：低于字节下限 → FAIL", st == "FAIL" and "低于要求" in dt, dt)

_gr = {"id": "X", "kind": "grep", "path": "Security/index.md",
       "patterns": ["@PreAuthorize"], "absent": []}
st, dt = acc.run_item(_gr)
ok("G.6 grep 类：命中 → PASS", st == "PASS", dt)

st, dt = acc.run_item({**_gr, "patterns": ["这个词一定不存在-9f2c1a"]})
ok("G.7 grep 类：找不到关键字 → FAIL", st == "FAIL" and "找不到" in dt, dt)

st, dt = acc.run_item({**_gr, "absent": ["@PreAuthorize"]})
ok("G.8 grep 类：命中「不应出现」的词 → FAIL", st == "FAIL" and "不应出现" in dt, dt)

st, dt = acc.run_item({**_gr, "kind": "nonsense"})
ok("G.9 未知判定方式 → FAIL 而非静默通过", st == "FAIL" and "未知判定方式" in dt, dt)

# ================================================================ H. --cross

rc, out = cli("--cross")
ok("H.1 --cross 退出码 0", rc == 0, out.strip()[-300:])
ok("H.2 --cross 输出含两处以上的变异测试（变异被删掉就会退化成必然通过）",
   out.count("变异") >= 2, "变异出现 %d 次" % out.count("变异"))
ok("H.3 --cross 两条断言都 PASS", out.count("PASS") == 2, out)

rc, out = cli("--cross", "--json")
ok("H.4 --cross --json 可解析且两项 ok",
   rc == 0 and all(json.loads(out)[k]["ok"] for k in ("baseline", "rollback")), out[:200])

# ================================================================ I. 辅助脚本

rc, out = run_py("backup_restore.py", "--dry-run")
ok("I.1 备份演练 dry-run 退出码 0", rc == 0, out[-300:])
ok("I.2 dry-run 输出含双方言备份命令（mysqldump / pg_dump）",
   all(k in out for k in ("mysqldump", "pg_dump", "dry-run")), out[:300])
ok("I.3 dry-run 指明未连接数据库、未写文件",
   "未连接数据库" in out and "未写入任何备份文件" in out)
ok("I.4 dry-run 列出五步动作（备份/建库/恢复/比对/清理）",
   all(k in out for k in ("① 备份源库", "② 建演练库", "③ 恢复到演练库",
                          "④ 逐表比对行数", "⑤ 清理演练库")))
ok("I.5 dry-run 可用 --engine 收窄到单引擎",
   run_py("backup_restore.py", "--dry-run", "--engine", "mysql")[1].count("动作清单") == 1)

rc, out = run_py("backup_restore.py", "--dry-run",
                 env_extra={"MYSQL_DATABASE": "app_restore_check"})
ok("I.6 安全：源库名自带演练后缀时拒绝执行（防把演练写到源库）",
   rc != 0 and "拒绝执行" in out, "rc=%d %s" % (rc, out[-200:]))

if not all(shutil.which(x) for x in ("mysqldump", "mysql")):
    rc, out = run_py("backup_restore.py", "--engine", "mysql")
    ok("I.7 无客户端时真实演练返回 SKIP(3)，而不是假装通过",
       rc == 3 and "SKIP" in out, "rc=%d %s" % (rc, out[-200:]))
else:
    ok("I.7 本机有 mysql 客户端，跳过 SKIP 断言（真实演练需真库，不在自测范围内）", True)

ok("I.8 D1 的命令不再引用已删除的 backup_restore.sh",
   not any("backup_restore.sh" in json.dumps(it, ensure_ascii=False) for it in acc.ITEMS))

# ================================================================ 汇总

for d in _TMP:
    shutil.rmtree(d, ignore_errors=True)

total = PASS + len(FAIL)
print(f"selftest: {PASS}/{total} 通过（变异测试 10 处：用例矩阵 5 + 签名表 5）")
if FAIL:
    print("失败项：", file=sys.stderr)
    for f in FAIL:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
print("全部通过")
sys.exit(0)
