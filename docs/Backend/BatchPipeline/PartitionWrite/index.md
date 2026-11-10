# 分区写入：覆盖、空窗与原子提交

批次的重跑是常态，不是例外。上游修正一版数据、口径改一个字、某个作业半夜挂了重跑——**每个分区在一生中都会被写不止一次**。

于是「怎么写」决定了三件事：重跑会不会翻倍、下游会不会读到空、历史那一版能不能追溯。

::: tip 一句话定位
本页回答「**同一个分区被写第二次时，库里应该发生什么**」；写之前的日期怎么定在[批次与实例](../BatchInstance/index.md)，写之后怎么判在[就绪与门禁](../ReadinessGate/index.md)。
:::

![覆盖写的空窗：删与插之间，读者读到什么](../assets/bp-window.svg)

## 一、三种写法，一次实测

用同一份源分区（1,916 行），把作业连跑 3 次，看表里最终有多少行：

| 写法 | SQL 形态 | 3 次之后 | 结果 |
| --- | --- | --- | --- |
| 追加 | `INSERT INTO t SELECT ... WHERE dt=?` | **5,748 行** | 3.0×，重复 3,832 行 |
| 主键覆盖 | `INSERT OR REPLACE INTO t ...`（`PRIMARY KEY (dt, id)`） | 1,916 行 | 正确，但依赖主键 |
| 先删后插 | `DELETE WHERE dt=?` + `INSERT ...` | 1,916 行 | 正确，**但有空窗** |

三种都能在「跑完之后」得到正确结果，区别在**跑的过程中**和**跑失败之后**：

| 场景 | 追加 | 主键覆盖 | 先删后插 |
| --- | --- | --- | --- |
| 跑 3 次 | 3 倍 | 不变 | 不变 |
| 跑到一半失败 | 半份新数据 + 整份旧数据（都不对） | 部分行被替换（新旧混合） | **整个分区为空** |
| 无主键的表 | 只能追加 | 不适用 | 可用 |

::: danger 「先删后插」不开事务 = 主动制造一个空分区窗口
实测：自动提交模式下 `DELETE` 先落地，此刻另一个连接读这个分区得到 **0 行**；换成显式事务（`BEGIN` 之后删、插、一起提交），同一时刻读到的是**旧的 1,916 行**。

差别只在一个 `BEGIN`，但后果差一个事故：下游恰好在那个窗口里取数，就会把「没有数据」当成「当天没有交易」。
:::

## 二、原子性的三个层次

「原子」不是一个开关，是一个层次选择。越往下越强，也越贵。

| 层次 | 做法 | 保证什么 | 代价 |
| --- | --- | --- | --- |
| 语句级 | 单条 `INSERT OR REPLACE` | 单行原子 | 只解决重复，不解决「整分区新旧混合」 |
| 事务级 | `BEGIN` … `COMMIT` 包住删+插 | 读者看不到中间态 | 事务期间锁住该分区（写阻塞） |
| 分区交换 | 写临时表/临时分区，再 `EXCHANGE PARTITION` 或 `RENAME` | 读者永远看到完整的一版 | 需要额外的表或分区名额 |
| 快照提交 | 列存/湖表的一次 commit（Iceberg、Delta、Hudi） | 多个分区一次原子可见 | 依赖表格式与元数据服务 |

选择判据只有一条：**下游有没有可能在你写的同一秒读这个分区**。

- 下游是「按点触发的下一个作业」，且依赖边上是「分区 READY」——事务级够用（READY 在提交之后才写）。
- 下游是「随时可查的在线接口 / BI 直连」——必须分区交换或快照提交，否则读者会撞上中间态。
- 下游是「另一个也在补数的作业」——两个写者并发，事务级也不够，要加分区级互斥。

```sql
-- 分区级互斥：同一 (job, data_date) 同一时刻只允许一个写者
CREATE TABLE partition_lock (
  job_id    TEXT NOT NULL,
  data_date TEXT NOT NULL,
  owner     TEXT NOT NULL,
  acquired_at TEXT NOT NULL,
  PRIMARY KEY (job_id, data_date));
-- 取锁：INSERT 成功即持有；释放：DELETE。抢锁失败说明有人在写同一天。
```

## 三、幂等键：分区的身份

幂等不是「写两次结果一样」，而是**「写两次，系统里只有一份」**。这要求有一个稳定的键。

| 键 | 幂等吗 | 问题 |
| --- | --- | --- |
| `(job_id, data_date)` | 是 | 正确：这就是分区的身份 |
| `(job_id, run_id)` | 否 | 每次重跑 `run_id` 都不同，等于没键 |
| `batch_id`（时间戳批次号） | 否 | 每次跑一个新批次号，重跑就是新数据 |
| `(job_id, data_date, attempt)` | 部分是 | 只能防「同一次尝试重复提交」，防不住重跑翻倍 |

::: warning 拿「批次号」当幂等键是最常见的错
`batch_id = 20260915_0210` 这种「日期+时刻」的批次号，看起来唯一、看起来很安全，但它是**每次运行新生成的**——重跑必然产生新批次号，于是「重跑」在库里表现为「又来了一批新数据」。幂等键必须是**业务上同一件事**的标识，也就是 `(job_id, data_date)`。
:::

## 四、空分区必须被登记

「0 行」是一个合法的结果，但它必须是**被登记过的 0 行**，不是「什么都没发生」。

