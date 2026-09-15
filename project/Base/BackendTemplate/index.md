# 后端通用模板

<p style="text-align:center;"><img src="./assets/backend-template-logo.png" style="zoom:75%;" /></p>

周期 3（第 61~90 天）的月度项目：从 0 到 1 构建一套**可直接复用的后端通用模板**。目标不是"跑通一个 Hello World"，而是交付一个具备统一响应、全局异常、参数校验、认证授权、多环境配置、数据访问、日志与健康检查、容器化部署的**完整工程基座**——新业务项目 fork 后改配置即可开工。

## 项目目标与验收标准

| 维度 | 具体目标 | 验收方式 |
| --- | --- | --- |
| 广度 | 覆盖工程结构、配置、Web、校验、异常、数据访问、认证、日志、监控、部署 | 每块都有可运行代码与文档 |
| 深度 | 每块都讲清"为什么这么设计"，不是抄一份配置 | 关键决策有对比与取舍说明 |
| 完整性 | 一键启动 + 一键打包 + 一键部署脚本 | 按文档从零可在 15 分钟内跑起来 |
| 可验证 | 每一步都有 curl / 命令 / 预期输出 | 验收清单逐条打勾 |

## 技术选型

| 组件 | 选型 | 版本基线 | 选型理由 |
| --- | --- | --- | --- |
| 语言 | Java | 25 LTS | 当前 LTS（Spring Boot 4.x 最低 Java 17，推荐 25） |
| 框架 | Spring Boot | 4.1.x | 2026 年当前稳定版（基于 Spring Framework 7、默认 Jackson 3） |
| 构建 | Maven | 3.9+ | 生态成熟、模板化程度高，多模块支持好 |
| Web | Spring MVC | 随 Boot | 团队熟悉度高，同步阻塞模型易排查 |
| 校验 | Jakarta Bean Validation | 随 Boot | 声明式校验，错误统一收集 |
| 文档 | springdoc-openapi | 3.x 线 | 注解即文档，配合 Knife4j 可观感更好；Boot 4.x 必须用 3.x（2.x 会启动失败） |
| 安全 | Spring Security 7.x ｜ Sa-Token 1.46+ | 二选一 | 默认 Spring Security（与 Boot 4.x 主线匹配）；追求开发效率、要注解式鉴权选 Sa-Token。见[技术栈可插拔](./StackSelect/index.md) |
| 数据库 | MySQL + JPA ｜ MyBatis ｜ MyBatis-Plus ｜ MyBatis-Flex | MySQL 8.4 LTS | 主库固定 MySQL 8.4；ORM 四选一，默认 MyBatis-Plus（国内团队主流，8.4 支持到 2032） |
| 缓存 | Redis 8.x ｜ Caffeine ｜ 无缓存 | 三选一 | 默认 Redis；选 Caffeine 或无缓存会让令牌撤销 / 失败计数 / 账号锁定三项降级，**必须显式接受** |
| 监控 | Spring Boot Actuator + Micrometer | 随 Boot | 零侵入暴露健康、指标、端点 |
| 测试 | JUnit + Testcontainers | JUnit 6.x / Testcontainers 2.0.x | **Boot 4.0 起默认 JUnit 6**（JUnit 5 的写法继续可用）；集成测试用**真实 MySQL / Redis 容器**，不用 H2 代替（见 [测试数据隔离与边界用例](./TestIsolation/index.md)） |
| 部署 | Docker + Compose | — | 环境一致性最好的落地方式 |

::: info 版本说明（2026-09 核对）
Spring Boot 4.1 于 2026-06 发布，为当前稳定版；**3.5.x 的 OSS 支持已于 2026-06-30 结束**，新项目不建议再以 3.x 为基线。Spring Security 7.x 对应 Spring Boot 4.x。若团队存量仍在 3.x，模板结构不变，只需把依赖与 `jakarta` 包名按 3.x 调整（详见仓库 Spring Boot 版本页）。
:::

## 模块划分

第 75 天之前是五个模块的直线结构（`application → web → security → data → common`）。第 76 天为了让技术栈可插拔，重构成**四层 + 可替换实现层**：

