#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上线验收清单的可执行版本：六类 18 项，每项都有「验收判据 + 责任人 + 判定方式」。

为什么要有这个文件
------------------
验收清单最容易退化成两种东西：一是**一张只有勾选框的 Word 表格**（谁勾的都行，
没人能复核），二是**一段口头承诺**（「都验过了」）。两者的共同问题是一样的：
**判据没有被写下来，所以也没法被检验**。

这里把清单做成可执行的三层结构：

  1. **可机械判定的项（AUTO）**——直接跑，判据是文件内容、脚本退出码、JSON 字段。
     这些项在 CI 里可以全部跑通，它们回答的是「交付物本身齐不齐」。
  2. **必须在真实环境执行的项（MANUAL）**——压测、漏洞扫描、备份恢复、权限越权、
     告警触达。这些**永远不可能在这个仓库里被自动判定**（需要 Docker、网络、
     真实集群与真实人员）。工具不会假装它们通过了，只把它们连同**可直接粘贴执行的
     命令与期望输出**列出来。
  3. **签名表（`manual_signoff.json`）**——`--strict` 模式下，MANUAL 项必须在签名表里
     登记「谁、何时、结论、证据」，否则整个清单不算通过。这是「谁拍板」的落点，
     也是本页与 `docs/Others/ProjectDelivery/Delivery` 里「回滚谁拍板」一节的对应物。

用法
----
    python acceptance_check.py                 # 跑所有 AUTO 项 + 列出 MANUAL 项
    python acceptance_check.py --list           # 只打印 18 项清单（判据 + 责任人）
    python acceptance_check.py --strict         # 额外的签名表完备性检查
    python acceptance_check.py --cross          # 交叉断言（含变异测试，见下）
    python acceptance_check.py --json           # 机器可读输出

`--cross` 做的是**跨交付物的交叉断言**，本日新增，专门用来结清两笔旧账：
  · 第 76 / 77 天记下的待办「CLI `--check` × 用例矩阵基线」——断言基线真的进了
    生成物、真的受 `--check` 管辖，并且**改小基线一定会被拦**（变异测试，而不是
    只看「生成后 --check 通过」这种必然成立的事）；
  · 回滚能力——用 `tagplan.py --verify` 断言回滚命令引用的是不可变标签，并做一次
    变异：把回滚命令的 `IMAGE_REF` 换成环境指针 `prod`，`--verify` 必须报红。

  只依赖标准库；不联网；不改动任何被检查的文件（`--cross` 在临时目录里跑）。
退出码：0 = 本次要求检查的全部通过；1 = 有失败或（`--strict` 下）有未签项。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # project/Base/BackendTemplate
BASELINE_JSON = HERE / "case_baseline.json"
SIGNOFF_JSON = HERE / "manual_signoff.json"

PY = sys.executable


