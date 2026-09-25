#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""备份可恢复演练（第 82 天交付物，验收清单 D1「备份可恢复（演练过）」）。

判据（D1 通过的定义）
--------------------
不是「备份命令没报错」，而是：

  1. 备份文件能生成且非空；
  2. 备份能**真实恢复到另一个库**（`<源库>_restore_check`），而不是就地覆盖；
  3. 恢复后**表集合完全一致**且**逐表行数完全一致**；
  4. 演练结束把演练库删掉，不留垃圾。

第 3 条是关键：只比总行数会漏掉「A 表少 100 行、B 表多 100 行」这类相互抵消的错误。
第 2 条则是这类演练最容易出的致命错：`mysqldump --databases` 会把 `USE <源库>` 写进
dump，于是「恢复到演练库」这一步会拐回去覆盖源库 —— 本脚本刻意不用 `--databases`，
dump 里只有建表与数据，恢复目标完全由 `mysql <演练库>` 决定。

为什么用 Python 而不是 shell
----------------------------
真实演练需要 mysql / pg 客户端，本仓库的本地环境（Windows）没有；但验收清单里的 D1
是 **AUTO** 项，CI 与本地都要能机械判定它没坏，而两边唯一共同拥有的运行时是 Python。
所以这个脚本是 Python，`--dry-run` 在无客户端的环境也能跑通（只打印动作清单），
真实演练则交给装有客户端的机器或容器。这与 `db/parity_check.py`、`Release/tagplan.py`、
`stack-select/stack-select.py` 是同一套约定，不额外引入一种「只有 CI 能跑」的东西。

用法
----
    python Acceptance/backup_restore.py --dry-run          # 只打印动作清单（本机可跑）
    python Acceptance/backup_restore.py --engine mysql     # 真实演练（需 mysql 客户端）
    python Acceptance/backup_restore.py --engine postgres  # 真实演练（需 pg 客户端）
    python Acceptance/backup_restore.py --engine both      # 两次都跑，任一失败即失败

连接参数走环境变量（`--dry-run` 也会读，用来把主机端口显示出来）：

    MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE
    PGHOST     / PGPORT     / PGUSER     / PGPASSWORD     / PGDATABASE

`--dry-run` 默认核对**双方言** —— 因为 D1 的判据本身就是「双方言备份路径都可用」，
只验一种就通过，等于把另一种留给上线那天发现。

退出码：0 通过 / 2 用法或安全拒绝 / 3 依赖缺失（未做真实演练）/ 4 比对不一致 / 5 命令失败
只依赖标准库；`--dry-run` 不调用任何数据库客户端、不写任何文件。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINES = ("mysql", "postgres")
SOURCE_SUFFIX = "_restore_check"          # 演练库必须带这个后缀，防止写错目标
REQUIRED = {"mysql": ["mysqldump", "mysql"], "postgres": ["pg_dump", "pg_restore", "psql"]}
LIST_SQL = {
    "mysql": "SELECT table_name FROM information_schema.tables "
             "WHERE table_schema='%s' AND table_type='BASE TABLE' ORDER BY table_name",
    "postgres": "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename",
}
COUNT_SQL = {"mysql": "SELECT COUNT(*) FROM `%s`", "postgres": 'SELECT COUNT(*) FROM public."%s"'}


# --------------------------------------------------------------------- 连接参数
def conn(engine: str) -> dict:
    if engine == "mysql":
        return {"host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
                "port": os.environ.get("MYSQL_PORT", "3306"),
                "user": os.environ.get("MYSQL_USER", "root"),
                "password": os.environ.get("MYSQL_PASSWORD", ""),
                "database": os.environ.get("MYSQL_DATABASE", "app")}
    return {"host": os.environ.get("PGHOST", "127.0.0.1"),
            "port": os.environ.get("PGPORT", "5432"),
            "user": os.environ.get("PGUSER", "postgres"),
            "password": os.environ.get("PGPASSWORD", ""),
            "database": os.environ.get("PGDATABASE", "app")}