```text
backend-template/
├─ template-common/                    # 统一响应、错误码、工具类、常量（不依赖任何模块）
├─ template-spi/                       # 契约层：AuthPort / TokenStatePort / CachePort + 仓储接口
├─ template-web/                       # 业务层：Controller、参数校验、全局异常、日志
│
├─ template-security-spring/     ┐     # 实现层：安全（二选一）
├─ template-security-satoken/    ┘
├─ template-data-jpa/            ┐     # 实现层：数据（四选一）
├─ template-data-mybatis/        │
├─ template-data-mybatis-plus/   │
├─ template-data-mybatis-flex/   ┘
├─ template-cache-redis/         ┐     # 实现层：缓存（三选一）
├─ template-cache-caffeine/      │
├─ template-cache-noop/          ┘
│
├─ template-application/               # 装配层：唯一依赖具体实现的地方（main + 配置 + 打包）
├─ stack-select/                       # 技术栈选择器脚本 + 自测（不是 Maven 模块）
├─ docker/                             # Dockerfile、compose 文件
└─ scripts/                            # 启动、打包、部署脚本
```

四条约定：

1. 依赖方向严格单向：**`application → web / 实现层 → spi → common`，永不反向。**
2. `template-common` 不依赖任何模块，否则立刻成环。
3. 实现层之间**零引用**，只通过 `spi` 的契约通信。
4. `template-web` **不依赖任何实现层**——这是"换技术栈不改业务代码"能成立的唯一原因。

::: info 为什么重构而不是新增模块
原结构里 `template-security` / `template-data` 既是"契约"又是"实现"，两者混在一个模块里，换实现就必须改业务模块的依赖，`AuthPort` 这类接口也无处安放。拆成 `spi`（契约）+ 多个实现模块之后，业务侧只认接口，装配层只认实现——**变化点被收敛到实现模块里**。

完整的模块边界论证、SPI 契约设计、两层装配机制与选择器脚本，见[技术栈可插拔](./StackSelect/index.md)。
:::

## 进度跟踪

| 日期 | 阶段 | 本次产出 | 状态 |
| --- | --- | --- | --- |
| 第 61-68 天 | 第 1 周：需求与设计 | 需求清单、技术选型、模块划分、目录结构、接口契约 | ✅ 见[需求与架构设计](./Architecture/index.md) |
| 第 69 天 | 第 2 周：核心编码 ① | 可运行骨架 + 统一响应 + 全局异常 + 健康检查 | ✅ 见下方模块页 |
| 第 70 天 | 第 2 周：核心编码 ② | 请求追踪 ID + 日志切面 + 参数校验增强 + MockMvc 集成测试 | ✅ 见下方模块页 |
| 第 71 天 | 第 2 周：核心编码 ③ | MyBatis-Plus 接入 + 分页插件 + 审计字段自动填充 + 逻辑删除/乐观锁 + 数据层集成测试 | ✅ 见下方模块页 |
| 第 72 天 | 第 2 周：核心编码 ④ | Spring Security 7 + JWT 无状态认证链路 + 声明式权限 + 401/403 统一出口 | ✅ 见下方模块页 |
| 第 73 天 | 第 3 周：联调与测试 ① | 登录业务闭环（账号锁定/密码强度/登录审计）+ 双令牌刷新与登出黑名单 + SecurityIT 扩到 8 用例 | ✅ 见下方模块页 |
| 第 74 天 | 第 3 周：联调与测试 ② | 性能基线（k6 脚本 + TPS/P95）、覆盖率补齐到 75% 并门禁化、OpenAPI 契约回归 | ✅ 见下方模块页 |
| 第 75 天 | 第 3 周：联调与测试 ③ | 测试数据隔离三档（事务回滚 / 清库 / Testcontainers）、并行执行配置、边界用例矩阵（长度、字符类、令牌 exp、锁定次数、并发刷新） | ✅ 见下方模块页 |
| 第 76 天 | 模板产品化 ①（插队） | 技术栈三维可插拔（四层模块划分 + SPI 契约 + 双层装配 + 降级门禁）、选择器脚本与 57 项自测、模板 CLI 设计评审与路线图 | ✅ 见下方模块页 |
| 第 77-79 天 | 第 3 周：联调与测试 ④ | 联调异常路径收口、用例清单化、测试约定落文档 | ⏳ |
| 第 80-90 天 | 第 4 周：部署与验收 | Docker 镜像、Compose、CI 流水线、验收清单 | ⏳ |

