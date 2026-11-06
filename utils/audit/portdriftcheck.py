#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地端口一致性巡检（第 142 项巡检）

存在的理由
----------
本库每一篇带示例的页面都会写「启动后访问 http://localhost:5173/」，也常会写
`docker run -p 8080:80 ...`。这两句话有一个共同的隐含前提：**读者敲的那个端口，必须是
宿主机上真的在监听的那个**。写错时页面本身是绿的：数字都在，只是不是同一个。

既有巡检都不读这两个数字：
  - `verifyevidencecheck` 判「有没有验证命令」，判不了命令里的端口；
  - `cmdtargetcheck` 判命令指向的脚本在不在；
  - `linkexistcheck` 只认 Markdown 链接，`http://localhost:8080` 不是链接；
  - `countclaimcheck` / `unitmixcheck` 数的是散文里的数；
  - `invisiblecheck` 读的是「不可见字符」。

判据（一错三提示）
------------------
  E0 ROOT_NOT_FOUND        既无 docs/ 也无 project/
  E1 NO_URLS               全库解析到的本地地址不足阈值（正则失效时拒绝判定）
  E2 INVALID_PORT          端口为 0 或 > 65535（绑不上，无反例可辩）
  W1 PUBLISH_CONFUSION     有 `-p 宿主:容器`，页面只出现 `localhost:容器`，从不出现 `localhost:宿主`
  W2 EXPOSE_MISMATCH       Dockerfile `EXPOSE C` 与 `-p 宿主:容器` 的容器端口对不上（C ≠ 容器端口）
  W3 MULTI_PORT_UNLABELED  同页宿主端口 ≥4 种，且全文没有「端口」二字

被否决的第四条判据（如实记录）
------------------------------
首版还有一条 `CURL_DIVERGENCE`：全页只有一个「访问端口」，而 `curl` 打的是另一个端口。
全库跑出 **12 条**，逐条打开看，**12 条全是正当写法**——「前端 5173 访问、后端 8080
健康检查」（`Frontend/DataVisualization/Practice`、`project/Complete/TeamBoard/Environment`）、
「Kibana 5601 访问、Elasticsearch 9200 查接口」（`DB/NoRelational/Elasticsearch`、
`Ops/LogSystem/ElasticStack`）、「Grafana 3000、Loki 3100」（`Ops/LogSystem/Loki`）。
根因是这条判据假设「一页只有一个服务」，而本库的页面**从来不需要声明哪个端口属于哪个服务**，
机器无法区分「漂移」与「并存」。→ **删掉判据，不加豁免名单**：豁免名单会让下一条真缺陷
也被同样的话术放过。这条与第 93 项 `svgcontrastcheck` 的 `E`→`W` 降级同源：**判据的确定性
必须高于它的覆盖面。**

用法
----
  python3 utils/audit/portdriftcheck.py [root] [--list] [--selftest]
