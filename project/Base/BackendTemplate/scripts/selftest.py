#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`run-gates.py` 的自测：对运行器本身做变异测试。

为什么自测要写这么多「故意弄坏」
--------------------------------
运行器的职责是「把该红的弄红」。所以它的自测不能是「跑一遍看看输出好不好看」，
而必须是**变异测试**：把一道门禁的期望退出码改坏、让一道门禁超时、把 id 改重复、
把一条假命令塞进文档——然后断言运行器**确实报了红**。

「生成后 --check 通过」这类断言跑了等于没跑，因为它在正确实现和空实现下都会通过。
本文件里每一处 `_mutate` 开头的小节，都是在回答同一个问题：
**把这块弄坏，工具会不会告诉我？**

同时它自己也是 `gates.json` 里的第 12 道门禁（id=`gates-selftest`）——
运行器错了，上面十一条全是摆设，所以运行器的自测必须和它一起跑。

用法：python3 scripts/selftest.py   （期望：selftest: N/N 通过）
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

_spec = importlib.util.spec_from_file_location("run_gates", HERE / "run-gates.py")
rg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rg)

passed = 0
total = 0


def check(name: str, cond: bool) -> None:
    global passed, total
    total += 1
    if cond:
        passed += 1
        print(f"  ok  {name}")
    else:
        print(f"FAIL  {name}")


# --------------------------------------------------------------------------- 夹具
REAL = json.loads((HERE / "gates.json").read_text(encoding="utf-8"))
DOC = (ROOT / "index.md").read_text(encoding="utf-8")

TINY_GATES = [
    dict(id="g1", name="甲", why="甲的理由", cmd="{py} -c \"print(1)\"", owner="研发",
         required=True, timeoutSec=60, weight=3, doc=True),
    dict(id="g2", name="乙", why="乙的理由", cmd="{py} -c \"print(2)\"", owner="研发",
         required=True, timeoutSec=60, weight=1, doc=True),
]
TINY_DOC = """# 演示

## 本地运行（快速上手）

```shell
{py} -c "print(1)"     # 期望：输出 1
{py} -c "print(2)"     # 期望：输出 2
```

## 参考资料
"""


def mutate(fn) -> dict:
    """返回被改坏的一份 gates.json 副本。"""
    d = copy.deepcopy(REAL)
    fn(d)
    return d


def mutate_gates(fn) -> list:
    """同上，但只取 gates 数组（check_doc_drift 的入参是列表）。"""
    return mutate(fn)["gates"]


def reasons(errors: list) -> str:
    return " | ".join(errors)


# --------------------------------------------------------------------------- 1 命令归一化
print("1. 命令归一化（占位符与注释）")
check("01 行尾注释不参与比对",
      rg.norm_tokens('python3 x.py   # 期望：OK') == ["python3", "x.py"])
check("02 {py} 与 python3 视为同义",
      rg.norm_tokens("{py} x.py") == rg.norm_tokens("python3 x.py"))
check("03 文档里的中文占位符当通配符",
      rg.norm_tokens("python3 t.py --sha <40位git sha> --channel prod")
      == ["python3", "t.py", "--sha", "*", "--channel", "prod"])
check("04 带空格的占位符整体归一为单个 *（不会撑出多余 token）",
      len(rg.norm_tokens("<a b c d>")) == 1)
check("05 通配符匹配具体值",
      rg._tokens_match(rg.norm_tokens("python3 a.py --sha <sha>"),
                       rg.norm_tokens("python3 a.py --sha 0123")))
check("06 参数不同则不等",
      not rg._tokens_match(rg.norm_tokens("python3 a.py --check"),
                           rg.norm_tokens("python3 a.py")))
check("07 多一个参数即不等（同脚本不同用途必须分别声明）",
      not rg._tokens_match(rg.norm_tokens("python3 a.py --cross --fast"),
                           rg.norm_tokens("python3 a.py --cross")))


# --------------------------------------------------------------------------- 2 载入与 schema
print("2. gates.json 载入与 schema 校验（损坏必须是 FAIL 而不是异常）")
with tempfile.TemporaryDirectory() as td:
    bad = Path(td) / "bad.json"
    bad.write_text('{"schemaVersion": 1, "gates": [ }', encoding="utf-8")
    data, errs = rg.load_gates(bad)
    check("08 JSON 损坏时返回错误而不是抛异常", data is None and len(errs) == 1)
    check("09 损坏错误里带行号列号（否则人不知道去哪修）", "行" in errs[0] and "列" in errs[0])
    missing = Path(td) / "none.json"
    d2, e2 = rg.load_gates(missing)
    check("10 文件不存在时报错", d2 is None and "不存在" in e2[0])

