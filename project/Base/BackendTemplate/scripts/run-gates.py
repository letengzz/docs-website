#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门禁运行器：把「提交前该跑什么」收敛成一份声明，本地与 CI 都从它读。

为什么要有这个文件
------------------
第 79 天把门禁串成了 CI 流水线，第 82 天把验收清单做成了可执行工具。但门禁清单
此刻仍然活在**三个地方**，而且三份都会各自演化：

  1. CI 工作流里的 `run:` 步骤；
  2. 项目总览「本地运行（快速上手）」的 9 步命令；
  3. 各工具自己的 `selftest.py`。

只要它们是三份手抄的清单，漂移就只是时间问题，而漂移的表现恰好是最难查的那一种：
**本地绿、CI 红**——作者本地少跑了一道门禁，直到推上去才知道。所以本步做的是
「单一来源」：门禁写在 `scripts/gates.json` 里，本地、CI、审计三处都读它。

设计上的九个关键取舍
--------------------
1. **声明与执行分离**。门禁是数据，不是代码。`gates.json` 可以被运行器执行、
   被 `--list` 打印、被审计工具消费、被文档核对。任何写死在脚本里的清单，
   第二次修改就会漏一处。

2. **`expectRc` 不一定为 0**。`Acceptance/acceptance_check.py --strict` 在签名表
   为空时**必须**返回 1——那是设计，不是缺陷。这类门禁在这里叫 **canary（哨兵）**：
   它一旦变绿不是好消息，而是警报，说明签名表被填满了（或 MANUAL 项的判定逻辑
   被改坏），必须有人重新拍板。因此哨兵的 `expectRc != 0`，且「变绿」判 FAIL。

3. **三种非通过状态要分清**：`FAIL`（跑了，结果不符合期望）、`BLOCKED`
   （前置条件不具备，**绝不是 PASS**）、`TIMEOUT`（跑不完，同样不是 PASS）。
   实测例证：本机 `mvn` 在 PATH 里，但 `JAVA_HOME` 没设，`mvn -v` 直接报
   `JAVA_HOME environment variable is not defined correctly`。
   ——可见 `requiresExec` 只查「命令在不在」是不够的，必须再配 `requiresEnv`。

4. **默认不放过任何非 PASS**。「本地没有 JDK」这类情况允许放宽，但必须由人显式
   写 `--allow-blocked`，让「这次跑不全」成为一个被记录的决定，而不是一个静默的
   绿勾。默认返回 1 才是正确状态——一份「跑起来全绿」但没人真验过的表格，
   比一份红色的表格危险。

5. **失败不早退**（`--fail-fast` 可选）。跑完所有门禁再汇总：本地跑一遍要几分钟到
   十几分钟，一次只暴露一个问题等于让人把同一段路走 N 遍。

6. **每道门禁必须有 `timeoutSec`**。本机实测 `stack-select/selftest.py` 要几十秒
   （内部要起几十个子进程），`Acceptance/selftest.py` 更久。没有超时的门禁会让
   「慢」和「死」看起来完全一样，而人只会得出一个结论：工具坏了。

7. **失败信息在尾部**。每道只留尾部 N 行（默认 10），全量落 `--log-dir`。
   把几千行进度日志糊在终端上，等于把真正的错误埋掉。

8. **`--check` 是防漂移断言，不是自检**。它断言「文档里写的」与「清单里声明的」
   一致：每条 `"doc": true` 的门禁，其命令必须出现在项目总览的「本地运行
   （快速上手）」小节里，且该行必须写明期望结果。理由是：**没写进快速上手的门禁，
   本地就不会有人跑它**。这条断言自己也被变异测试过（见 `scripts/selftest.py`：
   塞一条假命令进去，`--check` 必须报红）。

9. **`--shard` 用贪心装箱而不是取模**。取模会把最慢的两条分到同一片，于是并行的
   意义刚好被抵消。按 `weight` 从大到小逐一放进当前最轻的一片，才能让各片耗时接近。

