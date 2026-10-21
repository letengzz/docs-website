# 测试策略与门禁

「测试全绿但上线就出问题」的根因通常不是测试写得少，而是**测试写错了层**：单元测试里连数据库、集成测试里用 H2 假装 MySQL、端到端测试拿去覆盖分支。本页讲清每一层该干什么，以及门禁阈值怎么设才不会被绕过。

![测试分层：谁的活谁干，别让上层替下层兜底](../assets/test-pyramid.svg)

## 一句话定位

测试策略的核心是**分工**：越靠下的层跑得越快、覆盖越细；越靠上的层越少、但越接近「用户能不能用」。每层只做自己该做的事，测试总量才会既快又有意义。

## 分层职责

| 层次 | 覆盖什么 | 不该做什么 | 参考数量比 |
| --- | --- | --- | --- |
| 静态检查 | 格式、类型、明显缺陷、契约破坏性变更 | 逻辑正确性 | 每次提交必跑 |
| 单元测试 | 纯逻辑、算法、边界条件、状态机 | 连数据库 / 网络 / 文件系统 | 60%~70% |
| 集成测试 | 主链路、SQL 正确性、事务与并发、序列化 | 覆盖所有分支 | 20%~30% |
| 端到端 | 关键用户旅程「串起来是通的」 | 用它做分支覆盖 | 5~10 条核心旅程 |
| 性能基线 | 吞吐、延迟分位、资源占用 | 功能正确性 | 每轮发布一次 |

::: danger 三个「层写错」的典型症状
1. **单元测试启动慢**（几秒起）：说明它连了真实依赖。单元测试应当毫秒级，慢下来后团队就会跳过它。
2. **集成测试用内存数据库替代真实数据库**：方言差异、事务语义、`TRUNCATE` 的隐式提交、外键行为都会与生产不同，测试通过不代表能用。用真实数据库容器。
3. **端到端测试数量超过单元测试**：跑一轮要半小时，团队会开始绕过它——最终等于没有。
:::

## 覆盖率门禁怎么设

覆盖率是最容易被误用的指标：设一个全库平均线，只会被最容易测的模块拉高，而最危险的模块仍然没被覆盖。

| 做法 | 评价 |
| --- | --- |
| 全库设一个平均线（如 80%） | **不推荐**：达标靠的是简单模块，核心模块可能仍然裸奔 |
| 按模块设阈值 | **推荐**：核心模块（认证、支付、权限）阈值更高 |
| 只涨不跌（增量门禁） | **推荐**：对本次改动的覆盖率做要求，存量不倒退即可 |
| 把覆盖率当交付目标 | **反模式**：会催生大量无断言的「走过场」测试 |

