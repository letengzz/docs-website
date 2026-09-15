#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""后端通用模板 · 技术栈选择器（stack selector）

功能
----
按「安全 / 数据 / 缓存」三个维度选择实现模块，并把选择结果**确定性**地渲染到
工程文件里。设计目标是三件事：

1. **幂等**——同一条命令重复执行，Git 工作区不应有任何变化。
2. **可校验**——`--check` 比对生成物与 `stack.json` 是否一致，不一致以非 0 退出，
   可以直接当 CI 门禁（防止有人手改了 pom 却忘了同步配置）。
3. **零依赖**——只用 Python 标准库，`python3 scripts/stack-select.py` 就能跑。

**生成物是 (security, orm, cache) 三个取值的纯函数**，不含时间戳、不含预设名、不含
用户名。所以 `--check` 只要读到 `stack.json` 就能完整复现期望结果，不需要知道当初
是用哪个预设、哪条命令生成的——这是它敢当 CI 门禁的前提。

只写 marker 区间
----------------
脚本只改这两个区间的**内部**内容，区间外一个字符都不碰（连缩进与换行风格都保持原样）：

    pom.xml                            <!-- stack:modules:begin --> ... <!-- stack:modules:end -->
    template-application/pom.xml       <!-- stack:deps:begin    --> ... <!-- stack:deps:end    -->

所以手工改动与脚本改动不会互相覆盖；一旦有人手改了区间内内容，下次执行或
`--check` 会以 diff 的形式把它暴露出来，而不是悄悄冲掉。

用法
----
    python3 scripts/stack-select.py                                  # 交互式菜单
    python3 scripts/stack-select.py --preset classic                 # 用预设组合
    python3 scripts/stack-select.py --security satoken --orm mybatis-flex --cache redis
    python3 scripts/stack-select.py --list                           # 列出可选值与预设
    python3 scripts/stack-select.py --check                          # CI 门禁：不一致则非 0 退出
    python3 scripts/stack-select.py --dry-run --preset jpa-lite      # 只打印，不写文件
    python3 scripts/stack-select.py --print-mvn                      # 只输出当前组合对应的 mvn 命令
    python3 scripts/stack-select.py --root <工程根目录>               # 默认当前目录

`--check` 与 `--print-mvn` 是给 CI 和别的脚本调的，**永不进入交互**：两者都直接以
`stack.json` 为准。其余情况下，只有在「终端是真交互」且没给任何参数时才会弹菜单。

退出码
------
    0  成功 / --check 一致
    1  校验失败（非法取值、缺少 marker、--check 不一致、需要 --allow-degraded-cache）
    2  用法错误（参数组合不合法）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCHEMA_VERSION = 1

# --------------------------------------------------------------------------- 元数据
# 维度定义：值 -> 模块目录名。顺序即菜单顺序，也是渲染顺序（保证确定性）。
DIMENSIONS = {
    "security": {
        "label": "安全框架",
        "values": {
            "spring": "template-security-spring",
            "satoken": "template-security-satoken",
        },
        "default": "spring",
    },
    "orm": {
        "label": "ORM 框架",
        "values": {
            "jpa": "template-data-jpa",
            "mybatis": "template-data-mybatis",
            "mybatis-plus": "template-data-mybatis-plus",
            "mybatis-flex": "template-data-mybatis-flex",
        },
        "default": "mybatis-plus",
    },
    "cache": {
        "label": "缓存实现",
        "values": {
            "redis": "template-cache-redis",
            "caffeine": "template-cache-caffeine",
            "none": "template-cache-noop",
        },
        "default": "redis",
    },
}

# 固定不变的模块（永远在 reactor 里，且必须排在可插拔模块之前）
BASE_MODULES = ["template-common", "template-spi", "template-web"]
APP_MODULE = "template-application"

GROUP_ID = "com.example.template"