def conn_args(engine: str, c: dict) -> list:
    """只含连接参数（不含库名），便于在源库与演练库之间复用同一组参数。"""
    if engine == "mysql":
        return ["--host=%s" % c["host"], "--port=%s" % c["port"], "--user=%s" % c["user"]]
    return ["--host=%s" % c["host"], "--port=%s" % c["port"], "--username=%s" % c["user"]]


def env_for(engine: str, c: dict) -> dict:
    """密码走环境变量：比放在 argv 里安全（不会出现在 `ps` 与 shell history 中）。"""
    env = dict(os.environ)
    if c["password"]:
        env["MYSQL_PWD" if engine == "mysql" else "PGPASSWORD"] = c["password"]
    return env


# --------------------------------------------------------------------- SQL 组装
def list_tables_argv(engine: str, c: dict, db: str) -> list:
    sql = LIST_SQL[engine] % db if engine == "mysql" else LIST_SQL[engine]
    if engine == "mysql":
        return ["mysql", "--batch", "--skip-column-names", *conn_args(engine, c), db, "-e", sql]
    return ["psql", *conn_args(engine, c), "--dbname=%s" % db,
            "--tuples-only", "--no-align", "-c", sql]


def count_argv(engine: str, c: dict, db: str, table: str) -> list:
    sql = COUNT_SQL[engine] % table
    if engine == "mysql":
        return ["mysql", "--batch", "--skip-column-names", *conn_args(engine, c), db, "-e", sql]
    return ["psql", *conn_args(engine, c), "--dbname=%s" % db,
            "--tuples-only", "--no-align", "-c", sql]


# --------------------------------------------------------------------- 动作清单
# 先算出「要做什么」，`--dry-run` 只打印、真实模式才执行 —— 两条路径共用同一份组装
# 逻辑，不会出现「打印的命令」与「真正执行的命令」不一致。
def plan_engine(engine: str, workdir: Path) -> list:
    c = conn(engine)
    src = c["database"]
    dst = src + SOURCE_SUFFIX
    if src.endswith(SOURCE_SUFFIX):
        raise SystemExit("拒绝执行：源库名 %r 本身就带演练后缀，脚本可能被指错了目标" % src)
    env = env_for(engine, c)

    if engine == "mysql":
        out = workdir / "dump.sql"
        dump_argv = ["mysqldump", "--single-transaction", "--routines", "--triggers",
                     "--set-gtid-purged=OFF", src, *conn_args(engine, c)]
        return [
            {"step": "① 备份源库", "argv": dump_argv, "env": env, "stdout_to": out,
             "display": "%s > %s" % (shjoin(dump_argv), out.name)},
            {"step": "② 建演练库 %s" % dst, "env": env,
             "argv": ["mysql", *conn_args(engine, c), "-e",
                      "DROP DATABASE IF EXISTS %s; CREATE DATABASE %s" % (dst, dst)]},
            {"step": "③ 恢复到演练库", "env": env, "stdin": out,
             "argv": ["mysql", *conn_args(engine, c), dst]},
            {"step": "④ 逐表比对行数", "kind": "count", "env": env, "src": src, "dst": dst},
            {"step": "⑤ 清理演练库", "env": env,
             "argv": ["mysql", *conn_args(engine, c), "-e", "DROP DATABASE IF EXISTS %s" % dst]},
        ]

    out = workdir / "dump.pgc"
    dump_argv = ["pg_dump", "--format=custom", "--no-owner", "--no-privileges",
                 *conn_args(engine, c), "--dbname=%s" % src, "--file=%s" % str(out)]
    return [
        {"step": "① 备份源库", "argv": dump_argv, "env": env, "stdout_to": out},
        {"step": "② 建演练库 %s" % dst, "env": env,
         "argv": ["psql", *conn_args(engine, c), "--dbname=postgres", "-c",
                  "DROP DATABASE IF EXISTS %s; CREATE DATABASE %s" % (dst, dst)]},
        {"step": "③ 恢复到演练库", "env": env,
         "argv": ["pg_restore", "--no-owner", "--no-privileges", *conn_args(engine, c),
                  "--dbname=%s" % dst, str(out)]},
        {"step": "④ 逐表比对行数", "kind": "count", "env": env, "src": src, "dst": dst},
        {"step": "⑤ 清理演练库", "env": env,
         "argv": ["psql", *conn_args(engine, c), "--dbname=postgres", "-c",
                  "DROP DATABASE IF EXISTS %s" % dst]},
    ]


