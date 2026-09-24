#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tagplan.py 的自测：把「发布策略」里能离线判定的部分全部断言成测试。

零第三方依赖，直接运行::

    python selftest.py

退出码 0 = 全部通过；1 = 有断言失败（stderr 打印失败项）。

为什么值得写这么多断言：发布策略的错法有一个共同点——**它们都不报错**。
把环境指针写进部署命令、把 `latest` 推到线上、给预发布版本打 prod 指针，
这三件事在流水线里都会「成功」，直到某天有人发现线上跑的不是他以为的那次提交。
所以这些约束必须由工具在推送之前拦住，而不是靠人 review 时记得。
"""

from __future__ import annotations

import copy
import json
import sys

from tagplan import (
    CHANNELS,
    SHORT_SHA_LEN,
    TagPlanError,
    build_plan,
    is_prerelease,
    normalize_sha,
    render,
    verify_plan,
)

SHA = "9f2c1a4b6d8e0f1a2b3c4d5e6f708192a3b4c5d6"  # 40 位
SHA2 = "0123456789abcdef0123456789abcdef01234567"
SHA_UP = SHA.upper()

PASS = 0
FAIL: list[str] = []


def ok(name: str, cond: bool, extra: str = "") -> None:
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(f"{name}{(' — ' + extra) if extra else ''}")


def raises(name: str, fn, *a, **kw) -> None:
    """断言 fn 抛出 TagPlanError。"""
    try:
        fn(*a, **kw)
    except TagPlanError:
        ok(name, True)
    except Exception as e:  # noqa: BLE001
        ok(name, False, f"抛出了 {type(e).__name__} 而非 TagPlanError: {e}")
    else:
        ok(name, False, "未抛异常")


def plan_ok(name: str, plan, expect: int = 0) -> None:
    """断言计划的问题数等于 expect。"""
    probs = verify_plan(plan)
    ok(name, len(probs) == expect, f"问题数 {len(probs)} != {expect}：{probs}")


# ================================================================ 1. 基础生成

p = build_plan(version="1.2.0", sha=SHA, registry="reg.example.com/team", repo="backend-template", channel="staging")

ok("1.1 身份标签 = sha-<12位>", p["identity"] == f"sha-{SHA[:SHORT_SHA_LEN]}", p["identity"])
ok("1.2 身份标签落在 base 上", p["tags"]["immutable"][0]["ref"] == f"reg.example.com/team/backend-template:sha-{SHA[:SHORT_SHA_LEN]}")
ok("1.3 版本标签 = 1.2.0", p["tags"]["immutable"][1]["tag"] == "1.2.0")
ok("1.4 环境指针标签 = staging", [t["tag"] for t in p["tags"]["mutable"]] == ["staging"])
ok("1.5 不可变层恰好 2 个", len(p["tags"]["immutable"]) == 2)
ok("1.6 prerelease=False", p["prerelease"] is False)
plan_ok("1.7 合法计划无问题", p)

# 确定性：同输入同输出（幂等是「生成器」能被 review 的前提）
p2 = build_plan(version="1.2.0", sha=SHA, registry="reg.example.com/team", repo="backend-template", channel="staging")
ok("1.8 生成是纯函数（两次输出完全一致）", json.dumps(p, sort_keys=True) == json.dumps(p2, sort_keys=True))

# 大写 sha 规范化
p_up = build_plan(version="1.2.0", sha=SHA_UP, channel="staging")
ok("1.9 大写 sha 被规范化为小写", p_up["sha"] == SHA.lower())
ok("1.10 规范化后与传入小写结果一致", json.dumps(p_up, sort_keys=True) == json.dumps(p, sort_keys=True))

# ================================================================ 2. sha 校验

raises("2.1 拒绝 39 位 sha", normalize_sha, SHA[:39])
raises("2.2 拒绝 41 位 sha", normalize_sha, SHA + "a")
raises("2.3 拒绝非十六进制", normalize_sha, "z" * 40)
ok("2.4 接受 40 位 hex", normalize_sha(SHA) == SHA)
raises("2.5 拒绝空 sha", normalize_sha, "")

# ================================================================ 3. 版本校验

for bad in ("1.2", "v1.2.0", "1.2.0+build9", "1.2.0.1", "1.2.0-", "abc", "1.2.0-rc"):
    raises(f"3.x 拒绝非法版本 {bad!r}", build_plan, version=bad, sha=SHA)

for good in ("0.0.1", "1.2.0", "10.20.30", "1.3.0-rc.1", "2.0.0-beta.12", "3.1.0-alpha.3"):
    try:
        build_plan(version=good, sha=SHA, channel="staging")
        ok(f"3.y 接受合法版本 {good!r}", True)
    except TagPlanError as e:
        ok(f"3.y 接受合法版本 {good!r}", False, str(e))

ok("3.z1 is_prerelease('1.2.0')=False", is_prerelease("1.2.0") is False)
ok("3.z2 is_prerelease('1.2.0-rc.1')=True", is_prerelease("1.2.0-rc.1") is True)

# ================================================================ 4. registry / repo 校验

raises("4.1 拒绝空 registry", build_plan, version="1.2.0", sha=SHA, registry="", channel="staging")
raises("4.2 拒绝大写 registry", build_plan, version="1.2.0", sha=SHA, registry="Reg.example.com/team", channel="staging")
raises("4.3 拒绝大写 repo", build_plan, version="1.2.0", sha=SHA, repo="BackendTemplate", channel="staging")
raises("4.4 拒绝非法端口", build_plan, version="1.2.0", sha=SHA, registry="reg.local:99999/team", channel="staging")

p_port = build_plan(version="1.2.0", sha=SHA, registry="reg.local:5000/team", repo="bt", channel="staging")
ok("4.5 接受带端口的 registry", p_port["base"] == "reg.local:5000/team/bt")
plan_ok("4.6 带端口计划仍合法", p_port)

# ================================================================ 5. channel 与预发布（INV5 / INV6）

for ch in CHANNELS:
    try:
        build_plan(version="1.2.0", sha=SHA, channel=ch)
        ok(f"5.1 接受合法 channel {ch!r}", True)
    except TagPlanError as e:
        ok(f"5.1 接受合法 channel {ch!r}", False, str(e))

raises("5.2 拒绝非法 channel 'production'", build_plan, version="1.2.0", sha=SHA, channel="production")
raises("5.3 拒绝非法 channel 'prd'", build_plan, version="1.2.0", sha=SHA, channel="prd")

raises("5.4 预发布 + prod 被拒（生成期）", build_plan, version="1.3.0-rc.1", sha=SHA, channel="prod")

p_rc = build_plan(version="1.3.0-rc.1", sha=SHA, channel="staging")
ok("5.5 预发布 + staging 允许", p_rc["prerelease"] is True)
plan_ok("5.6 预发布 staging 计划合法", p_rc)

# 构造一个「预发布 + prod 指针」的计划，验证 INV6 在校验期也能拦住
bad6 = copy.deepcopy(p_rc)
bad6["channel"] = "prod"
bad6["tags"]["mutable"] = [{"tag": "prod", "role": "channel", "ref": f"{bad6['base']}:prod"}]
probs6 = verify_plan(bad6)
ok("5.7 INV6 校验期拦预发布+prod", any("INV6" in x for x in probs6), str(probs6))

# ================================================================ 6. INV1：身份层

bad1 = copy.deepcopy(p)
bad1["tags"]["immutable"].append({"tag": "sha-ffffffffffff", "role": "identity", "ref": "x"})
probs1 = verify_plan(bad1)
ok("6.1 INV1 拦住两个身份标签", any("INV1" in x for x in probs1), str(probs1))

bad1b = copy.deepcopy(p)
bad1b["tags"]["immutable"][0]["tag"] = "sha-" + "f" * SHORT_SHA_LEN
probs1b = verify_plan(bad1b)
ok("6.2 INV1 拦住身份标签与 sha 不一致", any("INV1" in x for x in probs1b), str(probs1b))

bad1c = copy.deepcopy(p)
bad1c["tags"]["immutable"][0]["tag"] = "9f2c1a4b6d8e"  # 少了 sha- 前缀
probs1c = verify_plan(bad1c)
ok("6.3 INV1 拦住身份标签格式错误", any("INV1" in x for x in probs1c), str(probs1c))

bad1d = copy.deepcopy(p)
bad1d["tags"]["immutable"] = bad1d["tags"]["immutable"][1:]  # 删掉身份标签
probs1d = verify_plan(bad1d)
ok("6.4 INV1 拦住身份层为空", any("INV1" in x for x in probs1d), str(probs1d))

# ================================================================ 7. INV2：版本层

bad2 = copy.deepcopy(p)
bad2["tags"]["immutable"][1]["tag"] = "v1.2.0"
probs2 = verify_plan(bad2)
ok("7.1 INV2 拦住带 v 前缀的版本标签", any("INV2" in x for x in probs2), str(probs2))

bad2b = copy.deepcopy(p)
bad2b["tags"]["immutable"].append({"tag": "1.2.1", "role": "version", "ref": "x"})
probs2b = verify_plan(bad2b)
ok("7.2 INV2 拦住两个版本标签", any("INV2" in x for x in probs2b), str(probs2b))

bad2c = copy.deepcopy(p)
bad2c["version"] = "9.9.9"
probs2c = verify_plan(bad2c)
ok("7.3 INV2 拦住版本标签与 plan.version 不一致", any("INV2" in x for x in probs2c), str(probs2c))

# ================================================================ 8. INV3：latest 全禁用

bad3 = copy.deepcopy(p)
bad3["commands"]["push_immutable"] = [f"{p['base']}:latest"]
probs3 = verify_plan(bad3)
ok("8.1 INV3 拦住 push latest", any("INV3" in x for x in probs3), str(probs3))

bad3b = copy.deepcopy(p)
bad3b["commands"]["deploy"] = f"docker run {p['base']}:latest"
probs3b = verify_plan(bad3b)
ok("8.2 INV3 拦住 deploy 引用 latest", any("INV3" in x for x in probs3b), str(probs3b))

ok("8.3 生成计划里没有任何 ':latest'", ":latest" not in json.dumps(p), "")
ok("8.4 render 输出里没有 'latest'", "latest" not in render(p))

for ch in CHANNELS:
    for ver in ("1.0.0", "2.5.1-rc.1"):
        if ch == "prod" and is_prerelease(ver):
            continue  # prod + 预发布在生成期就该被拒，见 5.4
        pp = build_plan(version=ver, sha=SHA, channel=ch)
        ok(f"8.5 {ch}/{ver} 计划内无 latest", ":latest" not in json.dumps(pp))

# ================================================================ 9. INV4：部署只引用不可变层

bad4 = copy.deepcopy(p)
bad4["commands"]["deploy"] = f"IMAGE_REF={p['base']}:staging docker compose up -d"
probs4 = verify_plan(bad4)
ok("9.1 INV4 拦住 deploy 引用环境指针", any("INV4" in x for x in probs4), str(probs4))

bad4b = copy.deepcopy(p)
bad4b["commands"]["deploy"] = f"IMAGE_REF={p['base']}:9.9.9 docker compose up -d"
probs4b = verify_plan(bad4b)
ok("9.2 INV4 拦住 deploy 引用未知标签", any("INV4" in x for x in probs4b), str(probs4b))

bad4c = copy.deepcopy(p)
bad4c["commands"]["deploy"] = "docker compose up -d"
probs4c = verify_plan(bad4c)
ok("9.3 INV4 拦住缺失 IMAGE_REF 的 deploy", any("INV4" in x for x in probs4c), str(probs4c))

ok("9.4 合法 deploy 引用身份标签", f":{p['identity']}" in p["commands"]["deploy"])

# ================================================================ 10. INV5：环境指针

bad5 = copy.deepcopy(p)
bad5["tags"]["mutable"] = [{"tag": "production", "role": "channel", "ref": "x"}]
probs5 = verify_plan(bad5)
ok("10.1 INV5 拦住非枚举环境指针", any("INV5" in x for x in probs5), str(probs5))

bad5b = copy.deepcopy(p)
bad5b["tags"]["mutable"] = [{"tag": "1.2.0", "role": "channel", "ref": "x"}]
probs5b = verify_plan(bad5b)
ok("10.2 INV5 拦住环境指针与不可变层重名", any("INV5" in x for x in probs5b), str(probs5b))

bad5c = copy.deepcopy(p)
bad5c["base"] = "backend-template"
probs5c = verify_plan(bad5c)
ok("10.3 INV5 拦住不含 '/' 的 base", any("INV5" in x for x in probs5c), str(probs5c))

# ================================================================ 11. 回滚命令

p_rb = build_plan(version="1.2.0", sha=SHA, channel="prod", previous_sha=SHA2)
ok("11.1 提供 previous_sha 时生成 rollback", "rollback" in p_rb["commands"])
ok("11.2 rollback 用上一个身份标签", f"sha-{SHA2[:SHORT_SHA_LEN]}" in p_rb["commands"]["rollback"])
plan_ok("11.3 含 rollback 的计划合法", p_rb)
ok("11.4 未提供 previous_sha 时无 rollback", "rollback" not in p["commands"])
ok("11.5 无 previous_sha 时备注提示手动回滚", any("previous-sha" in n for n in p["notes"]))
raises("11.6 非法 previous_sha 被拒", build_plan, version="1.2.0", sha=SHA, previous_sha="abc")

bad_rb = copy.deepcopy(p_rb)
bad_rb["commands"]["rollback"] = f"IMAGE_REF={p_rb['base']}:prod docker compose up -d"
ok("11.7 INV4 同样拦 rollback 引用环境指针", any("INV4" in x for x in verify_plan(bad_rb)))

# ================================================================ 12. 全组合扫描

combos = 0
for ch in CHANNELS:
    for ver in ("0.1.0", "1.0.0", "1.2.0", "2.0.0-rc.1"):
        if ch == "prod" and is_prerelease(ver):
            continue
        pp = build_plan(version=ver, sha=SHA, channel=ch, previous_sha=SHA2)
        probs = verify_plan(pp)
        ok(f"12.x 组合 {ch}/{ver} 无问题", not probs, str(probs))
        combos += 1

# ================================================================ 13. 异常类型

ok("13.1 verify_plan(非 dict) 返回问题而非抛错", verify_plan(["x"]) != [])
ok("13.2 verify_plan({}) 返回问题而非抛错", len(verify_plan({})) > 0)

# ================================================================ 汇总

total = PASS + len(FAIL)
print(f"selftest: {PASS}/{total} 通过（全组合扫描 {combos} 组）")
if FAIL:
    print("失败项：", file=sys.stderr)
    for f in FAIL:
        print(f"  - {f}", file=sys.stderr)
    sys.exit(1)
print("全部通过")
sys.exit(0)