PRESETS = {
    "classic": {
        "desc": "国内主流，开箱即用",
        "security": "spring",
        "orm": "mybatis-plus",
        "cache": "redis",
    },
    "jpa-lite": {
        "desc": "偏好 JPA 规范与派生查询",
        "security": "spring",
        "orm": "jpa",
        "cache": "redis",
    },
    "satoken-flex": {
        "desc": "轻量权限 + 新式 ORM",
        "security": "satoken",
        "orm": "mybatis-flex",
        "cache": "redis",
    },
    "minimal": {
        "desc": "依赖最少，单机、无缓存",
        "security": "spring",
        "orm": "mybatis",
        "cache": "none",
        "allow_degraded_cache": True,
    },
    "local-cache": {
        "desc": "单机部署，不引入 Redis",
        "security": "spring",
        "orm": "jpa",
        "cache": "caffeine",
        "allow_degraded_cache": True,
    },
}

# 依赖共享存储（Redis 类）才能正确工作的能力；cache != redis 时这些能力必须降级
SHARED_STORE_CAPABILITIES = [
    ("token_revocation", "令牌黑名单 / 撤销"),
    ("fail_counter", "登录失败计数"),
    ("account_lock", "账号锁定"),
]

MARKER_MODULES_BEGIN = "<!-- stack:modules:begin -->"
MARKER_MODULES_END = "<!-- stack:modules:end -->"
MARKER_MODULES_NOTE = "<!-- 本区间由 scripts/stack-select.py 生成，手工修改会在下次执行或 --check 时暴露 -->"

MARKER_DEPS_BEGIN = "<!-- stack:deps:begin -->"
MARKER_DEPS_END = "<!-- stack:deps:end -->"
MARKER_DEPS_NOTE = "<!-- 本区间由 scripts/stack-select.py 生成，手工修改会在下次执行或 --check 时暴露 -->"

STACK_JSON = "stack.json"
STACK_MD = "STACK.md"
PROFILES_FILE = ".mvn/stack-profiles.txt"
YML_FILE = "template-application/src/main/resources/application-stack.yml"
ROOT_POM = "pom.xml"
APP_POM = "template-application/pom.xml"


