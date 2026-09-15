#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stack-select.py 自测：在临时目录里复制 fixture，跑一整套断言。

为什么要有这个文件
------------------
选择器脚本的价值全在「幂等 + 可校验」这两条性质上，而这两条性质**光看代码看不出来**，
必须跑起来才算数。这里把验证固化成可提交的回归测试，任何一次改动只要破坏了
幂等性或 marker 边界，`python3 selftest.py` 立刻变红。

    python3 selftest.py            # 跑全部
    python3 selftest.py -v         # 每个用例都打印细节

只用标准库；不依赖 Maven、不联网、不动 fixture 本身（每次都拷到临时目录跑）。
退出码 0 = 全部通过，1 = 有失败。
"""

from __future__ import annotations

import hashlib
import itertools
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "stack-select.py"
FIXTURE = HERE / "fixture"

ROOT_POM = "pom.xml"
APP_POM = "template-application/pom.xml"
GENERATED = [
    ROOT_POM,
    APP_POM,
    "stack.json",
    "STACK.md",
    ".mvn/stack-profiles.txt",
    "template-application/src/main/resources/application-stack.yml",
]

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

_results = []


# --------------------------------------------------------------------------- 基础设施
def run(root: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict:
    return {rel: sha(root / rel) for rel in GENERATED if (root / rel).exists()}


def fresh(tmp: Path, name: str) -> Path:
    dst = tmp / name
    shutil.copytree(FIXTURE, dst)
    return dst


def check(name: str, cond: bool, detail: str = "") -> None:
    _results.append((name, bool(cond), detail))
    mark = "PASS" if cond else "FAIL"
    line = "  %-4s %s" % (mark, name)
    print(line)
    if not cond and detail:
        print("       " + detail.replace("\n", "\n       "))
    elif cond and VERBOSE and detail:
        print("       " + detail.replace("\n", "\n       "))


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- 用例
def case_list(tmp: Path) -> None:
    r = run(tmp, "--list")
    check("--list 退出码为 0", r.returncode == 0, r.stdout + r.stderr)
    check("--list 覆盖全部维度取值",
          all(k in r.stdout for k in ("spring", "satoken", "jpa", "mybatis-plus",
                                      "mybatis-flex", "redis", "caffeine", "none")),
          r.stdout)


def case_fresh_check_fails(tmp: Path) -> None:
    root = fresh(tmp, "fresh")
    r = run(root, "--check")
    check("出厂 fixture 上 --check 应当失败（还没生成）", r.returncode == 1,
          r.stdout + r.stderr)


def case_classic(tmp: Path) -> None:
    root = fresh(tmp, "classic")
    r = run(root, "--preset", "classic")
    check("--preset classic 退出码为 0", r.returncode == 0, r.stdout + r.stderr)

    pom = read(root / ROOT_POM)
    modules = [l.strip() for l in pom.splitlines() if "<module>" in l]
    expect = ["template-common", "template-spi", "template-web",
              "template-security-spring", "template-data-mybatis-plus",
              "template-cache-redis", "template-application"]
    check("根 pom 的 <modules> 顺序与内容正确",
          modules == ["<module>%s</module>" % m for m in expect],
          "实际：%s" % modules)

    check("注入内容缩进与 marker 对齐（8 空格）",
          all(l.startswith("        <module>") for l in modules if l in pom.splitlines()),
          "见 pom.xml")

    app = read(root / APP_POM)
    check("app pom 注入了 3 个实现模块依赖",
          app.count("<artifactId>template-security-spring</artifactId>") == 1
          and app.count("<artifactId>template-data-mybatis-plus</artifactId>") == 1
          and app.count("<artifactId>template-cache-redis</artifactId>") == 1,
          app)

    import json
    data = json.loads(read(root / "stack.json"))
    check("stack.json 记录三维取值与模块映射",
          (data["security"], data["orm"], data["cache"]) == ("spring", "mybatis-plus", "redis")
          and data["sharedCache"] is True and data["degraded"] == []
          and data["modules"]["orm"] == "template-data-mybatis-plus",
          read(root / "stack.json"))
    check("stack.json **不含** preset 字段（保证纯函数）", "preset" not in data, read(root / "stack.json"))

    yml = read(root / "template-application/src/main/resources/application-stack.yml")
    check("classic 下 5 个开关全为 true、无一个 false",
          yml.count(": true") == 5 and ": false" not in yml, yml)

    check("stack-profiles.txt 内容正确",
          read(root / ".mvn/stack-profiles.txt").strip()
          == "-Psecurity-spring -Porm-mybatis-plus -Pcache-redis",
          read(root / ".mvn/stack-profiles.txt"))

    md = read(root / "STACK.md")
    check("STACK.md 记录了 profile 且无降级项",
          "-Psecurity-spring -Porm-mybatis-plus -Pcache-redis" in md
          and "未启用任何降级项。" in md and "降级项" not in md.split("## 组合说明")[0],
          md)


def case_idempotent(tmp: Path) -> None:
    root = fresh(tmp, "idem")
    run(root, "--preset", "classic")
    before = snapshot(root)
    r = run(root, "--preset", "classic")
    after = snapshot(root)
    check("重复执行同一命令：退出码 0", r.returncode == 0, r.stdout + r.stderr)
    check("重复执行同一命令：6 个文件的字节内容完全不变", before == after,
          "差异：%s" % {k: (before.get(k), after.get(k)) for k in before if before.get(k) != after.get(k)})

    r = run(root, "--check")
    check("生成后 --check 通过", r.returncode == 0, r.stdout + r.stderr)
    check("--check 不改动任何文件", snapshot(root) == before)


def case_preset_overridable(tmp: Path) -> None:
    root = fresh(tmp, "override")
    run(root, "--preset", "classic", "--orm", "jpa")
    import json
    data = json.loads(read(root / "stack.json"))
    check("预设可被显式维度覆盖（classic + --orm jpa）",
          data["orm"] == "jpa" and data["security"] == "spring", read(root / "stack.json"))


def case_gate(tmp: Path) -> None:
    root = fresh(tmp, "gate")
    before = snapshot(root)
    r = run(root, "--security", "spring", "--orm", "jpa", "--cache", "caffeine")
    check("非 redis 缓存未加 --allow-degraded-cache：退出码 1", r.returncode == 1,
          r.stdout + r.stderr)
    check("拒绝时给出三项降级能力名",
          all(s in r.stdout for s in ("令牌黑名单", "登录失败计数", "账号锁定")), r.stdout)
    check("拒绝时不写任何文件（含已存在的 pom 也不被改动）", snapshot(root) == before,
          "before=%s\nafter =%s" % (before, snapshot(root)))

    r = run(root, "--security", "spring", "--orm", "jpa", "--cache", "caffeine",
            "--allow-degraded-cache")
    check("显式接受降级后：退出码 0", r.returncode == 0, r.stdout + r.stderr)
    yml = read(root / "template-application/src/main/resources/application-stack.yml")
    check("降级后三个开关被置为 false",
          "token-revocation-enabled: false" in yml
          and "fail-counter-enabled: false" in yml
          and "account-lock-enabled: false" in yml,
          yml)
    check("降级后 login-log-enabled 仍为 true（与缓存无关）",
          "login-log-enabled: true" in yml, yml)
    md = read(root / "STACK.md")
    check("STACK.md 明确列出降级项", "降级项（缺少共享存储）" in md, md)
    check("降级后 --check 仍通过", run(root, "--check").returncode == 0)


def case_stack_json_is_source_of_truth(tmp: Path) -> None:
    root = fresh(tmp, "sot")
    run(root, "--preset", "classic")
    # 只改 stack.json，不动命令行
    read_path = root / "stack.json"
    read_path.write_text(
        read(read_path)
        .replace('"security": "spring"', '"security": "satoken"')
        .replace('"orm": "mybatis-plus"', '"orm": "mybatis-flex"'),
        encoding="utf-8", newline="",
    )
    r = run(root, "--check")
    check("手改 stack.json 后 --check 报红（pom 还是旧的）", r.returncode == 1,
          r.stdout + r.stderr)
    check("报错点名了需要重新生成的两个 pom",
          ROOT_POM in r.stdout and APP_POM in r.stdout, r.stdout)

    r = run(root, "--yes")
    check("不带维度参数跑一次即按 stack.json 收敛：退出码 0", r.returncode == 0, r.stdout + r.stderr)
    pom = read(root / ROOT_POM)
    check("pom 已切到 satoken / mybatis-flex",
          "template-security-satoken" in pom and "template-data-mybatis-flex" in pom
          and "template-security-spring" not in pom, pom)
    check("收敛后 --check 通过", run(root, "--check").returncode == 0)


def case_tamper_detected(tmp: Path) -> None:
    """区间**内**被手改 → 必须报红；区间**外**手加模块 → 合法，脚本不碰。"""
    root = fresh(tmp, "tamper")
    run(root, "--preset", "classic")
    pom_path = root / ROOT_POM

    # (a) 区间内被塞私货：这是脚本管辖范围，必须被发现
    inside = read(pom_path).replace(
        "<!-- stack:modules:begin -->\n",
        "<!-- stack:modules:begin -->\n        <module>smuggled-in</module>\n",
    )
    pom_path.write_text(inside, encoding="utf-8", newline="")
    r = run(root, "--check")
    check("区间内被手工塞了模块 → --check 报红", r.returncode == 1, r.stdout + r.stderr)
    r = run(root, "--preset", "classic")
    check("重跑脚本把区间内的越界改动收敛回来",
          r.returncode == 0 and "smuggled-in" not in read(pom_path), read(pom_path))
    check("收敛后 --check 通过", run(root, "--check").returncode == 0)

    # (b) 区间外手加模块：那是用户自己的业务模块，脚本必须视而不见
    outside = read(pom_path).replace(
        "<!-- stack:modules:end -->\n    </modules>",
        "<!-- stack:modules:end -->\n        <module>my-business-module</module>\n    </modules>",
    )
    check("(b) 前置条件：确实加在了 stack:modules:end 之后",
          'my-business-module' in outside.split("<!-- stack:modules:end -->")[1], outside)
    pom_path.write_text(outside, encoding="utf-8", newline="")
    r = run(root, "--check")
    check("区间外手加模块 → --check 不报红（区间外的内容归用户管）",
          r.returncode == 0, r.stdout + r.stderr)
    r = run(root, "--preset", "satoken-flex")
    check("重跑脚本不会删掉区间外的自建模块",
          r.returncode == 0 and "my-business-module" in read(pom_path), read(pom_path))


def case_region_boundary(tmp: Path) -> None:
    """区间外一个字节都不能动——包括区间外的注释、空行、缩进。"""
    root = fresh(tmp, "boundary")
    run(root, "--preset", "classic")
    before_pom = read(root / ROOT_POM)
    head, rest = before_pom.split("<!-- stack:modules:begin -->", 1)
    _, tail = rest.split("<!-- stack:modules:end -->", 1)

    run(root, "--preset", "satoken-flex")
    after_pom = read(root / ROOT_POM)
    a_head, a_rest = after_pom.split("<!-- stack:modules:begin -->", 1)
    _, a_tail = a_rest.split("<!-- stack:modules:end -->", 1)

    check("切换组合后，marker 区间**之前**的内容逐字节不变", head == a_head,
          "before=%r\nafter =%r" % (head[-80:], a_head[-80:]))
    check("切换组合后，marker 区间**之后**的内容逐字节不变", tail == a_tail,
          "before=%r\nafter =%r" % (tail[:80], a_tail[:80]))


def case_missing_marker(tmp: Path) -> None:
    root = fresh(tmp, "nomarker")
    pom_path = root / ROOT_POM
    pom_path.write_text(
        read(pom_path)
        .replace("<!-- stack:modules:begin -->", "<!-- gone -->")
        .replace("<!-- stack:modules:end -->", "<!-- gone -->"),
        encoding="utf-8", newline="",
    )
    r = run(root, "--preset", "classic")
    check("marker 缺失时以退出码 1 明确报错，而不是瞎猜位置", r.returncode == 1,
          r.stdout + r.stderr)
    check("报错文案点明了缺哪个 marker",
          "stack:modules:begin" in (r.stdout + r.stderr), r.stdout + r.stderr)


def case_crlf_preserved(tmp: Path) -> None:
    root = fresh(tmp, "crlf")
    pom_path = root / ROOT_POM
    lf = read(pom_path)
    pom_path.write_bytes(lf.replace("\n", "\r\n").encode("utf-8"))

    r = run(root, "--preset", "classic")
    check("CRLF 仓库里执行成功", r.returncode == 0, r.stdout + r.stderr)
    raw = pom_path.read_bytes()
    check("CRLF 文件写回后仍是 CRLF，未被整文件改成 LF",
          b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b""), "见 pom.xml")
    check("CRLF 文件上 --check 通过（比较时已归一换行）",
          run(root, "--check").returncode == 0)


def case_print_mvn(tmp: Path) -> None:
    root = fresh(tmp, "mvn")
    run(root, "--preset", "satoken-flex")
    before = snapshot(root)
    r = run(root, "--print-mvn")
    check("--print-mvn 退出码 0", r.returncode == 0, r.stdout + r.stderr)
    check("--print-mvn 输出的命令与当前组合一致",
          r.stdout.strip() == "mvn -q clean verify -Psecurity-satoken -Porm-mybatis-flex -Pcache-redis",
          r.stdout)
    check("--print-mvn 不写文件", snapshot(root) == before)


def case_bad_value(tmp: Path) -> None:
    r = run(tmp, "--security", "shiro")
    check("非法取值被 argparse 拦下（退出码 2）", r.returncode == 2, r.stdout + r.stderr)


def case_no_marker_creation(tmp: Path) -> None:
    """区间外不存在 marker 时绝不能凭猜创建。"""
    root = fresh(tmp, "empty")
    (root / ROOT_POM).write_text(
        '<?xml version="1.0"?>\n<project><modules></modules></project>\n',
        encoding="utf-8", newline="",
    )
    r = run(root, "--preset", "classic")
    check("没有任何 marker 时拒绝执行且不改文件",
          r.returncode == 1 and "modules:begin" in (r.stdout + r.stderr)
          and "stack:modules" not in read(root / ROOT_POM))


def case_all_24_combinations(tmp: Path) -> None:
    """3 维度全组合：每个组合都要能生成，并且生成后 --check 自洽。"""
    combos = list(itertools.product(
        ["spring", "satoken"],
        ["jpa", "mybatis", "mybatis-plus", "mybatis-flex"],
        ["redis", "caffeine", "none"],
    ))
    bad = []
    for sec, orm, cache in combos:
        root = fresh(tmp, "m-%s-%s-%s" % (sec, orm, cache))
        r = run(root, "--security", sec, "--orm", orm, "--cache", cache,
                "--allow-degraded-cache")
        if r.returncode != 0:
            bad.append(("generate", sec, orm, cache, r.returncode))
            continue
        r = run(root, "--check")
        if r.returncode != 0:
            bad.append(("check", sec, orm, cache, r.returncode))
    check("24 种组合（2×4×3）全部可生成且自洽", not bad, "失败项：%s" % bad)


def case_degraded_matrix(tmp: Path) -> None:
    """只有 redis 才算共享存储；caffeine / none 一律记降级。"""
    import json
    for cache, shared, deg_count in (("redis", True, 0), ("caffeine", False, 3), ("none", False, 3)):
        root = fresh(tmp, "deg-" + cache)
        run(root, "--security", "spring", "--orm", "jpa", "--cache", cache,
            "--allow-degraded-cache")
        data = json.loads(read(root / "stack.json"))
        check("cache=%s → sharedCache=%s，degraded 有 %d 项" % (cache, shared, deg_count),
              data["sharedCache"] is shared and len(data["degraded"]) == deg_count,
              read(root / "stack.json"))


def case_presets_all(tmp: Path) -> None:
    import json
    for preset in ("classic", "jpa-lite", "satoken-flex", "minimal", "local-cache"):
        root = fresh(tmp, "p-" + preset)
        r = run(root, "--preset", preset)
        ok = r.returncode == 0 and run(root, "--check").returncode == 0
        data = json.loads(read(root / "stack.json")) if ok else {}
        check("预设 %s 可生成且自洽（%s/%s/%s）"
              % (preset, data.get("security"), data.get("orm"), data.get("cache")), ok,
              r.stdout + r.stderr)


# --------------------------------------------------------------------------- 主流程
def main() -> int:
    if not SCRIPT.exists():
        print("找不到 %s" % SCRIPT)
        return 1
    print("stack-select.py 自测\n" + "=" * 60)
    with tempfile.TemporaryDirectory(prefix="stack-select-selftest-") as td:
        tmp = Path(td)
        case_list(tmp)
        case_fresh_check_fails(tmp)
        case_bad_value(tmp)
        case_classic(tmp)
        case_idempotent(tmp)
        case_preset_overridable(tmp)
        case_gate(tmp)
        case_stack_json_is_source_of_truth(tmp)
        case_tamper_detected(tmp)
        case_region_boundary(tmp)
        case_missing_marker(tmp)
        case_no_marker_creation(tmp)
        case_crlf_preserved(tmp)
        case_print_mvn(tmp)
        case_degraded_matrix(tmp)
        case_presets_all(tmp)
        case_all_24_combinations(tmp)

    total = len(_results)
    failed = [n for n, ok, _ in _results if not ok]
    print("=" * 60)
    print("共 %d 项断言，通过 %d，失败 %d" % (total, total - len(failed), len(failed)))
    if failed:
        print("\n失败清单：")
        for n in failed:
            print("  - " + n)
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
