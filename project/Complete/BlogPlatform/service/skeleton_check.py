#!/usr/bin/env python3
"""骨架自检门禁（零第三方依赖，可进 CI）。

检查六组「写错了编译也能过、上线才炸」的骨架约定：

  S1 聚合 POM 的 modules 与实际子目录一致（少写一个模块 = 那个模块根本不构建）
  S2 子模块 POM 不得自带 <version>（绕过统一版本管理，升级必漏）
  S3 模块依赖方向单向 common ← data ← web ← application，且谁都不能依赖 application
  S4 迁移脚本命名 V<数字>__<描述>.sql，且 mysql / postgres 两套版本号集合一致
  S5 生产配置不得出现明文凭据；关键项必须是无默认值的占位符（${X} 而不是 ${X:默认值}）
  S6 迁移脚本必须由构建期复制进 classpath（SQL 只允许有一份来源）

用法：
  python skeleton_check.py                 正常检查
  python skeleton_check.py --selftest      跑内置变异用例，证明门禁本身有效
  python skeleton_check.py --root <dir>    指定 service 目录（自测用）
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
NS = {"m": "http://maven.apache.org/POM/4.0.0"}

EXPECTED_MODULES = ["blog-common", "blog-data", "blog-web", "blog-application"]

# 允许的直接依赖（模块名 → 允许依赖的兄弟模块）
ALLOWED_DEPS = {
    "blog-common": set(),
    "blog-data": {"blog-common"},
    "blog-web": {"blog-common", "blog-data"},
    "blog-application": {"blog-common", "blog-data", "blog-web"},
}

# 生产配置里必须出现、且必须无默认值的占位符
REQUIRED_PLACEHOLDERS = ["DB_URL", "DB_USER", "DB_PASSWORD", "JWT_SECRET", "BLOG_DB_VENDOR"]

VERSION_TAG = "version"
MIGRATION_RE = re.compile(r"^V(\d+(?:\.\d+)*)__[a-z0-9_]+\.sql$")


class Result:
    """检查结果收集器。

    每条检查可以给两个措辞：ok_message 与 fail_message。
    只给一个（fail_message=None）时两处复用，但**失败措辞不能当成功措辞用**——
    「OK  生产配置缺少占位符 ${DB_URL}」这种输出会让人把通过读成不通过。
    """

    def __init__(self):
        self.items = []  # (check, ok, message)

    def add(self, check, ok, ok_message, fail_message=None):
        message = ok_message if ok else (fail_message or ok_message)
        self.items.append((check, bool(ok), message))
        return ok

    @property
    def failed(self):
        return [i for i in self.items if not i[1]]


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _parse_pom(path):
    """POM 解析失败一律 FAIL 带位置，不抛异常——校验器崩了比校验失败危险。"""
    try:
        return ET.parse(path).getroot(), None
    except ET.ParseError as e:
        return None, f"XML 解析失败 {path}: {e}"
    except OSError as e:
        return None, f"无法读取 {path}: {e}"


def check_module_dependencies(pom_root, module_name):
    """返回该模块声明的 com.blog 依赖集合。"""
    deps = set()
    for dep in pom_root.findall(".//m:dependencies/m:dependency", NS):
        gid = dep.findtext("m:groupId", default="", namespaces=NS)
        aid = dep.findtext("m:artifactId", default="", namespaces=NS)
        if gid.strip() == "com.blog":
            deps.add(aid.strip())
    return deps


def check_own_versions(pom_root):
    """子模块 POM 里除 parent 段之外出现的 <version> 都算违规。

    分两类报，因为修法不同：
      - 依赖自带版本        → 应改由父 POM 的 dependencyManagement（或导入的 BOM）给
      - 插件自带版本        → 应改由父 POM 的 pluginManagement 给
    只报「是谁」，不给行号——门禁的输出是给人看的，坐标比行号好找。
    """
    offenders = []

    for dep in pom_root.findall(".//m:dependencies/m:dependency", NS):
        v = dep.findtext("m:version", default=None, namespaces=NS)
        if v is not None:
            gid = dep.findtext("m:groupId", default="?", namespaces=NS)
            aid = dep.findtext("m:artifactId", default="?", namespaces=NS)
            offenders.append(f"依赖 {gid}:{aid}={v.strip()}")

    for plugin in pom_root.findall(".//m:build//m:plugin", NS):
        v = plugin.findtext("m:version", default=None, namespaces=NS)
        if v is not None:
            aid = plugin.findtext("m:artifactId", default="?", namespaces=NS)
            offenders.append(f"插件 {aid}={v.strip()}")

    return offenders


def run_checks(service_dir, res):
    parent_pom = os.path.join(service_dir, "pom.xml")
    root, err = _parse_pom(parent_pom)
    if err:
        res.add("S1", False, err)
        return

    # ---------- S1 modules 与实际子目录一致 ----------
    declared = [m.text.strip() for m in root.findall(".//m:modules/m:module", NS)]
    on_disk = sorted(
        d for d in os.listdir(service_dir)
        if os.path.isdir(os.path.join(service_dir, d)) and os.path.isfile(os.path.join(service_dir, d, "pom.xml"))
    )
    res.add("S1", sorted(declared) == on_disk,
            f"modules 声明={sorted(declared)} 磁盘实际={on_disk}")
    res.add("S1", declared == EXPECTED_MODULES,
            f"模块名单应为 {EXPECTED_MODULES}，实际 {declared}")

    # ---------- S2 子模块不写 version ----------
    for mod in declared:
        pom = os.path.join(service_dir, mod, "pom.xml")
        r, e = _parse_pom(pom)
        if e:
            res.add("S2", False, e)
            continue
        offenders = check_own_versions(r)
        res.add("S2", not offenders, f"{mod} 自带 <version>：{offenders}" if offenders else f"{mod} 无自带版本")

    # ---------- S3 依赖方向 ----------
    for mod in declared:
        pom = os.path.join(service_dir, mod, "pom.xml")
        r, e = _parse_pom(pom)
        if e:
            res.add("S3", False, e)
            continue
        deps = check_module_dependencies(r, mod)
        allowed = ALLOWED_DEPS.get(mod, set())
        illegal = deps - allowed
        res.add("S3", not illegal,
                f"{mod} 非法依赖 {sorted(illegal)}（允许 {sorted(allowed)}）" if illegal
                else f"{mod} 依赖方向正确 {sorted(deps)}")
        res.add("S3", mod != "blog-application" or "blog-application" not in deps,
                f"{mod} 不得依赖可启动模块")

    # ---------- S4 迁移脚本命名与双方言一致 ----------
    db_dir = os.path.abspath(os.path.join(service_dir, "..", "db"))
    dialect_versions = {}
    for dialect in ("mysql", "postgres"):
        d = os.path.join(db_dir, dialect)
        if not os.path.isdir(d):
            res.add("S4", False, f"缺少方言目录 {d}")
            continue
        files = sorted(f for f in os.listdir(d) if f.endswith(".sql"))
        versions = set()
        for f in files:
            m = MIGRATION_RE.match(f)
            if not m:
                res.add("S4", False, f"{dialect}/{f} 命名不规范（应 V<版本>__<描述>.sql）")
                continue
            versions.add(m.group(1))
        dialect_versions[dialect] = versions
    if len(dialect_versions) == 2:
        same = dialect_versions["mysql"] == dialect_versions["postgres"]
        res.add("S4", same,
                f"双方言版本集合一致 {sorted(dialect_versions['mysql'])}" if same
                else f"双方言版本集合不一致 mysql={sorted(dialect_versions['mysql'])} "
                     f"postgres={sorted(dialect_versions['postgres'])}")

    # ---------- S5 生产配置无明文凭据、关键项无默认值 ----------
    prod = os.path.join(service_dir, "blog-application", "src", "main", "resources", "application-prod.yml")
    if not os.path.isfile(prod):
        res.add("S5", False, f"缺少 {prod}")
    else:
        text = _read(prod)
        for name in REQUIRED_PLACEHOLDERS:
            res.add("S5", f"${{{name}}}" in text,
                    f"生产配置含无默认值占位符 ${{{name}}}",
                    f"生产配置缺少无默认值占位符 ${{{name}}}")
        # 明确禁止 ${X:默认值} 这类写法出现在凭据项上
        bad = re.findall(r"\$\{(DB_URL|DB_USER|DB_PASSWORD|JWT_SECRET|BLOG_DB_VENDOR)[^}]*:([^}]*)\}", text)
        res.add("S5", not bad, "凭据项均无默认值", f"凭据项给了默认值：{bad}")
        for key in ("password", "secret"):
            for line in text.splitlines():
                s = line.strip()
                if s.startswith(key + ":") or " " + key + ":" in s:
                    val = s.split(":", 1)[1].strip()
                    res.add("S5", val.startswith("${"),
                            f"{key} 取自占位符：{s}",
                            f"{key} 疑似明文：{s}")

    # ---------- S6 迁移脚本由构建期复制进 classpath ----------
    app_pom = os.path.join(service_dir, "blog-application", "pom.xml")
    r, e = _parse_pom(app_pom)
    if e:
        res.add("S6", False, e)
    else:
        txt = _read(app_pom)
        res.add("S6", "maven-resources-plugin" in txt,
                "blog-application 已配置资源复制插件",
                "blog-application 未配置资源复制插件")
        res.add("S6", "db/migration/${blog.db.vendor}" in txt,
                "迁移脚本输出目录 db/migration/${blog.db.vendor}",
                "未见迁移脚本输出目录 db/migration/${blog.db.vendor}")
        res.add("S6", "../../db/${blog.db.vendor}" in txt,
                "迁移脚本来源目录 ../../db/${blog.db.vendor}",
                "未见迁移脚本来源目录 ../../db/${blog.db.vendor}")
        res.add("S6", "process-resources" in txt,
                "资源复制已绑到 process-resources 阶段",
                "资源复制未绑到 process-resources 阶段")


def selftest():
    """变异测试：把每一条规则都故意改坏，确认门禁会报红。"""
    import shutil
    import tempfile

    base = os.path.abspath(os.path.dirname(HERE))  # 项目根 = service 的上级
    src = HERE

    cases = []

    def mutate(name, fn, expect_fail_checks):
        tmp = tempfile.mkdtemp(prefix="skeleton-mut-")
        dst = os.path.join(tmp, "service")
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("target", "*.pyc"))
        # db 目录是 service 的兄弟，一起复制到同级位置
        shutil.copytree(os.path.join(base, "db"), os.path.join(tmp, "db"))
        fn(dst)
        r = Result()
        run_checks(dst, r)
        got = {c for c, ok, _ in r.items if not ok}
        ok = all(c in got for c in expect_fail_checks) and got
        cases.append((name, ok, sorted(got)))
        shutil.rmtree(tmp, ignore_errors=True)

    def m_modules(d):
        p = os.path.join(d, "pom.xml")
        t = _read(p).replace("<module>blog-web</module>", "")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def m_version(d):
        p = os.path.join(d, "blog-data", "pom.xml")
        t = _read(p).replace("</dependency>", "  <version>1.0.0</version>\n</dependency>", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def m_plugin_version(d):
        p = os.path.join(d, "blog-application", "pom.xml")
        t = _read(p).replace(
            "<artifactId>maven-resources-plugin</artifactId>",
            "<artifactId>maven-resources-plugin</artifactId>\n        <version>9.9.9</version>", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def m_direction(d):
        p = os.path.join(d, "blog-common", "pom.xml")
        t = _read(p).replace(
            "</project>",
            "  <dependencies><dependency><groupId>com.blog</groupId>"
            "<artifactId>blog-data</artifactId></dependency></dependencies>\n</project>")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def m_migration(d):
        # 注意：db/ 是 service/ 的兄弟目录，不是子目录——按 service 内部路径找必然 FileNotFoundError
        p = os.path.join(os.path.dirname(d), "db", "postgres")
        os.remove(os.path.join(p, "V1__blog_init.sql"))
        with open(os.path.join(p, "V2__only_pg.sql"), "w", encoding="utf-8") as f:
            f.write("-- 故意带上一个 mysql 没有的版本\n")

    def m_secret(d):
        p = os.path.join(d, "blog-application", "src", "main", "resources", "application-prod.yml")
        t = _read(p).replace("password: ${DB_PASSWORD}", "password: root123456")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def m_placeholder_default(d):
        p = os.path.join(d, "blog-application", "src", "main", "resources", "application-prod.yml")
        t = _read(p).replace("${JWT_SECRET}", "${JWT_SECRET:dev-secret}")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def m_resource_copy(d):
        p = os.path.join(d, "blog-application", "pom.xml")
        t = _read(p).replace("../../db/${blog.db.vendor}", "../../db/whatever")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    mutate("modules 少写一个", m_modules, ["S1"])
    mutate("子模块自带 version", m_version, ["S2"])
    mutate("插件自带 version", m_plugin_version, ["S2"])
    mutate("反向依赖", m_direction, ["S3"])
    mutate("双方言迁移版本不一致", m_migration, ["S4"])
    mutate("生产配置明文密码", m_secret, ["S5"])
    mutate("凭据给了默认值", m_placeholder_default, ["S5"])
    mutate("资源复制指向错误目录", m_resource_copy, ["S6"])

    print("=== skeleton_check 变异自测 ===")
    bad = 0
    for name, ok, got in cases:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<22} 命中规则={got}")
        if not ok:
            bad += 1
    print(f"selftest: {len(cases) - bad}/{len(cases)} 通过")
    return 1 if bad else 0


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()

    root = HERE
    if "--root" in args:
        root = args[args.index("--root") + 1]

    res = Result()
    run_checks(root, res)

    print("=== 骨架自检（service 目录）===")
    for check, ok, msg in res.items:
        print(f"  {'OK  ' if ok else 'FAIL'} [{check}] {msg}")
    failed = res.failed
    print(f"checks = {len(res.items)}  failed = {len(failed)}")
    print("RESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