check("11 真实 gates.json 载入成功", rg.load_gates()[0] is not None)
check("12 真实 gates.json schema 校验通过", rg.validate(REAL) == [])
check("13 schemaVersion 不对时报错",
      any("schemaVersion" in e for e in rg.validate(mutate(lambda d: d.update(schemaVersion=2)))))
check("14 缺字段被点名到具体字段",
      any(".timeoutSec: 缺少必填字段" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].pop("timeoutSec")))))
check("15 required 写成字符串 \"true\" 会被拦（这种写法不生效且很难看出来）",
      any("必须是布尔值" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(required="true")))))
check("16 timeoutSec 为 0 被拦（0 会让「慢」与「死」分不清）",
      any("timeoutSec" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(timeoutSec=0)))))
check("17 weight 为负数被拦",
      any("weight" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(weight=-1)))))
check("18 kind 取值非法被拦",
      any("kind" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(kind="whatever")))))
check("19 id 重复被点名（id 是 --only 与报告的键）",
      any("重复" in e
          for e in rg.validate(mutate(lambda d: d["gates"][1].update(id=d["gates"][0]["id"])))))
check("20 canary 的 expectRc 为 0 被拦（哨兵「变绿是好消息」就不是哨兵）",
      any("canary" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(kind="canary", expectRc=0)))))
check("21 无法替换的占位符被拦（否则会原样传给 shell 然后莫名失败）",
      any("占位符" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(cmd="{py} x.py <UNKNOWN>")))))
check("22 gates 为空数组被拦（没人跑的清单等于没有清单）",
      any("为空" in e for e in rg.validate({"schemaVersion": 1, "gates": []})))
check("23 顶层是数组时给出类型而不是崩",
      any("必须是对象" in e for e in rg.validate([])))
check("24 真实清单里至少有一条 canary（哨兵机制被真的用上了，不是摆设）",
      any(g.get("kind") == "canary" for g in REAL["gates"]))


# --------------------------------------------------------------------------- 3 防漂移断言
print("3. 文档防漂移断言（含变异测试）")
check("25 真实文档与真实清单一致", rg.check_doc_drift(REAL["gates"], DOC) == [])
check("26 变异：把一条门禁的命令改成文档里没有的 → 必须报红",
      len(rg.check_doc_drift(
          mutate_gates(lambda d: d["gates"][0].update(
              cmd="{py} stack-select/stack-select.py --check --extra")),
          DOC)) == 1)
check("26b 变异：把一条门禁的参数改掉（同脚本、同 --check，只多一个参数）→ 必须报红",
      len(rg.check_doc_drift(
          mutate_gates(lambda d: d["gates"][0].update(
              cmd="{py} stack-select/stack-select.py --root . --check --strict")),
          DOC)) == 1)
check("27 变异：新增一条 doc=true 的门禁但不写进文档 → 必须报红",
      len(rg.check_doc_drift(
          REAL["gates"] + [dict(id="ghost", name="幽灵", why="x", cmd="{py} ghost.py",
                                owner="研发", required=True, timeoutSec=10, weight=1, doc=True)],
          DOC)) == 1)
check("28 变异：文档里有命令但擦掉期望结果 → 必须报红（只给命令不给期望等于让下一个人猜）",
      len(rg.check_doc_drift(TINY_GATES, TINY_DOC.replace("# 期望：输出 1", "# 无"))) == 1)
check("29 缺少「本地运行」小节时明确报错而不是静默通过",
      any("找不到小节" in e for e in rg.check_doc_drift(REAL["gates"], "# 只有标题\n")))
check("30 自洽的迷你样本通过", rg.check_doc_drift(TINY_GATES, TINY_DOC) == [])
check("31 doc=false 的门禁不参与断言（它是 CI 专属，不该逼着写进快速上手）",
      rg.check_doc_drift([dict(id="ci", name="n", why="w", cmd="{py} ci.py", owner="x",
                               required=True, timeoutSec=10, weight=1, doc=False)], DOC) == [])


