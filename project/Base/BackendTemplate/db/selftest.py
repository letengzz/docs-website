#!/usr/bin/env python3
"""parity_check.py 的自测：11 项断言覆盖解析、归一化与三类不一致的检出。

用法：python3 db/selftest.py   （期望：selftest: 11/11 通过）
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity_check import compare, parse_ddl  # noqa: E402

BASE = Path(__file__).resolve().parent
passed = 0
total = 0


def check(name: str, cond: bool) -> None:
    global passed, total
    total += 1
    if cond:
        passed += 1
        print(f"  ok  {name}")
    else:
        print(f"FAIL  {name}")


MYSQL_SAMPLE = """
CREATE TABLE t_demo (
    id          BIGINT       NOT NULL COMMENT 'x',
    status      TINYINT      NOT NULL DEFAULT 1,
    ratio       TINYINT(1)   NOT NULL,
    name        VARCHAR(64)  NOT NULL,
    created     DATETIME(3)  NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_name (name),
    KEY idx_created (created)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '演示表';
"""

PG_SAMPLE = """
CREATE TABLE t_demo (
    id          BIGINT       NOT NULL,
    status      SMALLINT     NOT NULL DEFAULT 1,
    ratio       SMALLINT     NOT NULL,
    name        VARCHAR(64)  NOT NULL,
    created     TIMESTAMP(3) NOT NULL,
    CONSTRAINT pk_t_demo PRIMARY KEY (id),
    CONSTRAINT uk_name UNIQUE (name)
);
COMMENT ON TABLE t_demo IS '演示表';
CREATE INDEX idx_created ON t_demo (created);
"""

# 解析层
def parse_from(sql: str):
    import parity_check
    from pathlib import Path as P
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = P(d) / "x.sql"
        f.write_text(sql, encoding="utf-8")
        return parity_check.parse_ddl(f)


m = parse_from(MYSQL_SAMPLE)
g = parse_from(PG_SAMPLE)

check("01 解析出 t_demo", "t_demo" in m and "t_demo" in g)
check("02 列数一致且为 5", len(m["t_demo"].columns) == 5 and len(g["t_demo"].columns) == 5)
check("03 TINYINT 归一化为 smallint",
      next(c for c in m["t_demo"].columns if c.name == "status").norm_type == "smallint")
check("04 TINYINT(1) 归一化为 smallint",
      next(c for c in m["t_demo"].columns if c.name == "ratio").norm_type == "smallint")
check("05 DATETIME(3) 归一化为 timestamp",
      next(c for c in m["t_demo"].columns if c.name == "created").norm_type == "timestamp")
check("06 主键一致", m["t_demo"].primary_key == ["id"] == g["t_demo"].primary_key)
check("07 唯一约束列一致",
      [u[1] for u in m["t_demo"].uniques] == [u[1] for u in g["t_demo"].uniques])
check("08 内联 KEY 与表外 CREATE INDEX 归并一致",
      [i[1] for i in m["t_demo"].indexes] == [i[1] for i in g["t_demo"].indexes])
check("09 一致样本比对为空", compare(m, g) == [])

# 缺列检出
import copy

m2 = copy.deepcopy(m)
m2["t_demo"].columns = [c for c in m2["t_demo"].columns if c.name != "ratio"]
check("10 缺列被检出", any("ratio" in p for p in compare(m2, g)))

# 类型不一致检出
m3 = copy.deepcopy(m)
for c in m3["t_demo"].columns:
    if c.name == "name":
        c.raw_type = "VARCHAR(128)"
check("11 类型不一致被检出", any("name" in p and "不一致" in p for p in compare(m3, g)))

print(f"selftest: {passed}/{total} 通过")
sys.exit(0 if passed == total else 1)
