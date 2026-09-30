#!/usr/bin/env python3
"""管理端写链路冒烟验收（零第三方依赖，只要求服务已启动）。

为什么与 `api_smoke.py` 分开：读者端是**无状态查询**，用例之间互不影响，一张表就能表达；
写链路是**有状态流程**——创建拿 id、发布改状态、删除后再查。用同一张表写会退化成
「每条用例自己造数据再断言」，既慢又测不出「写完之后读得到吗」这个真正的问题。
所以这里按**顺序脚本**组织：每一步可以捕获上一步的返回值供后续使用。

这个安全边界是结构性的：本脚本会**写数据**，只能在本地/一次性环境跑；
`api_smoke.py` 只读，因此可以安全指向任何环境。

覆盖的不只是「200 成功」，更包括五类写接口最容易做错的分支：
  * 草稿写进去之后**读者端不能看见**（可见性回归）
  * slug 冲突必须 409，而不是 500 或静默覆盖
  * 参数校验必须 400 且 **message 里带字段名**（否则后台表单无法定位）
  * 状态机：重复发布必须 409，而不是「幂等成功」
  * 更新已发布文章**不得重置状态与发布时间**，但 contentHtml **必须重算**
    （沿用旧 HTML 会让读者一直看到上一版正文——这是最隐蔽的一类 bug）

可重复运行：本轮创建的 slug 带时间戳，总数断言全部相对**本轮抓到的基线**比较，
因此**不需要重启服务**就能连着跑第二遍。

用法：
  python admin_smoke.py                          # 默认打 http://127.0.0.1:18080
  python admin_smoke.py --base http://127.0.0.1:8080
  python admin_smoke.py --selftest                # 证明断言不是恒真

退出码：0 全通过；1 有失败；2 服务不可达。
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

DEFAULT_BASE = "http://127.0.0.1:18080"
TIMEOUT = 5.0

# 每轮跑一套独立数据，避免与上一轮残留撞唯一键（本地内存仓储在服务重启前不会自清）。
# 后缀里必须带随机位：只精确到秒的话，同一秒内连跑两遍会撞 slug，
# 于是「创建」这一步拿到 409，后面依赖它的步骤级联失败——而真正的原因是数据撞名，
# 不是接口错了。这类假失败最浪费时间，所以在源头消掉。
RUN_TAG = time.strftime("%y%m%d%H%M%S") + uuid.uuid4().hex[:4]
SMOKE_SLUG = f"smoke-post-{RUN_TAG}"
XSS_SLUG = f"smoke-xss-{RUN_TAG}"
NEW_CAT_SLUG = f"smoke-cat-{RUN_TAG}"
DUP_CAT_SLUG = f"dup-cat-{RUN_TAG}"
NEW_TAG_SLUG = f"smoke-tag-{RUN_TAG}"
DUP_TAG_SLUG = f"dup-tag-{RUN_TAG}"

# 正文里的标记串：更新后必须消失，用来证明 contentHtml 真的重算了
MARK_V1 = "冒烟正文标记V1"
MARK_V2 = "更新后的正文V2"

_POST_BODY = {
    "title": "冒烟用例：写入链路",
    "slug": SMOKE_SLUG,
    "categoryId": 1,
    "tagIds": [11, 12],
    "contentMd": f"# 冒烟\n\n{MARK_V1}：**加粗** 与 `代码`。",
}

_POST_BODY_V2 = {
    "title": "冒烟用例：写入链路（已改）",
    "slug": SMOKE_SLUG,
    "categoryId": 2,
    "tagIds": [13],
    "contentMd": f"## 更新后的正文\n\n{MARK_V2}。",
}

_BODY_AFTER_PUBLISH = {
    "title": "冒烟用例：发布后再改",
    "slug": SMOKE_SLUG,
    "categoryId": 1,
    "tagIds": [11],
    "contentMd": f"### 第三版\n\n{MARK_V1} 换成新正文。",
}

_XSS_BODY = {
    "title": "XSS 探针",
    "slug": XSS_SLUG,
    "categoryId": 1,
    "contentMd": (
        "# XSS\n\n<script>alert(1)</script>\n\n"
        "[危险链接](javascript:alert(1))\n\n"
        "[合法外链](https://example.com)\n\n[站内链接](/docs/)"
    ),
}


# ---------------------------------------------------------------- 断言助手
# 签名统一为 (status, payload, ctx) -> (ok, detail)。
# 断言函数返回 (标签, 断言) 二元组：标签在定义处给出，不在使用处重复一遍。
# 失败时打印「标签 + 实际值」，比只打实际值更容易定位是哪条判据没满足。


def _check(label, fn):
    return (label, fn)


def code_is(want):
    return _check(f"code={want}",
                  lambda s, p, c: (p.get("code") == want, f"code={p.get('code')}（期望 {want}）"))


def data_is_null():
    return _check("data=null",
                  lambda s, p, c: (p.get("data") is None, f"data={p.get('data')!r}（期望 null）"))


def field_eq(field, want):
    def f(s, p, c):
        got = (p.get("data") or {}).get(field)
        return (got == want, f"data.{field}={got!r}（期望 {want!r}）")
    return _check(f"data.{field}={want!r}", f)


def field_non_null(field):
    def f(s, p, c):
        got = (p.get("data") or {}).get(field)
        return (got is not None, f"data.{field}={got!r}（期望非 null）")
    return _check(f"data.{field} 非 null", f)


def field_eq_ctx(field, key):
    """响应字段必须等于前面抓到的值 —— 用来证明「更新没有重置发布时间」。"""
    def f(s, p, c):
        want = c.get(key)
        if want is None:
            return (False, f"上下文 {key} 未抓到")
        got = (p.get("data") or {}).get(field)
        return (got == want, f"data.{field}={got!r}（期望 {want!r}，来自 ctx.{key}）")
    return _check(f"data.{field} == ctx.{key}", f)


def total_is_ctx(key, delta):
    """总数与基线比较。写死数字的断言在「不重启连跑第二遍」时必然误报。"""
    def f(s, p, c):
        base = c.get(key)
        if not isinstance(base, int):
            return (False, f"上下文 {key} 未抓到基线（{base!r}）")
        got = (p.get("data") or {}).get("total")
        want = base + delta
        return (got == want, f"total={got}（期望 {want} = {key}{delta:+d}）")
    return _check(f"total = {key}{delta:+d}", f)


def list_len_ctx(key, delta):
    def f(s, p, c):
        base = c.get(key)
        if not isinstance(base, int):
            return (False, f"上下文 {key} 未抓到基线（{base!r}）")
        d = p.get("data")
        got = len(d) if isinstance(d, list) else None
        want = base + delta
        return (got == want, f"列表长度={got}（期望 {want} = {key}{delta:+d}）")
    return _check(f"列表长度 = {key}{delta:+d}", f)


def list_has_slug(slug):
    def f(s, p, c):
        d = p.get("data")
        if not isinstance(d, list):
            return (False, f"data 不是数组（{type(d).__name__}）")
        got = [x.get("slug") for x in d if isinstance(x, dict)]
        return (slug in got, f"slug 列表={got}（期望含 {slug}）")
    return _check(f"列表含 slug={slug}", f)


def message_contains(*needles):
    def f(s, p, c):
        msg = p.get("message") or ""
        missing = [n for n in needles if n not in msg]
        return (not missing, f"message={msg!r} 缺少 {missing}")
    return _check("message 含 " + "/".join(needles), f)


def _html(p):
    got = (p.get("data") or {}).get("contentHtml")
    return got if isinstance(got, str) and got else None


def html_contains(*needles):
    def f(s, p, c):
        html = _html(p)
        if html is None:
            return (False, "contentHtml 为空或缺失")
        missing = [n for n in needles if n not in html]
        return (not missing, f"contentHtml 缺少 {missing}｜实际={html[:120]!r}")
    return _check("contentHtml 含 " + "/".join(needles), f)


def html_lacks(*needles):
    """必须先确认 contentHtml 非空再判「不含」：空串下「不含」恒真，那是假门禁。"""
    def f(s, p, c):
        html = _html(p)
        if html is None:
            return (False, "contentHtml 为空或缺失，无法判断消毒/重算是否生效")
        found = [n for n in needles if n in html]
        return (not found, f"contentHtml 不应包含 {found}｜实际={html[:120]!r}")
    return _check("contentHtml 不含 " + "/".join(needles), f)


def anchor_count(want):
    """数 `<a ` 出现次数：同时排除「少生成」与「多生成」，因此能证明
    「合法链接放行了 n 条、危险链接一条都没放行」。"""
    def f(s, p, c):
        html = _html(p)
        if html is None:
            return (False, "contentHtml 为空或缺失")
        got = html.count("<a ")
        return (got == want, f"<a> 标签数={got}（期望 {want}）")
    return _check(f"<a> 标签数={want}", f)


def no_content_md():
    def f(s, p, c):
        present = "contentMd" in (p.get("data") or {})
        return (not present, "响应里出现了 contentMd（读者端不应暴露原文）")
    return _check("无 contentMd", f)


def field_gt(field, floor):
    """id 这类「必须递增」的字段：判 > 下限，而不是判非空 —— 0 或占位值不该蒙混过关。"""
    def f(s, p, c):
        got = (p.get("data") or {}).get(field)
        return (isinstance(got, int) and got > floor, f"data.{field}={got!r}（期望 > {floor}）")
    return _check(f"data.{field} > {floor}", f)


# ---------------------------------------------------------------- 用例脚本
# 每步：方法 / 路径 / 请求体 / 期望 HTTP / 断言 / 捕获（把响应值存进 ctx 供后续使用）。
# 捕获值可以是 JSON 路径元组，也可以是 (payload) -> value 的回调。
# checks 里直接写断言函数即可 —— 标签由断言自己提供，不在调用处重写一遍。


def step(name, method, path, *, body=None, expect=200, checks=(), capture=None):
    return {"name": name, "method": method, "path": path, "body": body,
            "expect": expect, "checks": list(checks), "capture": capture or {}}


def build_steps():
    return [
        # ---------- 基线：本轮开始前有多少数据 ----------
        step("基线：读者端已发布总数", "GET", "/api/v1/posts",
             checks=[code_is(0)], capture={"baseTotal": ("data", "total")}),

        step("基线：分类列表可用且含种子分类", "GET", "/api/v1/categories",
             checks=[code_is(0), list_has_slug("engineering")],
             capture={"baseCats": lambda p: len(p.get("data") or [])}),

        step("基线：标签列表可用且含种子标签", "GET", "/api/v1/tags",
             checks=[code_is(0), list_has_slug("nuxt")],
             capture={"baseTags": lambda p: len(p.get("data") or [])}),

        # ---------- 创建草稿 ----------
        step("创建草稿成功", "POST", "/api/v1/admin/posts", body=_POST_BODY,
             checks=[code_is(0), field_gt("id", 9000), field_eq("slug", SMOKE_SLUG),
                     field_eq("status", "DRAFT"),
                     field_eq("publishedAt", None), field_eq("categorySlug", "engineering"),
                     field_eq("viewCount", 0)],
             capture={"smokeId": ("data", "id")}),

        step("草稿对读者端不可见（总数不变）", "GET", "/api/v1/posts",
             checks=[total_is_ctx("baseTotal", 0)]),

        step("草稿详情对读者端是 404", "GET", f"/api/v1/posts/{SMOKE_SLUG}",
             expect=404, checks=[code_is(2001)]),

        # ---------- 冲突与校验 ----------
        step("slug 冲突必须 409", "POST", "/api/v1/admin/posts",
             body={"title": "重复 slug", "slug": SMOKE_SLUG, "categoryId": 1, "contentMd": "x"},
             expect=409, checks=[code_is(2002)]),

        step("slug 不合法必须 400 且指出字段", "POST", "/api/v1/admin/posts",
             body={"title": "非法 slug", "slug": "Bad Slug", "categoryId": 1, "contentMd": "x"},
             expect=400, checks=[code_is(1001), message_contains("slug")]),

        step("title 为空必须 400 且指出字段", "POST", "/api/v1/admin/posts",
             body={"title": "", "slug": "empty-title", "categoryId": 1, "contentMd": "x"},
             expect=400, checks=[code_is(1001), message_contains("title")]),

        step("categoryId 不存在必须 400", "POST", "/api/v1/admin/posts",
             body={"title": "坏分类", "slug": "bad-category", "categoryId": 9999, "contentMd": "x"},
             expect=400, checks=[code_is(1001), message_contains("categoryId")]),

        step("tagIds 含无效值必须 400", "POST", "/api/v1/admin/posts",
             body={"title": "坏标签", "slug": "bad-tag", "categoryId": 1, "tagIds": [9999],
                   "contentMd": "x"},
             expect=400, checks=[code_is(1001), message_contains("tagIds")]),

        # ---------- 更新（草稿阶段） ----------
        step("更新草稿：分类可改、状态与发布时间不变", "PUT", "/api/v1/admin/posts/{smokeId}",
             body=_POST_BODY_V2,
             checks=[code_is(0), field_eq("title", _POST_BODY_V2["title"]),
                     field_eq("status", "DRAFT"), field_eq("categorySlug", "database"),
                     field_eq("publishedAt", None)]),

        step("更新不存在的文章必须 404", "PUT", "/api/v1/admin/posts/999999",
             body={"title": "x", "slug": "no-such", "categoryId": 1, "contentMd": "x"},
             expect=404, checks=[code_is(2001)]),

        # ---------- 发布 ----------
        step("发布成功，状态与发布时间同时落定", "POST", "/api/v1/admin/posts/{smokeId}/publish",
             checks=[code_is(0), field_eq("status", "PUBLISHED"), field_non_null("publishedAt")],
             capture={"pubAt": ("data", "publishedAt")}),

        step("重复发布必须 409（不做幂等假象）", "POST", "/api/v1/admin/posts/{smokeId}/publish",
             expect=409, checks=[code_is(2003)]),

        step("发布后读者端可读，且拿到渲染后的 HTML", "GET", f"/api/v1/posts/{SMOKE_SLUG}",
             checks=[code_is(0), no_content_md(), field_eq_ctx("publishedAt", "pubAt"),
                     html_contains("<h2>更新后的正文</h2>", MARK_V2)]),

        step("发布后总数 +1", "GET", "/api/v1/posts", checks=[total_is_ctx("baseTotal", 1)]),

        # ---------- 关键回归：更新已发布文章 ----------
        # 改标题与正文，状态机与发布时间都不能被动到，但 contentHtml 必须跟着重算
        step("更新已发布文章：状态与发布时间不变", "PUT", "/api/v1/admin/posts/{smokeId}",
             body=_BODY_AFTER_PUBLISH,
             checks=[code_is(0), field_eq("title", _BODY_AFTER_PUBLISH["title"]),
                     field_eq("status", "PUBLISHED"), field_eq_ctx("publishedAt", "pubAt"),
                     field_eq("categorySlug", "engineering")]),

        step("更新后 contentHtml 必须重算（否则读者一直看到旧版）",
             "GET", f"/api/v1/posts/{SMOKE_SLUG}",
             checks=[code_is(0),
                     html_contains("<h3>第三版</h3>", "换成新正文"),
                     html_lacks("<h2>更新后的正文</h2>")]),

        # ---------- XSS 消毒 ----------
        step("创建含脚本与危险链接的正文", "POST", "/api/v1/admin/posts", body=_XSS_BODY,
             checks=[code_is(0)], capture={"xssId": ("data", "id")}),

        step("发布 XSS 探针", "POST", "/api/v1/admin/posts/{xssId}/publish",
             checks=[code_is(0), field_eq("status", "PUBLISHED")]),

        step("渲染后的 HTML 里脚本必须被转义", "GET", f"/api/v1/posts/{XSS_SLUG}",
             checks=[code_is(0), html_lacks("<script"), html_contains("&lt;script&gt;")]),

        step("只放行合法链接：恰 2 个 a 标签，javascript: 一条都不放行",
             "GET", f"/api/v1/posts/{XSS_SLUG}",
             checks=[code_is(0), html_lacks('href="javascript'), anchor_count(2),
                     html_contains('<a href="https://example.com">合法外链</a>',
                                   '<a href="/docs/">站内链接</a>')]),

        # ---------- 软删除 ----------
        step("软删除 XSS 探针（data 为 null）", "DELETE", "/api/v1/admin/posts/{xssId}",
             checks=[code_is(0), data_is_null()]),

        step("重复删除必须 404（不假装幂等）", "DELETE", "/api/v1/admin/posts/{xssId}",
             expect=404, checks=[code_is(2001)]),

        step("已删除文章对读者端是 404", "GET", f"/api/v1/posts/{XSS_SLUG}",
             expect=404, checks=[code_is(2001)]),

        step("软删除正文章，收尾清场", "DELETE", "/api/v1/admin/posts/{smokeId}",
             checks=[code_is(0), data_is_null()]),

        step("已删除文章对读者端是 404（正文章）", "GET", f"/api/v1/posts/{SMOKE_SLUG}",
             expect=404, checks=[code_is(2001)]),

        step("清场后总数回到基线（证明软删除真的不计入）", "GET", "/api/v1/posts",
             checks=[total_is_ctx("baseTotal", 0)]),

        # ---------- 分类与标签 ----------
        step("创建分类成功", "POST", "/api/v1/admin/categories",
             body={"name": f"冒烟分类{RUN_TAG}", "slug": NEW_CAT_SLUG},
             checks=[code_is(0), field_eq("slug", NEW_CAT_SLUG), field_non_null("id")]),

        step("分类 slug 冲突必须 409", "POST", "/api/v1/admin/categories",
             body={"name": "另一个工程实践", "slug": "engineering"},
             expect=409, checks=[code_is(2002)]),

        step("分类 name 冲突（slug 不同）也必须 409", "POST", "/api/v1/admin/categories",
             body={"name": "工程实践", "slug": DUP_CAT_SLUG},
             expect=409, checks=[code_is(2002)]),

        step("分类列表长度 +1", "GET", "/api/v1/categories",
             checks=[code_is(0), list_len_ctx("baseCats", 1)]),

        step("创建标签成功", "POST", "/api/v1/admin/tags",
             body={"name": f"冒烟标签{RUN_TAG}", "slug": NEW_TAG_SLUG},
             checks=[code_is(0), field_eq("slug", NEW_TAG_SLUG)]),

        step("标签 name 冲突（slug 不同）也必须 409", "POST", "/api/v1/admin/tags",
             body={"name": f"冒烟标签{RUN_TAG}", "slug": DUP_TAG_SLUG},
             expect=409, checks=[code_is(2002)]),

        step("标签 slug 不合法必须 400", "POST", "/api/v1/admin/tags",
             body={"name": "K8s", "slug": "K8s!"},
             expect=400, checks=[code_is(1001), message_contains("slug")]),

        step("标签列表长度 +1", "GET", "/api/v1/tags",
             checks=[code_is(0), list_len_ctx("baseTags", 1)]),
    ]


# ---------------------------------------------------------------- 执行


def _resolve(path, ctx):
    """把路径里的 {name} 占位替换成上下文里捕获到的值。"""
    out = path
    for key, value in ctx.items():
        out = out.replace("{" + key + "}", str(value))
    return out


def _request(base, method, path, body=None):
    url = base.rstrip("/") + path
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, _json(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, _json(e.read().decode("utf-8", errors="replace"))


def _json(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"__raw__": raw[:300]}


def _capture(value, payload):
    """取捕获值：元组按 JSON 路径走，回调直接算。"""
    if callable(value):
        return value(payload)
    node = payload
    for part in value:
        node = node.get(part) if isinstance(node, dict) else None
    return node


def run(base, verbose=True):
    steps = build_steps()
    ctx = {}
    passed = 0
    failures = []
    for st in steps:
        try:
            status, payload = _request(base, st["method"], _resolve(st["path"], ctx), st["body"])
        except urllib.error.URLError as e:
            return passed, len(steps), [("连接失败", f"{st['path']}: {e}")], True

        marks = [f"HTTP {status}"]
        ok = status == st["expect"]
        if not ok:
            marks.append(f"（期望 {st['expect']}）")
        for label, fn in st["checks"]:
            good, detail = fn(status, payload, ctx)
            if not good:
                marks.append(f"{label} ✗ {detail}")
                ok = False
        if ok:
            passed += 1
            for key, value in st["capture"].items():
                ctx[key] = _capture(value, payload)
        else:
            failures.append((st["name"], "; ".join(marks)))

        if verbose:
            print(f"  {'PASS' if ok else 'FAIL'}  {st['name']}")
            if not ok:
                for m in marks[1:]:
                    print(f"          → {m}")
    return passed, len(steps), failures, False


def selftest():
    """变异测试：对空响应执行同一批断言。

    如果某一步的断言在「空响应 + HTTP 0」下依然全部通过，说明它分辨不出对错——
    这类断言放进门禁只会制造「绿灯的假象」。
    """
    steps = build_steps()
    print("=== admin_smoke 断言有效性自测（喂空响应，探针）===")
    bad = 0
    for st in steps:
        ctx = {"smokeId": 9001, "xssId": 9002, "baseTotal": 3, "baseCats": 3, "baseTags": 5,
               "pubAt": "2026-09-30T00:00:00Z"}
        verdicts = [fn(0, {}, ctx)[0] for _, fn in st["checks"]]
        has_teeth = bool(verdicts) and not all(verdicts)
        print(f"  {'PASS' if has_teeth else 'FAIL'}  {st['name']}  "
              f"（对空响应仍通过 {sum(verdicts)}/{len(verdicts)} 条）")
        if not has_teeth:
            bad += 1
    print(f"selftest: {len(steps) - bad}/{len(steps)} 通过")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="管理端写链路冒烟验收")
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"服务地址，默认 {DEFAULT_BASE}")
    ap.add_argument("--selftest", action="store_true", help="只做断言有效性自测，不发请求")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    print(f"=== 管理端写链路冒烟验收  base={args.base}  run={RUN_TAG} ===")
    passed, total, failures, unreachable = run(args.base)
    if unreachable:
        print(f"  服务不可达：{args.base}")
        print("  先启动：cd blog-application && SERVER_PORT=18080 mvn spring-boot:run")
        print("RESULT: UNREACHABLE")
        return 2
    print(f"steps = {total}  passed = {passed}  failed = {total - passed}")
    print("RESULT:", "FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