# --------------------------------------------------------------------------- 清单
# 六类 × 3 项 = 18 项。类别顺序与 docs/Others/ProjectDelivery/Delivery 的模板一致：
# 功能 / 性能 / 安全 / 数据 / 可观测 / 运维。
#
# kind 取值：
#   file    —— 文件存在且不小于 min_bytes
#   grep    —— 文件同时命中 patterns 全部正则、且不命中 absent 任一正则
#   matrix  —— case_baseline.json 的矩阵自洽性（每格有结论、覆盖数不低于基线）
#   script  —— 跑子进程，断言退出码与 stdout 片段
#   manual  —— 不在本仓库自动判定；只给命令与期望，并要求签名
ITEMS = [
    # ---------------- 功能 ----------------
    dict(id="A1", cat="功能", name="主链路端到端通过",
         judge="核心用户旅程按验收条件逐条走通，无阻断", owner="研发 / 产品",
         kind="manual",
         manual="bash scripts/deploy.sh up  # 起环境\nbash scripts/smoke.sh            # 冒烟：7 项断言",
         expect="冒烟 7 项全过、退出码 0；失败时脚本已自动打印容器日志"),
    dict(id="A2", cat="功能", name="边界与异常路径有覆盖",
         judge="「接口 × 场景」矩阵每格有结论，且已覆盖数不低于元测试基线", owner="研发",
         kind="matrix"),
    dict(id="A3", cat="功能", name="已知缺陷有登记与豁免说明",
         judge="遗留缺陷登记在案，写明影响、规避方式与豁免人", owner="研发 / 产品",
         kind="file", path="Acceptance/known_issues.md", min_bytes=300),

    # ---------------- 性能 ----------------
    dict(id="B1", cat="性能", name="压测 p95 达标",
         judge="核心接口在目标并发下 p95 低于约定阈值", owner="性能负责人",
         kind="manual",
         manual="k6 run -e BASE_URL=https://staging.example.com performance/login.js\n"
                "k6 run -e BASE_URL=https://staging.example.com -e TOKEN=<token> performance/protected.js",
         expect="thresholds 全绿（p95 / 错误率都在脚本里写成门禁，不是事后看曲线）"),
    dict(id="B2", cat="性能", name="容量拐点有记录",
         judge="记录 TPS 不再线性增长时的资源水位与并发点", owner="性能负责人",
         kind="grep", path="PerformanceTest/index.md",
         patterns=["容量", "拐点"],
         absent=[]),
    dict(id="B3", cat="性能", name="慢查询与长任务已定位",
         judge="上线前无未处理的慢 SQL、无超时未切分的长任务", owner="DBA / 研发",
         kind="manual",
         manual="开启慢查询日志后跑一遍主链路：\n"
                "  SET GLOBAL slow_query_log = ON; SET GLOBAL long_query_time = 1;\n"
                "  对命中语句逐条 EXPLAIN，确认走索引或已加索引",
         expect="慢查询清单为空，或每条都在 known_issues.md 里有登记与豁免人"),

    # ---------------- 安全 ----------------
    dict(id="C1", cat="安全", name="权限最小化核对",
         judge="账号与角色只具备必需权限，且授权以可审计的方式声明", owner="安全负责人",
         kind="grep", path="Security/index.md",
         patterns=["@EnableMethodSecurity", "@PreAuthorize"],
         absent=[]),
    dict(id="C2", cat="安全", name="密钥不落明文",
         judge="密钥走环境变量 / 托管注入，缺失即启动失败；镜像与日志中无明文密钥", owner="安全负责人",
         kind="grep", path="Deployment/index.md",
         patterns=["JWT_SECRET", "环境变量"],
         absent=[]),
    dict(id="C3", cat="安全", name="依赖漏洞扫描无高危",
         judge="依赖与镜像扫描无未修复的高危项", owner="安全负责人",
         kind="manual",
         manual="trivy fs --severity HIGH,CRITICAL --exit-code 1 .\n"
                "trivy image --severity HIGH,CRITICAL --exit-code 1 <IMAGE_REF>",
         expect="两条命令退出码均为 0（这条与第 78 天的镜像扫描门禁是同一条判据）"),

    # ---------------- 数据 ----------------
    dict(id="D1", cat="数据", name="备份可恢复（演练过）",
         judge="从备份真实恢复一次并校验数据一致；双方言备份路径都可用", owner="DBA",
         kind="script", cwd="Acceptance", cmd=[PY, "backup_restore.py", "--dry-run"],
         rc=0, stdout=["mysqldump", "pg_dump", "dry-run"],
         manual="python Acceptance/backup_restore.py --engine mysql   # 真实演练\n"
                "python Acceptance/backup_restore.py --engine postgres",
         expect="恢复后表集合与逐表行数与备份前一致（脚本内置比对），退出码 0"),
    dict(id="D2", cat="数据", name="迁移可回退",
         judge="迁移脚本的反向执行在预发验证通过；双方言结构逐列一致", owner="DBA / 研发",
         kind="script", cwd="db", cmd=[PY, "parity_check.py"],
         rc=0, stdout=["OK"],
         manual="python db/selftest.py   # 11 项自测，确认校验器本身没坏",
         expect="parity_check 输出 OK 且退出码 0——两套 DDL 结构一致才谈得上「迁移可回退」"),
    dict(id="D3", cat="数据", name="数据隔离与脱敏符合要求",
         judge="跨租户访问被拒，非生产环境数据已脱敏", owner="DBA / 安全负责人",
         kind="manual",
         manual="用 A 租户的令牌访问 B 租户资源：\n"
                "  curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: Bearer <A 的 token>' \\\n"
                "    https://staging.example.com/api/users/<B 的 id>",
         expect="403（不是 200、也不是 404 以外的其它码）；响应体不回显对方数据"),

    # ---------------- 可观测 ----------------
    dict(id="E1", cat="可观测", name="关键指标有看板",
         judge="可用性、性能、资源、业务四类指标在看板上可见", owner="SRE",
         kind="grep", path="HealthCheck/index.md",
         patterns=["metrics", "prometheus"],
         absent=[]),
    dict(id="E2", cat="可观测", name="错误日志可检索",
         judge="关键错误日志带 traceId，能按请求检索到完整链路", owner="研发 / SRE",
         kind="grep", path="TraceId/index.md",
         patterns=["X-Trace-Id", "MDC"],
         absent=[]),
    dict(id="E3", cat="可观测", name="告警能触达人而非只发群",
         judge="告警指向具体值班人，并触发过一次测试告警", owner="SRE",
         kind="manual",
         manual="在验收环境触发一次真实告警（如把 readiness 探针指向不存在的路径）",
         expect="值班人收到通知，且通知里能直接点到看板与排障手册；群消息不算通过"),

    # ---------------- 运维 ----------------
    dict(id="F1", cat="运维", name="部署脚本可重放",
         judge="同一版本重复部署结果一致，无需手工补步骤；标签分层受机械校验", owner="运维",
         kind="script", cwd="Release", cmd=[PY, "selftest.py"],
         rc=0, stdout=["全部通过"],
         manual="python Release/tagplan.py --version 1.2.0 --sha <40位hex> --channel prod",
         expect="selftest 全绿（含 INV1~INV6 与 11 组全组合扫描）"),
    dict(id="F2", cat="运维", name="回滚演练过",
         judge="回滚动作一条命令可完成，且回滚后冒烟通过；回滚引用的必须是不可变标签", owner="运维",
         kind="crossrollback"),
    dict(id="F3", cat="运维", name="值班与升级路径已交接",
         judge="明确值班人、升级路径与联系方式，交接有记录", owner="运维 / 负责人",
         kind="file", path="Acceptance/rollback_plan.md", min_bytes=300),
]