## 各阶段交付内容

**第 69 天（骨架与基础能力）**：

1. [骨架与目录结构](./Skeleton/index.md)：Maven 多模块骨架、启动类、配置文件，可 `mvn spring-boot:run` 启动；并用 **Maven Profile** 管理同一大版本下的依赖小版本与 JDK 编译目标差异（含 BOM 导入取舍、toolchains、`.mvn/maven.config` 与 CI 矩阵）。
2. [统一响应与全局异常](./CommonResponse/index.md)：`Result<T>` 统一返回结构、`ErrorCode` 错误码、`@RestControllerAdvice` 全局异常处理。
3. [健康检查与配置](./HealthCheck/index.md)：Actuator 暴露健康与指标端点、多环境配置、启动验证。

**第 70 天（可观测性与校验）**：

4. [请求追踪 ID 与日志切面](./TraceId/index.md)：`TraceIdFilter` 生成/透传 `X-Trace-Id` 并写入 MDC，Logback 日志串联，`WebLogAspect` 统一切面埋点。
5. [参数校验增强](./Validation/index.md)：分组校验、自定义 `@Mobile` 注解、字段级错误明细。
6. [MockMvc 集成测试](./IntegrationTest/index.md)：把 curl 验证固化为自动化用例，并接入 JaCoCo 覆盖率门禁。

**第 71 天（数据访问）**：

7. [数据访问：MyBatis-Plus 接入](./DataAccess/index.md)：`BaseEntity` + 拦截器链（分页/乐观锁/防全表更新）、`MetaObjectHandler` 审计字段自动填充、逻辑删除、`PageResult` 统一分页出参、Testcontainers 数据层集成测试。

**第 72 天（认证与授权）**：

8. [认证授权：Spring Security 7 + JWT](./Security/index.md)：无状态认证链路（`JwtAuthenticationFilter` 插在 `UsernamePasswordAuthenticationFilter` 之前）、jjwt 令牌签发与校验、`UserContext` 桥接审计字段、401/403 统一走 `Result<T>` 出口、`@PreAuthorize` 声明式权限与 12 条踩坑清单。

**第 73 天（第 3 周：联调与测试）**：

9. [登录业务闭环与令牌生命周期](./AuthLifecycle/index.md)：`AuthService` 账号锁定（连续 5 次失败锁 15 分钟）+ 密码强度校验 + 登录审计表 `t_login_log`、Redis 键设计、双令牌刷新（Refresh 一次性消费防重放）与登出 `jti` 黑名单，`SecurityIT` 从 4 个用例扩到 8 个。

**第 74 天（第 3 周：性能与契约门禁）**：

10. [压测与性能基线](./PerformanceTest/index.md)：k6 压测脚本（登录 + 受保护接口双场景）与 TPS / P95 基线三要素、JaCoCo 0.8.15 按模块设覆盖率阈值（`template-security` ≥ 75%）并绑定 `verify` 门禁、springdoc-openapi 3.1.x 导出 `openapi.json` 做契约回归与破坏性变更拦截。

11. [测试数据隔离与边界用例](./TestIsolation/index.md)：**不再用 H2 假装 MySQL**——Testcontainers 2.x 起真实 MySQL 8.4 + Redis 8（singleton container 模式 + `@DynamicPropertySource`）；隔离三档（`@Transactional` 回滚 / `@Sql` 清库 / 独立库）各自的速度、隔离度与失效场景；`TRUNCATE` 的隐式提交与外键约束坑；清库与 Redis `flushDb` 必须成对；JUnit 并行执行配置与 `@ResourceLock`；边界用例四步法与矩阵（9 类输入 × 三值取法）、参数化测试、注入 `Clock` 替代 `Thread.sleep`、`CountDownLatch` 对齐起跑线的并发刷新用例。

