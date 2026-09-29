#!/usr/bin/env python3
"""读者端 API 冒烟验收（零第三方依赖，只要求服务已启动）。

为什么需要它：`skeleton_check.py` 只能证明**结构对不对**（模块、版本、依赖方向、配置），
证明不了**接口真的按契约工作**。两者合起来才是当日的验收判据。

覆盖的不只是「正常返回 200」，还包括三类最容易写成 200 的错误路径：
  * 草稿必须 404，而不是 200 + 空内容（否则等于泄露了存在性）
  * 越界分页必须 400，而不是被悄悄截断成 size=50
  * 详情不能把 contentMd 带出去（读者端只该拿到渲染后的 HTML）

用法：
  python api_smoke.py                            # 默认打 http://127.0.0.1:18080
  python api_smoke.py --base http://127.0.0.1:8080
  python api_smoke.py --selftest                 # 证明这里的断言不是恒真

退出码：0 全通过；1 有失败；2 服务不可达。
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:18080"
TIMEOUT = 5.0


class Case:
    """一个验收用例：期望的 HTTP 状态 + 对响应体的一组断言。"""

    def __init__(self, name, path, expect_http, checks):
        self.name = name
        self.path = path
        self.expect_http = expect_http
        self.checks = checks  # [(说明, payload -> (ok, detail))]


def _get(base, path):
    """返回 (http_status, payload)。HTTP 4xx/5xx 也要拿到 body —— 错误码就在里面。"""
    url = base.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"__raw__": raw}


# ---------------------------------------------------------------- 断言助手
# 每个助手返回 (ok, detail)。detail 在失败时才有人看，所以写成「实际是什么」。


def code_is(want):
    return lambda p: (p.get("code") == want, f"code={p.get('code')}（期望 {want}）")


def data_present():
    def f(p):
        d = p.get("data")
        return (isinstance(d, dict), f"data 类型={type(d).__name__}")
    return f


def total_is(want):
    def f(p):
        got = (p.get("data") or {}).get("total")
        return (got == want, f"total={got}（期望 {want}）")
    return f


def records_len(want):
    def f(p):
        rec = (p.get("data") or {}).get("records")
        n = len(rec) if isinstance(rec, list) else None
        return (n == want, f"records 条数={n}（期望 {want}）")
    return f


def record_field(row_index, field, want):
    def f(p):
        rec = (p.get("data") or {}).get("records") or []
        if row_index >= len(rec):
            return (False, f"records 只有 {len(rec)} 条，取不到第 {row_index} 条")
        got = rec[row_index].get(field)
        return (got == want, f"records[{row_index}].{field}={got!r}（期望 {want!r}）")
    return f


def slugs_all_published():
    def f(p):
        rec = (p.get("data") or {}).get("records") or []
        bad = [r.get("slug") for r in rec if r.get("status") != "PUBLISHED"]
        return (not bad, f"列表里混入了非 PUBLISHED：{bad}" if bad else "全部为 PUBLISHED")
    return f


def has_field(field):
    def f(p):
        present = field in (p.get("data") or {})
        return (present, f"data.{field} {'存在' if present else '缺失'}")
    return f


def lacks_field(field):
    def f(p):
        absent = field not in (p.get("data") or {})
        return (absent, f"data.{field} {'不应出现但出现了' if not absent else '未出现'}")
    return f


def equal(want):
    return lambda p: (p == want, f"实际 {p!r}（期望 {want!r}）")


# 序号按 publishedAt 倒序：nuxt-ssr-notes(09-10) > mysql-ngram-search(09-06) > hello-blog(09-03)
CASES = [
    Case("列表只返回已发布文章", "/api/v1/posts",
         200, [
             ("code=0", code_is(0)),
             ("data 为对象", data_present()),
             ("total=3（草稿不计入）", total_is(3)),
             ("页大小默认 10", records_len(3)),
             ("按发布时间倒序，首条为 nuxt-ssr-notes", record_field(0, "slug", "nuxt-ssr-notes")),
             ("列表不含非 PUBLISHED", slugs_all_published()),
             ("列表项不含 contentHtml", lambda p: (
                 all("contentHtml" not in r for r in (p.get("data") or {}).get("records") or []),
                 "列表项泄漏了 contentHtml" if any(
                     "contentHtml" in r for r in (p.get("data") or {}).get("records") or []) else "未泄漏正文")),
         ]),

    Case("详情返回渲染后的 HTML", "/api/v1/posts/hello-blog",
         200, [
             ("code=0", code_is(0)),
             ("含 contentHtml", has_field("contentHtml")),
             ("不含 contentMd（读者端只给 HTML）", lacks_field("contentMd")),
             ("slug 正确", lambda p: ((p.get("data") or {}).get("slug") == "hello-blog",
                                     f"slug={(p.get('data') or {}).get('slug')}")),
         ]),

    Case("草稿一律 404，不暴露存在性", "/api/v1/posts/draft-post",
         404, [
             ("code=2001", code_is(2001)),
             ("data 为空", lambda p: (p.get("data") is None, f"data={p.get('data')!r}")),
         ]),

    Case("不存在的 slug 与草稿同码", "/api/v1/posts/no-such-post",
         404, [
             ("code=2001", code_is(2001)),
         ]),

    Case("size 超上限必须 400（不得悄悄截断）", "/api/v1/posts?size=51",
         400, [
             ("code=1002", code_is(1002)),
         ]),

    Case("page=0 必须 400", "/api/v1/posts?page=0",
         400, [
             ("code=1002", code_is(1002)),
         ]),

    Case("tagSlug 过滤生效", "/api/v1/posts?tagSlug=nuxt",
         200, [
             ("code=0", code_is(0)),
             ("total=1", total_is(1)),
             ("命中的是 nuxt 标签文章", record_field(0, "slug", "nuxt-ssr-notes")),
         ]),

    Case("categorySlug 过滤生效", "/api/v1/posts?categorySlug=database",
         200, [
             ("code=0", code_is(0)),
             ("total=1", total_is(1)),
             ("命中的是 database 分类文章", record_field(0, "slug", "mysql-ngram-search")),
         ]),

    Case("actuator 健康检查", "/actuator/health",
         200, [
             ("status=UP", lambda p: (p.get("status") == "UP", f"status={p.get('status')!r}")),
         ]),
]


def run(base, verbose=True):
    """执行全部用例，返回 (通过数, 总数, 失败明细, 是否连不上服务)。"""
    passed = 0
    failures = []
    for case in CASES:
        try:
            status, payload = _get(base, case.path)
        except urllib.error.URLError as e:
            return passed, len(CASES), [("连接失败", f"{case.path}: {e}")], True

        marks = []
        ok = status == case.expect_http
        marks.append(f"HTTP {status}" + ("" if ok else f"（期望 {case.expect_http}）"))
        if ok:
            for label, fn in case.checks:
                good, detail = fn(payload)
                marks.append(f"{label}{'' if good else ' ✗ ' + detail}")
                if not good:
                    ok = False
        if ok:
            passed += 1
        else:
            failures.append((case.name, "; ".join(marks)))

        if verbose:
            print(f"  {'PASS' if ok else 'FAIL'}  {case.name}")
            if not ok:
                for m in marks:
                    if "✗" in m or "期望" in m:
                        print(f"          → {m}")
    return passed, len(CASES), failures, False


def selftest():
    """变异测试：断言如果对空响应也通过，那它就是个假门禁。

    做法很直接——把响应体换成 `{}`。任何「恒真」的断言都会在此暴露：
    它照样通过，于是这条用例在被喂空响应时仍然全绿 → 判为无效断言。
    """
    print("=== api_smoke 断言有效性自测（喂空响应，探针）===")
    bad = 0
    for case in CASES:
        empty = {}
        verdicts = [fn(empty)[0] for _, fn in case.checks]
        # 期望：空响应下至少要有一条断言报错，否则这组断言分辨不出对错
        has_teeth = not all(verdicts)
        print(f"  {'PASS' if has_teeth else 'FAIL'}  {case.name}  "
              f"（对空响应仍通过 {sum(verdicts)}/{len(verdicts)} 条）")
        if not has_teeth:
            bad += 1
    print(f"selftest: {len(CASES) - bad}/{len(CASES)} 通过")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="读者端 API 冒烟验收")
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"服务地址，默认 {DEFAULT_BASE}")
    ap.add_argument("--selftest", action="store_true", help="只做断言有效性自测，不发请求")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    print(f"=== 读者端 API 冒烟验收  base={args.base} ===")
    passed, total, failures, unreachable = run(args.base)
    if unreachable:
        print(f"  服务不可达：{args.base}")
        print("  先启动：cd blog-application && SERVER_PORT=18080 mvn spring-boot:run")
        print("RESULT: UNREACHABLE")
        return 2
    print(f"cases = {total}  passed = {passed}  failed = {total - passed}")
    print("RESULT:", "FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