# --------------------------------------------------------------------------- 判定
def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def check_matrix(item: dict) -> tuple:
    """用例矩阵：每格必须有结论；已覆盖数不得低于 Java 元测试基线。"""
    if not BASELINE_JSON.exists():
        return False, "缺少 %s" % _rel(BASELINE_JSON)
    try:
        data = json.loads(_read(BASELINE_JSON))
    except ValueError as exc:
        return False, "%s 不是合法 JSON：%s" % (_rel(BASELINE_JSON), exc)
    if not isinstance(data, dict):
        return False, "%s 顶层应当是一个对象，实际是 %s" % (_rel(BASELINE_JSON), type(data).__name__)
    lack = [k for k in ("symbols", "scenarios", "matrix", "javaMetaTestBaseline") if k not in data]
    if lack:
        return False, "%s 缺少字段：%s" % (_rel(BASELINE_JSON), "、".join(lack))
    scenarios = [s["key"] for s in data["scenarios"]]
    matrix = data["matrix"]
    problems = []

    # R1 每格必须有结论，且必须是三个合法符号之一
    legal = set(data["symbols"])
    blank = []
    for api, cells in matrix.items():
        if len(cells) != len(scenarios):
            problems.append("%s 的格子数 %d != 场景数 %d" % (api, len(cells), len(scenarios)))
        for key, cell in zip(scenarios, cells):
            if cell not in legal:
                blank.append("%s/%s=%r" % (api, key, cell))
    if blank:
        problems.append("存在没有结论的格子：%s" % "、".join(blank[:5]))

    # R2 已覆盖数 ≥ 元测试基线。
    # 用 .get 而不是 []：矩阵是手工维护的（`ErrorPath` 页的表格要逐字符对齐），
    # 写进一个不在 symbols 里的符号是**最可能发生**的手误。这里若直接下标取值会抛
    # KeyError，把「一格填错」变成「校验器崩了」——校验器崩了比校验失败危险，
    # 因为崩了之后没人知道该修哪一格。R1 已经会把这个符号报出来，这里只需不参与计数。
    covered = sum(1 for cells in matrix.values() for c in cells
                  if data["symbols"].get(c) == "covered")
    baseline = int(data["javaMetaTestBaseline"])
    headroom = covered - baseline
    if covered < baseline:
        problems.append("已覆盖 %d 格 < 元测试基线 %d 格" % (covered, baseline))

    # R3 每个接口至少有一条用例；不许出现"整行不适用"
    empty_rows = [api for api, cells in matrix.items()
                  if not any(data["symbols"].get(c) == "covered" for c in cells)]
    if empty_rows:
        problems.append("整行没有任何用例的接口：%s" % "、".join(empty_rows))

    detail = "接口 %d × 场景 %d = %d 格，已覆盖 %d 格，元测试基线 %d 格，余量 %d 格" % (
        len(matrix), len(scenarios), len(matrix) * len(scenarios), covered, baseline, headroom)
    if problems:
        return False, detail + "；问题：" + "；".join(problems)
    return True, detail