def display_of(engine: str, st: dict) -> str:
    if st.get("display"):
        return st["display"]
    if st.get("stdin"):
        return "%s < %s" % (shjoin(st["argv"]), Path(st["stdin"]).name)
    if st.get("kind") == "count":
        where = ("information_schema（源库 %s）" % st["src"] if engine == "mysql"
                 else "pg_tables.schemaname='public'（源库 %s）" % st["src"])
        return "逐表取 COUNT(*) 与源库比对；表名来自 %s" % where
    if st["argv"][0] in ("pg_dump", "pg_restore"):
        return shjoin(st["argv"])
    return shjoin(st["argv"])


def _needs_quote(a: str) -> bool:
    return not a or any(ch in a for ch in " \t\"'$&|;<>()*?[]{}!#~`\\")


def shq(s: str) -> str:
    return "'" + s.replace("'", "'\\''") + "'"


def shjoin(argv: list) -> str:
    return " ".join(shq(a) if _needs_quote(a) else a for a in argv)


# --------------------------------------------------------------------- 执行
def run_step(step: dict) -> None:
    argv = list(step["argv"])
    stdin = None
    fh = None
    try:
        if step.get("stdout_to"):
            fh = open(step["stdout_to"], "wb")
        if step.get("stdin"):
            stdin = open(step["stdin"], "rb")
        r = subprocess.run(argv, stdin=stdin, stdout=fh, stderr=subprocess.PIPE,
                           env=step.get("env"), timeout=900)
    finally:
        if stdin is not None:
            stdin.close()
        if fh is not None:
            fh.close()
    if r.returncode != 0:
        print("  命令失败（rc=%d）：%s" % (r.returncode, shjoin(argv)))
        err = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        print("  " + "\n  ".join(err[-12:]))
        raise SystemExit(5)
    if step.get("stdout_to"):
        size = Path(step["stdout_to"]).stat().st_size
        if size == 0:
            print("  备份文件为空：%s" % step["stdout_to"])
            print("  空备份比没有备份更危险 —— 没有备份时大家知道要小心，空备份会让人以为有。")
            raise SystemExit(5)
        print("       → %s（%d 字节）" % (Path(step["stdout_to"]).name, size))


def _capture(engine: str, argv: list, env: dict) -> str:
    r = subprocess.run(argv, capture_output=True, env=env, timeout=300)
    if r.returncode != 0:
        msg = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        print("  命令失败（rc=%d）：%s" % (r.returncode, shjoin(argv)))
        print("  " + "\n  ".join(msg[-8:]))
        raise SystemExit(5)
    return (r.stdout or b"").decode("utf-8", "replace")


def counts_of(engine: str, step: dict, db: str) -> dict:
    c = conn(engine)
    env = step["env"]
    names = [ln.strip() for ln in _capture(engine, list_tables_argv(engine, c, db), env).splitlines()
             if ln.strip()]
    if not names:
        print("  源/目标库 %s 里一张表都没有 —— 演练无法证明「备份可恢复」，只是没东西可恢复。" % db)
        raise SystemExit(4)
    counts = {}
    for name in names:
        val = _capture(engine, count_argv(engine, c, db, name), env).strip()
        try:
            counts[name] = int(val)
        except ValueError:
            print("  行数不是整数（%s / %s）：%r" % (db, name, val))
            raise SystemExit(5)
    return counts


