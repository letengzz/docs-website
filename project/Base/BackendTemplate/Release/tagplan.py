#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布标签计划生成与校验器。

第 80 天（第 4 周③：镜像推送与发布策略）的可执行交付物。

它只做一件纯逻辑的事：**把「这一次要推哪些标签、部署命令引用哪个标签、怎么退回去」
算清楚并校验成计划**。之所以把它独立成工具而不是写进流水线脚本，是因为发布策略里
最容易出错的那部分（标签分层与「谁可以出现在部署命令里」）与 Docker、registry 都无关，
完全可以离线验证——而依赖 registry 才能验证的部分一旦出错，代价是线上事故。

零第三方依赖。

用法::

    # 生成计划（人读）
    python tagplan.py --version 1.2.0 --sha <40位hex> --registry reg.example.com/team \\
                      --repo backend-template --channel prod

    # 生成计划（机器读，喂给流水线）
    python tagplan.py --version 1.2.0 --sha <40位hex> --json

    # 校验一份既有计划（CI 门禁：任何人改过计划都要过这一关）
    python tagplan.py --verify plan.json

    # 只校验不生成：给流水线留一个「先算再推」的干燥开关
    python tagplan.py --version 1.2.0 --sha <40位hex> --dry-run --json

退出码：0 = 通过；1 = 参数或校验失败（stderr 给出原因）。

不变量（INV1~INV6，定义见 verify_plan 的 docstring）：任何一份计划都必须同时满足。
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# ---------------------------------------------------------------- 常量

#: 允许的环境指针取值。写死枚举而不是自由文本，是为了避免出现
#: 「prod / production / prd」三套写法各自指向同一个环境却互不知情。
CHANNELS = ("dev", "staging", "prod")

#: 预发布后缀。带这些后缀的版本不得打 prod 指针。
PRERELEASE_RE = re.compile(r"-(rc|beta|alpha)\.(\d+)$")

#: 严格的语义化版本（MAJOR.MINOR.PATCH），可选预发布后缀。
#: 明确不接受 `1.2`（少一段）、`v1.2.0`（带前导 v）、`1.2.0+build9`（带构建元数据）。
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-(?:rc|beta|alpha)\.\d+)?$")

#: 仓库名允许的字符（Docker 的 repository name 规则）。
REPO_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")

#: registry / namespace 一段允许的字符。
REGSEG_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")

SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")

#: 身份标签用的短 sha 长度。12 位在「同一个仓库一次发布几十个提交」的量级下
#: 碰撞概率可忽略，同时在日志里足够好读；这是取舍不是定理，改这里要保持一致。
SHORT_SHA_LEN = 12

#: 绝不允许出现在任何命令里的标签。
FORBIDDEN_TAG = "latest"


class TagPlanError(Exception):
    """计划生成或校验失败。"""


# ---------------------------------------------------------------- 校验小工具


def _fail(msg: str) -> None:
    raise TagPlanError(msg)


def normalize_sha(sha: str) -> str:
    """校验并规范化 40 位 git sha：必须 40 位十六进制，统一转小写。

    只接受完整 40 位而不是 7 位短 sha：短 sha 的长度是「当下够用」的经验值，
    仓库长到一定规模后不保证唯一；而**身份标签一旦不唯一，回滚就会指错镜像**。
    需要好读时在展示层截短（见 SHORT_SHA_LEN），但入库与比对一律用全长。
    """
    if not isinstance(sha, str) or not SHA_RE.match(sha):
        _fail(f"sha 必须是 40 位十六进制 git sha，收到：{sha!r}")
    return sha.lower()


def short_sha(sha: str) -> str:
    """取身份标签用的短 sha（已规范化的小写全长 sha）。"""
    return sha[:SHORT_SHA_LEN]


def validate_version(version: str) -> str:
    """校验语义化版本，返回原值。"""
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        _fail(
            f"版本必须形如 MAJOR.MINOR.PATCH（可带 -rc.N/-beta.N/-alpha.N），"
            f"不接受前导 v 与构建元数据；收到：{version!r}"
        )
    return version