# --------------------------------------------------------------------------- 4 前置条件
print("4. 前置条件判定（BLOCKED 不是 PASS）")
check("32 缺前置文件时报 BLOCKED 且说明原因",
      "pom.xml" in (rg.blocked_reason(dict(requiresFiles=["pom.xml"])) or ""))
check("33 PATH 里没有的命令报 BLOCKED",
      "PATH" in (rg.blocked_reason(dict(requiresExec=["definitely-not-a-real-cmd-xyz"])) or ""))
check("34 环境变量未设置报 BLOCKED",
      "未设置" in (rg.blocked_reason(dict(requiresEnv=["GATES_SELFTEST_NOPE"])) or ""))
_prev = os.environ.get("GATES_SELFTEST_NOPE")
os.environ["GATES_SELFTEST_NOPE"] = "1"
check("35 环境变量已设置则放行", rg.blocked_reason(dict(requiresEnv=["GATES_SELFTEST_NOPE"])) is None)
if _prev is None:
    os.environ.pop("GATES_SELFTEST_NOPE", None)
check("36 无前置条件时放行", rg.blocked_reason({}) is None)
check("37 真实清单里 mvn-verify 声明了 JAVA_HOME 前置"
      "（本机实测 mvn 在 PATH 里但 JAVA_HOME 没设时直接报错，"
      "可见只查命令存在性不够）",
      [g for g in REAL["gates"] if g["id"] == "mvn-verify"][0].get("requiresEnv") == ["JAVA_HOME"])


# --------------------------------------------------------------------------- 5 分片
print("5. 分片（贪心装箱，让各片耗时接近）")
_sh = [dict(id=f"s{i}", name="n", why="w", cmd="x", owner="o", required=True,
            timeoutSec=10, weight=w, doc=False)
       for i, w in enumerate([10, 8, 6, 4, 2, 1])]
_s1, _s2 = rg.shard_gates(_sh, 1, 2), rg.shard_gates(_sh, 2, 2)
check("38 分片不丢也不重",
      sorted(g["id"] for g in _s1 + _s2) == sorted(g["id"] for g in _sh))
check("39 最重的两条不在同一片（取模分片恰好会犯这个错）",
      not ({"s0", "s1"} <= {g["id"] for g in _s1} or {"s0", "s1"} <= {g["id"] for g in _s2}))
check("40 两片权重接近（差值不超过最重的一条）",
      abs(sum(g["weight"] for g in _s1) - sum(g["weight"] for g in _s2)) <= 10)
check("41 N=1 时原样返回", rg.shard_gates(_sh, 1, 1) == _sh)