**第 76 天（模板产品化：从"一套焊死的基座"到"可参数化的基座"）**：

13. [技术栈可插拔：模块边界与选择器脚本](./StackSelect/index.md)：安全 / 数据 / 缓存三个维度各自可插拔。四层模块划分（`common → spi → web / 实现层 → application`）与依赖单向约定；SPI 契约设计（`AuthPort` / `TokenStatePort` / `CachePort` / `UserRepository`，以及**为什么不统一 ORM 的 CRUD 接口**）；两层装配（Maven profile 决定谁进 reactor，Spring 条件决定谁生效）；24 种组合与 5 个预设；**能力降级门禁**（`cache != redis` 时令牌撤销 / 失败计数 / 账号锁定必须显式接受）；`stack-select.py` 选择器（幂等 / `--check` CI 门禁 / 只写 marker 区间）与 **57 项断言的自测**。

14. [模板 CLI：从 0 到 1 的设计评审与路线图](./TemplateCli/index.md)：把上面这套能力产品化成命令行工具。**生成器（greenfield）与切换器（brownfield）是两个不同问题**——前者渲染模板写新目录，后者只改 marker 区间不动业务代码，共用的是选择模型与版本目录。三处事实纠正（Java 25 才是当前 LTS、Shiro 3.0 的定位、"总是取最新稳定版"与可复现冲突）；生成内核选型（自研 vs 复用 Spring Initializr）；模板组织与**文件级条件包含**；Picocli 与 GraalVM native image；**starter 坐标随 Boot 线变化**的实证坑与 Boot 4 模块化的两个显式依赖；支持矩阵先收窄、MVP 验收标准与明确不做的事。

15. [进展记录](./Progress/index.md)：逐日做了什么、如何验证、下一步是什么。

## 本地运行（快速上手）

```shell
# 环境要求：JDK 25、Maven 3.9+、Python 3.11+（选择器脚本用，零第三方依赖）
java -version     # 期望：openjdk version "25"
mvn -v            # 期望：Apache Maven 3.9.x
python3 -V        # 期望：Python 3.11 及以上

cd backend-template

# 1) 先选技术栈（默认 classic：Spring Security + MyBatis-Plus + Redis）
python3 stack-select/stack-select.py --list
python3 stack-select/stack-select.py --preset classic

# 2) 选完之后自测一遍：57 项断言覆盖幂等、marker 边界、降级门禁与 24 种组合
python3 stack-select/selftest.py     # 期望：共 57 项断言，通过 57，失败 0

# 3) 构建与启动
mvn -q clean package -DskipTests
java -jar template-application/target/template-application-1.0.0.jar

# 4) 改了 stack.json 或 pom 之后，用 --check 确认没漂移（可直接当 CI 门禁）
python3 stack-select/stack-select.py --root . --check   # 期望：OK，退出码 0
```

::: info 关于本文的验证环境
本文代码按 **Spring Boot 4.1.x + Java 25** 编写并逐处核对官方文档，但当前编写环境没有 JDK / Maven，**未在本地实际编译运行**。请按各页「验证方式」在本地执行，若版本号与官方最新补丁不一致，以 Spring Boot 官方发布的当前补丁版本为准。
:::

## 参考资料

- Spring Boot 官方文档：[docs.spring.io/spring-boot](https://docs.spring.io/spring-boot/index.html)
- Spring Boot 4.0 发布公告：[spring.io/blog](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now)
- 相关文档：[Spring Boot 通用指南](../../../docs/Backend/Java/Frame/SpringBoot/Common/index.md) / [Spring Security 7](../../../docs/Backend/Java/Frame/SpringSecurity/v7/index.md) / [数据建模](../../../docs/DB/DataModeling/index.md)
- 本项目的产品化两条：[技术栈可插拔：模块边界与选择器脚本](./StackSelect/index.md) / [模板 CLI：设计与路线图](./TemplateCli/index.md)
- 开发环境与工具链：[效率工具](../../../docs/Tools/Efficiency/index.md)（终端、命令行、脚本自动化）、[效率工具 · 实战](../../../docs/Tools/Efficiency/Practice/index.md)（把脚本、Git 钩子、容器化接进项目的六步清单）