用法
----
    python3 scripts/run-gates.py                    # 跑全部门禁，失败即返回 1
    python3 scripts/run-gates.py --list             # 打印清单（判据 + 责任人 + 耗时权重）
    python3 scripts/run-gates.py --check            # 只做 schema 校验 + 文档防漂移断言
    python3 scripts/run-gates.py --only acceptance-cross,db-parity
    python3 scripts/run-gates.py --allow-blocked    # 缺工具链时放宽（会被记进报告）
    python3 scripts/run-gates.py --json report.json --log-dir .gate-logs
    python3 scripts/run-gates.py --shard 1/3        # CI 并行分片

只依赖标准库；不联网；不改动任何被检查的文件。
退出码：0 = 本次执行范围内全部门禁符合期望；1 = 有 FAIL / TIMEOUT / (未放宽的) BLOCKED。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                  # project/Base/BackendTemplate
GATES_JSON = HERE / "gates.json"
DOC_MD = ROOT / "index.md"
DOC_SECTION = "## 本地运行（快速上手）"

VALID_KINDS = {"gate", "canary"}
REQUIRED_FIELDS = ("id", "name", "why", "cmd", "owner", "required", "timeoutSec", "weight", "doc")

# 占位符：运行前替换，比对前一律视作通配符。
# 为什么要有 `{py}`：文档里写 `python3`，本机可能只有 `python`，CI 里可能是
# `python3.13`——把解释器名写死，同一份清单会在三种环境里各挂一次。
PY_TOKEN = "{py}"
SHA_TOKEN = "<SHA40>"
_PLACEHOLDER_RE = re.compile(r"<[^<>]*>")
_TAIL_LINES = 10

# 嵌套深度环境变量。`gates-selftest` 这道门禁跑的是 `scripts/selftest.py`，而自测里
# 又会调 `main()`——一旦有人把它写进「会被自己选中」的位置，就是无限 fork。
# 所以运行器要能识别「我正在被自己调用」，并把不安全的门禁判 BLOCKED。
# （这条是自测先发现的：第一版自测真的递归到自己超时被 SIGTERM 杀掉。）
NEST_ENV = "GATES_NEST_DEPTH"


# --------------------------------------------------------------------------- 载入与校验
def load_gates(path: Path = GATES_JSON) -> tuple:
    """读 gates.json。**损坏的 JSON 是 FAIL 而不是异常**——校验器崩了比校验失败危险。"""
    if not path.exists():
        return None, [f"{path.name}: 文件不存在"]
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"{path.name}: JSON 解析失败（第 {exc.lineno} 行第 {exc.colno} 列）：{exc.msg}"]
    if not isinstance(data, dict):
        return None, [f"{path.name}: 顶层必须是对象，实际是 {type(data).__name__}"]
    return data, []