def is_prerelease(version: str) -> bool:
    """是否为预发布版本。"""
    return bool(PRERELEASE_RE.search(version))


def validate_base(registry: str, repo: str) -> str:
    """校验并拼出镜像名前缀 `<registry>/<repo>`。"""
    if not registry:
        _fail("registry 不能为空（部署用的镜像名必须带完整来源，靠默认 registry 会拉错仓库）")
    segs = registry.split("/")
    for i, s in enumerate(segs):
        # 首段允许带端口（`host:5000` 这种内网 registry 很常见），其余段不允许。
        if i == 0 and ":" in s:
            host, _, port = s.partition(":")
            if not REGSEG_RE.match(host):
                _fail(f"registry host 不合法：{host!r}")
            if not port.isdigit() or not 1 <= int(port) <= 65535:
                _fail(f"registry 端口不合法：{port!r}")
            continue
        if not REGSEG_RE.match(s):
            _fail(f"registry 段不合法（须小写、数字、. _ -）：{s!r}")
    if not REPO_RE.match(repo):
        _fail(f"repo 不合法（须小写、数字、. _ -）：{repo!r}")
    return f"{registry}/{repo}"


# ---------------------------------------------------------------- 计划生成


def build_plan(
    version: str,
    sha: str,
    registry: str = "reg.example.com/team",
    repo: str = "backend-template",
    channel: str = "staging",
    previous_sha: str | None = None,
) -> dict:
    """生成一份发布标签计划（纯函数：同样的入参永远得到同样的计划）。

    计划把标签分成三层，分层的依据是**「这个标签会不会变」**而不是「这个标签好不好看」：

    ==========  ==================  ==========  ==================================
    层          形式                会不会变    谁可以引用
    ==========  ==================  ==========  ==================================
    身份        ``sha-<12>``        永不变      部署、回滚、审计、issue 里贴
    版本        ``1.2.0``           永不变      发布公告、对外沟通、release note
    环境指针    ``prod`` / ``staging``  会变    只能用于「问现在跑的是什么」
    ==========  ==================  ==========  ==================================

    第 4 层 ``latest`` **不生成**：它在语义上就是「最后被推上来的那个」，
    既不能回答「线上是哪一次提交」，又会被任何一次误推悄悄改掉。
    """
    version = validate_version(version)
    sha = normalize_sha(sha)
    base = validate_base(registry, repo)

    if channel not in CHANNELS:
        _fail(f"channel 必须是 {CHANNELS} 之一，收到：{channel!r}")
    if is_prerelease(version) and channel == "prod":
        _fail(
            f"预发布版本 {version} 不得打 prod 环境指针："
            "预发布与生产是两种发布，用同一个指针会让「生产在跑 rc」这件事无人察觉"
        )
    if previous_sha is not None:
        previous_sha = normalize_sha(previous_sha)

    identity = f"sha-{short_sha(sha)}"
    ref = f"{base}:{identity}"
    version_ref = f"{base}:{version}"

    tags = {
        "immutable": [
            {"tag": identity, "role": "identity", "ref": ref},
            {"tag": version, "role": "version", "ref": version_ref},
        ],
        # 环境指针是**计划里唯一会变的东西**，单独放一层就是为了让 review 时一眼看到它。
        "mutable": [{"tag": channel, "role": "channel", "ref": f"{base}:{channel}"}],
    }

    commands = {
        "build": (
            f"docker buildx build --platform linux/amd64,linux/arm64 \\\n"
            f"    --provenance=true --sbom=true \\\n"
            f"    --label org.opencontainers.image.revision={sha} \\\n"
            f"    -t {ref} -t {version_ref} \\\n"
            f"    --push ."
        ),
        "sign": [f"cosign sign --yes {ref}", f"cosign sign --yes {version_ref}"],
        # 只推不可变层。环境指针单独一步、单独一次审批。
        "push_immutable": [f"docker push {ref}", f"docker push {version_ref}"],
        "promote_channel": [f"docker tag {ref} {base}:{channel}", f"docker push {base}:{channel}"],
        # 部署引用身份标签：这样「部署命令本身」就记录了是哪次提交。
        "deploy": (
            f"IMAGE_REF={ref} docker compose -f compose.yaml -f compose.prod.yaml up -d"
        ),
        # 想知道「现在跑的是什么」时才用环境指针，且必须回到身份。
        "resolve": [
            f"docker image inspect {base}:{channel} --format '{{{{.Id}}}}'",
            f"docker image inspect {ref} --format '{{{{index .Config.Labels \"org.opencontainers.image.revision\"}}}}'",
        ],
    }
    if previous_sha is not None:
        commands["rollback"] = (
            f"IMAGE_REF={base}:sha-{short_sha(previous_sha)} "
            f"docker compose -f compose.yaml -f compose.prod.yaml up -d"
        )

    notes = [
        "环境指针（mutable 层）会变：它回答「现在是什么」，不回答「这是哪次提交」。",
        "部署命令只引用不可变层；引用环境指针会让「线上跑的是哪次提交」重新变成未知。",
        f"镜像内写入 org.opencontainers.image.revision={sha}，使镜像身份可自证、不必依赖外部台账。",
    ]
    if previous_sha is None:
        notes.append("未提供 --previous-sha：本次计划不含 rollback 命令，回滚需手动指定上一个身份标签。")

    return {
        "schema": 1,
        "registry": registry,
        "repo": repo,
        "base": base,
        "sha": sha,
        "identity": identity,
        "version": version,
        "channel": channel,
        "prerelease": is_prerelease(version),
        "previous_sha": previous_sha,
        "tags": tags,
        "commands": commands,
        "notes": notes,
    }