# --------------------------------------------------------------------------- 6 执行语义
print("6. 执行语义（退出码期望、哨兵、超时）")
with tempfile.TemporaryDirectory() as td:
    logdir = Path(td) / "logs"
    ok = rg.run_one(dict(id="ok", name="n", why="w", cmd="{py} -c \"print('hi')\"",
                         owner="o", required=True, timeoutSec=60, weight=1, doc=False),
                    "0" * 40, sys.executable, logdir)
    check("42 退出码符合期望判 PASS", ok["status"] == "PASS" and ok["rc"] == 0)
    check("43 全量输出落盘（终端只留尾部，全量去日志里翻）",
          (logdir / "ok.log").read_text(encoding="utf-8").strip() == "hi")

    bad = rg.run_one(dict(id="bad", name="n", why="w", cmd="{py} -c \"raise SystemExit(3)\"",
                          owner="o", required=True, timeoutSec=60, weight=1, doc=False),
                     "0" * 40, sys.executable, None)
    check("44 退出码不符判 FAIL", bad["status"] == "FAIL" and bad["rc"] == 3)
    check("45 FAIL 的说明里同时给出实际与期望退出码",
          "3" in bad["note"] and "0" in bad["note"])

    exp = rg.run_one(dict(id="exp", name="n", why="w", cmd="{py} -c \"raise SystemExit(1)\"",
                          owner="o", required=True, timeoutSec=60, weight=1,
                          expectRc=1, doc=False), "0" * 40, sys.executable, None)
    check("46 expectRc=1 且真返回 1 → PASS（期望为红是合法状态）", exp["status"] == "PASS")

    canary_red = rg.run_one(dict(id="c1", name="n", why="w", cmd="{py} -c \"raise SystemExit(1)\"",
                                 owner="o", required=True, timeoutSec=60, weight=1,
                                 expectRc=1, kind="canary", doc=False), "0" * 40, sys.executable, None)
    check("47 哨兵返回 expectRc（=1）→ PASS（预期为红就是合规，不是失败）",
          canary_red["status"] == "PASS")
    canary_green = rg.run_one(dict(id="c2", name="n", why="w", cmd="{py} -c \"pass\"",
                                   owner="o", required=True, timeoutSec=60, weight=1,
                                   expectRc=1, kind="canary", doc=False), "0" * 40, sys.executable, None)
    check("48 哨兵变绿（返回 0）→ FAIL，且说明里点名「哨兵变绿」",
          canary_green["status"] == "FAIL" and "哨兵变绿" in canary_green["note"])
    canary_other = rg.run_one(dict(id="c3", name="n", why="w",
                                   cmd="{py} -c \"raise SystemExit(2)\"",
                                   owner="o", required=True, timeoutSec=60, weight=1,
                                   expectRc=1, kind="canary", doc=False),
                              "0" * 40, sys.executable, None)
    check("48b 哨兵返回第三种退出码 → FAIL，但说明是「退出码不符」而不是误报「变绿」",
          canary_other["status"] == "FAIL" and "哨兵变绿" not in canary_other["note"])

    to = rg.run_one(dict(id="to", name="n", why="w",
                         cmd="{py} -c \"import time; time.sleep(20)\"",
                         owner="o", required=True, timeoutSec=2, weight=1, doc=False),
                    "0" * 40, sys.executable, None)
    check("49 超时判 TIMEOUT 而不是 FAIL（慢与死要能分开）",
          to["status"] == "TIMEOUT" and "2s" in to["note"])
    check("50 超时项也给出耗时（判断是死循环还是只差一点）", to["elapsedSec"] >= 2)

print("7. 每道门禁只起一个子进程（回归：曾把取值函数调两遍，真跑两遍子进程）")
_calls = {"n": 0}
_real_run = rg.subprocess.run


def _spy(*a, **kw):
    _calls["n"] += 1
    return _real_run([sys.executable, "-c", "print('once')"], stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT, timeout=30)


rg.subprocess.run = _spy
try:
    _r = rg.run_one(dict(id="once", name="n", why="w", cmd="{py} -c \"print('once')\"",
                         owner="o", required=True, timeoutSec=60, weight=1, doc=False),
                    "0" * 40, sys.executable, None)
finally:
    rg.subprocess.run = _real_run
check("51 一次 run_one 只起一个子进程", _calls["n"] == 1)
check("52 该次结果为 PASS（spy 不能改变语义）", _r["status"] == "PASS")


# --------------------------------------------------------------------------- 8 指纹
print("8. 命令集合指纹（回答「当时跑的是哪几条命令」）")
ra = [dict(id="a", cmd="python3 x.py"), dict(id="b", cmd="python3 y.py")]
rb = [dict(id="a", cmd="python3 x.py"), dict(id="b", cmd="python3 y.py --check")]
check("53 命令相同则指纹相同", rg.digest_of(ra) == rg.digest_of(list(ra)))
check("54 改一个参数指纹就变（清单是数据，改了清单不必改代码，版本号回答不了这个问题）",
      rg.digest_of(ra) != rg.digest_of(rb))
check("55 指纹是固定长度短串", len(rg.digest_of(ra)) == 16)