```sql
-- 空分区也要写一行：state='EMPTY'，row_cnt=0，water_mark=NULL
INSERT INTO partition_registry (job_id, data_date, run_id, row_cnt, amt_sum, water_mark, checksum, state, committed_at)
VALUES ('ods_order', '2026-10-03', 1234, 0, 0, NULL, '0-0', 'EMPTY', '2026-10-04 00:41:00');
```

三种「0 行」的区别，决定了下游能做什么：

| 情形 | 记录形态 | 下游应该 |
| --- | --- | --- |
| 那天真的没有业务（节假日） | `state='EMPTY'`，有运行记录 | 正常继续，产出 0 |
| 上游文件没来 | **没有分区记录** | 阻塞、告警，不能当 0 |
| 读到了文件但解析出 0 行 | `state='EMPTY'` + 判据 `ROW_ZERO` 未通过 | 阻塞，等人工确认 |

实测里国庆 7 天产生了 6 次「`exit 0` 且 0 行」，其中 1 天是因为「跨切点的单落到了 10-01 的文件里」——它是 0 行，但不是「没有业务」。这两种 0 行必须能分开，靠的就是判据（见[就绪与门禁](../ReadinessGate/index.md)）。

## 五、分区裁剪：写对了还要读得动

分区列的类型与写法，直接决定查询能不能裁剪。在 106,747 行的表上实测五种写法：

| 写法 | 执行计划 | 单次耗时 | 相对 |
| --- | --- | --- | --- |
| `dt = ?` | `SEARCH ... USING COVERING INDEX (dt=?)` | 0.066 ms | 1.0× |
| `dt >= ? AND dt < ?` | `SEARCH ... (dt>? AND dt<?)` | 0.101 ms | 1.5× |
| `dt LIKE '2026-09%'` | **`SCAN`** | 6.518 ms | **98.8×** |
| `substr(dt,1,7) = ?` | **`SCAN`** | 8.554 ms | **129.7×** |
| `date(dt) = ?` | **`SCAN`** | 11.611 ms | **176.1×** |

三条推论：

1. **分区列必须是「可直接比较的类型」**。`dt` 用 `TEXT('YYYY-MM-DD')` 或 `DATE`，不要用 `TIMESTAMP` 再靠 `date()` 转——一旦套了函数，索引与分区裁剪一起失效。
2. **范围条件优于函数条件**。要查一个月，写 `dt >= '2026-09-01' AND dt < '2026-10-01'`，不要写 `substr(dt,1,7)='2026-09'`。
3. **`LIKE '前缀%'` 在 SQLite 里也不走索引**（实测 98.8×）。MySQL 上它会走，换库时要重测——**这是「同一句 SQL 换引擎变慢」的典型来源**。

## 六、判据清单

| 编号 | 判据 | 不满足时改哪里 |
| --- | --- | --- |
| `BPW-A` | 分区写入是「覆盖」语义，同一分区跑 3 次行数不变 | 写入语句 |
| `BPW-B` | 删+插在同一事务内，或使用分区交换/快照提交 | 写入脚本的事务边界 |
| `BPW-C` | 幂等键是 `(job_id, data_date)`，不是批次号或 `run_id` | 去重逻辑 |
| `BPW-D` | 空分区写一行 `state='EMPTY'`，与「没有记录」可区分 | 提交逻辑 |
| `BPW-E` | 分区列类型可直接比较，查询里没有 `date(dt)`/`substr(dt,...)` 这类包裹 | 列类型与查询 |
| `BPW-F` | 金额列为整数分，无浮点列参与求和 | 列类型 |
| `BPW-G` | 存在分区级互斥（锁表或调度器独占），两个写者不会同时写同一天 | 写入入口 |
| `BPW-H` | 覆盖写的中间态对外不可见：有一次性验证「删后未插时读者读到旧版本」 | 事务边界 |

## 七、验证方式

```shell
cd /tmp && python3 - <<'PY'
import sqlite3
con = sqlite3.connect("/tmp/bplab.db")
q = lambda s: con.execute(s).fetchone()[0]

print("1) 同一分区重跑三次后的行数（应等于源行数）：")
print("   rows =", q("SELECT COUNT(*) FROM dwd_order WHERE dt='2026-09-10'"))
print("2) 源分区行数：")
print("   src  =", q("SELECT COUNT(*) FROM ods_order WHERE dt='2026-09-10'"))
print("3) 执行计划（必须是 SEARCH）：")
for r in con.execute("EXPLAIN QUERY PLAN SELECT COUNT(*) FROM ods_order WHERE dt='2026-09-10'"):
    print("  ", r[3])
PY
```

预期输出：

```text
1) 同一分区重跑三次后的行数（应等于源行数）：
   rows = 1916
2) 源分区行数：
   src  = 1916
3) 执行计划（必须是 SEARCH）：
   SEARCH ods_order USING COVERING INDEX ix_ods_dt (dt=?)
```

第 1 段若是源行数的 2~3 倍，说明写成了追加；第 3 段若出现 `SCAN`，说明查询里给分区列套了函数。

## 参考资料

- [PostgreSQL 18: INSERT ... ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: Partitioning（DETACH/ATTACH 与并发）](https://www.postgresql.org/docs/18/ddl-partitioning.html)
- [MySQL 8.4: EXCHANGE PARTITION](https://dev.mysql.com/doc/refman/8.4/en/partitioning-management-exchange.html)
- [Apache Iceberg: Reliability（原子提交与快照隔离）](https://iceberg.apache.org/docs/latest/reliability/)
- [SQLite: Transaction](https://sqlite.org/lang_transaction.html)