# ---------------------------------------------------------------- 计划校验


def verify_plan(plan: dict) -> list[str]:
    """校验一份计划是否满足全部不变量，返回问题列表（空列表 = 通过）。

    不变量：

    - **INV1** 身份层有且只有一个标签，形如 ``sha-<12>``，且等于 ``plan['sha']`` 的前 12 位。
      「有且只有一个」是因为回滚要靠它唯一定位；两个身份标签等于没有身份。
    - **INV2** 版本标签符合严格语义化版本，且不在身份层里重复出现。
    - **INV3** 任何 ``push`` 命令不推送 ``latest``，任何命令的**引用位置**（``:`` 之后）
      不出现 ``latest``。
    - **INV4** 部署与回滚命令引用的标签必须落在**可引用的不可变集合**内——即本计划创建的
      身份/版本标签，或（生成回滚命令时）上一个发布的身份标签；不得引用环境指针。
      允许引用「上一个发布的身份标签」是刻意的：回滚本就该指向旧镜像，若强行要求它属于
      本次构建产物，回滚就只能靠重新构建来「实现」，而那不叫回滚。
    - **INV5** 环境指针层的标签必须是 ``CHANNELS`` 枚举内的值，且不得与身份/版本层重名。
    - **INV6** 预发布版本不得生成 ``prod`` 环境指针。
    """
    problems: list[str] = []
    if not isinstance(plan, dict):
        return ["计划必须是 JSON 对象"]

    imm = plan.get("tags", {}).get("immutable", [])
    mut = plan.get("tags", {}).get("mutable", [])
    if not isinstance(imm, list) or not isinstance(mut, list):
        return ["tags.immutable / tags.mutable 必须是数组"]

    sha = plan.get("sha")
    version = plan.get("version")
    channel = plan.get("channel")
    base = plan.get("base")

    # ---- INV1 身份唯一
    identities = [t for t in imm if t.get("role") == "identity"]
    if len(identities) != 1:
        problems.append(f"INV1 身份层必须恰好一个标签，实际 {len(identities)} 个")
    else:
        itag = identities[0].get("tag", "")
        if isinstance(sha, str) and itag != f"sha-{sha[:SHORT_SHA_LEN]}":
            problems.append(
                f"INV1 身份标签 {itag!r} 与 sha 前 {SHORT_SHA_LEN} 位不一致（sha={sha!r}）"
            )
        if not re.match(r"^sha-[0-9a-f]{%d}$" % SHORT_SHA_LEN, itag):
            problems.append(f"INV1 身份标签格式应为 sha-<{SHORT_SHA_LEN}位小写hex>，收到 {itag!r}")

    # ---- INV2 版本标签
    ver_tags = [t for t in imm if t.get("role") == "version"]
    if len(ver_tags) != 1:
        problems.append(f"INV2 版本层必须恰好一个标签，实际 {len(ver_tags)} 个")
    else:
        vtag = ver_tags[0].get("tag", "")
        if not SEMVER_RE.match(str(vtag)):
            problems.append(f"INV2 版本标签不符合严格语义化版本：{vtag!r}")
        if isinstance(version, str) and vtag != version:
            problems.append(f"INV2 版本标签 {vtag!r} 与 plan.version {version!r} 不一致")

    all_immutable_tags = {t.get("tag") for t in imm}

    # ---- INV3 latest 全面禁用：扫描命令里的**每一个** token 的镜像引用部分。
    # 只看首个 token 是不够的——`docker run <base>:latest` 的首 token 是 `docker`，
    # 而真正被引用的镜像在第三个 token 上。这类「命令里某个位置出现 latest」的写法
    # 恰恰是事故现场最常见的样子，必须逐 token 查。
    def _iter_cmds():
        for k, v in plan.get("commands", {}).items():
            if isinstance(v, list):
                for item in v:
                    yield k, item
            elif isinstance(v, str):
                yield k, v

    def _ref_tag(text: str) -> str:
        """取镜像引用的标签部分（对该 token 的最后一个 ':' 之后）。"""
        if ":" not in text:
            return ""
        return text.rsplit(":", 1)[-1]

    for key, cmd in _iter_cmds():
        if not isinstance(cmd, str):
            continue
        for token in cmd.split():
            if _ref_tag(token) == FORBIDDEN_TAG:
                problems.append(f"INV3 命令 {key!r} 引用了 {FORBIDDEN_TAG}：{token!r}")

    # ---- INV4 部署/回滚只引用不可变标签
    # 可引用的集合 = 本计划创建的身份/版本标签 ∪ 上一个发布的身份标签。
    # **回滚必须能指向「不是本次构建产物」的镜像**——否则回滚就退化成重新构建，
    # 而重新构建出来的东西是否等价于出事时线上那个镜像，谁也证明不了。
    # 这也是「身份标签要永久保留」的原因：回滚能力取决于旧标签还在不在。
    referenceable = set(all_immutable_tags)
    prev = plan.get("previous_sha")
    if isinstance(prev, str) and SHA_RE.match(prev):
        referenceable.add(f"sha-{prev[:SHORT_SHA_LEN]}")

    for key in ("deploy", "rollback"):
        cmd = plan.get("commands", {}).get(key)
        if not isinstance(cmd, str):
            continue
        m = re.search(r"IMAGE_REF=(\S+)", cmd)
        if not m:
            problems.append(f"INV4 {key} 命令必须显式给出 IMAGE_REF=<不可变标签>：{cmd!r}")
            continue
        ref = m.group(1)
        tag = _ref_tag(ref)
        if tag in referenceable:
            continue
        if tag == channel:
            problems.append(
                f"INV4 {key} 引用了环境指针 {tag!r}：环境指针会变，" "部署命令必须指向不可变层，否则无法回答「线上是哪次提交」"
            )
        else:
            problems.append(f"INV4 {key} 引用的标签 {tag!r} 不在可引用的不可变集合内：{ref!r}")

    # ---- INV5 环境指针枚举与去重
    for t in mut:
        tag = t.get("tag")
        if tag not in CHANNELS:
            problems.append(f"INV5 环境指针必须是 {CHANNELS} 之一，收到 {tag!r}")
        if tag in all_immutable_tags:
            problems.append(f"INV5 环境指针 {tag!r} 与不可变层重名（会把身份层原地覆盖掉）")
    if not base or not isinstance(base, str) or "/" not in base:
        problems.append("INV5 base 必须是 <registry>/<repo> 形式")

    # ---- INV6 预发布不得打 prod
    if plan.get("prerelease") and channel == "prod":
        problems.append("INV6 预发布版本不得生成 prod 环境指针")

    return problems


