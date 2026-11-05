# 对局结算与幂等：七个写入点，只有一处是「分数」

一局打完，客户端没收到结算包，玩家点了「重试」。服务端其实第一次就成功了，于是第二次也写了——MMR +16 变成 +32，胜场记录变成两条。玩家没有察觉，因为界面上只显示「+16」；直到他赛季末发现自己比同水平的人高了一截。

**结算是一条链上最容易「看起来成功」的一段：接口返回 200、分数变了、记录也有，唯独多算了一次。** 而它不像下单那样有金额核对，多算 16 分不会触发任何告警。

::: tip 一句话理解
结算的唯一硬约束是「一局对一个人只能结算一次」。这条约束不能靠 `select` 判断，只能靠**主键**——因为判断与写入之间永远有窗口。
:::

## 一、一局结算要写七个地方

![结算的七个写入点与幂等闸门](../assets/mk-settle.svg)

| 序 | 写什么 | 落哪张表 | 失败后能否重放 | 能否重复 |
| --- | --- | --- | --- | --- |
| ① | 冻结对局 | `match.state = 'SETTLED'` | 能 | 幂等（同状态再写无变化） |
| ② | 写结算单 | `settle_log(match_id, player_id)` | 能 | **不能**（主键挡住） |
| ③ | 改 MMR | `player.mmr += delta` | 能 | **不能**（重复就多加） |
| ④ | 记流水 | `mmr_history(before, after, reason)` | 能 | 不能（与③同事务） |
| ⑤ | 算赛季分 | `season_point += delta` | 能 | 不能 |
| ⑥ | 刷榜单 | `ZADD` / 更新榜表 | 能 | 幂等（覆盖写） |
| ⑦ | 发奖励 | `reward_grant(idem_key)` | 能 | **不能**（`idem_key` 唯一） |

七个点里有四个「不能重复」，一个「幂等」，两个「覆盖写」。**这就是为什么要先写 ②**：`settle_log` 的主键 `(match_id, player_id)` 是整条链唯一能天然挡住重放的东西；先写它，后面的 ③④⑤ 就变成「已经过了闸门」的顺理成章。

顺序反过来（先改 MMR 再写日志）会怎样？第一次成功、第二次在写日志时被主键挡住并回滚——但 MMR 已经改了。**回滚只回滚同事务内的写入**，如果 ③ 在另一个事务里，它就永远多加了。

## 二、幂等：三个数与两条记录

本机把「网关超时 → 客户端重试 3 次」这件事复现了一遍：

| 写法 | 玩家 A 的 MMR | 玩家 B 的 MMR | 记录条数 |
| --- | --- | --- | --- |
| 无幂等键 | **1,554** | 1,446 | 3 条 |
| `UNIQUE(match_id, player_id)` | 1,518 | 1,482 | 1 条 + 2 次被拒 |

无键版本多算了 36 分（+18 × 2），而两次被拒的写法结算结果与「只打了一局」完全一致。更关键的是**记录条数**：无键版本留下 3 条 `settle_log`，意味着「这局到底算了几分」永远说不清；有键版本只有 1 条，另外两次是明确的 `IntegrityError`，可以计数、可以告警。

### 为什么不用「先查有没有」

```sql
-- 错误写法：判断与写入之间有窗口
select count(*) from settle_log where match_id = ? and player_id = ?;
-- 若为 0，则 insert
```

两个并发的重试请求会同时查到 0，然后同时插入。这不是理论问题：本机 16 线程各加 10 分 20 次（应得 4,700），**先查后改实得 1,700，丢了 63.8%**，而且全程没有一条错误日志。正确的做法只有两种：

1. **唯一约束**：让数据库拒绝第二次。
2. **条件更新**：`update ... where state = 'RUNNING'`，用 `rowcount` 判断谁赢了。

本册两者都用：`settle_log` 用主键挡重放，`match.state` 用条件更新挡并发。

## 三、并发：谁先到，谁说了算

同一局被两个进程同时结算（一个来自对局服，一个来自补偿任务），本质是「两个写者抢同一行」。本机的两组读数：

| 场景 | 写法 | 结果 | 正确值 |
| --- | --- | --- | --- |
| 16 线程各加 10 分 × 20 次 | 先查后改 | **1,700** | 4,700 |
| 16 线程各加 10 分 × 20 次 | `mmr = mmr + 10` | 4,700 | 4,700 |
| 同一局结算 3 次 | 无唯一键 | 1,554 | 1,518 |
| 同一局结算 3 次 | 主键 + 唯一键 | 1,518 | 1,518 |

注意第一行与第二行的区别不是「加了锁」，而是**「读-改-写」被压成了一个原子语句**。SQLite 的写事务是串行的，`update player set mmr = mmr + 10` 在事务内天然原子；换成 MySQL / PostgreSQL 也一样，只要不在应用层做「读出来加完再写回去」。

## 四、掉线、平局、重连：三种「非正常结束」

结算逻辑里最容易被忽略的不是并发，而是**结果枚举不全**。本机在实战表里用的 `result` 有四个值：`WIN` / `LOSE` / `DRAW` / 空缺（未结束）。但真实系统至少还要区分：