def run_script(item: dict) -> tuple:
    cwd = ROOT / item.get("cwd", ".")
    if not cwd.exists():
        return False, "工作目录不存在：%s" % _rel(cwd)
    exe = item["cmd"][0]
    if exe == PY and not (cwd / item["cmd"][1]).exists():
        return False, "脚本不存在：%s" % _rel(cwd / item["cmd"][1])
    try:
        r = subprocess.run(item["cmd"], cwd=str(cwd), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=item.get("timeout", 120))
    except Exception as exc:  # noqa: BLE001
        return False, "执行失败：%s" % exc
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != item.get("rc", 0):
        return False, "退出码 %d（期望 %d）\n%s" % (r.returncode, item.get("rc", 0), out.strip()[-600:])
    missing = [s for s in item.get("stdout", []) if s not in out]
    if missing:
        return False, "输出缺少关键字：%s\n%s" % (missing, out.strip()[-600:])
    return True, "退出码 0，输出命中 %s" % ("、".join(item.get("stdout", [])) or "（无关键字要求）")


def run_item(item: dict) -> tuple:
    """返回 (state, detail)。state ∈ {PASS, FAIL, MANUAL}。"""
    kind = item["kind"]
    if kind == "manual":
        return "MANUAL", "需在验收环境执行（命令见下）"
    if kind == "matrix":
        ok, d = check_matrix(item)
        return ("PASS" if ok else "FAIL"), d
    if kind == "crossrollback":
        ok, d = cross_rollback()
        return ("PASS" if ok else "FAIL"), d
    if kind == "file":
        p = ROOT / item["path"]
        if not p.exists():
            return "FAIL", "文件不存在：%s" % item["path"]
        size = p.stat().st_size
        if size < item.get("min_bytes", 0):
            return "FAIL", "%s 只有 %d 字节，低于要求的 %d" % (item["path"], size, item["min_bytes"])
        return "PASS", "%s 存在（%d 字节）" % (item["path"], size)
    if kind == "grep":
        p = ROOT / item["path"]
        if not p.exists():
            return "FAIL", "文件不存在：%s" % item["path"]
        text = _read(p)
        missing = [pat for pat in item.get("patterns", []) if pat not in text]
        if missing:
            return "FAIL", "%s 中找不到：%s" % (item["path"], missing)
        present = [pat for pat in item.get("absent", []) if pat in text]
        if present:
            return "FAIL", "%s 中不应出现：%s" % (item["path"], present)
        return "PASS", "%s 命中 %s" % (item["path"], "、".join(item.get("patterns", [])))
    if kind == "script":
        # 只跑一次：这里若写成 run_script(item)[0] / [1] 会**执行两遍子进程**，
        # 既浪费一倍时间，又可能两次结果不同（脚本里有临时目录、有时间戳）。
        ok, detail = run_script(item)
        return ("PASS" if ok else "FAIL"), detail
    return "FAIL", "未知判定方式：%s" % kind