def check_or_die(plan: dict) -> None:
    """校验计划，有问题则抛 TagPlanError。"""
    problems = verify_plan(plan)
    if problems:
        _fail("计划未通过校验：\n  - " + "\n  - ".join(problems))


# ---------------------------------------------------------------- 输出


def render(plan: dict) -> str:
    """把计划渲染成人读文本。"""
    out: list[str] = []
    out.append(f"镜像前缀 : {plan['base']}")
    out.append(f"提交     : {plan['sha']}  →  身份标签 {plan['identity']}")
    out.append(f"版本     : {plan['version']}" + ("（预发布）" if plan["prerelease"] else ""))
    out.append(f"环境指针 : {plan['channel']}")
    out.append("")
    out.append("标签计划：")
    for layer in ("immutable", "mutable"):
        kind = "不可变" if layer == "immutable" else "会变  "
        for t in plan["tags"][layer]:
            out.append(f"  [{kind}] {t['ref']}   ({t['role']})")
    out.append("")
    out.append("命令：")
    for key in ("build", "sign", "push_immutable", "promote_channel", "deploy", "resolve", "rollback"):
        v = plan["commands"].get(key)
        if v is None:
            continue
        out.append(f"  # {key}")
        for item in v if isinstance(v, list) else [v]:
            for line in str(item).splitlines():
                out.append(f"  {line}")
        out.append("")
    out.append("说明：")
    for n in plan["notes"]:
        out.append(f"  - {n}")
    return "\n".join(out)


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="tagplan.py",
        description="发布标签计划生成与校验（第 80 天交付物）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--version", help="语义化版本，如 1.2.0 或 1.3.0-rc.1")
    ap.add_argument("--sha", help="40 位 git sha（构建该镜像的那次提交）")
    ap.add_argument("--registry", default="reg.example.com/team", help="registry 与 namespace")
    ap.add_argument("--repo", default="backend-template", help="仓库名")
    ap.add_argument("--channel", default="staging", choices=CHANNELS, help="要更新的环境指针")
    ap.add_argument("--previous-sha", dest="previous_sha", help="上一个成功发布的 sha（用于生成回滚命令）")
    ap.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    ap.add_argument("--dry-run", action="store_true", help="只生成与校验，不打印可直接执行的命令块")
    ap.add_argument("--verify", metavar="PLAN.json", help="校验一份既有计划")
    args = ap.parse_args(argv)

    try:
        if args.verify:
            with open(args.verify, "r", encoding="utf-8") as f:
                plan = json.load(f)
            problems = verify_plan(plan)
            if problems:
                print("FAIL: 计划未通过校验", file=sys.stderr)
                for p in problems:
                    print(f"  - {p}", file=sys.stderr)
                return 1
            print(f"OK: {args.verify} 通过全部不变量（INV1~INV6）")
            return 0

        if not args.version or not args.sha:
            ap.error("生成计划需要 --version 与 --sha（或改用 --verify）")

        plan = build_plan(
            version=args.version,
            sha=args.sha,
            registry=args.registry,
            repo=args.repo,
            channel=args.channel,
            previous_sha=args.previous_sha,
        )
        check_or_die(plan)

        if args.json:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        elif args.dry_run:
            print("DRY-RUN OK：计划已生成并通过 INV1~INV6 校验")
            print(render(plan))
        else:
            print(render(plan))
        return 0
    except TagPlanError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"FAIL: 读取计划失败：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
