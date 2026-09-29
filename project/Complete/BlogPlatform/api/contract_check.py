#!/usr/bin/env python3
"""接口契约校验（零第三方依赖）。

用法：
    python api/contract_check.py
退出码：0 通过；1 不通过。

检查项：
1. JSON 可解析，openapi 字段为 3.1.x；
2. 每个 $ref 都能在文档内解析（内部引用一致性）；
3. 每个 operation 都声明了 responses，且 200 响应有 content；
4. 四条链路的路径前缀齐全（文章 / 分类标签 / 评论 / 搜索）；
5. 统一响应 Result 在 components.schemas 注册。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CHAIN_PREFIXES = {
    "文章": ("/api/v1/posts", "/api/v1/admin/posts"),
    "分类标签": ("/api/v1/categories", "/api/v1/tags"),
    "评论": ("/api/v1/posts/{slug}/comments", "/api/v1/comments/{id}"),
    "搜索": ("/api/v1/search",),
}

HTTP_METHODS = {"get", "post", "put", "delete", "patch"}


def fail(msg: str) -> None:
    print("FAIL:", msg)


def main() -> int:
    doc_path = Path(__file__).resolve().parent / "openapi.json"
    try:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fail(f"契约文件无法读取或解析：{e}")
        return 1

    problems: list[str] = []

    # ① 版本与元信息
    if not re.match(r"^3\.1\.\d+$", str(doc.get("openapi", ""))):
        problems.append(f"openapi 版本应为 3.1.x，实际 {doc.get('openapi')!r}")
    if not doc.get("info", {}).get("title"):
        problems.append("info.title 缺失")

    # ② $ref 全部可解析
    refs: list[str] = []

    def _collect(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "$ref" and isinstance(v, str):
                    refs.append(v)
                else:
                    _collect(v)
        elif isinstance(node, list):
            for v in node:
                _collect(v)

    _collect(doc)
    for ref in refs:
        if not ref.startswith("#/"):
            problems.append(f"外部引用本契约无法校验：{ref}")
            continue
        node = doc
        for part in ref[2:].split("/"):
            node = node.get(part) if isinstance(node, dict) else None
            if node is None:
                break
        if node is None:
            problems.append(f"$ref 无法解析：{ref}")

    # ③ 每个 operation 都有 responses
    ops = 0
    for path, item in doc.get("paths", {}).items():
        for method, op in item.items():
            if method not in HTTP_METHODS:
                continue
            ops += 1
            responses = op.get("responses", {})
            if not responses:
                problems.append(f"{method.upper()} {path} 缺少 responses")
                continue
            ok = op.get("tags")
            if not ok:
                problems.append(f"{method.upper()} {path} 缺少 tags 分组")
            r200 = responses.get("200") or responses.get("201")
            if r200 and "content" not in r200:
                problems.append(f"{method.upper()} {path} 的 200 响应缺少 content")

    # ④ 四条链路路径齐全
    all_paths = set(doc.get("paths", {}))
    for chain, prefixes in CHAIN_PREFIXES.items():
        for p in prefixes:
            if p not in all_paths:
                problems.append(f"链路「{chain}」缺路径：{p}")

    # ⑤ 统一响应注册
    if "Result" not in doc.get("components", {}).get("schemas", {}):
        problems.append("components.schemas 缺少统一响应 Result")

    if problems:
        for p in problems:
            fail(p)
        return 1

    print(f"OK: {len(all_paths)} 条路径 / {ops} 个操作，$ref 全部可解析，四条链路齐全")
    return 0


if __name__ == "__main__":
    sys.exit(main())
