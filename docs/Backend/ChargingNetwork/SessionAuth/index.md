# 启充与鉴权：谁证明这枪该给他用

一位车主插上枪，App 显示「启动中」，两分钟后变成「启动失败，请联系客服」。桩的日志里却是另一回事：`Authorize` 通过了，`StartTransaction` 也回了，**电已经在充了**。失败的是平台的账户服务——它拒绝了那笔预授权冻结，但这条拒绝没有回传给桩。

**启充是充电链路里唯一一个「双方都要说同意」的动作。** 桩说「我能充」，平台说「他付得起」，两者缺一，结果都不是「没充上」，而是「充了但没记账」。

::: tip 一句话理解
鉴权解决「能不能充」，唯一约束解决「会不会重复计费」。**这是两件事，不能用同一个机制兜**。
:::

## 一、四条启充路径

![四条启充路径与各自的失败形态](../assets/cn-session.svg)

本机模型按 62% / 21% / 14% / 3% 的四条路径分布生成会话（这是建模输入，不是行业统计），四条路径的鉴权强度与离线能力完全不同：

| 路径 | 谁在做鉴权 | 需要联网吗 | 失败形态 |
| --- | --- | --- | --- |
| 扫码启充 | 平台（`RemoteStartTransaction`） | 桩与平台都要在线 | 桩离线 → 启不了；平台慢 → 车主干等 |
| 刷卡启充 | 桩本地白名单 / 离线钱包 | **不需要** | 能充，但余额由桩自算，可能与平台不一致 |
| 即插即充 | 车桩握手（ISO 15118 / MAC） | 首次绑定时需要 | 换车、换牌后不重绑 → 认不出 |
| 预约锁枪 | 平台（预约单占位） | 需要 | 过期不解锁 → 白占一天 |

四条路径共用一个结果：**生成一个 `charging_session`，并锁住那把枪**。

## 二、鉴权强度 × 离线能力的四象限

把「要不要联网」和「谁承担金额风险」画成两维，四条路径的定位就清楚了：

| | 离线也能充 | 必须联网 |
| --- | --- | --- |
| **平台承担金额风险** | 刷卡（离线钱包，额度由桩自控） | 扫码、即插即充 |
| **用户承担金额风险** | 无（不存在） | 预约锁枪（占位费先扣） |

第二行第一列是空的，这不是巧合：**离线状态下没有任何机制能证明「这个账户付得起」**。所以刷卡路径的离线钱包必须由桩侧设上限，而这个上限是一个商务参数，不是技术参数。

::: danger 离线钱包的三个必错
1. **额度写死在固件里。** 换一个客户、换一个城市就要重新烧固件。正确做法是随 `BootNotification` 下发配置。
2. **离线消费不同步到平台。** 桩记了 30 元，平台不知道，车主在 App 上看到余额没变，于是继续刷——直到某天桩上报一笔「历史欠费」。
3. **挂失卡在离线桩上仍然可用。** 挂失是平台侧状态，桩不知道。只能靠「下次联网时同步黑名单 + 对已发生的离线消费做追认」这一套补丁。
:::

## 三、一枪一活动会话：唯一约束比鉴权更重要

无论走哪条路径，最终都落同一条硬约束：

```sql
CREATE TRIGGER trg_one_active_session
BEFORE INSERT ON charging_session
WHEN NEW.state = 'CHARGING'
BEGIN
  SELECT RAISE(ABORT, 'ACTIVE_SESSION_EXISTS')
  WHERE EXISTS (SELECT 1 FROM charging_session
                WHERE connector_no = NEW.connector_no AND state = 'CHARGING');
END;
```

为什么这条约束必须在数据库里，而不是在代码里？因为**它要防的不是并发，是重试**：

- 车主点了两次「启动」，平台发出两条 `RemoteStartTransaction`。
- 桩超时重发，平台收到两条 `StartTransaction`。
- 补偿任务扫到「有开始没结束」的单，又补了一条。

三种情况在代码层看起来都像「一次正常的请求」，只有数据库知道「这把枪已经有一个活动会话了」。

本机实测：插一条同枪活动会话，报 `ACTIVE_SESSION_EXISTS`；换一把枪则正常通过。

## 四、预授权与冻结：钱要在充电前就锁住

扫码与即插即充在启充前要做一次预授权（冻结一笔金额），否则充完发现扣不到钱，只能走坏账。