# --------------------------------------------------------------------------- 输出工具
def _utf8_stdout() -> None:
    """Windows 控制台默认不是 UTF-8，中文会乱码或抛 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass


def info(msg: str) -> None:
    print(msg)


def warn(msg: str) -> None:
    print("WARN  " + msg)


def fail(msg: str) -> None:
    print("ERROR " + msg)


# --------------------------------------------------------------------------- 选择与校验
def build_selection(security: str, orm: str, cache: str) -> dict:
    return {"security": security, "orm": orm, "cache": cache}


def validate_values(selection: dict) -> list:
    errors = []
    for dim, cfg in DIMENSIONS.items():
        value = selection.get(dim)
        if value not in cfg["values"]:
            errors.append(
                "%s（%s）取值 '{%s}' 不合法，可选：%s"
                % (dim, cfg["label"], value, " / ".join(cfg["values"]))
            )
    return errors


def shared_store_available(selection: dict) -> bool:
    return selection["cache"] == "redis"


def degraded_capabilities(selection: dict) -> list:
    """返回因缺少共享存储而降级的能力列表。"""
    if shared_store_available(selection):
        return []
    return list(SHARED_STORE_CAPABILITIES)


# --------------------------------------------------------------------------- 渲染
# 约定：render_* 只产出**区间内部**的正文，缩进按「标记所在行的缩进」为 0 基线。
# 最终缩进由 replace_block 统一套上，这样 marker 缩进多少、正文就缩进多少。
def render_modules_block(selection: dict) -> str:
    lines = [MARKER_MODULES_NOTE]
    for name in BASE_MODULES:
        lines.append("<module>%s</module>" % name)
    # 可插拔模块：按 DIMENSIONS 的声明顺序，保证确定性
    for dim in DIMENSIONS:
        lines.append("<module>%s</module>" % DIMENSIONS[dim]["values"][selection[dim]])
    lines.append("<module>%s</module>" % APP_MODULE)
    return "\n".join(lines)


def render_deps_block(selection: dict) -> str:
    lines = [MARKER_DEPS_NOTE]
    for dim in DIMENSIONS:
        artifact = DIMENSIONS[dim]["values"][selection[dim]]
        lines += [
            "<dependency>",
            "    <groupId>%s</groupId>" % GROUP_ID,
            "    <artifactId>%s</artifactId>" % artifact,
            "    <version>${project.version}</version>",
            "</dependency>",
        ]
    return "\n".join(lines)


def render_stack_json(selection: dict) -> str:
    """生成物必须是 (security, orm, cache) 的**纯函数**。

    这里刻意不记录 preset 名：预设只是「怎么选」的便捷入口，不是「选成了什么」的一部分。
    一旦把 preset 写进生成物，`--check` 就得知道当初用的预设才能复现，CI 里就会出错；
    人手改 stack.json 也会让 preset 名变成一句谎话。
    """
    degraded = degraded_capabilities(selection)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "security": selection["security"],
        "orm": selection["orm"],
        "cache": selection["cache"],
        "sharedCache": shared_store_available(selection),
        "degraded": [key for key, _ in degraded],
        "modules": {
            dim: DIMENSIONS[dim]["values"][selection[dim]] for dim in DIMENSIONS
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def render_stack_yml(selection: dict) -> str:
    degraded_keys = {key for key, _ in degraded_capabilities(selection)}
    shared = shared_store_available(selection)
    lines = [
        "# 本文件由 scripts/stack-select.py 生成，请勿手工编辑。",
        "# 唯一事实来源：stack.json（改那一个，然后重新跑脚本）。",
        "",
        "stack:",
        "  security: %s" % selection["security"],
        "  orm: %s" % selection["orm"],
        "  cache: %s" % selection["cache"],
        "  shared-cache: %s" % ("true" if shared else "false"),
        "",
        "app:",
        "  auth:",
        "    # 以下三项依赖共享存储；cache != redis 时会降级关闭（值变为 false）",
        "    token-revocation-enabled: %s" % ("true" if "token_revocation" not in degraded_keys else "false"),
        "    fail-counter-enabled: %s" % ("true" if "fail_counter" not in degraded_keys else "false"),
        "    account-lock-enabled: %s" % ("true" if "account_lock" not in degraded_keys else "false"),
        "  audit:",
        "    # 登录审计与缓存无关，始终启用",
        "    login-log-enabled: true",
        "",
    ]
    return "\n".join(lines)


def render_profiles(selection: dict) -> str:
    parts = ["-P%s-%s" % (dim, selection[dim]) for dim in DIMENSIONS]
    return " ".join(parts) + "\n"


def render_stack_md(selection: dict) -> str:
    degraded = degraded_capabilities(selection)
    profiles = render_profiles(selection).strip()
    rows = []
    for dim, cfg in DIMENSIONS.items():
        rows.append(
            "| %s | %s | %s |" % (cfg["label"], selection[dim], cfg["values"][selection[dim]])
        )
    out = [
        "# 当前技术栈组合",
        "",
        "> 本文件由 `scripts/stack-select.py` 生成，请勿手工编辑。",
        "> 切换组合：改 `stack.json` 里的取值，再跑一次脚本；或直接用 `--preset` / 三个维度参数。",
        "",
        "| 维度 | 取值 | 模块 |",
        "| --- | --- | --- |",
    ]
    out += rows
    out += [
        "",
        "## 启动",
        "",
        "```shell",
        "mvn -q clean verify %s" % profiles,
        "mvn -q spring-boot:run %s -pl template-application" % profiles,
        "```",
        "",
        "## 组合说明",
        "",
        "- Maven profile：`%s`" % profiles,
        "- 共享缓存：%s" % ("是（Redis）" if shared_store_available(selection) else "否"),
    ]
    if degraded:
        out += ["", "## 降级项（缺少共享存储）", ""]
        for _, label in degraded:
            out.append("- %s：已关闭。多实例部署时该能力不可用，单实例可用。" % label)
        out += [
            "",
            "生产环境多实例部署时请把 `cache` 切回 `redis`，或在网关/应用层补齐共享状态。",
        ]
    else:
        out += ["", "未启用任何降级项。"]
    out += [""]
    return "\n".join(out)


def mvn_command(selection: dict) -> str:
    return "mvn -q clean verify %s" % render_profiles(selection).strip()


# --------------------------------------------------------------------------- marker 区间读写
def indent_block(body: str, indent: str) -> str:
    """给正文每一行的**非空**部分加前缀缩进；空行保持为空（不留尾随空白）。"""
    if not indent:
        return body
    return "\n".join((indent + line) if line.strip() else "" for line in body.split("\n"))


def replace_block(text: str, begin: str, end: str, body: str, path: str) -> str:
    """只替换 begin..end 两个标记**连同其间的全部内容**，区间外一个字符都不动。

    正文缩进跟随 begin 标记所在行的缩进；end 标记保持它原有的缩进。
    """
    start = text.find(begin)
    stop = text.find(end)
    if start < 0 or stop < 0:
        raise SystemExit(
            "ERROR %s 缺少 marker 区间：\n  %s\n  %s\n"
            "请先在文件里补上这两行（脚本不会自动创建，以免猜错位置）。" % (path, begin, end)
        )
    if stop < start:
        raise SystemExit("ERROR %s 的 marker 顺序颠倒了" % path)

    begin_line_start = text.rfind("\n", 0, start) + 1
    begin_indent = text[begin_line_start:start]
    end_line_start = text.rfind("\n", 0, stop) + 1
    end_indent = text[end_line_start:stop]

    payload = "\n".join([
        begin_indent + begin,
        indent_block(body, begin_indent),
        end_indent + end,
    ])
    return text[:begin_line_start] + payload + text[stop + len(end):]


def read_text(path: Path) -> str:
    """按 UTF-8 读入并把 CRLF / CR 归一为 LF，让渲染逻辑只面对一种换行。"""
    raw = path.read_text(encoding="utf-8")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def detect_newline(path: Path) -> str:
    """探测文件原有的换行风格，写回时保持原样，避免 CRLF 仓库被整文件改写。"""
    try:
        raw = path.read_bytes()
    except OSError:
        return "\n"
    return "\r\n" if b"\r\n" in raw else "\n"


def write_text(path: Path, text: str, dry_run: bool, newline: str = "\n") -> None:
    if dry_run:
        info("---- [dry-run] %s ----" % path)
        info(text.rstrip("\n"))
        info("---- [dry-run] end ----")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    out = text if newline == "\n" else text.replace("\n", newline)
    # newline="" 表示不做平台翻译，换行完全由 out 决定
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(out)


def build_outputs(root: Path, selection: dict) -> dict:
    """返回 {相对路径: 期望内容}；文本类文件全部在这里生成，便于 --check 比对。"""
    root_pom = read_text(root / ROOT_POM)
    app_pom = read_text(root / APP_POM)
    return {
        ROOT_POM: replace_block(
            root_pom, MARKER_MODULES_BEGIN, MARKER_MODULES_END,
            render_modules_block(selection), ROOT_POM,
        ),
        APP_POM: replace_block(
            app_pom, MARKER_DEPS_BEGIN, MARKER_DEPS_END,
            render_deps_block(selection), APP_POM,
        ),
        STACK_JSON: render_stack_json(selection),
        YML_FILE: render_stack_yml(selection),
        PROFILES_FILE: render_profiles(selection),
        STACK_MD: render_stack_md(selection),
    }


# --------------------------------------------------------------------------- 交互式菜单
def _prompt(prompt: str) -> str:
    """读一行输入。读到 EOF（管道里没有更多数据）时给出可操作的提示而不是 traceback。"""
    try:
        return input(prompt).strip()
    except EOFError:
        raise SystemExit(
            "ERROR 交互输入被中断（stdin 已结束）。\n"
            "非交互场景请显式给参数，例如：--preset classic 或 --yes"
        )


def interactive_menu(current: dict) -> dict:
    selection = dict(current)
    info("当前组合：%s" % " / ".join("%s=%s" % (k, selection[k]) for k in DIMENSIONS))
    info("直接回车表示保持当前取值。\n")
    for dim, cfg in DIMENSIONS.items():
        keys = list(cfg["values"])
        info("%s（%s）" % (cfg["label"], dim))
        for idx, key in enumerate(keys, 1):
            info("  %d) %-14s -> %s" % (idx, key, cfg["values"][key]))
        raw = _prompt("  选择 [1-%d，回车保持不变]： " % len(keys))
        if raw == "":
            continue
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            selection[dim] = keys[int(raw) - 1]
        elif raw in keys:
            selection[dim] = raw
        else:
            raise SystemExit("ERROR 无效输入：%s" % raw)
        info("")
    return selection


# --------------------------------------------------------------------------- 主流程
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="stack-select.py",
        description="后端通用模板技术栈选择器（安全 / 数据 / 缓存三维度可插拔）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", default=".", help="工程根目录，默认当前目录")
    parser.add_argument("--security", choices=list(DIMENSIONS["security"]["values"]))
    parser.add_argument("--orm", choices=list(DIMENSIONS["orm"]["values"]))
    parser.add_argument("--cache", choices=list(DIMENSIONS["cache"]["values"]))
    parser.add_argument("--preset", choices=list(PRESETS), help="使用预设组合")
    parser.add_argument("--list", action="store_true", help="列出可选值与预设后退出")
    parser.add_argument("--check", action="store_true",
                        help="只校验生成物与 stack.json 是否一致，不一致以非 0 退出（CI 用）")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要写入的内容")
    parser.add_argument("--print-mvn", action="store_true", help="只输出对应的 mvn 命令")
    parser.add_argument("--allow-degraded-cache", action="store_true",
                        help="显式接受 cache != redis 带来的能力降级（令牌撤销/失败计数/账号锁定）")
    parser.add_argument("--yes", "-y", action="store_true", help="非交互模式（缺少维度时用默认值）")
    return parser.parse_args(argv)


def list_options() -> None:
    info("可用维度与取值：")
    for dim, cfg in DIMENSIONS.items():
        info("  --%s : %s" % (dim, " / ".join(cfg["values"])))
        for key, artifact in cfg["values"].items():
            info("      %-14s -> %s" % (key, artifact))
    info("")
    info("预设组合：")
    for name, cfg in PRESETS.items():
        info("  %-13s security=%-8s orm=%-14s cache=%-9s  # %s"
             % (name, cfg["security"], cfg["orm"], cfg["cache"], cfg["desc"]))
    info("")
    info("注意：预设 minimal / local-cache 自带 allow_degraded_cache，其余预设都需要共享缓存。")


def load_current(root: Path) -> dict:
    path = root / STACK_JSON
    if path.exists():
        try:
            data = json.loads(read_text(path))
            return {dim: data.get(dim, DIMENSIONS[dim]["default"]) for dim in DIMENSIONS}
        except Exception:  # noqa: BLE001
            warn("%s 解析失败，退回默认取值" % STACK_JSON)
    return {dim: DIMENSIONS[dim]["default"] for dim in DIMENSIONS}


def do_check(root: Path, selection: dict) -> int:
    try:
        expected = build_outputs(root, selection)
    except SystemExit as exc:
        fail(str(exc))
        return 1
    mismatched = []
    for rel, want in expected.items():
        path = root / rel
        if not path.exists():
            mismatched.append((rel, "文件不存在"))
            continue
        got = read_text(path)
        # pom 与 yml：只比 marker 区间 / 全文；这里统一比全文，因为生成物都是受管的
        if got != want:
            mismatched.append((rel, "内容与 stack.json 不一致"))
    if mismatched:
        fail("--check 未通过，以下文件需要重新生成（执行不带 --check 的同一条命令即可）：")
        for rel, why in mismatched:
            info("  - %s：%s" % (rel, why))
        return 1
    info("OK    --check 通过：6 个生成物与 stack.json 完全一致")
    return 0


def main(argv=None) -> int:
    _utf8_stdout()
    args = parse_args(argv)

    if args.list:
        list_options()
        return 0

    root = Path(args.root).resolve()
    if not (root / ROOT_POM).exists():
        fail("在 %s 下找不到 pom.xml，--root 指错了？" % root)
        return 1

    current = load_current(root)

    # ---- 决定本次选择：预设 > 显式维度 > stack.json > 交互
    # --check / --print-mvn 是给 CI 与脚本用的，**永不交互**：完全以 stack.json 为准。
    # （在分配了 PTY 的环境里 sys.stdin.isatty() 会是 True，不能靠它兜底。）
    non_interactive = args.check or args.print_mvn
    preset = args.preset or ""
    allow_degraded = args.allow_degraded_cache

    if preset:
        cfg = PRESETS[preset]
        selection = build_selection(cfg["security"], cfg["orm"], cfg["cache"])
        allow_degraded = allow_degraded or bool(cfg.get("allow_degraded_cache"))
        # 预设允许被显式维度覆盖
        for dim in DIMENSIONS:
            explicit = getattr(args, dim)
            if explicit:
                selection[dim] = explicit
                if dim == "cache" and explicit == "redis":
                    allow_degraded = args.allow_degraded_cache
    else:
        explicit_any = any(getattr(args, dim) for dim in DIMENSIONS)
        if non_interactive and not explicit_any:
            selection = dict(current)
        elif explicit_any or args.yes or not sys.stdin.isatty():
            selection = build_selection(
                args.security or current["security"],
                args.orm or current["orm"],
                args.cache or current["cache"],
            )
        else:
            selection = interactive_menu(current)

    # ---- 取值白名单校验
    errors = validate_values(selection)
    if errors:
        fail("取值校验未通过：")
        for err in errors:
            info("  - " + err)
        return 1

    if args.print_mvn:
        info(mvn_command(selection))
        return 0

    # ---- --check 是「核对」，不是「决策」：不做降级门禁（stack.json 已记录该组合）
    if args.check:
        return do_check(root, selection)

    # ---- 生成前的能力依赖校验：cache != redis 会带来降级，必须显式接受
    degraded = degraded_capabilities(selection)
    if degraded and not allow_degraded:
        fail("组合 cache=%s 会让以下能力降级，脚本默认拒绝：" % selection["cache"])
        for _, label in degraded:
            info("  - %s" % label)
        info("")
        info("原因：这三项能力都需要多实例共享的状态。用本地缓存或没有缓存时，")
        info("      单实例能跑通，但一旦部署两个副本，撤销与锁定就会各算各的。")
        info("")
        info("处理方式二选一：")
        info("  a) 换回共享缓存：    --cache redis")
        info("  b) 明确接受降级：    --allow-degraded-cache（生成物会把这些开关置为 false）")
        return 1

    # ---- 生成
    outputs = build_outputs(root, selection)
    for rel, content in outputs.items():
        write_text(root / rel, content, args.dry_run, detect_newline(root / rel))

    info("")
    info("选中组合：security=%s  orm=%s  cache=%s%s"
         % (selection["security"], selection["orm"], selection["cache"],
            ("（预设 %s）" % preset) if preset else ""))
    info("已写出 %d 个文件：%s" % (len(outputs), "、".join(outputs)))
    if degraded:
        info("")
        for _, label in degraded:
            warn("已降级：%s（生成物中已置为 false）" % label)
    info("")
    info("下一步：")
    info("  %s" % mvn_command(selection))
    info("  mvn help:active-profiles   # 确认生效的 profile")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
    except SystemExit as exc:  # build_outputs 里抛出的 marker 缺失
        if isinstance(exc.code, str):
            print(exc.code)
            sys.exit(1)
        raise