# --------------------------------------------------------------------------- 9 端到端
print("9. 端到端（命令行）")
_rc = rg.main(["--check"])
check("56 main(['--check']) 在真实仓库上返回 0", _rc == 0)
_rc = rg.main(["--list"])
check("57 main(['--list']) 返回 0", _rc == 0)
_rc = rg.main(["--only", "no-such-gate"])
check("58 --only 写了不存在的 id 时返回 1（静默跑 0 条是最坏的结果）", _rc == 1)
_rc = rg.main(["--shard", "5/2"])
check("59 --shard 越界时返回 1", _rc == 1)
with tempfile.TemporaryDirectory() as td:
    rp = Path(td) / "r.json"
    # 注意这里**不能**选 gates-selftest：那道门禁跑的就是本文件，选中它等于递归自己。
    # 第一版自测真的这么写了，结果是跑到超时被 SIGTERM 杀掉——
    # 于是运行器补了嵌套保护（NEST_ENV + nestSafe），见下面第 65~67 条。
    _rc = rg.main(["--only", "db-parity,db-selftest", "--json", str(rp),
                   "--log-dir", str(Path(td) / "logs"), "--quiet", "--allow-blocked"])
    rep = json.loads(rp.read_text(encoding="utf-8"))
    check("60 JSON 报告写出且含 digest / sha / results", "digest" in rep and "results" in rep)
    check("61 报告里每条含 id/status/rc/elapsedSec/cmd（否则事后无法复盘）",
          all({"id", "status", "rc", "elapsedSec", "cmd"} <= set(x) for x in rep["results"]))
    check("62 --only 下只跑选中的两条", sorted(x["id"] for x in rep["results"]) == ["db-parity", "db-selftest"])
    check("63 两条都通过时返回 0", _rc == 0)
    _rc = rg.main(["--only", "acceptance-strict-canary", "--quiet"])
    check("64 哨兵单独跑时返回 0（它返回 1 是符合期望）", _rc == 0)


# --------------------------------------------------------------------------- 9b 嵌套保护
print("9b. 嵌套保护（门禁 → 自测 → 运行器 会成环，运行器必须认得出自己）")
check("65 真实清单里 gates-selftest 标了 nestSafe=false",
      [g for g in REAL["gates"] if g["id"] == "gates-selftest"][0].get("nestSafe") is False)
check("66 nestSafe 写成字符串会被 schema 拦下",
      any("nestSafe" in e
          for e in rg.validate(mutate(lambda d: d["gates"][0].update(nestSafe="no")))))
os.environ[rg.NEST_ENV] = "1"
try:
    check("67 嵌套第 1 层时 depth 读得到", rg.nest_depth() == 1)
    _n = rg.run_one(dict(id="ns", name="n", why="w", cmd="{py} -c \"print('hit')\"",
                         owner="o", required=True, timeoutSec=60, weight=1,
                         nestSafe=False, doc=False), "0" * 40, sys.executable, None)
    check("68 run_one 不知道 nestSafe（保护做在 main 的分发层，不在执行层）",
          _n["status"] == "PASS")
    _rc = rg.main(["--only", "gates-selftest", "--quiet"])
    check("69 嵌套下选中 gates-selftest → 判 BLOCKED 并返回 1，而不是无限 fork",
          _rc == 1 and rg.nest_depth() == 1)
    _rc2 = rg.main(["--only", "gates-selftest", "--quiet", "--allow-blocked"])
    check("70 --allow-blocked 时它才被放过（放宽必须是人写的）", _rc2 == 0)
finally:
    os.environ.pop(rg.NEST_ENV, None)
check("71 非嵌套环境下 depth 为 0", rg.nest_depth() == 0)


# --------------------------------------------------------------------------- 10 真实的「预期为红」
print("10. 真实的「预期为红」（默认不放宽，放宽要写出来）")
# 本仓库没有 pom.xml 与 JAVA_HOME，两条依赖真实源码树/工具链的门禁必须是 BLOCKED。
reasons_txt = reasons([rg.blocked_reason(g) or "" for g in REAL["gates"]])
check("65 本仓库下确实存在 BLOCKED 项（否则本节的断言是空跑）",
      any(rg.blocked_reason(g) for g in REAL["gates"]))
check("66 BLOCKED 的原因可读（说明缺什么，而不是一句 fail）",
      "pom.xml" in reasons_txt)
_rc_blocked = rg.main(["--only", "stack-select-check", "--quiet"])
check("67 默认下 BLOCKED 让运行器返回 1（默认不放过任何非 PASS）", _rc_blocked == 1)
_rc_ok = rg.main(["--only", "stack-select-check", "--quiet", "--allow-blocked"])
check("68 显式 --allow-blocked 才返回 0", _rc_ok == 0)
_rc_skip = rg.main(["--skip", "stack-select-check,mvn-verify", "--quiet", "--allow-blocked",
                    "--only", "db-parity"])
check("69 --skip 生效", _rc_skip == 0)


# --------------------------------------------------------------------------- 收尾
print("")
print(f"selftest: {passed}/{total} 通过")
sys.exit(0 if passed == total else 1)