```xml
<!-- 按模块设阈值（Maven + JaCoCo，示例） -->
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.15</version>            <!-- 版本以官方最新为准 -->
  <executions>
    <execution>
      <id>check</id>
      <goals><goal>check</goal></goals>
      <configuration>
        <rules>
          <rule>
            <element>BUNDLE</element>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.75</minimum>   <!-- 默认线：只降不升才拦 -->
              </limit>
            </limits>
          </rule>
          <rule>
            <!-- 核心模块单独抬高：安全与权限相关代码必须有测试 -->
            <element>CLASS</element>
            <includes>
              <include>com.example.security.*</include>
            </includes>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.85</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

### 门禁阈值的三条设定原则

1. **从现状往上抬一小步**，不要一步到 90%。定一个永远达不成的阈值，等于把门禁关掉。
2. **区分模块**：核心链路（认证、鉴权、资金、状态机）阈值高于工具类。
3. **新代码必须带测试**：用增量覆盖率卡住新提交，比全量阈值有效得多。

## 集成测试要接真实依赖

| 依赖 | 错误的替身 | 后果 |
| --- | --- | --- |
| 数据库 | H2 / 内存库 | SQL 方言、事务、锁行为不同，测试通过但生产失败 |
| 缓存 | `ConcurrentHashMap` | 序列化、过期策略、宕机行为完全不同 |
| 消息队列 | 直接调用消费者方法 | 丢失重试、幂等、顺序性的验证 |
| 外部 HTTP 服务 | 全局 mock | 超时、重试、降级逻辑没人验证 |

推荐组合：**Testcontainers 起真实的 MySQL / Redis 容器**，用 `@DynamicPropertySource` 把随机端口注入配置。

```java
// 集成测试：真实 MySQL 容器 + 真实 Redis（Spring Boot 4 / Testcontainers 2.x 写法示意）
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderApiIT {

    @Container
    @ServiceConnection                       // 自动把容器地址注入 Spring 配置
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.4");

    @Container
    @ServiceConnection
    static RedisContainer<?> redis = new RedisContainer<>("redis:8");

    @Autowired TestRestTemplate rest;        // Boot 4 亦可考虑 RestTestClient

    @Test
    void 按状态筛选订单_返回分页且条数正确() {
        // 1) 准备数据：12 笔待发货订单
        // 2) 调用接口 GET /api/orders?status=待发货&page=1&size=10
        // 3) 断言 total=12、records.size=10，且每条 status 均为「待发货」
    }
}
```

::: tip 容器启动太慢怎么办
三条常用手段：① **singleton container 模式**（静态容器 + 手动启动，整个测试类/套件共用一个实例）；② 镜像预热（CI 里 `docker pull` 提前拉好）；③ 分层执行（单元测试与集成测试分阶段，单元测试先给快速反馈）。

具体做法（包括 singleton 容器的写法、清库与 Redis `flushDb` 必须成对等细节）见 [测试数据隔离与边界用例](../../../../project/Base/BackendTemplate/TestIsolation/index.md)。
:::

## 测试数据隔离：三档各有适用场景

| 档位 | 做法 | 速度 | 隔离度 | 适用 |
| --- | --- | --- | --- | --- |
| 事务回滚 | `@Transactional` 自动回滚 | 最快 | 中（跨线程/跨事务失效） | 单事务内的查询类用例 |
| 清库 | `@Sql` / 清表脚本 | 中 | 高 | 涉及多事务、异步的用例 |
| 独立库 | 每个套件独立 schema/容器 | 最慢 | 最高 | 并发、序列、事务隔离级别的验证 |

::: warning 清库与缓存必须成对清理
只清库不清缓存，会出现「第一次跑通过、第二次跑就失败」的玄学问题——上一次的令牌黑名单、失败计数还留在 Redis 里。**数据库清理与缓存清理必须在同一个 `@BeforeEach` 里成对写。**
:::

## 边界用例：三值法 + 矩阵

每个输入取三个值（下界 −1、下界、上界 +1），把「输入 × 场景」写成矩阵，确保没有漏格：

| 输入 | 下界 −1 | 下界 | 上界 +1 |
| --- | --- | --- | --- |
| `size`（1~100） | 0 → 400 | 1 → 200 | 101 → 400 |
| 令牌 `exp` | 已过期 1 秒 → 401 | 恰好等于当前 → 判定一致 | 未过期 → 200 |
| 失败次数（上限 5） | 4 次 → 仍可登录 | 5 次 → 锁定 | 6 次 → 保持锁定 |
| 字符串长度（1~64） | 0 → 400 | 1 → 200 | 65 → 400 |

```java
@ParameterizedTest
@ValueSource(ints = {0, 1, 101})
void 分页参数边界(int size) {
    var resp = rest.postForEntity("/api/orders?page=1&size=" + size, null, String.class);
    int expected = (size == 1) ? 200 : 400;
    assertThat(resp.getStatusCode().value()).isEqualTo(expected);
}
```

::: tip 用「恰好的边界值」而不是「差不多的值」
「恰好等于上界」与「上界 +1」是两个不同的用例，前者常被漏掉。判据是：**每个校验规则至少有三个用例——刚好合法、刚好越界、明显越界**。
:::

## flaky 测试：当天修或删除

随机失败（flaky）的测试比没有测试更糟，因为它训练团队忽略红色。

| 常见根因 | 修法 |
| --- | --- |
| `Thread.sleep` 等待异步结果 | 改用轮询断言（Awaitility）或注入可控时钟 |
| 并发用例起跑线不齐 | 用 `CountDownLatch` 让线程同时起跑 |
| 依赖时间（当前日期、时区） | 注入 `Clock`，测试固定时间 |
| 依赖执行顺序（共享静态状态） | 每个用例自建数据，不共享可变状态 |
| 随机端口/随机数据冲突 | 隔离到独立 schema，或使用随机化但可复现的种子 |

约定：**发现 flaky 当天处理**——要么修，要么删掉并开一条明确的重写任务。挂着不修的红灯就是没有红灯。

## 性能基线：三个必需元素

```text
① 可复现的压测脚本（场景、并发数、持续时间都写在脚本里）
② 明确的判据（例如：登录 50 并发下 TPS ≥ 200，P95 < 500ms）
③ 基线记录（上一版的数字，用于判断这次的改动是不是回退）
```

只报「TPS 是 X」而没有基线，等于没有结论——**性能结论永远是相对的**。

## 门禁清单：CI 里该拦哪些

```text
每次提交（3 分钟内给结论）：
  □ 编译通过
  □ 静态检查（lint / 类型 / 依赖漏洞）
  □ 单元测试全绿
  □ 契约破坏性变更检查（无破坏性变更）