| 情况 | 结果怎么记 | 分数怎么算 | 常见错法 |
| --- | --- | --- | --- |
| 正常分出胜负 | `WIN` / `LOSE` | 按 Elo | — |
| 平局 | `DRAW` | `S = 0.5` | 当成双方都输，两人都掉分 |
| 开局前有人掉线 | `ABORTED`（不结算） | 不计分 | 记成 LOSE，玩家申诉无门 |
| 中途掉线（4v5 打完） | 按实际结果 | 需按人数修正实力函数 | 按队均分算，掉线方胜率仍 50.21% |
| 掉线后重连 | 同一 `match_id` | **不能二次结算** | 重连触发一次「补结算」，多算一遍 |

第四行是本册反复强调的那条：按队均分算，4v5 的胜率是 **50.21%**（几乎无惩罚）；按队总分算，只剩 **7.29%**。**实力函数选错，掉线判定就等于没做。**

::: danger 三个「重试友好、业务致命」的写法
1. **用 `match_id` 做幂等键但作用域搞错**：只写 `UNIQUE(match_id)`，会导致「一局只能结算一个人」。作用域必须是 `(match_id, player_id)`。
2. **补偿任务不检查状态**：定时任务每小时扫「未结算的局」，它必须只看 `state = 'RUNNING' AND ended_at IS NOT NULL`，否则会把已经结算的局再算一次。
3. **把「发奖励」放在结算事务外面**：结算成功、发奖失败，玩家少了奖励；反过来（先发奖后结算）则可能出现「奖励发了、分没加」。正确做法是发奖走独立的 `idem_key`，允许异步重放，见[实战](../Practice/index.md)的 `reward_grant`。
:::

## 五、可回滚：为什么必须记 `before` 和 `after`

结算出错（比如那局其实是自定义房间）需要回滚。能不能回滚，取决于你当初存了什么：

| 存法 | 能否回滚 | 说明 |
| --- | --- | --- |
| 只存 `delta` | 不能 | 不知道当时是多少分，`-16` 可能把它扣成负数 |
| 存 `before` / `after` | 能 | `update player set mmr = :before`，并可留一条 `reason='CORRECTION'` |
| 存事件流（每局一条） | 能，且可重放 | 最适合做「如果那局不算」的假设分析 |

本册的 `trg_settle_apply` 在写入 `delta` 的同一条语句里，把 `before`（当前值）与 `after`（当前值 + delta）一起写进 `mmr_history`。这样任何一次回滚都有据可依，而且**回滚本身也是一条 history**，不会被误认为「没发生过」。

## 六、判据族 `MKS-A ~ MKS-H`

本页判据族 `MKS-A` ~ `MKS-H`，共 8 条。它们描述「这一局的分是不是只加了一次、加得对不对」。

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `MKS-A` | `settle_log` 主键为 `(match_id, player_id)` | 第二次插入同一对报唯一约束 |
| `MKS-B` | 结算与改分在同一事务 | 中途失败后 `mmr` 与日志都不变 |
| `MKS-C` | MMR 用原子自增，不用「先查后改」 | 并发结果等于理论值 |
| `MKS-D` | `delta` 符号与 `result` 一致 | 输的人写正分被触发器拒绝 |
| `MKS-E` | 结算前校验两侧人数相等、无空缺结果 | 4v5 或有人无结果时结算被拒 |
| `MKS-F` | 重连不触发二次结算 | 同一 `match_id` 重连后 `settle_log` 仍只有一行 |
| `MKS-G` | 回滚写 `reason='CORRECTION'` 并保留原记录 | 回滚后能查到两条 history |
| `MKS-H` | 补偿任务只扫 `RUNNING` 且已结束的局 | 扫已结算局时 result 为 0 行 |

## 七、验证方式

```shell
# 1. 结算两次会怎样（期望第二次被主键挡住）
sqlite3 :memory: "
create table settle_log(match_id text, player_id text, delta real,
  primary key(match_id, player_id));
insert into settle_log values ('M1','P1',16);
insert into settle_log values ('M1','P1',16);"
# 期望输出：Error: stepping, UNIQUE constraint failed: settle_log.match_id, settle_log.player_id (19)

# 2. 条件更新只有一个赢家（期望 changes() = 1，第二次 = 0）
sqlite3 :memory: "
create table match(id text primary key, state text);
insert into match values ('M1','RUNNING');
update match set state='SETTLED' where id='M1' and state='RUNNING';
select changes() as first_win;
update match set state='SETTLED' where id='M1' and state='RUNNING';
select changes() as second_win;"
# 期望输出：1 与 0

# 3. 原子自增（期望 1540，不是 1500）
sqlite3 :memory: "
create table p(id int, mmr real);
insert into p values (1,1500);
update p set mmr = mmr + 20 where id=1;
update p set mmr = mmr + 20 where id=1;
select mmr from p;"
# 期望输出：1540.0
```

第二条是本页的核心：`changes()` 返回 1 的那个进程才有权继续写后续六步，返回 0 的直接退出。**这就是「不用锁也能互斥」的最小实现**。

## 参考资料

- PostgreSQL 官方文档《Concurrency Control》第 13 章：事务隔离与「读-改-写」丢失更新的成因。
- SQLite 官方文档《Transaction》与 `changes()` 函数说明：行级影响计数与条件更新的判定方式。
- 《信息安全技术 网络安全等级保护基本要求》GB/T 22239—2019：结算类数据的完整性与可追溯要求（本册以「留 before/after」满足）。
- 与本页相邻：[配对与匹配质量](../Match/index.md)、[幂等键](../../IdempotencyStateMachine/IdempotencyKey/index.md)、[实战](../Practice/index.md)。