退出码：0 = 无 E；1 = 有 E；2 = 用法错误
"""
import argparse
import os
import re
import sys
import tempfile

URL_RE = re.compile(r"(?:localhost|127\.0\.0\.1):(\d{2,5})\b")
PUB_RE = re.compile(r"-p\s+(\d{2,5}):(\d{2,5})\b")
EXPOSE_RE = re.compile(r"^\s*EXPOSE\s+([\d\s]+)$", re.M)
COND_HINT = ("占用", "如果", "若", "改为", "改成", "替换", "另一种")
MIN_URLS = 20


def iter_pages(root):
    for base in ("docs", "project"):
        for dp, dn, fn in os.walk(os.path.join(root, base)):
            dn[:] = [d for d in dn if d not in ("node_modules", "assets", ".vitepress", ".git")]
            for f in fn:
                if f.endswith(".md"):
                    yield os.path.join(dp, f)


def check(root, min_urls=MIN_URLS):
    errs, warns = [], []
    counts = {"pages": 0, "urls": 0, "publish": 0}
    if not os.path.isdir(root):
        return [("E0", "ROOT_NOT_FOUND", root, 0, "")], [], counts
    for page in iter_pages(root):
        counts["pages"] += 1
        rel = os.path.relpath(page, root).replace("\\", "/")
        text = open(page, encoding="utf-8", errors="ignore").read()
        urls, line_of = [], {}
        for i, line in enumerate(text.splitlines(), 1):
            for m in URL_RE.finditer(line):
                p = int(m.group(1))
                urls.append(p)
                line_of.setdefault(p, i)
        counts["urls"] += len(urls)
        ports = set(urls)
        pubs = [(int(a), int(b)) for a, b in PUB_RE.findall(text)]
        counts["publish"] += len(pubs)
        exposed = {int(n) for grp in EXPOSE_RE.findall(text) for n in grp.split()}

        for p in sorted(ports):
            if p == 0 or p > 65535:
                errs.append(("E2", "INVALID_PORT", rel, line_of.get(p, 0), str(p)))

        for host, cont in pubs:
            ln = next((i for i, l in enumerate(text.splitlines(), 1) if f"-p {host}:{cont}" in l), 0)
            conditional = ln and any(h in text.splitlines()[ln - 1] for h in COND_HINT)
            if host != cont and cont in ports and host not in ports and not conditional:
                warns.append(("W1", "PUBLISH_CONFUSION", rel, ln, f"-p {host}:{cont} 但只出现 localhost:{cont}"))
            if exposed and cont not in exposed:
                warns.append(("W2", "EXPOSE_MISMATCH", rel, ln,
                              f"EXPOSE {sorted(exposed)} 与 -p {host}:{cont} 的容器端口不一致"))

        if len(ports) >= 4 and "端口" not in text:
            warns.append(("W3", "MULTI_PORT_UNLABELED", rel, 0, f"{len(ports)} 个端口 {sorted(ports)}"))

    if counts["urls"] < max(min_urls, 1):
        errs.append(("E1", "NO_URLS", root, 0, f"urls={counts['urls']} < {min_urls}"))
    return errs, warns, counts


# ------------------------------ selftest ------------------------------
CASES = [
    ("case-01-ok", "访问 http://localhost:5173/ 与 127.0.0.1:5173\n", set()),
    ("case-02-publish", "```shell\ndocker run -p 8080:80 nginx\n```\n\n访问 http://localhost:80/\n", {"W1"}),
    ("case-03-publish-ok", "```shell\ndocker run -p 8080:80 nginx\n```\n\n访问 http://localhost:8080/\n", set()),
    ("case-04-expose", "```dockerfile\nEXPOSE 8000\n```\n\n```shell\ndocker run -p 9090:9090 x\n```\n\n访问 http://localhost:9090/\n", {"W2"}),
    ("case-05-multi", "\n".join(f"curl http://localhost:{p}/" for p in (3000, 4000, 5000, 6000)), {"W3"}),
    ("case-06-labeled", "四个端口各司其职，端口分别是 3000 / 4000 / 5000 / 6000。\n"
                        + "\n".join(f"curl http://localhost:{p}/" for p in (3000, 4000, 5000, 6000)), set()),
    ("case-07-invalid", "访问 http://localhost:70000/\n", {"E2"}),
    ("case-08-activity", "没有地址。\n", {"E1"}),
    ("case-09-conditional", "若端口被占用，改 `-p 5433:5432` 并同步连接串。\n\n访问 http://localhost:5432/\n", set()),
    ("case-10-expose-multi", "```dockerfile\nEXPOSE 8000 9090\n```\n\n```shell\ndocker run -p 9090:9090 x\n```\n\n访问 http://localhost:9090/\n", set()),
]


def selftest():
    tmp = os.path.join(tempfile.gettempdir(), "portdrift-selftest")
    passed = 0
    for idx, (name, body, want) in enumerate(CASES, 1):
        d = os.path.join(tmp, name)
        os.makedirs(os.path.join(d, "docs"), exist_ok=True)
        with open(os.path.join(d, "docs", "a.md"), "w", encoding="utf-8") as f:
            f.write(body)
        errs, warns, _ = check(d, min_urls=0)
        got = {c for c, *_ in errs} | {c for c, *_ in warns}
        ok = got == want
        passed += 1 if ok else 0
        print(("PASS " if ok else "FAIL ") + f"{idx:02d} {name} want={sorted(want)} got={sorted(got)}")
    print(f"selftest {passed}/{len(CASES)}")
    return 0 if passed == len(CASES) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    errs, warns, counts = check(os.path.abspath(a.root))
    for c, code, path, line, detail in errs:
        print(f"{c} {code} {path}:{line} {detail}")
    if a.list:
        for c, code, path, line, detail in warns:
            print(f"{c} {code} {path}:{line} {detail}")
    print(f"pages={counts['pages']} urls={counts['urls']} publish={counts['publish']} "
          f"E={len(errs)} W={len(warns)}")
    print("RESULT", "OK" if not errs else "FAIL", "EXIT=" + ("0" if not errs else "1"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