每次合并 / 发布前：
  □ 集成测试全绿（真实数据库与缓存容器）
  □ 覆盖率门禁（按模块阈值）
  □ 种子数据 + 迁移脚本在空库上跑通
  □ 冒烟测试通过（部署后）
  □ 性能基线未回退（或回退在允许范围内）
```

## 本页的可验证收尾

```shell
# ① 单元测试快：整轮应在秒级到分钟级
mvn -q test -Dtest='*Test' -DfailIfNoTests=false && echo "单元测试通过"

# ② 集成测试真的连了容器（日志里能看到容器启动）
mvn -q verify -Dtest='*IT' 2>&1 | grep -i "container" | head -3

# ③ 覆盖率门禁能被触发：故意删掉一个测试，门禁应当失败
mvn -q verify -Djacoco.skip=false && echo "门禁通过"

# ④ 检查是否存在 flaky 隐患（搜索固定等待）
grep -rn "Thread.sleep" src/test | grep -v "// 已评估" || echo "无固定等待"
```

## 工具层落点

本页给出的是**职责边界、测试数据隔离的三档取舍与 CI 门禁清单**——回答「哪一层该测什么、门禁卡在什么标准、数据怎么隔离」。至于每一层**具体用哪个工具、脚本怎么写、命令怎么敲**，落在 [测试工具专题](../../../Tools/TestingTools/index.md)，那里给的是能照着跑一遍的工具细节。

| 测试目标 | 本项目（本页）的方法 | 对应工具页 |
| --- | --- | --- |
| 纯逻辑与边界条件 | 单元测试不碰网络 / 文件 / 时间，三值法覆盖边界 | [测试工具专题总览](../../../Tools/TestingTools/index.md) |
| 接口主链路与契约 | 集成测试连真实容器，契约破坏性变更进 CI 拦截 | [接口自动化](../../../Tools/TestingTools/APIAutomation/index.md) |
| 性能基线与容量拐点 | 可复现压测脚本 + 明确判据 + 上一版基线对照 | [JMeter 压力测试](../../../Tools/TestingTools/JMeter/index.md) |
| 跨浏览器端到端旅程 | 关键旅程 5~10 条，等待策略稳定、flaky 当天处理 | [Selenium 端到端测试](../../../Tools/TestingTools/Selenium/index.md) |

## 与在线协作任务板的分工

本页讲**测试策略**：分层怎么切、用例放哪一层、覆盖率门禁卡在哪一步。

[在线协作任务看板 · 可运行验证](../../../../project/Complete/TeamBoard/Verification/index.md) 是本页策略在「**并发型系统**」上的一份实例，它多出两类本页没有的验证：

| 验证类型 | 本页的通用做法 | 任务看板的做法 |
| --- | --- | --- |
| 功能正确性 | 单测 + 集成测试 + 端到端 | 同左，但断言多一条：**响应里必须回传 `version`** |
| 并发正确性 | 通常只说「注意竞态」 | **两个终端同时拖同一张卡片**：期望一成一败、`version` 只前进 1——单用户操作永远测不出这类缺陷 |
| 实时正确性 | 不在本页范围 | 两个 WebSocket 客户端：A 改动 → B 收到事件，且 `seq` 连续无缺口 |
| 顺序正确性 | 不在本页范围 | 「**一次拖动只更新一行**」——它是能证伪的性能判据，不是描述性说法 |

::: warning 并发与实时这两类判据不能靠「跑一遍通过」来证明
功能用例可以通过一次执行证明，并发与实时判据**必须能被证伪**：把乐观锁去掉、把广播改到提交之前，判据应当立刻变红。**跑一遍是绿的、改坏了还是绿的**，这条判据就没有价值。
:::

## 与「联调与测试」章节集的分工（第 148 天补充）

第 148 天为[在线协作任务看板](/project/Complete/TeamBoard/index.md)交付了「联调与测试」章节集八页（[联调](/project/Complete/TeamBoard/Integration/index.md) / [自动化测试分层](/project/Complete/TeamBoard/TestStrategy/index.md) / [覆盖率门禁](/project/Complete/TeamBoard/CoverageGate/index.md) / [端到端测试](/project/Complete/TeamBoard/E2ETest/index.md) / [并发与幂等](/project/Complete/TeamBoard/Concurrency/index.md) / [权限矩阵](/project/Complete/TeamBoard/PermissionMatrix/index.md) / [压测与容量](/project/Complete/TeamBoard/CapacityTest/index.md) / [周验收收口](/project/Complete/TeamBoard/Week3Acceptance/index.md)）。两者是**方法论 vs 落地记录**的关系：

| 边界问题 | 归本页 | 归章节集 |
| --- | --- | --- |
| 测试策略该怎么定、四层怎么划分 | 给通用口径（分层原则、配比区间、评审要点） | 给这一套系统的四层职责表与**逐条定值理由**（为什么端到端只占 5%） |
| 覆盖率门禁该不该上、上到什么程度 | 给决策依据（成本与收益、组织前提） | 给三档阈值、门禁五步链与**棘轮 + 豁免**的具体机制 |
| 「验收条件怎么写」 | 给四类验收条件与 Given/When/Then 的写法 | 给 `A1`~`A8` 与 `TB-A`~`TB-H`，以及**阻塞项台账**的真实形态 |
| 测试数据与质量门禁的组织问题 | 给流程与角色（谁定阈值、谁批豁免） | 给可复算的读数与 `grep -c` 判据（期望值均为实跑回填） |

一句话：**本页回答「这件事该不该做、组织上怎么定」；章节集回答「在协作看板这一个系统上，它具体长什么样、怎么验」。**

## 与「租户边界」章节集的分工（第 155 天补充）

| 维度 | 本页 | 「租户边界」章节集（第 155 天） |
| --- | --- | --- |
| 回答的问题 | 测试分层、用例设计、覆盖率与门禁 | 越权用例为什么必须「先红后绿」，以及 18 格矩阵怎么表达成参数化用例 |
| 用例性质 | 验证「功能对不对」 | 验证「不该发生的事有没有发生」——后者只能用「期望失败」表达 |
| 写法 | 断言返回值 | 断言状态码 + body 为空 + 审计行数，三者缺一不可 |
| 门禁 | 覆盖率与用例通过率 | 跨租户矩阵进合并前门禁，不做 nightly |

一句话结论：**本页讲「怎么证明功能是对的」，章节集讲「怎么证明越权是不成立的」**。

::: danger 这一页特有的坑
越权用例最常见的退化是「照着当前实现写断言」：实现返回 `403` 就断言 `403`。这是记录现状，不是验证要求——正确的顺序是先写会红的用例，再改实现。
:::

## 与「测试数据与仿真环境」专题的分工（第 165 天补充）

| 专题 | 负责什么 | 与本页的边界 |
| --- | --- | --- |
| 本页 | 测试分层、覆盖率门禁、集成测试接真实依赖、flaky 治理 | —— |
| [测试数据与仿真环境](../../../Tools/TestDataSimulation/index.md) | 数据的生成、脱敏、版本化，环境的隔离，依赖的仿真 | 那边回答「**状态从哪来**」；本页回答「**测哪一层、什么算通过**」 |
| [环境隔离](../../../Tools/TestDataSimulation/EnvironmentIsolation/index.md) | 按需环境、租约、三档数据隔离成本 | 本页只说「集成测试要接真实依赖」，怎么把它拉起来在那边 |
| [实战：测试数据流水线](../../../Tools/TestDataSimulation/Practice/index.md) | 多租户系统的八步流水线与 S1~S10 | 本页的「测试数据隔离三档」是**选型**；那边的八步是**落地顺序** |

::: danger 本页特有的坑：覆盖率能刷、判别力不能
`assertNotNull(result)` 一行就能把覆盖率顶上去，但它对「金额算错」「权限判反」一个都抓不到。
用本页的门禁时，同时看一个数：**变更代码被多少条「有实质断言」的用例覆盖**。只数行数，门禁迟早变成形式。
:::

## 与「研发效能度量」专题的分工（第 172 天补充）

本页讲测试分层、覆盖率门禁与 flaky 治理，核心是「**怎么测**」；[研发效能度量](../../../Tools/EngineeringMetrics/index.md) 关心的是「**测完之后漏了多少**」——覆盖率是过程量，逃逸率是结果量。

| 问题 | 归本页 | 归研发效能度量 |
| --- | --- | --- |
| 测试分层、用例组织、覆盖率门禁怎么设 | ✅ | —— |
| 覆盖率 80% 为什么线上还出问题 | 给策略解释 | ✅ [质量指标](../../../Tools/EngineeringMetrics/QualityMetrics/index.md) 的逃逸率 |
| 一个故障被 30 个用户各报一次，算 1 个还是 30 个 | —— | ✅ 同一页的「工单口径 vs 根因口径」（实测 25.0% / 14.3%） |
| flaky 用例算不算缺陷 | 归本页 | 若要进质量指标，需先定口径 |

**本页特有的坑**：覆盖率的分母如果包含生成代码（protobuf 生成物、前端构建产物、AI 生成的样板），覆盖率会被**稀释**；反过来只统计手写代码会**虚高**。两种口径都能到 80%，含义完全不同——所以覆盖率进 CI 门禁时必须写明分母范围，否则「达标」只是换了个分母。

## 相关实战

- [博客平台 · 一条龙回归](/project/Complete/BlogPlatform/CoreFlow/Regression/index.md)（第 110 天）：端到端回归报告的固定五节结构与 CF1~CF14 步骤表——本页「分层职责」中「端到端测试越少越接近用户」一条的完整落档示例，含「实测列只填真跑出来的输出」的报告纪律。

## 参考资料

- [JUnit 5 用户指南](https://junit.org/junit5/docs/current/user-guide/)
- [Testcontainers 官方文档](https://java.testcontainers.org/)
- [JaCoCo：覆盖率与 check 规则](https://www.jacoco.org/jacoco/trunk/doc/check-mojo.html)
- [Awaitility：异步断言](https://github.com/awaitility/awaitility)
- [Martin Fowler：测试金字塔与实用主义](https://martinfowler.com/articles/practical-test-pyramid.html)