def validate(data: dict) -> list:
    """逐格校验，每条错误都带位置。缺字段 / 类型不对 / 取值非法一律 FAIL。"""
    errors: list = []
    if not isinstance(data, dict):
        return ["顶层必须是对象"]
    if data.get("schemaVersion") != 1:
        errors.append(f"schemaVersion: 期望 1，实际 {data.get('schemaVersion')!r}")

    gates = data.get("gates")
    if not isinstance(gates, list):
        return errors + ["gates: 必须是数组"]
    if not gates:
        errors.append("gates: 数组为空（一份没人跑的门禁清单等于没有清单）")

    seen: dict = {}
    for i, g in enumerate(gates):
        loc = f"gates[{i}]"
        if not isinstance(g, dict):
            errors.append(f"{loc}: 必须是对象，实际是 {type(g).__name__}")
            continue
        gid = g.get("id")
        loc = f"gates[{i}]({gid})" if isinstance(gid, str) else f"gates[{i}]"
        for f in REQUIRED_FIELDS:
            if f not in g:
                errors.append(f"{loc}.{f}: 缺少必填字段")
        if isinstance(gid, str):
            if gid in seen:
                errors.append(f"{loc}.id: 与 gates[{seen[gid]}] 重复（id 是报告与 --only 的键）")
            seen[gid] = i
        elif gid is not None:
            errors.append(f"{loc}.id: 必须是字符串，实际是 {type(gid).__name__}")

        for f in ("name", "why", "cmd", "owner"):
            v = g.get(f)
            if v is not None and (not isinstance(v, str) or not v.strip()):
                errors.append(f"{loc}.{f}: 必须是非空字符串")

        for f in ("required", "doc"):
            v = g.get(f)
            if v is not None and not isinstance(v, bool):
                errors.append(f"{loc}.{f}: 必须是布尔值，实际是 {type(v).__name__}（写 \"true\" 不生效）")

        ts = g.get("timeoutSec")
        if ts is not None and (not isinstance(ts, int) or isinstance(ts, bool) or ts <= 0):
            errors.append(f"{loc}.timeoutSec: 必须是正整数，实际 {ts!r}（0 或缺失会让「慢」与「死」分不清）")

        w = g.get("weight")
        if w is not None and (not isinstance(w, (int, float)) or isinstance(w, bool) or w <= 0):
            errors.append(f"{loc}.weight: 必须是正数，实际 {w!r}")

        kind = g.get("kind", "gate")
        if kind not in VALID_KINDS:
            errors.append(f"{loc}.kind: 必须是 {sorted(VALID_KINDS)} 之一，实际 {kind!r}")

        erc = g.get("expectRc", 0)
        if not isinstance(erc, int) or isinstance(erc, bool):
            errors.append(f"{loc}.expectRc: 必须是整数，实际 {erc!r}")
        elif kind == "canary" and erc == 0:
            errors.append(f"{loc}: canary 的 expectRc 不能为 0——哨兵「变绿是好消息」就不是哨兵了")

        for f in ("requiresFiles", "requiresExec", "requiresEnv"):
            v = g.get(f, [])
            if not isinstance(v, list) or any(not isinstance(x, str) or not x for x in v):
                errors.append(f"{loc}.{f}: 必须是字符串数组，实际 {v!r}")

        ns = g.get("nestSafe", True)
        if not isinstance(ns, bool):
            errors.append(f"{loc}.nestSafe: 必须是布尔值，实际 {type(ns).__name__}")

        cmd = g.get("cmd")
        if isinstance(cmd, str) and cmd.strip():
            _, unresolved = substitute(cmd, "0" * 40)
            if unresolved:
                errors.append(
                    f"{loc}.cmd: 存在无法替换的占位符 {unresolved}——"
                    f"只支持 {PY_TOKEN} 与 {SHA_TOKEN}，运行时会原样传给 shell 然后莫名失败"
                )
    return errors


# --------------------------------------------------------------------------- 命令归一化
def substitute(cmd: str, sha40: str, py: str = None) -> tuple:
    """把占位符换成真值；返回 (命令, 未能替换的占位符列表)。"""
    out = cmd.replace(PY_TOKEN, py or sys.executable).replace(SHA_TOKEN, sha40)
    left = re.findall(r"<[^<>]*>", out)
    return out, left


def norm_tokens(cmd: str) -> list:
    """归一化后比对。

    三条规则都是踩过之后补的：
      · 行尾 `# 注释` 不算命令的一部分；
      · **文档里的占位符当通配符**（文档写 `--sha <40位git sha>`，清单写具体 sha）。
        不做归一化的话每次核对都报红，然后人就会把这条核对关掉；
      · `{py}` 与 `python3` 视为同义，理由见文件头第 1 条的注释。
    """
    s = cmd.split("#", 1)[0]
    s = s.replace("{py}", "python3").replace("python3", "python3")
    s = _PLACEHOLDER_RE.sub("*", s)
    return re.sub(r"\s+", " ", s).strip().split()


