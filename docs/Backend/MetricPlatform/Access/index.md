# 权限、行级过滤与脱敏

指标平台的权限比业务系统更容易出错，原因是它**看起来很简单**：谁能看哪个指标，配一张表就完了。但真正决定「看到多少」的不是指标权限，而是**行级过滤**——同一张「区域成交额」，华东经理应该只看到华东的五分之一，而不是全域总数。

漏掉行级过滤的表现极其安静：接口返回 200、数字有量级、格式完全正确，只是**多给了 79.88% 的行**。没有任何人会因此报警，除了三个月后的合规审计。

![权限三轴与过滤下推](../assets/mp-rls.svg)

## 一、三轴模型：缺一轴就等于没有权限

| 轴 | 回答 | 实现位置 | 漏掉的后果 |
| --- | --- | --- | --- |
| 指标权限 | 能不能查这个指标 | 语义层（请求校验） | 查到不该看的指标 |
| 行级过滤 | 能看到哪几行 | 编译期注入 `where` | 看到别人的数据（本题） |
| 列级脱敏 | 能看到哪些列、什么精度 | 结果集处理 | 看到手机号、身份证、成本价 |

三轴是**相乘**关系，不是相加。只做第一轴的系统，相当于给每个人发了全域数据，只是限制了「能看哪些报表」。

## 二、行级过滤的四种实现

| 方式 | 做法 | 优点 | 风险 |
| --- | --- | --- | --- |
| 数据库 RLS | `create policy` + `current_setting` | 无法绕过（连直连也生效） | 依赖具体数据库；连接池需正确设置会话变量 |
| 视图封装 | 每个表建一个带过滤的视图 | 实现简单、可移植 | 视图数量爆炸；join 时容易漏用视图 |
| 编译期注入 | 语义层在生成 SQL 时加谓词 | 与指标平台天然一体 | 编译逻辑有 bug 就全线失效 |
| 结果集过滤 | 查完再在应用层筛 | 不改 SQL | **最危险**：总数已泄露，且分页/聚合全错 |

前三种都能做对，第四种**永远做不对**。原因很简单：先 `sum` 再过滤，得到的是全域总额减去可见部分，两头的数都错；而分页场景下「第 2 页」可能一条都不剩。

### 本机读数

| 场景 | 应见行数 | 实见行数 | 越权比例 |
| --- | --- | --- | --- |
| 订单表（区域 = east） | 6,811 | 33,858 | **79.88%** |
| join 明细后 | — | 56,167 | 明细全部可见 |

6,811 是 east 区域的订单数，33,858 是全域订单数。一个只做了「指标权限」的系统，华东经理看到的正是 33,858——而这个数看起来完全正常。

::: danger 过滤后置的两种典型漏法
1. **先聚合再过滤**：`select region, sum(amount) group by region` 查完，在应用层挑出 `region='east'`。返回给用户的行数是对的，但**总数已经算过全域**；一旦接口支持「总计」字段，全域数字直接泄露。
2. **join 后过滤落在错误的表**：`where o.region='east'` 只过滤了订单表，明细表 `fact_item` 没有 `region` 列，于是 join 出来的明细行数仍是全量。本机 join 后 56,167 行即此类。
:::

## 三、下推：让数据库替你做过滤

正确的做法是把谓词编译进 SQL 的 `where`，并且**下推到每一张参与的表**：

```sql
-- 正例：两处都带过滤
select o.region, sum(i.item_amount) as gmv
from fact_order o
join fact_item i on i.order_id = o.id
where o.region = ?                       -- 订单侧过滤
  and o.status = 'paid'
  and i.order_id in (select id from fact_order where region = ?)   -- 明细侧同步收窄
group by o.region;
```

第二行的子查询看起来冗余，实际是很多优化器的「过滤传播」未必能穿透 join 的保险。更稳的写法是把过滤放到 CTE 里，先收窄再 join：

```sql
with scoped_order as (
  select id, region, amount from fact_order where region = ? and status = 'paid'
)
select s.region, sum(s.amount)
from scoped_order s
join fact_item i on i.order_id = s.id
group by s.region;
```