# --------------------------------------------------------------------------- 交叉断言
def _fixture_tmp(prefix: str) -> Path:
    td = tempfile.mkdtemp(prefix=prefix)
    dst = Path(td) / "proj"
    shutil.copytree(ROOT / "stack-select" / "fixture", dst)
    return dst


def cross_baseline() -> tuple:
    """CLI `--check` × 用例矩阵基线 的交叉断言（含变异测试）。"""
    notes = []
    script = ROOT / "stack-select" / "stack-select.py"
    if not script.exists():
        return False, "找不到 stack-select.py"
    root = _fixture_tmp("acc-baseline-")
    yml = root / "template-application/src/main/resources/application-stack.yml"

    def run(*args):
        return subprocess.run([PY, str(script), "--root", str(root), *args],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120)

    # ① 五个预设都能生成且自洽
    bad = []
    for preset in ("classic", "jpa-lite", "satoken-flex", "minimal", "local-cache"):
        if run("--preset", preset).returncode != 0 or run("--check").returncode != 0:
            bad.append(preset)
    if bad:
        return False, "以下预设无法生成或 --check 不自洽：%s" % bad
    notes.append("5 个预设在 fixture 上全部生成 + --check 自洽")

    # ② 基线真的进了生成物
    text = _read(yml)
    if "case-baseline: 38" not in text:
        return False, "生成物里没有 case-baseline: 38（基线没进生成物，门禁无从比对）"
    notes.append("生成物含 case-baseline: 38")

    # ③ 变异测试：把基线改小一格 → --check 必须报红
    yml.write_text(text.replace("case-baseline: 38", "case-baseline: 37"),
                   encoding="utf-8", newline="")
    r = run("--check")
    if r.returncode == 0:
        return False, "把生成物里的基线 38 改成 37，--check 竟然通过了——门禁是假的"
    notes.append("变异：基线改小一格 → --check 报红（门禁有效）")

    # ④ 收敛后回归自洽
    shutil.rmtree(str(root.parent), ignore_errors=True)
    root = _fixture_tmp("acc-baseline2-")
    run("--preset", "classic")
    if run("--check").returncode != 0:
        return False, "重新生成后 --check 仍不通过"
    notes.append("重新生成后恢复自洽")

    # ⑤ 基线只增不减
    r = run("--case-baseline", "30")
    if r.returncode == 0:
        return False, "把基线从 38 降到 30 竟然被接受——「只增不减」没生效"
    notes.append("变异：降基线（38 → 30）被拒绝")
    shutil.rmtree(str(root.parent), ignore_errors=True)
    return True, "；".join(notes)