def _tokens_match(doc_tokens: list, gate_tokens: list) -> bool:
    if len(doc_tokens) != len(gate_tokens):
        return False
    return all(d == g or d == "*" or g == "*" for d, g in zip(doc_tokens, gate_tokens))


def extract_doc_section(text: str) -> tuple:
    """取出「本地运行（快速上手）」小节；返回 (小节内容, 起始行号)。"""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == DOC_SECTION:
            start = i + 1
            break
    if start is None:
        return None, 0
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]), start


def extract_doc_commands(section: str) -> list:
    """抽出候选命令：非空、非纯注释行。返回 [(归一化 token, 原始行)]。"""
    out = []
    for raw in section.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        toks = norm_tokens(s)
        if toks:
            out.append((toks, raw))
    return out


# --------------------------------------------------------------------------- 防漂移断言
def check_doc_drift(gates: list, doc_text: str) -> list:
    """断言「文档里写的」与「清单里声明的」一致。

    方向是**单向**的（清单 → 文档），理由是失败模式的代价不对等：
    · 门禁加了但文档没写 → 本地没人跑它 → 本地绿 CI 红（真事故）；
    · 文档里写了但不是门禁（环境探测、生成命令、演示命令）→ 无害，
      强制双向会让「快速上手」退化成门禁清单的镜像，于是没人愿意维护它。
    """
    errors: list = []
    section, line0 = extract_doc_section(doc_text)
    if section is None:
        return [f"index.md: 找不到小节 {DOC_SECTION!r}（门禁的期望结果必须有地方写下来）"]

    doc_cmds = extract_doc_commands(section)
    for g in gates:
        if not g.get("doc"):
            continue
        want = norm_tokens(g["cmd"])
        hits = [(toks, raw) for toks, raw in doc_cmds if _tokens_match(toks, want)]
        loc = f"gates.json:{g['id']}"
        if not hits:
            errors.append(
                f"{loc}: 声明为 doc=true，但 {DOC_MD.name} 的「本地运行（快速上手）」里找不到这条命令"
                f"（没写进快速上手的门禁，本地就不会有人跑它）：{' '.join(want)}"
            )
            continue
        if not any("期望" in raw for _, raw in hits):
            errors.append(
                f"{loc}: 文档里有这条命令但没写期望结果（附近第 {line0} 行起）——"
                f"只给命令不给期望，等于让下一个人自己猜「跑出来什么样算过」"
            )
    return errors


# --------------------------------------------------------------------------- 前置条件
def blocked_reason(gate: dict) -> str:
    """返回阻塞原因，None 表示可以跑。**BLOCKED 不是 PASS。**"""
    for rel in gate.get("requiresFiles", []):
        if not (ROOT / rel).exists():
            return f"缺少前置文件 {rel}（当前目录不是真实源码树？）"
    for exe in gate.get("requiresExec", []):
        if shutil.which(exe) is None:
            return f"PATH 里找不到命令 {exe}"
    for var in gate.get("requiresEnv", []):
        if not os.environ.get(var):
            j = os.environ.get(f"{var}_HOME") or ""
            return (
                f"环境变量 {var} 未设置"
                + (f"（{var}_HOME={j!r} 不是可用的设置方式）" if j else "")
            )
    return None


# --------------------------------------------------------------------------- 分片
def shard_gates(gates: list, index: int, total: int) -> list:
    """贪心装箱：按 weight 从大到小，放进当前最轻的一片。

    为什么不是取模：最慢的两条常常是相邻声明的（同一批 selftest），取模会把它们
    分到不同片——但更常见的是总权重为奇数时最重的一条和最轻的一条同片。
    文档里的分片规则应当是「让各片耗时接近」，那就照耗时装箱。
    """
    if total <= 1:
        return list(gates)
    buckets: list = [[] for _ in range(total)]
    load = [0.0] * total
    for g in sorted(gates, key=lambda x: -x["weight"]):
        i = load.index(min(load))
        buckets[i].append(g)
        load[i] += g["weight"]
    # 片内按原声明顺序跑，便于对照
    order = {g["id"]: i for i, g in enumerate(gates)}
    return sorted(buckets[index - 1], key=lambda g: order[g["id"]])