代价是可能少用一次索引；收益是**不可能漏**。在权限这件事上，正确性优先于性能。

## 四、缓存键：最容易穿权限的地方

缓存键里必须包含**权限上下文**，否则 A 查过的结果会被 B 直接命中：

```text
错误键：gmv|2026-06|month|region:all
正确键：gmv|2026-06|month|region:all|scope:region=east|v2
```

三个必须进键的元素：

| 元素 | 为什么 | 漏掉的后果 |
| --- | --- | --- |
| 行级过滤条件 | 不同人看到不同行 | 越权（最严重） |
| 口径版本 | 口径切换后旧结果失效 | 新旧口径混用 |
| 脱敏级别 | 同一指标不同角色可见列不同 | 明文泄露 |

**一个常见的错误优化**是「按指标 + 期间缓存，命中后再过滤」。这在数值型指标上尤其危险：缓存里存的是全域总额，过滤后无法还原成「该用户可见的总额」。

## 五、聚合泄露与小样本抑制

即使行级过滤做对了，聚合结果仍可能泄露个体信息：

| 泄露形态 | 例子 | 抑制方式 |
| --- | --- | --- |
| 小样本 | 某区域只有 2 个客户，`count=2` 且 `sum` 已知 | `count < k` 时置空或合并（k 通常取 5~10） |
| 差分推断 | 查「全域」与「除某人外」两个数，相减得个体值 | 限制查询组合、记录异常查询模式 |
| 极值暴露 | `max` / `min` 直接暴露某个个体 | 极值类指标按权限收紧 |

小样本抑制会带来一个新问题：**总数与分项之和不等**（被抑制的格子变成空）。这不是 bug，必须在文档里写清楚，否则会引发「平台算错了」的工单。

## 六、列级脱敏：精度也是权限

脱敏不只是「打星号」，还包括精度：

| 类型 | 原始 | 脱敏后 | 注意 |
| --- | --- | --- | --- |
| 手机号 | `13812345678` | `138****5678` | 保留前 3 后 4，便于客服核对 |
| 金额 | `12345.67` | `12000`（按千取整） | 取整后仍可能被差分推断 |
| 成本价 | `12.34` | 不可见 | 成本类字段通常整列屏蔽 |
| 用户 ID | `u_88213` | `hash(u_88213)` | 哈希需加盐，否则可撞库 |

精度脱敏的坑在于**聚合后的还原**：给业务看「按千取整」的金额，业务拿去算占比，误差会被放大到不可用。正确做法是**在聚合之后脱敏**，而不是在明细上脱敏再聚合。

## 七、审计：证明「没有越权」而不是「应该没越权」

审计日志要能回答三个问题：

```sql
create table metric_access_log (
  id integer primary key,
  ts text not null,
  actor text not null,          -- 谁
  metric_key text not null,     -- 查了什么
  scope text not null,          -- 当时的行级过滤条件（编译后的谓词）
  rows_returned int not null,   -- 返回多少行
  denied int not null default 0 -- 是否被拒
);
```

| 问题 | 查法 |
| --- | --- |
| 谁看过全域数据 | `where scope like '%region:all%' and actor not in (select actor from admin_list)` |
| 有没有异常大结果集 | `where rows_returned > 100000 order by rows_returned desc` |
| 拒绝率是否异常 | `where denied=1` 按天聚合，突增说明权限配置错了 |

「应该没越权」是设计，「证明没越权」是日志。合规检查要的是后者。

## 八、本专题的判据族

本页判据族 `MSP-A` ~ `MSP-H`，共 8 条。