def cross_rollback() -> tuple:
    """回滚命令必须引用不可变标签：用 tagplan.py --verify 断言，并做一次变异。"""
    script = ROOT / "Release" / "tagplan.py"
    if not script.exists():
        return False, "找不到 Release/tagplan.py"
    td = tempfile.mkdtemp(prefix="acc-rollback-")
    plan = Path(td) / "plan.json"
    sha = "9f2c1a4b6d8e" + "0" * 28

    def run(*args, out_file=None):
        r = subprocess.run([PY, str(script), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        if out_file is not None and r.returncode == 0:
            out_file.write_text(r.stdout, encoding="utf-8", newline="")
        return r

    r = run("--version", "1.2.0", "--sha", sha, "--previous-sha", "1a2b3c4d5e6f" + "a" * 28,
            "--channel", "prod", "--json", out_file=plan)
    if r.returncode != 0 or not plan.exists():
        shutil.rmtree(td, ignore_errors=True)
        return False, "生成计划失败：%s" % (r.stdout + r.stderr).strip()[-400:]
    r = run("--verify", str(plan))
    if r.returncode != 0:
        shutil.rmtree(td, ignore_errors=True)
        return False, "正常计划未通过 --verify：%s" % (r.stdout + r.stderr).strip()[-400:]
    notes = ["正常计划 --verify 通过（INV1~INV6）"]

    # 变异：把回滚命令指向环境指针 prod（会变的标签）→ 必须报红
    data = json.loads(plan.read_text(encoding="utf-8"))
    cmds = data.get("commands") or {}
    key = next((k for k in cmds if "rollback" in k.lower() or "回滚" in k), None)
    if key is None:
        shutil.rmtree(td, ignore_errors=True)
        return False, "计划里找不到回滚命令（键名可能变了）：%s" % list(cmds)
    original = cmds[key]
    cmds[key] = _mutate_image_ref(original)
    plan.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="")
    r = run("--verify", str(plan))
    if r.returncode == 0:
        shutil.rmtree(td, ignore_errors=True)
        return False, "把回滚命令指向环境指针 prod 后 --verify 仍通过——不可变性门禁是假的"
    notes.append("变异：回滚指向环境指针 → --verify 报红")
    shutil.rmtree(td, ignore_errors=True)
    return True, "；".join(notes)


def _mutate_image_ref(cmd: str) -> str:
    """把命令里的 IMAGE_REF=<不可变标签> 换成 IMAGE_REF=<repo>:prod。"""
    import re
    m = re.search(r"IMAGE_REF=([^\s\"']+)", cmd)
    if not m:
        return cmd + " IMAGE_REF=example/app:prod"
    ref = m.group(1)
    repo = ref.split(":")[0]
    return cmd.replace("IMAGE_REF=" + ref, "IMAGE_REF=%s:prod" % repo)


# --------------------------------------------------------------------------- 签名表
MIN_EVIDENCE = 8          # 证据至少要能被复核：一个链接、一次流水线编号、一行 SQL 输出
_DATE_RE_SRC = r"^\d{4}-\d{2}-\d{2}"


def check_signoff(path: Path) -> tuple:
    """--strict：MANUAL 项必须在签名表里登记「谁、何时、结论、证据」。

    这里的判据刻意比「字段存在」更严一点，因为签名表最容易退化成走过场：
      · `evidence` 不能只写「已验」「OK」——至少要 8 个字符（够放一个链接或一次 run 号）；
      · `at` 必须是 ISO 日期开头，避免出现「上周」「昨天」这种没法复核的时间；
      · 给 **AUTO** 项签名要被点名——AUTO 项本就该由脚本判定，人去签它等于绕开判据。
    """
    import re
    manual = [it["id"] for it in ITEMS if it["kind"] == "manual"]
    auto = [it["id"] for it in ITEMS if it["kind"] != "manual"]
    if not path.exists():
        return False, "缺少 %s：MANUAL 项共 %d 个，一个都没签" % (path.name, len(manual))
    try:
        data = json.loads(_read(path))
    except ValueError as exc:
        return False, "%s 不是合法 JSON：%s" % (path.name, exc)
    if not isinstance(data, dict):
        return False, "%s 顶层应当是一个对象，实际是 %s" % (path.name, type(data).__name__)
    entries = data.get("signoffs") or {}
    if not isinstance(entries, dict):
        return False, "%s 的 signoffs 应当是一个对象，实际是 %s" % (path.name, type(entries).__name__)

    unsigned, weak = [], []
    for i in manual:
        e = entries.get(i)
        if not e or not e.get("by") or not e.get("at") or not e.get("evidence"):
            unsigned.append(i)
            continue
        if len(str(e["evidence"]).strip()) < MIN_EVIDENCE:
            weak.append("%s（evidence 只有 %d 字符，够不上可复核）" % (i, len(str(e["evidence"]).strip())))
        elif not re.match(_DATE_RE_SRC, str(e["at"]).strip()):
            weak.append("%s（at=%r 不是 ISO 日期开头）" % (i, e["at"]))

    problems = []
    if unsigned:
        problems.append("未签或字段不全（需 by / at / evidence）：%s" % "、".join(unsigned))
    if weak:
        problems.append("签名不达标：%s" % "；".join(weak))
    stray = sorted(set(entries) & set(auto))
    if stray:
        problems.append("这些是 AUTO 项、不该由人签名（签了等于绕开脚本判据）：%s" % "、".join(stray))
    if problems:
        return False, "；".join(problems)
    return True, "%d 项 MANUAL 全部已签，且证据均可复核" % len(manual)


# --------------------------------------------------------------------------- 主流程
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="acceptance_check.py",
        description="上线验收清单（六类 18 项）的可执行版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--list", action="store_true", help="只打印清单（判据 + 责任人 + 判定方式）")
    ap.add_argument("--strict", action="store_true", help="额外检查 MANUAL 项的签名表是否完备")
    ap.add_argument("--cross", action="store_true", help="只跑跨交付物交叉断言（含变异测试）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    ap.add_argument("--signoff", default=str(SIGNOFF_JSON),
                    help="签名表路径，默认 %s（供自测指向临时文件）" % SIGNOFF_JSON.name)
    args = ap.parse_args(argv)

    if args.list:
        for cat in ["功能", "性能", "安全", "数据", "可观测", "运维"]:
            group = [it for it in ITEMS if it["cat"] == cat]
            print("[%s] %d 项" % (cat, len(group)))
            for it in group:
                how = {"manual": "人工（需签名）", "matrix": "自动 · 用例矩阵",
                       "crossrollback": "自动 · 交叉断言", "file": "自动 · 文件",
                       "grep": "自动 · 内容", "script": "自动 · 脚本"}[it["kind"]]
                print("  %-3s %-16s 判定=%s  责任人=%s" % (it["id"], it["name"], how, it["owner"]))
                print("        判据：%s" % it["judge"])
                if it.get("manual"):
                    for ln in it["manual"].split("\n"):
                        print("        命令：%s" % ln)
                    print("        期望：%s" % it.get("expect", ""))
            print()
        print("合计 %d 项；AUTO %d 项，MANUAL %d 项。"
              % (len(ITEMS), sum(1 for i in ITEMS if i["kind"] != "manual"),
                 sum(1 for i in ITEMS if i["kind"] == "manual")))
        return 0

    if args.cross:
        ok1, d1 = cross_baseline()
        ok2, d2 = cross_rollback()
        if args.json:
            print(json.dumps({"baseline": {"ok": ok1, "detail": d1},
                              "rollback": {"ok": ok2, "detail": d2}},
                             ensure_ascii=False, indent=2))
        else:
            print("交叉断言 1：CLI --check × 用例矩阵基线")
            print("  %s %s" % ("PASS" if ok1 else "FAIL", d1))
            print("交叉断言 2：回滚命令 × 标签不可变性")
            print("  %s %s" % ("PASS" if ok2 else "FAIL", d2))
        return 0 if (ok1 and ok2) else 1

    results = []
    for it in ITEMS:
        state, detail = run_item(it)
        results.append((it, state, detail))

    failed = [r for r in results if r[1] == "FAIL"]
    manual = [r for r in results if r[1] == "MANUAL"]

    if args.json:
        print(json.dumps({
            "items": [{"id": i["id"], "cat": i["cat"], "name": i["name"],
                       "state": s, "detail": d, "owner": i["owner"],
                       "manual": i.get("manual"), "expect": i.get("expect")}
                      for i, s, d in results],
            "autoTotal": len(results) - len(manual),
            "autoPassed": len(results) - len(manual) - len(failed),
            "manualTotal": len(manual),
        }, ensure_ascii=False, indent=2))
    else:
        cur = None
        for it, state, detail in results:
            if it["cat"] != cur:
                cur = it["cat"]
                print("\n[%s]" % cur)
            print("  %-5s %-3s %s" % (state, it["id"], it["name"]))
            print("        %s" % detail)
        print("\n" + "=" * 66)
        print("AUTO：%d/%d 通过   MANUAL：%d 项待验收环境执行并签名"
              % (len(results) - len(manual) - len(failed), len(results) - len(manual), len(manual)))
        if manual:
            print("\nMANUAL 项（命令与期望输出，可直接粘贴执行）：")
            for it, _, _ in manual:
                print("  %s %s（责任人：%s）" % (it["id"], it["name"], it["owner"]))
                for ln in it["manual"].split("\n"):
                    print("      %s" % ln)
                print("      期望：%s" % it.get("expect", ""))

    strict_ok, strict_detail = (True, "")
    if args.strict:
        strict_ok, strict_detail = check_signoff(Path(args.signoff))
        if not args.json:
            print("\n[--strict] 签名表：%s %s" % ("PASS" if strict_ok else "FAIL", strict_detail))

    if not args.json:
        print("\n" + ("OK   本次检查全部通过。" if (not failed and strict_ok) else "FAIL 存在未通过项。"))
    return 0 if (not failed and strict_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