def drill(engine: str, workdir: Path, keep: bool) -> bool:
    missing = [x for x in REQUIRED[engine] if shutil.which(x) is None]
    if missing:
        print("  SKIP %s：缺少客户端 %s" % (engine, "、".join(missing)))
        print("       真实演练需要在装有客户端的机器或容器里跑（CI 里由服务容器提供）。")
        print("       本机可以用 --dry-run 核对动作清单 —— 但 dry-run 通过不等于演练通过。")
        return False

    c = conn(engine)
    print("  源库 %s @ %s:%s  →  演练库 %s" % (c["database"], c["host"], c["port"],
                                              c["database"] + SOURCE_SUFFIX))
    steps = plan_engine(engine, workdir)
    for st in steps:
        if st.get("kind") == "count":
            continue
        print("  %s" % st["step"])
        run_step(st)

    cnt = [s for s in steps if s.get("kind") == "count"][0]
    src_counts = counts_of(engine, cnt, cnt["src"])
    dst_counts = counts_of(engine, cnt, cnt["dst"])

    ok = True
    for t in sorted(set(src_counts) - set(dst_counts)):
        print("  不一致：恢复后缺少表 %s" % t)
        ok = False
    for t in sorted(set(dst_counts) - set(src_counts)):
        print("  不一致：恢复后多出表 %s" % t)
        ok = False
    for t in sorted(set(src_counts) & set(dst_counts)):
        if src_counts[t] != dst_counts[t]:
            print("  不一致：表 %s 备份前 %d 行、恢复后 %d 行" % (t, src_counts[t], dst_counts[t]))
            ok = False
    if ok:
        print("  一致：%d 张表逐表行数完全相同（合计 %d 行）"
              % (len(src_counts), sum(src_counts.values())))
    else:
        print("  提示：不一致时**不要**直接重跑备份 —— 先确认是备份期间有写入，")
        print("        还是恢复过程丢表。前者说明备份方式不满足一致性要求（需要停写或快照），")
        print("        后者说明恢复脚本本身有缺陷，两者要修的都不是备份频率。")

    if not keep:
        for st in steps:
            if st.get("stdout_to"):
                try:
                    Path(st["stdout_to"]).unlink()
                except OSError:
                    pass
    return ok


# --------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="backup_restore.py",
        description="备份可恢复演练（验收清单 D1）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--engine", choices=(*ENGINES, "both"), default="both",
                    help="要演练的引擎，默认 both（D1 的判据就是双方言都可用）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只打印动作清单与判据，不连接任何数据库、不执行任何命令")
    ap.add_argument("--keep", action="store_true", help="保留备份文件（默认演练后删除）")
    args = ap.parse_args(argv)

    engines = ENGINES if args.engine == "both" else (args.engine,)
    workdir = Path(tempfile.mkdtemp(prefix="backup-restore-drill-"))

    print("备份恢复演练%s（引擎：%s）"
          % (" [dry-run] " if args.dry_run else " ", "、".join(engines)))
    print("判据：备份非空 → 恢复到 <源库>%s → 表集合与逐表行数完全一致 → 清理演练库"
          % SOURCE_SUFFIX)

    if args.dry_run:
        print("说明：本次是 dry-run，只打印不执行；真实演练用 "
              "`python Acceptance/backup_restore.py --engine mysql`。")
        print()
        for engine in engines:
            c = conn(engine)
            print("[%s] 动作清单（目标 %s:%s）" % (engine, c["host"], c["port"]))
            for st in plan_engine(engine, workdir):
                print("  %s" % st["step"])
                print("      %s" % display_of(engine, st))
            print()
            print("      比对规则：表集合必须一致，且每张表的 COUNT(*) 必须相等。")
        print("依赖：mysql → %s；postgres → %s"
              % ("、".join(REQUIRED["mysql"]), "、".join(REQUIRED["postgres"])))
        print("dry-run 完成：未连接数据库、未写入任何备份文件。")
        return 0

    print("说明：真实演练会**新建并最后删除**一个名为 <源库>%s 的库，源库本身只读。"
          % SOURCE_SUFFIX)
    print()
    results = []
    for engine in engines:
        print("[%s]" % engine)
        results.append(drill(engine, workdir, args.keep))
        print()
    shutil.rmtree(str(workdir), ignore_errors=True)

    if all(results):
        print("OK 全部演练通过：备份可恢复，双方言表集合与逐表行数一致。")
        return 0
    if not any(results):
        print("SKIP 无可用客户端，未做真实演练。")
        return 3
    print("FAIL 存在不一致或执行失败，详见上方。")
    return 4


if __name__ == "__main__":
    sys.exit(main())