| 环节 | 时机 | 金额口径 | 失败后果 |
| --- | --- | --- | --- |
| 预授权冻结 | `StartTransaction` 之前 | 按车型电池容量估（如 60 度 × 1.3 元 = 78 元） | 不冻结 → 充完可能扣不到钱 |
| 充电中 | 每 15 s | 实时累计，接近冻结额时提醒 | 不提醒 → 充到一半被停 |
| 结算解冻 | `StopTransaction` 之后 | 按实际金额扣款，差额解冻 | 不解冻 → 用户额度被长期占用 |

本机读数里有一组数字能说明「冻结额估小了会怎样」：单均 36.81 kWh、度电流水 1.1847 元，单均金额约 43.6 元；但充电上限是 100 度电池从 12% 充到 100%，最贵的一单能到 100 元以上。**按均值冻结，必然有一批单在充电中途触顶**。

::: warning 一个反直觉的结论
**「启充失败率」这个指标几乎没有意义。** 本机 120 把枪 60 天的在线率是 99.71%，而可用率只有 97.70%——中间那 2.01 个点的桩，心跳正常但启不了充。

对车主来说，「启不了」的体验完全一样，但归因完全不同：一个是网络问题（改协议），一个是设备问题（派工单）。**只有把「启充失败」拆成「桩不可用」「鉴权拒绝」「预授权失败」三类，指标才有行动价值。**
:::

## 五、判据族 `CNR-A ~ CNR-H`

本页判据族 `CNR-A` ~ `CNR-H`，共 8 条。它们描述「一次启充是否只有一个赢家、一笔钱是否被锁住」。

| 编号 | 判据 | 怎么验 |
| --- | --- | --- |
| `CNR-A` | 一把枪同一时刻只能有一个活动会话 | 同枪第二次插 `CHARGING` 报 `ACTIVE_SESSION_EXISTS` |
| `CNR-B` | 会话记录启充路径（`auth_type`），不是只记「成功」 | 可按路径统计成功率与金额分布 |
| `CNR-C` | 启充失败按三类归因（桩不可用 / 鉴权拒绝 / 预授权失败） | 失败码枚举恰好三组 |
| `CNR-D` | 预授权金额按电池容量估，不按均值 | 冻结额与 `soc_end - soc_start` 正相关 |
| `CNR-E` | 离线钱包额度来自配置下发，不写在固件里 | 改配置后离线可消费额度变化 |
| `CNR-F` | 挂失卡在下次联网时进入本地黑名单 | 存在同步环节与生效时间字段 |
| `CNR-G` | 预约过期有解锁机制，不永久占枪 | 存在 `expired_at` 与解锁任务 |
| `CNR-H` | 会话结束与解冻是两步，中间可重试 | 存在 `state='CLOSED'` 但未解冻的中间态 |

## 六、验证方式

```shell
# 1. 一枪一活动会话（期望报错）
sqlite3 :memory: "
create table s(txn text primary key, conn text, state text);
create trigger t before insert on s when new.state='CHARGING'
begin
  select raise(abort,'ACTIVE_SESSION_EXISTS')
  where exists (select 1 from s where conn=new.conn and state='CHARGING');
end;
insert into s values ('T1','C1','CHARGING');
insert into s values ('T2','C1','CHARGING');" 2>&1 | head -1
# 期望输出：Error: stepping, ACTIVE_SESSION_EXISTS (19)

# 2. 换一把枪则通过（期望插入成功、计数为 2）
sqlite3 :memory: "
create table s(txn text primary key, conn text, state text);
insert into s values ('T1','C1','CHARGING'),('T2','C2','CHARGING');
select count(*) from s;"
# 期望输出：2

# 3. 按均值冻结必然触顶（期望 43.6 与 118.4 的对比）
python3 -c "
avg=36.81*1.1847; peak=100*1.1847
print(round(avg,1), round(peak,1), round(peak/avg,1))"
# 期望输出：43.6 118.5 2.7
```

第 3 步说明：**均值与峰值的差距是 2.7 倍**。按均值冻结，最贵的那批单一定会在充电中途触顶；按峰值冻结，绝大多数用户的额度被过度占用。

## 参考资料

- Open Charge Alliance《OCPP 2.0.1 Specification》：`Authorize`、`RemoteStartTransaction`、`Reservation` 的消息定义。
- ISO 15118-2:2014《Road vehicles — Vehicle-to-Grid Communication Interface》：即插即充的证书链与鉴权流程。
- GB/T 18487.1—2023《电动汽车传导充电系统 第 1 部分：通用要求》：充电启动与停止的控制导引时序。
- 与本页相邻：[接入与协议](../ProtocolAccess/index.md)、[充电与计量](../Metering/index.md)、[结算与分成](../SettlementSplit/index.md)。