# --------------------------------------------------------------------------- 执行
def nest_depth() -> int:
    """当前已经嵌套了几层运行器。"""
    try:
        return int(os.environ.get(NEST_ENV, "0") or 0)
    except ValueError:
        return 0


def run_one(gate: dict, sha40: str, py: str, log_dir: Path) -> dict:
    cmd, _ = substitute(gate["cmd"], sha40, py)
    # 让子进程知道「自己是被运行器叫起来的」，避免 「门禁 → 自测 → 运行器」 成环。
    child_env = dict(os.environ, **{NEST_ENV: str(nest_depth() + 1)})
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=str(ROOT), env=child_env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=gate["timeoutSec"],
        )
        rc, out, timed_out = proc.returncode, proc.stdout.decode("utf-8", "replace"), False
    except subprocess.TimeoutExpired as exc:
        rc, out, timed_out = None, (exc.stdout or b"").decode("utf-8", "replace"), True
    elapsed = round(time.time() - t0, 1)

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{gate['id']}.log").write_text(out, encoding="utf-8")

    expect = gate.get("expectRc", 0)
    canary = gate.get("kind") == "canary"
    if timed_out:
        status, note = "TIMEOUT", f"超过 {gate['timeoutSec']}s 未结束（慢与死要能分开）"
    elif rc == expect:
        # 哨兵也走这一支：`--strict` 返回 1 是**符合期望**，不是失败。
        status, note = "PASS", ""
    elif canary and rc == 0:
        # 哨兵的 expectRc 被 schema 限制为 != 0，所以走到这里就是「本应为红却变绿」。
        status = "FAIL"
        note = (
            f"哨兵变绿：期望退出码 {expect}、实际 0。这不是好消息——"
            f"要么签名表被填满了，要么 MANUAL 项的判定逻辑被改坏，需要重新拍板。"
        )
    else:
        status = "FAIL"
        note = f"退出码 {rc}，期望 {expect}"

    tail = [ln for ln in out.splitlines() if ln.strip()][-_TAIL_LINES:]
    return dict(id=gate["id"], name=gate["name"], status=status, rc=rc,
                expectRc=expect, elapsedSec=elapsed, cmd=cmd, note=note,
                tail=tail, owner=gate.get("owner", ""))


# --------------------------------------------------------------------------- 报告
def digest_of(results: list) -> str:
    """本次执行的命令集合指纹。

    回答的是「当时跑的到底是哪几条命令」——纯代码版本号回答不了这个问题，
    因为清单是数据，改了清单不必改代码。审计与事后复盘都要靠它。
    """
    payload = json.dumps([[r["id"], r["cmd"]] for r in results], ensure_ascii=False,
                         sort_keys=True).encode("utf-8")
    return sha256(payload).hexdigest()[:16]


def print_report(results: list, skipped: int, blocked_allowed: bool) -> None:
    width = max((len(r["id"]) for r in results), default=4)
    print("")
    print("=" * 78)
    fails = [r for r in results if r["status"] != "PASS"]
    for r in results:
        print(f"  {r['status']:<8} {r['id']:<{width}}  {r['elapsedSec']:>7.1f}s  {r['name']}")
        if r["note"]:
            print(f"           └─ {r['note']}")
        for ln in r["tail"]:
            print(f"           │  {ln}")
    print("-" * 78)
    by = {}
    for r in results:
        by[r["status"]] = by.get(r["status"], 0) + 1
    summary = "  ".join(f"{k}={v}" for k, v in sorted(by.items())) or "（本次无可执行门禁）"
    print(f"  合计 {len(results)} 道：{summary}   跳过（--only/--skip）={skipped}")
    print(f"  命令集合指纹 digest={digest_of(results)}")
    if blocked_allowed and any(r["status"] == "BLOCKED" for r in results):
        print("  注意：本次带 --allow-blocked，BLOCKED 项**未被验证**，这个放宽已记进报告。")
    print(f"  结论：{'全部符合期望' if not fails else '存在未通过项'}")
    print("=" * 78)