| 判据 | 要求 | 判定方式 |
| --- | --- | --- |
| `MSP-A` | 三轴齐全，行级过滤不得后置 | 编译产物 SQL 里能看到过滤谓词 |
| `MSP-B` | 行级过滤实现四选一，且写明风险 | 实现方式可查，不选「结果集过滤」 |
| `MSP-C` | 过滤下推到每张参与表 | join 场景下明细表同样被收窄 |
| `MSP-D` | 缓存键含过滤条件、版本、脱敏级别 | 键结构可解析出三段 |
| `MSP-E` | 小样本抑制有阈值 k | `count < k` 时返回空而非数值 |
| `MSP-F` | 脱敏在聚合之后，不在明细上 | 聚合结果精度符合预期 |
| `MSP-G` | 审计日志记录 `scope` 与 `rows_returned` | 三类审计查询都能跑 |
| `MSP-H` | 越权验证有可复跑的用例 | 构造 east 用户查询，行数等于 east 行数 |

## 九、验证方式

```shell
# 1. 对比「先过滤后聚合」与「先聚合后过滤」的结果
sqlite3 :memory: "
create table o(id int, region text, amount real);
insert into o values (1,'east',100),(2,'east',200),(3,'north',900);
select region, sum(amount) from o where region='east' group by region;
select sum(amount) from (select region, sum(amount) s, amount from o group by region) where region='east';"
# 期望：east|300.0 然后 300.0 —— 两种写法在这一层看起来一样
```

```shell
# 2. 但「总计」会暴露：先聚合再过滤的系统，总计仍是全域
sqlite3 :memory: "
create table o(id int, region text, amount real);
insert into o values (1,'east',100),(2,'east',200),(3,'north',900);
select sum(amount) as 全域 from o;
select sum(amount) as 可见 from o where region='east';"
# 期望：1200.0 | 300.0 —— 900 元的越权信息藏在第一个数里
```

```shell
# 3. 确认 join 场景下明细侧也被收窄
sqlite3 :memory: "
create table o(id int, region text, amount real);
create table i(oid int, amt real);
insert into o values (1,'east',100),(2,'north',900);
insert into i values (1,100),(2,900);
select count(*) from o join i on i.oid=o.id;                          -- 未过滤
select count(*) from o join i on i.oid=o.id where o.region='east';    -- 订单侧过滤
select count(*) from (select * from o where region='east') s join i on i.oid=s.id;  -- 下推"
# 期望：2 | 1 | 1
```

第 2 条命令的 `1200.0` 与 `300.0` 是本页最重要的两个数：**只要接口还能返回「总计」，后置过滤就等于没过滤**。

## 与「报表与自助分析工程」专题的分工（第 262 天补充）

本页定义「策略长什么样、怎么下推、怎么证明没越权」；[报表与自助分析工程](../../ReportAnalytics/index.md)回答「同一份策略在页面的合计行、下钻结果、导出文件三处是不是同一个结果」。策略只有一份，落地有三处，三处不同源就是越权或漏数。

::: danger 一页一坑：权限过滤了结果，而不是过滤了输入
「先聚合再按权限筛行」在代码里非常自然：先跑出 4 个大区的汇总，再把没权限的行去掉。本机 40,000 单、权限范围 30 位负责人的实测：

| 实现 | 合计 | 明细和 | 差 |
| --- | --- | --- | --- |
| 先过滤后聚合 | 394,643,731 | 394,643,731 | 0 |
| 先聚合后裁剪 | **1,814,179,432** | 394,643,731 | **4.60 倍** |

表格里每一行都对，只有最下面那个合计错——而用户第一眼看的是合计。判据只有一条：**合计行必须能由它自己的明细行加总得到**。做不到，就不是「显示问题」，是过滤位置错了。

:::

## 参考资料

- PostgreSQL 官方文档《Row Security Policies》：`create policy` 与 `current_setting` 的用法与限制，<https://www.postgresql.org/docs/current/ddl-rowsecurity.html>
- Apache Ranger 官方文档：跨组件的列级与行级策略模型，<https://ranger.apache.org/>
- Open Policy Agent《Policy Language》：把权限判定从代码里抽出来做统一策略，<https://www.openpolicyagent.org/docs/latest/policy-language/>
- 与本页相邻的册子：[多租户的租户上下文](../../MultiTenantSaaS/TenantContext/index.md)、[查询编译](../Compile/index.md)、[双口径对账](../Reconcile/index.md)。