def print_list(gates: list) -> None:
    print(f"门禁清单（来源 {GATES_JSON.relative_to(ROOT).as_posix()}）")
    print("-" * 78)
    for g in gates:
        tag = "哨兵" if g.get("kind") == "canary" else "门禁"
        exp = g.get("expectRc", 0)
        print(f"[{g['id']}] {g['name']}   ({tag} / 责任人 {g['owner']} / 权重 {g['weight']}"
              f" / 超时 {g['timeoutSec']}s / 期望退出码 {exp})")
        print(f"    命令：{g['cmd']}")
        print(f"    理由：{g['why']}")
        need = []
        if g.get("requiresFiles"):
            need.append("前置文件 " + ", ".join(g["requiresFiles"]))
        if g.get("requiresExec"):
            need.append("命令 " + ", ".join(g["requiresExec"]))
        if g.get("requiresEnv"):
            need.append("环境变量 " + ", ".join(g["requiresEnv"]))
        print(f"    前置：{'；'.join(need) if need else '无'}")
        print("")


# --------------------------------------------------------------------------- 主流程
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="门禁运行器：本地与 CI 共用一份门禁声明（scripts/gates.json）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="默认返回 1 才是正确状态：缺工具链时 BLOCKED 不算通过，放宽要写 --allow-blocked。",
    )
    ap.add_argument("--list", action="store_true", help="只打印清单，不执行")
    ap.add_argument("--check", action="store_true", help="只做 schema 校验与文档防漂移断言")
    ap.add_argument("--only", help="只跑这些门禁（逗号分隔的 id）")
    ap.add_argument("--skip", help="跳过这些门禁（逗号分隔的 id）")
    ap.add_argument("--shard", metavar="I/N", help="只跑第 I 片（共 N 片），CI 并行用")
    ap.add_argument("--allow-blocked", action="store_true",
                    help="把 BLOCKED 视为可接受（会被记进报告）；默认不放宽")
    ap.add_argument("--fail-fast", action="store_true", help="第一道失败就停")
    ap.add_argument("--json", metavar="PATH", help="把报告写成 JSON")
    ap.add_argument("--log-dir", metavar="DIR", help="每道门禁的全量输出落盘目录")
    ap.add_argument("--python", help=f"替换 {PY_TOKEN} 的解释器路径（默认当前解释器）")
    ap.add_argument("--sha", help=f"替换 {SHA_TOKEN} 的 40 位提交号（默认取 git rev-parse HEAD）")
    ap.add_argument("--quiet", action="store_true", help="不打印逐条结果，只打印汇总")
    args = ap.parse_args(argv)

    data, errors = load_gates()
    if errors:
        print("\n".join("ERROR " + e for e in errors))
        return 1
    errors = validate(data)
    if errors:
        print(f"gates.json 校验失败（{len(errors)} 处）：")
        print("\n".join("  ERROR " + e for e in errors))
        return 1

    gates = data["gates"]
    if args.list:
        print_list(gates)
        return 0

    if args.check:
        doc_errs = check_doc_drift(gates, DOC_MD.read_text(encoding="utf-8"))
        if doc_errs:
            print(f"防漂移断言失败（{len(doc_errs)} 处）：")
            print("\n".join("  ERROR " + e for e in doc_errs))
            return 1
        print(f"OK：gates.json schema 校验通过（{len(gates)} 条）；"
              f"文档防漂移断言通过（每条 doc=true 的命令都在「本地运行」小节里且写了期望结果）。")
        return 0

    sha40 = args.sha
    if not sha40:
        try:
            r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=15)
            sha40 = r.stdout.decode().strip()
        except Exception:
            sha40 = ""
    if not re.fullmatch(r"[0-9a-fA-F]{40}", sha40 or ""):
        sha40 = "0" * 40
        print(f"警告：未取到合法 40 位提交号，{SHA_TOKEN} 暂用全 0 占位（门禁本身不依赖它，"
              f"但报告里的 sha 不可信）；需要精确值时传 --sha <40位>。")

    selected = list(gates)
    if args.only:
        want = {x.strip() for x in args.only.split(",") if x.strip()}
        unknown = want - {g["id"] for g in gates}
        if unknown:
            print(f"ERROR --only 里有清单中不存在的 id：{sorted(unknown)}")
            return 1
        selected = [g for g in selected if g["id"] in want]
    if args.skip:
        drop = {x.strip() for x in args.skip.split(",") if x.strip()}
        unknown = drop - {g["id"] for g in gates}
        if unknown:
            print(f"ERROR --skip 里有清单中不存在的 id：{sorted(unknown)}")
            return 1
        selected = [g for g in selected if g["id"] not in drop]

    if args.shard:
        m = re.fullmatch(r"(\d+)/(\d+)", args.shard)
        if not m:
            print("ERROR --shard 需要形如 1/3 的取值")
            return 1
        i, n = int(m.group(1)), int(m.group(2))
        if not 1 <= i <= n or n < 2:
            print(f"ERROR --shard 取值越界：{args.shard}（要求 1 <= I <= N 且 N >= 2）")
            return 1
        selected = shard_gates(selected, i, n)

    log_dir = Path(args.log_dir).resolve() if args.log_dir else None
    results: list = []
    depth = nest_depth()
    for g in selected:
        if depth > 0 and not g.get("nestSafe", True):
            reason = (f"禁止嵌套调用：运行器已在嵌套第 {depth} 层，再跑这道门禁会无限 fork"
                      f"（门禁 → 脚本 → 运行器成环）")
            results.append(dict(id=g["id"], name=g["name"], status="BLOCKED", rc=None,
                                expectRc=g.get("expectRc", 0), elapsedSec=0.0, cmd=g["cmd"],
                                note=reason, tail=[], owner=g.get("owner", "")))
            if not args.quiet:
                print(f"  BLOCKED  {g['id']}  {reason}")
            if args.fail_fast:
                break
            continue
        reason = blocked_reason(g)
        if reason:
            results.append(dict(id=g["id"], name=g["name"], status="BLOCKED", rc=None,
                                expectRc=g.get("expectRc", 0), elapsedSec=0.0, cmd=g["cmd"],
                                note=reason, tail=[], owner=g.get("owner", "")))
            if not args.quiet:
                print(f"  BLOCKED  {g['id']}  {reason}")
            if args.fail_fast:
                break
            continue
        if not args.quiet:
            print(f"  RUN      {g['id']}  {g['name']} …", flush=True)
        r = run_one(g, sha40, args.python, log_dir)
        results.append(r)
        if not args.quiet:
            print(f"  {r['status']:<8} {g['id']}  {r['elapsedSec']}s")
        if args.fail_fast and r["status"] != "PASS":
            break

    print_report(results, skipped=len(gates) - len(selected), blocked_allowed=args.allow_blocked)

    if args.json:
        Path(args.json).write_text(json.dumps(dict(
            digest=digest_of(results), sha=sha40, python=args.python or sys.executable,
            allowBlocked=args.allow_blocked, shard=args.shard,
            results=results,
        ), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"报告已写入 {args.json}")

    bad = [r for r in results if r["status"] != "PASS"]
    if args.allow_blocked:
        bad = [r for r in bad if r["status"] != "BLOCKED"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
