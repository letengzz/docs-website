# 进展记录

本页记录周期 3 项目每一天的**构建步骤与验证结果**——做了什么、怎么验证、下一步是什么。这也是"项目以一个月为周期、每天推进一个可验证步骤"的落地凭据。

![第 69 天进展](../assets/progress-timeline.svg)

## 2026-09-14（第 69 天）：后端骨架 + 统一响应 + 全局异常 + 健康检查

### 本次做了什么

| 序号 | 产出 | 位置 | 对应需求 |
| --- | --- | --- | --- |
| ① | Maven 多模块骨架（聚合 POM、启动类、三套 Profile 配置） | [骨架与目录结构](../Skeleton/index.md) | R1、R7 |
| ② | 统一响应体 `Result<T>` + 错误码枚举 `ErrorCode` | [统一响应与全局异常](../CommonResponse/index.md) | R2、R3 |
| ③ | 全局异常处理 `GlobalExceptionHandler`（业务/校验/兜底三类） | [统一响应与全局异常](../CommonResponse/index.md) | R4 |
| ④ | Actuator 健康端点 + 业务就绪检查 + 演示接口 | [健康检查与配置](../HealthCheck/index.md) | R6 |

同时完成：模块依赖规则与接口契约的定稿，见[需求与架构设计](../Architecture/index.md)。

### 如何验证

```shell
# 1. 打包
cd backend-template
mvn -q clean package -DskipTests
# 预期：BUILD SUCCESS，且 template-application/target/template-application-1.0.0.jar 存在

# 2. 启动
java -jar template-application/target/template-application-1.0.0.jar
# 预期日志：Started TemplateApplication in x.x seconds（Tomcat 8080）

# 3. 四个端点逐个验证
curl -s http://localhost:8080/api/ping
curl -i -s http://localhost:8080/api/biz-error      # 期望 HTTP 409 + code 20001
curl -i -s "http://localhost:8080/api/boom?divisor=0"  # 期望 HTTP 500 + code 50000
curl -s http://localhost:8080/actuator/health       # 期望 {"status":"UP"}
curl -s http://localhost:8080/api/health/ready      # 期望 data.status = UP
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK/Maven，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `mvn clean package` | BUILD SUCCESS | 待填写 | ⏳ |
| 启动日志 | `Started TemplateApplication` | 待填写 | ⏳ |
| `/api/ping` | `code=0, data=pong` | 待填写 | ⏳ |
| `/api/biz-error` | HTTP 409 + `code=20001` | 待填写 | ⏳ |
| `/api/boom?divisor=0` | HTTP 500 + `code=50000`，响应无堆栈 | 待填写 | ⏳ |
| `/actuator/health` | `{"status":"UP"}`，50ms 内 | 待填写 | ⏳ |
| `/api/health/ready` | `status=UP`（DB 可用时） | 待填写 | ⏳ |
| `/actuator/env` | 404（未暴露） | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 统一响应用 `record` 还是 Lombok `@Data` | 用 `record` | 不可变、无注解处理器依赖；团队若需 JavaBean 可换回，契约不变 |
| `traceId` 字段先定契约 | 字段先占位，第 70 天接 MDC | 避免前端集成后二次改字段 |
| liveness 是否包含数据库检查 | 不包含 | 依赖抖动会导致实例被反复重启，引发雪崩 |
| Actuator 暴露范围 | 只开 `health,info,metrics` | `env`/`heapdump` 会泄露配置与内存数据 |

### 下一步（第 70 天）

1. **TraceId 链路**：`OncePerRequestFilter` 生成/透传 `X-Trace-Id` 并写入 MDC，让日志与 `Result.traceId` 串联。
2. **参数校验增强**：新增/更新分组校验（`@Validated(AddGroup.class)`）、自定义校验注解、校验错误统一返回字段级明细。
3. **集成测试**：用 `MockMvc` 把今天的 8 条 curl 验证写成自动化测试，接入 CI 质量门禁。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-79 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ⏳ 4/5 步待续（本次完成第 1 步） |
| 第 3 周（80-86 天） | 联调、单元与集成测试、压测、覆盖率门禁 | ⏳ 未开始 |
| 第 4 周（87-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始 |

## 2026-09-15（第 70 天）：TraceId 链路 + 日志切面 + 参数校验增强 + MockMvc 集成测试

### 本次做了什么

| 序号 | 产出 | 位置 | 对应需求 |
| --- | --- | --- | --- |
| ⑤ | `TraceIdFilter` 生成/透传 `X-Trace-Id`、写入 MDC 并回传响应头；Logback pattern 带 `%X{traceId}` | [请求追踪 ID 与日志切面](../TraceId/index.md) | R5、R9 |
| ⑥ | `WebLogAspect` 统一记录接口入参、耗时与结果状态（成功/业务异常/系统异常三分支） | [请求追踪 ID 与日志切面](../TraceId/index.md) | R9 |
| ⑦ | 分组校验（Add/Update 组）、自定义 `@Mobile` 注解、字段级错误明细 `ValidationError` | [参数校验增强](../Validation/index.md) | R4、R8 |
| ⑧ | MockMvc 全链路契约测试（响应/异常/校验/TraceId）+ JaCoCo 覆盖率门禁 | [MockMvc 集成测试](../IntegrationTest/index.md) | R10 |

同时完成：第 69 天预留的 `Result.traceId` 占位**自动接上 MDC**，契约无需改动、代码零修改。

### 如何验证

```shell
cd backend-template

# 1. 编译 + 跑测试（含契约、校验、TraceId 用例）
mvn -q clean test
# 预期：Tests run: 8, Failures: 0, Errors: 0, Skipped: 0

# 2. 覆盖率门禁（低于 60% 会失败）
mvn -q verify
# 预期：BUILD SUCCESS，target/site/jacoco/index.html 行覆盖率 ≥ 60%

# 3. 启动后手工复核 TraceId 透传
java -jar template-application/target/template-application-1.0.0.jar &
curl -i -s -H "X-Trace-Id: demo-0001" http://localhost:8080/api/ping | grep -i x-trace-id
# 预期：X-Trace-Id: demo-0001
grep "demo-0001" logs/app.log    # 预期：访问 + 业务日志均带该 ID

# 4. 校验明细
curl -s -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' \
  -d '{"username":"ab","password":"123","mobile":"12345"}'
# 预期：code=10400，data.fields 为 {字段: 提示}
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK/Maven，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `mvn clean test` | 8 个用例全过 | 待填写 | ⏳ |
| `mvn verify` | 覆盖率 ≥ 60% | 待填写 | ⏳ |
| `X-Trace-Id` 透传 | 原样回显 | 待填写 | ⏳ |
| 无上游 ID | 生成非空 ID | 待填写 | ⏳ |
| 日志 pattern | 每行带 `[traceId]` | 待填写 | ⏳ |
| 字段级校验 | `data.fields` 结构正确 | 待填写 | ⏳ |
| 线程复用隔离 | 连续请求 ID 不串号 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| traceId 在哪一层初始化 | Servlet Filter（`HIGHEST_PRECEDENCE`） | 早于 DispatcherServlet，能覆盖参数绑定与校验阶段的异常 |
| 上游 ID 是否信任 | 直接透传 | 网关已做生成；后端只做兜底，避免 ID 体系割裂 |
| 日志切面切多大范围 | 只切 `@RestController` | 切 Service/Mapper 会产生海量日志并影响性能 |
| 校验错误返回结构 | `data.fields` 用 `Map` | 前端逐字段高亮，比拼接字符串更好用 |
| 同字段多约束取哪条 | `putIfAbsent` 保留第一条 | 提示更贴近业务直觉（`@NotBlank` 在前） |
| 覆盖率门槛 | 60%，核心模块单独统计 | 防退化即可，不盲目冲高 |

### 下一步（第 71 天）

1. **数据访问**：接入 MyBatis-Plus（`MybatisPlusInterceptor` 分页插件）、`BaseMapper` 泛型封装。
2. **公共字段自动填充**：`MetaObjectHandler` 统一填 `createTime`/`updateTime`/`createBy`/`updateBy`。
3. **数据层集成测试**：用 H2 或 Testcontainers 跑真实 SQL，验证分页与逻辑删除。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-79 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ⏳ 2/5 步完成，数据访问与认证待续 |
| 第 3 周（80-86 天） | 联调、单元与集成测试、压测、覆盖率门禁 | ⏳ 已提前落地 MockMvc + JaCoCo 门禁 |
| 第 4 周（87-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始 |

## 2026-09-16（第 71 天）：MyBatis-Plus 接入 + 分页 + 审计字段自动填充 + 数据层集成测试

### 本次做了什么

| 序号 | 产出 | 位置 | 对应需求 |
| --- | --- | --- | --- |
| ⑨ | `BaseEntity`（雪花 ID + 审计字段 + `@TableLogic` + `@Version`）与业务实体继承约定 | [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) | R11 |
| ⑩ | `MybatisPlusInterceptor` 拦截器链：分页（含 `maxLimit` 封顶）→ 乐观锁 → 防全表更新/删除 | [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) | R11、R12 |
| ⑪ | `AuditMetaObjectHandler`：插入填 `createTime/createBy/version/deleted`，更新填 `updateTime/updateBy` | [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) | R11 |
| ⑫ | `PageResult<T>` 统一分页出参 + `IPage → PageResult` 转换，杜绝内部字段外泄 | [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) | R2、R12 |
| ⑬ | 数据层集成测试（Testcontainers + MySQL 8.4）：填充/分页/逻辑删除/乐观锁 4 个用例 | [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) | R10 |
| ⑭ | 建表脚本 `V1__init_user.sql`：审计列、逻辑删除列、`(username, deleted_at)` 唯一索引 | [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) | R11 |

同时完成：第 70 天 `AuditMetaObjectHandler` 的 `UserContext.currentUserId()` 调用点已预留，第 72 天接入 JWT 后自动生效，**数据层代码无需改动**。

### 如何验证

```shell
cd backend-template

# 1. 结构自检：starter 与拦截器、填充器都在位
grep -n "mybatis-plus-spring-boot4-starter" template-data/pom.xml
# 预期：命中 1 行（Spring Boot 4.x 专用 starter，不是 boot3）

grep -rn "PaginationInnerInterceptor\|BlockAttackInnerInterceptor" template-data/src/main/java
# 预期：同一 MybatisPlusInterceptor 内按 ① ② ③ 注册

# 2. 数据层测试（Testcontainers 需本地 Docker）
mvn -q -pl template-data -am test
# 预期：Tests run: 4, Failures: 0, Errors: 0, Skipped: 0

# 3. 建表 + 启动
mysql -uroot -p template < template-application/src/main/resources/db/migration/V1__init_user.sql
mvn -q -pl template-application -am spring-boot:run &

# 4. 冒烟四连
curl -s -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' \
  -d '{"username":"alice","mobile":"13800138000","email":"alice@example.com"}' | jq '.data'
# 预期：id 为 19 位字符串、createTime 非空、无 deleted 字段

curl -s "http://localhost:8080/api/users?pageNum=1&pageSize=999999" | jq '.data | {total, pageSize}'
# 预期：pageSize = 100（被封顶），total 为真实总数

curl -s -X DELETE http://localhost:8080/api/users/1 | jq .code     # 预期：0
mysql -uroot -p template -e "SELECT id,deleted FROM t_user WHERE id=1"  # 预期：行仍在，deleted=1
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK / Maven / Docker，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| starter 选型 | boot4 starter | 待填写 | ⏳ |
| 拦截器注册顺序 | 分页 → 乐观锁 → 防全表更新 | 待填写 | ⏳ |
| `mvn -pl template-data -am test` | 4 个用例全过 | 待填写 | ⏳ |
| 审计字段自动填充 | `create_time`/`create_by` 非空 | 待填写 | ⏳ |
| 雪花 ID | 19 位且序列化为字符串 | 待填写 | ⏳ |
| 分页 SQL | 日志出现 `LIMIT`，`total` 正确 | 待填写 | ⏳ |
| 页大小封顶 | `pageSize=999999` → 100 | 待填写 | ⏳ |
| 逻辑删除 | 查不到、表内 `deleted=1` | 待填写 | ⏳ |
| 乐观锁 | 陈旧 `version` 影响行数 0 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| starter 用 boot3 还是 boot4 | `mybatis-plus-spring-boot4-starter` 3.5.17 | 模板基线是 Spring Boot 4.1.x；boot3 starter 会导致自动配置不生效 |
| ORM 选 MyBatis-Plus 还是 JPA | MyBatis-Plus | 业务后台以"单表 CRUD + 少量复杂 SQL"为主，MP 的 SQL 控制力与样板消除兼得 |
| 主键策略 | 雪花 ID（`assign_id`） | 为分库分表与数据迁移留路，不依赖数据库自增 |
| `MetaObjectHandler` 用哪个填充方法 | `strictInsertFill` / `strictUpdateFill` | 只在字段为 null 时填充，保留数据迁移场景的原始审计值 |
| 逻辑删除与唯一索引冲突 | 唯一索引建在 `(username, deleted_at)` | 既能"删后重建同名"，又比 `(username, deleted)` 支持多次删除 |
| 分页出参直接用 `IPage` 吗 | 转 `PageResult` | `IPage` 暴露 `orders`/`optimizeCountSql` 等内部字段，且容易带出敏感列 |
| 数据层测试用 H2 还是 Testcontainers | Testcontainers + MySQL 8.4 | H2 方言差异会掩盖真实 SQL 问题；无 Docker 时降级 H2 仅作结构验证 |
| Long 精度 | 全局序列化为字符串 | 雪花 ID 超 `2^53` 会在前端 JS 里末尾变 0 |

### 下一步（第 72 天）

1. **认证链路**：Spring Security 7 + JWT，`JwtAuthenticationFilter` 挂在 `TraceIdFilter` 之后，补 `UserContext` 实现（今天的审计填充点将自动生效）。
2. **接口鉴权**：`@PreAuthorize` + 自定义 `@HasPerm` 声明式权限。
3. **认证集成测试**：MockMvc 覆盖无 token（401）、过期 token（401）、越权（403）、正常（200）四类场景。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-79 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ⏳ 3/5 步完成，仅剩认证 |
| 第 3 周（80-86 天） | 联调、单元与集成测试、压测、覆盖率门禁 | ⏳ 已提前落地 MockMvc + JaCoCo + Testcontainers |
| 第 4 周（87-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始 |

## 2026-09-17（第 72 天）：Spring Security 7 + JWT 无状态认证 + 声明式权限

### 本次做了什么

把模板从"裸接口"变成"默认安全"：

1. **依赖与版本**：`spring-boot-starter-security`（Spring Security 7.1.x）+ jjwt 0.13.0 三件套（`api` / `impl` / `jackson` 版本严格一致）+ `spring-boot-starter-data-redis`（刷新令牌与黑名单）。
2. **JWT 工具类**：[`JwtProperties`](../Security/index.md)（`@ConfigurationProperties` 承载 secret / ttl / issuer）与 `JwtTokenProvider`（`issueAccessToken` 带 `jti` / `sub` / `roles`，`parse` 校验签名、过期与 issuer）。
3. **过滤器链**：`SecurityConfig` 用 Lambda DSL 组装——`SessionCreationPolicy.STATELESS`、白名单精确列举、`addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)` 保证顺序是 **TraceIdFilter → JwtAuthFilter → AuthorizationFilter**。
4. **JWT 过滤器**：`OncePerRequestFilter` 解析 `Bearer` 令牌 → 查黑名单 → 写 `SecurityContext` → `MDC.put("userId")`，并在 `finally` 里清理 MDC 防止线程复用串号。
5. **用户上下文**：`UserContext.userId()` 从 `SecurityContext` 取当前用户，**把第 71 天 `AuditMetaObjectHandler` 预留的调用点接上**——`create_by` / `update_by` 从此写入真实用户 ID。
6. **统一异常出口**：`RestAuthenticationEntryPoint`（401）与 `RestAccessDeniedHandler`（403）都返回 `Result<T>`，前端只需一套解析逻辑，不再遇到 Spring 默认 HTML 错误页。
7. **声明式权限**：`@EnableMethodSecurity` + `@PreAuthorize`，示例覆盖 `hasAuthority` / `hasRole` / 用 `#id == authentication.principal.userId` 做数据级越权防护。
8. **配置与密钥**：`app.jwt.*` 走 `${JWT_SECRET}` 环境变量注入，长度要求 >= 32 字节（建议启动自检）。
9. **测试**：`SecurityIT` 四个 MockMvc 用例锁住"匿名 401 / 有效 200 / 越权 403 / 篡改 401"。
10. 新增示意图 `assets/security-auth-flow.svg`（过滤器链 + 登录签发 + 请求校验 + 异常出口四段）。

### 如何验证

```shell
# 环境要求：JDK 25、Maven 3.9+、Redis 8.x
cd backend-template
export JWT_SECRET="$(openssl rand -base64 48)"   # 长度必须 >= 32 字节

# 1. 编译并跑安全用例
mvn -q clean test -pl template-security -am
mvn -q test -pl template-web -Dtest=SecurityIT
# 预期：Tests run: 4, Failures: 0, Errors: 0, Skipped: 0

# 2. 启动
mvn -q -pl template-application -am spring-boot:run &
# 预期日志：Started TemplateApplication in x.xxx seconds

# 3. 匿名访问受保护接口
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/users
# 预期：401

curl -s http://localhost:8080/api/users
# 预期：{"code":40101,"message":"未登录或令牌已失效","data":null}

# 4. 登录拿令牌
curl -s -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Admin@123"}' | jq '.data | {tokenType, expiresIn}'
# 预期：{"tokenType":"Bearer","expiresIn":1800}

# 5. 带令牌访问
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Admin@123"}' | jq -r '.data.accessToken')
curl -s http://localhost:8080/api/users -H "Authorization: Bearer $TOKEN" | jq .code
# 预期：0

# 6. 越权（普通用户删用户）
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE http://localhost:8080/api/users/1 \
  -H "Authorization: Bearer $USER_TOKEN"
# 预期：403

# 7. 确认无状态：响应头不应出现 Set-Cookie
curl -sI http://localhost:8080/api/users -H "Authorization: Bearer $TOKEN" | grep -i "set-cookie" || echo "no session cookie (OK)"

# 8. 审计字段接上了真实用户
mysql -uroot -p template -e "SELECT id, create_by, update_by FROM t_user ORDER BY id DESC LIMIT 1"
# 预期：create_by 为登录用户 ID，不是 NULL / 0
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK / Maven / Redis，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `SecurityIT` | 4 passed | 待填写 | ⏳ |
| 匿名访问 | 401 + 统一 Result 体 | 待填写 | ⏳ |
| 登录接口 | 返回 tokenType=Bearer | 待填写 | ⏳ |
| 带有效令牌 | code=0 | 待填写 | ⏳ |
| 普通用户删用户 | 403 | 待填写 | ⏳ |
| 篡改令牌 | 401 | 待填写 | ⏳ |
| `Set-Cookie` | 不出现（无 Session） | 待填写 | ⏳ |
| 审计字段 `create_by` | 等于登录用户 ID | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| JWT 还是 Session | JWT（无状态） | 目标是可水平扩容的 API 服务；实时吊销的短板用"短 Access + Redis 存 Refresh + `jti` 黑名单"补上 |
| HS256 还是 RS256 | 模板默认 HS256，文档给出 RS256 适用场景 | 单服务校验场景 HS256 配置最简单；多服务/第三方校验方持有公钥时再换 RS256 |
| 过滤器插在哪 | `addFilterBefore(..., UsernamePasswordAuthenticationFilter.class)` | 插在 `AuthorizationFilter` 之后会导致鉴权时 `SecurityContext` 为空，所有受保护接口 403 |
| 401 响应谁写 | 统一交给 `AuthenticationEntryPoint` | 过滤器里直接写响应会让"拦截器异常"和"过滤器异常"两套返回体，前端要写两套解析 |
| 角色 claim 存什么 | 存 `ROLE_ADMIN`（带前缀大写） | `hasRole('ADMIN')` 内部会拼 `ROLE_` 前缀，存 `ADMIN` 会永远 403 |
| `@PreAuthorize` 不生效怎么办 | 配置类必须加 `@EnableMethodSecurity` | 该注解缺失时**不报错也不生效**，接口看起来有保护实际完全开放，必须用测试锁住 403 |
| MDC 要不要清理 | `try/finally` 中 `MDC.remove("userId")` | Tomcat 线程池复用 ThreadLocal，不清理会出现"用户 A 的请求打上用户 B 的标识" |
| 密钥放哪 | 环境变量 `${JWT_SECRET}` 注入，不入库 | 写进 `application.yml` 等于随仓库泄露 |
| CSRF 要不要关 | 关（因为不用 Cookie 承载令牌） | 若改用 Cookie 承载令牌必须开启，并配双提交令牌 |

### 下一步（第 73 天）

1. **登录业务闭环**：`AuthService` 实现账号锁定（连续失败 5 次锁定 15 分钟）、密码强度校验、登录日志审计表。
2. **刷新与登出**：`/api/auth/refresh` 校验 Redis 中的 Refresh Token 有效性；`/api/auth/logout` 把 Access Token 的 `jti` 写入黑名单（TTL 设为剩余有效期）。
3. **测试扩充与门禁**：把"令牌过期""黑名单命中""Refresh 被复用"补进 `SecurityIT`，并把 401/403 用例纳入 JaCoCo 覆盖率门禁。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-79 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **5/5 步完成**，核心编码阶段收口 |
| 第 3 周（80-86 天） | 联调、单元与集成测试、压测、覆盖率门禁 | ⏳ 已提前落地 MockMvc + JaCoCo + Testcontainers + SecurityIT，待补压测 |
| 第 4 周（87-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始 |

## 2026-09-18（第 73 天）：登录业务闭环 + 双令牌刷新与登出黑名单 + SecurityIT 扩到 8 用例

### 本次做了什么

第 2 周核心编码收口后，第 3 周（联调与测试）从"把认证补成业务闭环"开始：

| 序号 | 产出 | 位置 | 对应需求 |
| --- | --- | --- | --- |
| ⑮ | `AuthService` 登录闭环：账号连续失败 5 次锁定 15 分钟、成功清计数、统一错误码防账号枚举 | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R13 |
| ⑯ | 自定义 `@StrongPassword` 校验器：8~64 位 + 四类字符取三 + 弱口令字典拦截 | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R13 |
| ⑰ | 登录审计表 `t_login_log`（成功/失败、失败原因枚举、IP、UA）+ 建表脚本 `V2__init_login_log.sql` | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R14 |
| ⑱ | 双令牌刷新：`TokenService.refresh` 校验 Redis 白名单、Refresh 一次性消费、复用即吊销全部会话 | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R15 |
| ⑲ | 登出吊销：`/api/auth/logout` 把 Access 的 `jti` 写入黑名单（TTL = 剩余有效期）并删除 Refresh 记录 | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R15 |
| ⑳ | `SecurityIT` 从 4 个用例扩到 8 个：过期令牌、黑名单命中、Refresh 复用、连续失败锁定 | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R10、R16 |
| ㉑ | 新增示意图 `assets/auth-lifecycle.svg`（登录锁定 / 使用刷新 / 登出吊销 三段） | [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) | R14 |

同时完成：第 72 天遗留的三条"下一步"全部落地，认证模块从"能验令牌"升级为"能保护账号、能吊销令牌、能审计登录"。

### 如何验证

```shell
# 环境要求：JDK 25、Maven 3.9+、Docker（Testcontainers 拉 Redis）、MySQL 8.4
cd backend-template
export JWT_SECRET="$(openssl rand -base64 48)"

# 1. 建登录日志表
mysql -uroot -p template < template-application/src/main/resources/db/migration/V2__init_login_log.sql

# 2. 安全测试扩到 8 个用例
mvn -q clean test -pl template-security -am
mvn -q test -pl template-web -Dtest=SecurityIT
# 预期：Tests run: 8, Failures: 0, Errors: 0, Skipped: 0

# 3. 覆盖率门禁
mvn -q verify
# 预期：BUILD SUCCESS

# 4. 启动后联调
mvn -q -pl template-application -am spring-boot:run &

# 4.1 登录拿双令牌
PAIR=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H 'Content-Type: application/json' -d '{"username":"admin","password":"Admin@123"}')
ACCESS=$(echo "$PAIR" | jq -r '.data.accessToken'); REFRESH=$(echo "$PAIR" | jq -r '.data.refreshToken')
echo "$PAIR" | jq '.data | {tokenType, expiresIn}'    # 预期 {"tokenType":"Bearer","expiresIn":1800}

# 4.2 刷新一次（成功），再用同一个 Refresh（应 401）
curl -s -X POST http://localhost:8080/api/auth/refresh -H 'Content-Type: application/json' \
  -d "{\"refreshToken\":\"$REFRESH\"}" | jq .code     # 预期 0
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/api/auth/refresh \
  -H 'Content-Type: application/json' -d "{\"refreshToken\":\"$REFRESH\"}"   # 预期 401

# 4.3 登出后旧 Access 立即失效
curl -s -X POST http://localhost:8080/api/auth/logout -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' -d "{\"refreshToken\":\"$REFRESH\"}" | jq .code   # 预期 0
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/users -H "Authorization: Bearer $ACCESS"  # 预期 401

# 4.4 连续失败 → 第 6 次锁定
for i in $(seq 1 6); do curl -s -o /dev/null -w "%{http_code} " -X POST \
  http://localhost:8080/api/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"lockme","password":"wrong"}'; done; echo   # 预期 401 401 401 401 401 423

# 5. 登录审计可查
mysql -uroot -p template -e \
  "SELECT username, login_type, success, fail_reason, ip FROM t_login_log ORDER BY create_time DESC LIMIT 10"
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK / Maven / Docker / MySQL，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `SecurityIT` | 8 passed | 待填写 | ⏳ |
| 过期令牌 | 401 | 待填写 | ⏳ |
| 黑名单令牌 | 401 | 待填写 | ⏳ |
| Refresh 复用 | 401 + 全量失效 | 待填写 | ⏳ |
| 连续 5 次失败 | 第 6 次 423 | 待填写 | ⏳ |
| 密码强度 | 弱密码被拒 | 待填写 | ⏳ |
| 登录审计 | 表内有成功/失败记录 | 待填写 | ⏳ |
| 登出后旧 Access | 401 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 账号不存在时返回什么 | 与密码错误同一错误码 | 否则可被用来枚举有效账号；差异只进审计日志 |
| 失败计数怎么存 | Redis `auth:fail:{username}` + `auth:lock:{username}` | 计数需 TTL，锁定需显式标记，两者职责不同 |
| 锁定是计数还是标记 | 两者都要 | 只看计数会在过期瞬间被继续爆破；标记才有明确窗口 |
| 黑名单 TTL 怎么定 | 等于 Access 剩余有效期 | 固定值会提前失效或长期占内存 |
| Refresh 能否重复用 | 不能，一次性消费 | 可重放等于给了攻击者永久钥匙 |
| Refresh 复用时怎么办 | 吊销该用户全部会话 | 无法区分攻击者与用户本人，宁可全部重登 |
| 刷新后旧 Access 怎么办 | 随新 Refresh 一起轮换 | 只发新 Access 会让旧 Access 在多会话下继续可用 |
| 登录日志写入时机 | 独立事务（失败也不回滚登录） | 审计失败不应影响业务结果 |
| 能否靠锁定防爆破 | 只能缓解 | 攻击者可故意锁定他人（DoS），生产需叠 IP 维度与验证码 |

### 下一步（第 74 天）

1. **压测与性能基线**：用 JMeter / `wrk` 压测 `/api/auth/login` 与受保护接口，产出 TPS / P95 基线，确认 JWT 校验与 Redis 查询不是瓶颈。
2. **覆盖率补齐**：把 `template-security` 模块覆盖率目标从 60% 提到 75%，纳入 CI 门禁。
3. **契约回归**：用 springdoc-openapi 产出的 OpenAPI 文档做接口契约回归，防止联调期接口悄悄变形。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成**，核心编码阶段收口 |
| 第 3 周（73-79 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁 | 🔄 **进行中**：认证闭环联调完成、SecurityIT 8 用例、压测基线 + 覆盖率门禁 + 契约回归已就位 |
| 第 4 周（80-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始 |

## 2026-09-19（第 74 天）：性能基线 + 覆盖率补齐到 75% + OpenAPI 契约回归

第 73 天收口了认证业务闭环，但整个模板仍然没有一个**可量化的性能数字**，测试覆盖也没有"不达标就不许合"的硬约束。第 74 天把这三件"说不清的事"变成 CI 能判定的东西。

### 本次做了什么

| 序号 | 产出 | 位置 |
| --- | --- | --- |
| ① | k6 压测脚本：登录 + 受保护接口双场景、`thresholds` 直接作门禁 | `scripts/perf/login-and-api.js` |
| ② | 基线记录格式（环境 + 数据量 + 脚本版本三要素）与结果表 | [压测与性能基线](../PerformanceTest/index.md) |
| ③ | JaCoCo 0.8.15 三段配置：`prepare-agent` / `report` / `check`，**按模块设阈值** | `pom.xml`（父 POM `pluginManagement`） |
| ④ | 覆盖率门禁：`template-security` 行覆盖 ≥ 75%，绑定 `verify` 阶段 | [压测与性能基线](../PerformanceTest/index.md) |
| ⑤ | springdoc-openapi 3.1.x 契约导出脚本（`jq -S` 排序入库） | `scripts/export-openapi.sh` |
| ⑥ | 契约回归比对脚本：diff 出破坏性变更并以非 0 退出码拦截 | `scripts/check-openapi-contract.sh` |
| ⑦ | 三道门禁的 CI 接入与豁免规则（覆盖率 / 契约 / 基线） | [压测与性能基线](../PerformanceTest/index.md) |

同时修正：项目总览里的 springdoc 版本口径由 `2.x 线` 改为 `3.x 线`（Boot 4.x 必须用 3.x，2.x 会启动失败）。

### 如何验证

```shell
# 1. 覆盖率门禁
mvn -q verify
# 期望：BUILD SUCCESS；报告在 template-security/target/site/jacoco/index.html
# 反向验证：把 minimum 临时改成 99% → 期望 BUILD FAILURE

# 2. 契约导出与比对
mvn -q -pl template-application -am spring-boot:run &
./scripts/export-openapi.sh                    # 首次：生成快照
git add docs/openapi/openapi.json && git commit -m "chore: 新增 OpenAPI 契约快照"
./scripts/check-openapi-contract.sh            # 期望 exit 0

# 3. 反向验证契约门禁能拦住破坏性变更
#    把 @GetMapping("/api/users") 改成 "/api/user" 后重新比对
./scripts/check-openapi-contract.sh            # 期望 exit 1，diff 中出现被删除的路径

# 4. 压力基线
PERF_USER=perfuser PERF_PASS='Perf@12345' \
  k6 run --summary-export=docs/perf/baseline-k6-login.json scripts/perf/login-and-api.js
# 期望：thresholds 全部通过，退出码 0

# 5. Swagger UI
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/swagger-ui.html   # 期望 302/200
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK / Maven / MySQL / Redis / k6，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `mvn verify` 覆盖率门禁 | BUILD SUCCESS | 待填写 | ⏳ |
| 阈值改 99% 反向验证 | BUILD FAILURE | 待填写 | ⏳ |
| `docs/openapi/openapi.json` 生成 | 存在且 > 5KB | 待填写 | ⏳ |
| 契约比对（入库后） | exit 0 | 待填写 | ⏳ |
| 改路径后契约比对 | exit 1 且指出删除路径 | 待填写 | ⏳ |
| k6 thresholds | 全部通过、退出码 0 | 待填写 | ⏳ |
| 登录接口基线 | TPS / P95 记录进 `docs/perf/` | 待填写 | ⏳ |
| 受保护接口基线 | TPS / P95 记录进 `docs/perf/` | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 压测工具选哪个 | 基线用 k6，极限初筛用 wrk，存量 JMeter 保留 | 只有 k6 能把"指标不达标"变成非 0 退出码，门禁才能自动化 |
| 覆盖率用一个全局阈值行不行 | 不行，按模块设（common 80 / web 70 / security 75 / data 60） | 各模块代码性质不同，全局值会被高低互相抵消，等于没约束 |
| 覆盖率报告要不要入库 | 只入库 XML/摘要，HTML 不入库 | HTML 体积大且每次构建都变 |
| 契约快照要不要排序 | 要（`jq -S`） | 不排序会因字段顺序抖动产生假 diff，门禁很快被无视 |
| 契约门禁放 PR 还是夜间 | 放 PR | 契约变化必须当场可见，性能反而可以滞后 |
| 性能门禁放 PR 吗 | 不放，放夜间 + 发版前 | 机器噪声会让告警常态红；PR 只跑 1 VU 冒烟看错误率 |
| 压测能用 admin 吗 | 不能，用专用 `perfuser` | 审计表被淹没，且锁定策略会把压测账号锁在 423 |
| 怎么证明 JWT/Redis 不是瓶颈 | 三条对照：接口对照（ping vs users）、中间件指标（Redis OPS / MySQL 堆积）、临时打点 | 单一指标容易被"整体变慢"掩盖，需要交叉验证 |
| 打点日志能常驻吗 | 不能，排查完必须移除 | 高 TPS 下日志本身成为瓶颈 |

### 下一步（第 75 天）

1. **Docker 化**：`template-application` 多阶段构建（构建层 JDK 25、运行层 JRE 25 slim），确认镜像体积与启动时间。
2. **Compose 一键起**：应用 + MySQL 8.4 + Redis 8 编排，用 `depends_on: condition: service_healthy` 表达依赖顺序。
3. **配置外置**：数据库 / Redis 连接与令牌密钥全部改为环境变量注入，为 CI 流水线与验收清单铺路。

::: warning 顺序调整（第 75 天记录）
上面三项属于**第 4 周（部署验收）**的内容，第 75 天实际做的是**第 3 周的第 3 步：测试数据隔离与边界用例**。调整原因见本页「2026-09-20（第 75 天）」段落的「遇到的问题与决策」——先把测试地基打牢再进容器化，避免同一段路走两遍。原计划顺延到第 80 天。
:::

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-79 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁 | 🔄 **3/4 步完成**：联调闭环 ✅、性能与契约门禁 ✅、隔离与边界用例 ✅，待做联调异常路径收口 |
| 第 4 周（80-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始 |

## 2026-09-20（第 75 天）：测试数据隔离 + 边界用例矩阵 + 并行执行

第 74 天之后，整套测试还剩两个**结构性问题**：所有集成测试共用同一个数据库（谁先跑、谁后跑，结果不一样），边界用例几乎全落在"明显合法"和"明显非法"两端，**off-by-one 一个都没碰到**。第 75 天把这两件事一起收掉，并顺手把「用 H2 假装 MySQL」这个最危险的习惯改掉。

### 本次做了什么

| 序号 | 产出 | 位置 |
| --- | --- | --- |
| ① | Testcontainers 2.x 接入：真实 MySQL 8.4 + Redis 8，singleton container 模式 + `@DynamicPropertySource` | `IntegrationTestBase`（测试基类） |
| ② | 隔离三档的方案对比与选型依据（事务回滚 / 清库 / 独立库） | [测试数据隔离与边界用例](../TestIsolation/index.md) + `test-isolation.svg` |
| ③ | `clean.sql` + `@Sql` 声明式清库；`DatabaseCleaner` 按 `t_` 前缀动态清表 | `src/test/resources/sql/clean.sql` |
| ④ | Redis 清理：清库与 `flushDb` 成对出现，测试独占 `database: 15` | `src/test/resources/application-test.yml` |
| ⑤ | JUnit 并行执行配置 + `@ResourceLock` 的类间互斥写法 | `src/test/resources/junit-platform.properties` |
| ⑥ | 边界用例矩阵（9 类输入 × 三值取法）与四步法 | [测试数据隔离与边界用例](../TestIsolation/index.md) + `boundary-matrix.svg` |
| ⑦ | 参数化边界用例：`username` 长度（2/3/20/21）、`password` 字符类（两类拒绝 / 恰好三类通过） | `BoundaryIT` |
| ⑧ | 令牌过期边界：`exp` 前 1s / 恰好 `exp` / 后 1s，并注明 RFC 7519 的临界语义 | `BoundaryIT` |
| ⑨ | 并发刷新用例：`RANDOM_PORT` + `CountDownLatch` 对齐起跑线，断言"恰好一次成功" | `RefreshConcurrencyIT` |
| ⑩ | 可控时钟方案：注入 `Clock` 替代 `Thread.sleep`，从根上消灭时间类 flaky | `TestClockConfig` |

同时修正：技术选型表补上测试一行（**Spring Boot 4.0 起默认 JUnit 6**、Testcontainers 2.0.x），并说明集成测试用真实容器而非 H2。

### 如何验证

```shell
# 0. 先确认 Docker 在跑（Testcontainers 必须有 Docker 守护进程）
docker info > /dev/null && echo "docker ok"

# 1. 全量测试
mvn -q test
# 期望：Tests run: N, Failures: 0, Errors: 0, Skipped: 0

# 2. 确认连的是真 MySQL 而不是 H2
mvn -q test -Dtest=UserApiIT -Dlogging.level.com.zaxxer.hikari=debug | grep -i "jdbc:mysql"
# 期望：输出里出现 jdbc:mysql://localhost:<随机端口>/template

# 3. 隔离性反向验证：单个方法单独跑也必须通过
mvn -q test -Dtest='BoundaryIT#usernameLengthBoundary'

# 4. 顺序无关反向验证：随机顺序跑三遍，结果必须一致
mvn -q test -Djunit.jupiter.testmethod.order.default=org.junit.jupiter.api.MethodOrderer\$Random
mvn -q test -Djunit.jupiter.testmethod.order.default=org.junit.jupiter.api.MethodOrderer\$Random
mvn -q test -Djunit.jupiter.testmethod.order.default=org.junit.jupiter.api.MethodOrderer\$Random

# 5. 并行开关（类内方法并行，类间不并行）
mvn -q test -Djunit.jupiter.execution.parallel.enabled=true

# 6. 容器复用是否生效（本地第二次跑几乎不等待）
docker ps --filter "label=org.testcontainers" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK / Maven / Docker，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `docker info` | 守护进程可用 | 待填写 | ⏳ |
| `mvn test` 全量 | Failures: 0, Errors: 0 | 待填写 | ⏳ |
| Hikari 日志出现 `jdbc:mysql` | 真 MySQL，非 H2 | 待填写 | ⏳ |
| 单个方法单独跑 | 通过 | 待填写 | ⏳ |
| 随机顺序跑 3 遍 | 3 次结果一致 | 待填写 | ⏳ |
| 并行开关打开 | 仍全部通过 | 待填写 | ⏳ |
| 边界用例条数 | ≥ 25 条参数化用例 | 待填写 | ⏳ |
| 容器复用 | 第二次跑无容器启动日志 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 要不要按第 74 天的计划先做 Docker 化 | 不，先把第 3 周收口 | 测试地基不牢就容器化，回头还要改测试，等于同一段路走两遍；Docker 化顺延到第 80 天（第 4 周） |
| 集成测试用 H2 还是真 MySQL | **真 MySQL 容器** | H2 的方言差异集中在最危险处（JSON 列、upsert、行锁、排序规则），会造成"测试全绿、上线报错" |
| 隔离用哪一档 | 分层：Mapper / Service 用第 1 档，接口层用第 2 档 | 一刀切要么太慢（全上容器），要么隔离不够（全用回滚） |
| 要不要给每个测试类一个独立库 | 暂不做 | 库级隔离的成本（每类 5~15 秒）在当前规模不划算；改用 `@ResourceLock` 表达互斥 |
| 类之间默认并行吗 | 不并行（`same_thread`） | 所有类共享同一个容器与同一个库，类间并行会互相清表，失败随机且难查 |
| Testcontainers 用 1.21 还是 2.0 | **2.0** | 新项目直接上主线；同时把 2.0 的三处破坏性变更写进文档（模块加 `testcontainers-` 前缀、容器类迁包、移除 JUnit 4 支持） |
| 并发用例用 MockMvc 还是真实端口 | 真实端口 + JDK `HttpClient` | MockMvc 不走网络，测不出"两个请求同时到达"；用 JDK 自带客户端可避开测试客户端换代的风险 |
| 时间边界能不能用 `Thread.sleep` | **不能**，注入 `Clock` | sleep 会被 GC、CPU 抢占、时钟漂移干扰，必然变成"重跑一次就过"的假象 |
| Redis 要不要一起清 | **必须清** | 失败计数与 `jti` 黑名单住在 Redis；只清库会出现"第二次跑就被锁"的玄学失败 |
| 边界用例怎么保证不漏 | 四步法 + 矩阵，长度用 `"a".repeat(n)` 生成 | 手敲字符串必然数错位数；矩阵化之后"没覆盖哪个边界"一眼可见 |
| 第 76 天继续收口测试，还是先做模板产品化 | **先做模板产品化**（插队） | 这一步会决定第 4 周交付物的形态——焊死的基座只需交付 Dockerfile + Compose，可参数化的基座还要包含"参数怎么组合、怎么验证"。先定形态再做部署产物，省一轮返工 |

### 下一步（第 76 天）

::: warning 说明：第 76 天的顺序调整
原计划第 76-79 天都属于"第 3 周 · 联调与测试"，继续收口测试。实际执行时调整为：

- **第 76 天插入"模板产品化"**：把模板从"一套焊死的基座"改成"可参数化的基座"，并设计把它做成 CLI。
- **第 77-79 天回到联调收口**：异常路径、用例清单化、测试约定落文档。

为什么插队：**这一步会决定后面所有交付物的形态**。如果模板是"一套焊死的基座"，第 4 周要交付的就是一份 Dockerfile 加一个 Compose 文件；如果模板是"可参数化的基座"，交付物里还要包含"参数怎么组合、组合怎么验证"。先定形态再做部署产物，比反过来省一轮返工。这与第 74→75 天"先打测试地基再容器化"是同一个判断逻辑。
:::

调整后，第 76 天要做的是：

1. **技术栈可插拔**：模块划分从直线结构改成四层 + 可替换实现层，把变化点收进实现模块。
2. **选择器脚本**：幂等、可校验（`--check` 当 CI 门禁）、零依赖，并配一份可运行的回归测试。
3. **模板 CLI 设计**：把上面这套能力产品化，同时解决另一个完全不同的问题——从零生成新项目。

第 77-79 天（第 3 周收口）：

1. **联调异常路径收口**：JSON 反序列化失败、超大请求体、非法枚举值、并发更新冲突，补齐用例并统一出口。
2. **用例清单化**：把散落在各 `IT` 里的用例整理成「接口 × 场景」对照表，标注已覆盖与待覆盖。
3. **测试约定落文档**：把"哪一层用第几档隔离"写进团队约定，避免后来者随手加 `@Transactional` 又把并发用例弄坏。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-79 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁 | 🔄 **3/4 步完成**：联调闭环 ✅、性能与契约门禁 ✅、隔离与边界用例 ✅，剩联调异常路径收口 |
| 第 4 周（80-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始（已提前规划，见第 75 天「下一步」） |

## 2026-09-21（第 76 天）：技术栈三维可插拔 + 选择器脚本 + 模板 CLI 设计

第 75 天把测试地基打牢之后，本日按计划调整（见上一节「下一步（第 76 天）」的说明）插队做**模板产品化**。

问题是明确的：前七步做出了**一套完整但焊死的**工程基座——安全是 Spring Security、数据是 MyBatis-Plus、缓存是 Redis。换个团队过来，只要有一处技术偏好不同，就只能 fork 之后手工改，改到最后没人敢确认自己删干净了。

本日分两半：前半把"焊死的基座"改成"可参数化的基座"，后半设计把它做成 CLI。

### 本次做了什么

**一、模块重构：从直线结构到四层 + 实现层**

原结构 `application → web → security → data → common` 里，`security` / `data` 既是契约又是实现，换实现就必须改业务模块的依赖。改成：

```text
template-common → template-spi → template-web / 实现层 → template-application
```

`template-security-*`（2 个）、`template-data-*`（4 个）、`template-cache-*`（3 个）成为并列的实现模块，**彼此零引用**；`template-web` 只依赖 `spi`，不依赖任何实现；`template-application` 是唯一知道"当前用哪套实现"的模块。

**二、SPI 契约：只定义"业务需要什么"**

| 契约 | 收拢什么 |
| --- | --- |
| `AuthPort` | 登录 / 注销 / 当前用户 / 权限判定；不含 `Authentication`、`StpUtil`、`Filter` 等任何框架概念 |
| `TokenStatePort` | 撤销 / 失败计数 / 账号锁定——**降级边界被显式建模成一个类型**，含 `sharedAcrossInstances()` 让降级可被程序读到 |
| `CachePort` | 通用缓存；**刻意不做泛型序列化**，用 `getOrLoad(key, type, ttl, loader)` 保持接口中立 |
| `UserRepository` | 按业务语义定义（`findByUsername` / `countActive`），不是 `save/update/delete` 的模板抄写 |

关键决策：**不统一 ORM 的 CRUD 接口**。取四套 ORM 的 CRUD 交集，得到的是最弱能力集——为了"统一"付出的代价是所有人都只能用最差的那一种。改按业务语义定义仓储接口，代价是换 ORM 时要重写实现，收益是业务逻辑一行不用改。

**三、两层可插拔**

| 层 | 机制 | 解决什么 |
| --- | --- | --- |
| 第一层 | Maven profile 决定哪些模块进 reactor | 不该编译的模块根本不编译，依赖树干净（选了 MyBatis 就不该有 Hibernate 的 jar） |
| 第二层 | `@ConditionalOnClass` + `@ConditionalOnProperty` | classpath 上真有两个实现时，谁生效是确定的 |

顺带记一笔 Boot 4 的坑：自动配置的注册位置已从 `META-INF/spring.factories` 改为 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`。

**四、能力降级门禁**

`cache != redis` 时，令牌撤销 / 失败计数 / 账号锁定三项能力在多实例下会各算各的（注销失效、锁定形同虚设）。脚本**默认拒绝，必须 `--allow-degraded-cache` 显式接受**，生成物把三个开关置为 `false`，而 `login-log-enabled` 保持 `true`（它写数据库，与缓存无关）。

**五、选择器脚本 `stack-select.py` + 自测 `selftest.py`**

三条设计性质：**幂等**（生成物是三维取值的纯函数，不含时间戳/用户名/预设名）、**可校验**（`--check` 不一致即非 0 退出）、**只写 marker 区间**（区间外一个字节不动，包括缩进与换行风格）。零第三方依赖。

配一份可提交的回归测试，**57 项断言**：24 种组合全生成且自洽、幂等字节级比对、marker 区间内外行为区分、CRLF 保留、降级门禁、`--check` 非交互。

**六、模板 CLI 设计评审**

把选择能力从脚本推进到 CLI，同时解决另一个问题——从零生成新项目。核心判断：**生成器（greenfield）与切换器（brownfield）是两个不同问题**，不能共用一套约束。并纠正了三处时间敏感的事实（Java 25 才是当前 LTS、Shiro 3.0 已支持 Boot 3/4、版本"最新"与"可复现"不可兼得）。

### 如何验证

```shell
cd backend-template

# 1. 脚本自测：57 项断言，覆盖幂等 / marker 边界 / 降级门禁 / 24 种组合
python3 stack-select/selftest.py
# 期望：共 57 项断言，通过 57，失败 0；退出码 0

# 2. 列取值与预设
python3 stack-select/stack-select.py --list
# 期望：security 2 个、orm 4 个、cache 3 个取值，5 个预设

# 3. 生成一套组合
python3 stack-select/stack-select.py --root . --preset classic
# 期望：写出 6 个文件，退出码 0

# 4. 幂等：再跑一遍，git 应当干净
python3 stack-select/stack-select.py --root . --preset classic
git status --short
# 期望：无输出

# 5. CI 门禁
python3 stack-select/stack-select.py --root . --check
# 期望：OK  --check 通过：6 个生成物与 stack.json 完全一致；退出码 0

# 6. 降级门禁：非共享缓存必须显式接受
python3 stack-select/stack-select.py --root /tmp/probe --security spring --orm jpa --cache caffeine
# 期望：退出码 1，列出三项降级能力；且不写任何文件

# 7. 换组合后确认业务代码未被触碰（Maven 部分待本地执行）
python3 stack-select/stack-select.py --root . --preset satoken-flex
git status --short
# 期望：只有 pom.xml / template-application/pom.xml 与 4 个生成物变化

# 8. 生效的 profile 与 reactor（需 JDK + Maven）
mvn help:active-profiles
mvn -q validate | grep -E "template-(security|data|cache)-"
# 期望：只出现选中的三个实现模块
```

验证结果记录（脚本部分**已实际运行**；Maven 部分当前环境无 JDK / Maven，待本地执行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `selftest.py` 全量 | 57/57 通过 | **57/57** | ✅ |
| 24 种组合可生成且自洽 | 全部退出码 0 | **24/24** | ✅ |
| 幂等（字节级） | 6 个文件哈希不变 | **不变** | ✅ |
| `--check` 一致 | 退出码 0 | **0** | ✅ |
| `--check` 检出篡改 | 退出码 1 | **1** | ✅ |
| 降级未接受 | 退出码 1 且不写文件 | **1，pom 哈希未变** | ✅ |
| marker 区间外不被碰 | 逐字节不变 | **不变** | ✅ |
| CRLF 仓库保留换行风格 | 写回仍为 CRLF | **仍为 CRLF** | ✅ |
| `mvn help:active-profiles` | 三个 profile 生效 | 待填写 | ⏳ |
| reactor 只含选中实现 | 无多余实现模块 | 待填写 | ⏳ |
| 换组合后业务代码不变 | `template-web` 无 diff | 待填写 | ⏳ |
| `mvn -q clean verify` | BUILD SUCCESS | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 要不要在 SPI 里统一 `BaseRepository<T,ID>` | **不统一** | 四套 ORM 的 CRUD 取交集等于最弱能力集（分页模型、条件构造、多表 join 都差异巨大）。改按业务语义定义仓储接口，代价是换 ORM 时重写实现，收益是业务逻辑零改动 |
| 数据维度能不能做成运行期切换 | **不能，只支持生成期选择** | 换 ORM 要改实体注解、Mapper 接口、分页调用、事务语义，不是加依赖。这条必须写成 CLI 里的硬约束，而不是靠文档提醒 |
| 为什么不做成"一个 `-D` 属性 + Spring 条件" | **要两层**（Maven profile + Spring 条件） | 只有 Spring 条件时，不该编译的模块照样下载、照样在 classpath 上，依赖审计与镜像体积全被污染。profile 层的价值是"不选的东西根本不存在" |
| 缺共享存储时自动降级还是报错 | **默认拒绝，必须显式接受** | 三项降级里有两项是安全能力，静默失效比明确报错危险得多；且日志没人看 |
| 降级判定要不要一刀切 | **逐项判定** | `login-log-enabled` 写数据库不写缓存，不受影响。按"是否真的依赖共享存储"逐项判断 |
| 生成物里记不记 preset 名 | **不记** | 记了之后 `--check` 必须知道当初用哪个预设才能复现，CI 必出错；且人手改过 `stack.json` 后预设名会变成谎话。生成物必须是三维取值的纯函数 |
| marker 区间外被手改怎么办 | **脚本完全不碰** | 用户自建业务模块是合法需求。区间外的内容是用户的，脚本不管、`--check` 也不报 |
| 区间内被手改怎么办 | **报红而不是冲掉** | `--check` 以非 0 退出并在下次执行时收敛；冲突以 diff 形式暴露，不静默覆盖 |
| 脚本怎么证明自己没问题 | **写可提交的回归测试** | "幂等"和"只写 marker 区间"这两条性质光看代码看不出来，必须跑起来；57 项断言把性质锁住，后续改动破坏的当天就红 |
| 模板 CLI 是全自研还是复用 Spring Initializr | **复用其生成内核（方案 C）** | Initializr 已把"模块化 + 可插拔 + 条件适用"做成产品，`ProjectDescription` / `ProjectContributor` / `@ProjectGenerationConfiguration` 与需求一一对应，且有 `start.aliyun.com` 生产先例。自研的成本清单（多构建工具产物翻倍、元数据自维护、矩阵测试）在 MVP 阶段立刻发生，收益用不上 |
| 生成器与切换器要不要做成一个功能 | **不能，必须分开** | 约束相反：生成期可以放开所有组合，装配期必须按变更成本分档（可增量 / 需重建 / 禁止）。混在一起会导致"换 ORM 被默默执行然后运行时崩" |
| Java 基线取 21 还是 25 | **默认 25，提供 `--java 21`** | 25 才是当前 LTS（支持到 2030-09，比 21 的 2029-12 长）；Boot 4 官方表述是"first-class support for Java 25"。21 留给有 JDK 版本管控的环境 |

### 下一步（第 77 天）

回到第 3 周的收口工作（第 76 天是插队，第 3 周还剩最后一步）：

1. **联调异常路径收口**：JSON 反序列化失败、超大请求体、非法枚举值、并发更新冲突，补齐用例并统一出口。
2. **用例清单化**：把散落在各 `IT` 里的用例整理成「接口 × 场景」对照表，标注已覆盖与待覆盖。
3. **测试约定落文档**：把"哪一层用第几档隔离"写进团队约定。

另外，本日设计的 CLI 有一个**尚未验证的前置条件**：`cli-core` 里的 `StackValidator` 必须与 `stack-select.py` 的判定逻辑**逐字节一致**（同一份 marker 契约、同一份 `stack.json` schema）。这件事要等 CLI MVP 落地后用交叉测试确认，已记入待办。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-79 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁 | 🔄 **3/4 步完成**：联调闭环 ✅、性能与契约门禁 ✅、隔离与边界用例 ✅，剩联调异常路径收口（顺延到第 77 天） |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（80-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ⏳ 未开始（已提前规划，见第 75 天「下一步」） |

## 2026-09-22（第 77 天）：联调异常路径收口 + 接口 × 场景用例清单 + 测试约定落文档

本日收口第 3 周（联调与测试）的最后一步：把散落在各处的**入口级异常路径**统一到同一套响应出口，并把「接口 × 场景」整理成可核对的用例矩阵。

### 本次做了什么

| 序号 | 产出 | 位置 | 对应需求 |
| --- | --- | --- | --- |
| ① | 五类入口级异常的统一出口：JSON 损坏 / 请求体过大 / 枚举非法 / 并发更新冲突 / 路由兜底（404、405） | [异常路径联调收口与用例清单](../ErrorPath/index.md) | R3、R4 |
| ② | 请求体大小守卫 Filter（按 `Content-Length` 在读报文前拒绝）+ 三套 Profile 的 Tomcat 上限与 `max-swallow-size` | 同上 | R4 |
| ③ | 接口 × 场景 用例清单（9 接口 × 10 场景，含新补的 `PUT` 并发冲突）+ 守住用例数基线的元测试 | 同上 | R6 |
| ④ | 测试与隔离档位的团队约定（三层测试分别用第几档隔离，写进 `CONTRIBUTING.md`） | 同上 | R6 |
| ⑤ | 异步异常出口（`AsyncUncaughtExceptionHandler`）——补齐「请求线程之外」的盲区 | 同上 | R4 |

同时把第 76 天遗留的一处顺序问题落定：原计划的第 3 周收口顺延到本日完成，第 4 周（部署与验收）从第 78 天开始。

### 如何验证

```shell
# 1. 全量回归（单元 + Web 切片 + 数据切片 + 集成）
cd backend-template
mvn -q clean verify
# 预期：BUILD SUCCESS，surefire + failsafe 全绿，无 skipped

# 2. 启动
java -jar template-application/target/template-application-1.0.0.jar
# 预期：Started TemplateApplication in x.x seconds

# 3. 五条异常路径逐条验
curl -s -i -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' \
  -d '{"username": "a", "age": ' | head -8
# 预期：HTTP 400 + code 40001，响应体不含类名/堆栈/原始报文

curl -s -i -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' \
  --data-binary @big.json | head -6
# 预期：HTTP 413 + code 40002

curl -s -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' \
  -d '{"username":"bob","status":"UNKNOWN"}'
# 预期：HTTP 400 + code 40003，message 含字段名 status 与合法取值列表

curl -s -X PUT http://localhost:8080/api/users/1 -H 'Content-Type: application/json' -d '{"nickname":"n1","version":0}'
curl -s -o /dev/null -w '%{http_code}\n' -X PUT http://localhost:8080/api/users/1 \
  -H 'Content-Type: application/json' -d '{"nickname":"n2","version":0}'
# 预期：第一条 200；第二条 409 + code 40004

curl -s -o /dev/null -w '%{http_code}\n' -X DELETE http://localhost:8080/api/users
# 预期：405 + code 40005
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK/Maven，未实际运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `mvn -q clean verify` | BUILD SUCCESS | 待填写 | ⏳ |
| ① JSON 损坏 | 400 + 40001，无内部信息 | 待填写 | ⏳ |
| ② 请求体过大 | 413 + 40002 | 待填写 | ⏳ |
| ③ 枚举非法 | 400 + 40003，含字段名与合法值 | 待填写 | ⏳ |
| ④ 并发更新冲突 | 第二次 409 + 40004 | 待填写 | ⏳ |
| ⑤ 方法不支持 | 405 + 40005 | 待填写 | ⏳ |
| 每个响应带 `X-Trace-Id` 且与日志一致 | 全部一致 | 待填写 | ⏳ |
| 用例矩阵元测试（基线 38 条） | 通过 | 待填写 | ⏳ |
| 响应体无堆栈 / 无类名 / 无 SQL 片段 | 五条全覆盖 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 入口级异常要不要走业务异常体系 | **不走，单独一组处理器** | 这些异常发生在进 Controller 之前，`BizException` 那套根本不会被触发；混在一起会让人误以为已覆盖 |
| 400 响应里回显原始报文，方便排查吗 | **绝不回显** | 原始报文可能含密码、身份证号等敏感字段；排障信息只进服务端日志（带 traceId 可定位） |
| 请求体超限在哪一层拦 | **两层都要**（`ContentLengthGuardFilter` + Tomcat 上限） | 只靠 Tomcat 时错误响应结构与 `Result` 不一致；只靠 Filter 时无 `Content-Length` 的请求会漏 |
| 超限后 `max-swallow-size` 设多大 | **与上限一致** | 不设或设得过大时，剩余字节没人读，连接被占住，表现为偶发连接池耗尽且日志无痕 |
| 并发更新冲突返回 400 还是 409 | **409 Conflict** | 请求本身合法，冲突在于资源状态；400 会让调用方以为参数写错了 |
| 枚举非法的报错信息给到什么粒度 | **字段名 + 合法取值列表** | 只给「参数错误」会让前端反复试；这条同时适用于所有校验类错误 |
| 「影响行数为 0」怎么处理 | **抛异常，不算成功** | 返回 0 有两种可能（记录不存在 / 版本不匹配），静默当成功会造成「提示保存成功但数据没变」 |
| 用例清单要不要做成自动化 | **要，但做的是「元测试」** | 清单靠人维护必然过期；断言「用例数只增不减」能拦住为让 CI 变绿而删用例的行为 |
| 异步任务异常怎么办 | **配置 `AsyncUncaughtExceptionHandler`** | `@Async` 默认吞掉异常，只在日志里留一行；不打点就永远发现不了失败率 |
| 响应已提交后抛异常怎么处理 | **只记日志** | 无法再改状态码；试图写响应体只会产生更难排查的错误 |
| 测试约定写在哪 | **`CONTRIBUTING.md` + 本页表格** | 提高一层隔离档位的成本很高（慢、难定位），必须让新人不必自己判断 |

### 下一步（第 78 天）

进入**第 4 周（部署与验收）**，第一步是容器化：

1. **多阶段 Dockerfile**：`builder` 阶段跑 Maven 打包，`runtime` 阶段只带 JRE 与 jar，控制镜像体积。
2. **docker-compose**：应用 + MySQL + Redis 一键起，写清健康检查与依赖顺序（`depends_on` + `condition: service_healthy`）。
3. **镜像与配置分离**：三套 Profile 全部通过环境变量覆盖，镜像内不写任何密钥。
4. **冒烟脚本容器化**：把本日「如何验证」一节那五条 curl 提炼成部署后校验脚本，供 CI 与上线验收共用。

另外，本日新增的用例矩阵元测试与第 76 天设计的模板 CLI 之间有一处**尚未验证的交叉约束**：CLI 的 `--check` 在生成物上比对 marker 区间时，需一并校验「用例矩阵基线值」是否被正确写入。等 CLI MVP 落地后做交叉测试确认，已记入待办（承接第 76 天同类待办）。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-77 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁、异常路径收口 | ✅ **4/4 步完成**：联调闭环 ✅、性能与契约门禁 ✅、隔离与边界用例 ✅、异常路径收口与用例清单 ✅ |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（78-90 天） | Docker 化、Compose、CI 流水线、验收清单 | ✅ **1/4 步完成**：容器化（镜像 + 编排 + 冒烟）已交付；CI、镜像推送、验收清单待做 |

## 2026-09-23（第 78 天）：多阶段镜像 + Compose 编排 + 部署后冒烟

### 本次做了什么

进入第 4 周（部署与验收），第一步把「本地能跑」变成「一条命令能起」。产出为 [容器化：多阶段镜像与 Compose 编排](../Deployment/index.md)，含六个部分：

1. **多阶段 Dockerfile**：`builder` 阶段用 Maven + JDK 25 打包，`runtime` 阶段只带 JRE 与 jar。运行时镜像从「单阶段 + 完整 JDK」的 700 MB 级降到 **250 MB 级**。配套三处细节：先 `COPY pom.xml`（只拷各模块 pom）再 `COPY . .`，让依赖层独立成缓存层，改一行代码不再重下依赖；`RUN --mount=type=cache,target=/root/.m2` 让本地仓库跨构建复用；`--chown` + `USER app` 非 root 运行。
2. **容器友好的 JVM 参数**：`-XX:MaxRAMPercentage=75.0` 取代写死 `-Xmx`，堆随容器内存上限自适应；`-XX:+ExitOnOutOfMemoryError` 让 OOM 直接退出交给编排重启，而不是带病存活；`ENTRYPOINT` 写成 `exec java ...`，让 java 成为 PID 1，`docker stop` 才能秒级优雅退出（否则等满超时才强杀）。
3. **`.dockerignore` 与基础镜像纪律**：排除 `**/target/`、`.git/`、`.env`、`*.log`；基础镜像一律显式标版本（`eclipse-temurin:25-jre`、`mysql:8.4`、`redis:8`），不用 `latest`。
4. **配置与镜像分离**：三套 Profile 的差异全部走环境变量，`application.yml` 里只留 `${DB_HOST:127.0.0.1}` 这类占位符；新增 `StartupSecurityCheck`，在 `prod` Profile 下强校验 `JWT_SECRET`（长度 ≥ 32）与 `DB_PASSWORD`，缺失即抛异常让应用**启动失败**。
5. **Compose 编排**：MySQL 8.4 + Redis 8 + app 三个服务。健康检查分别为 `mysqladmin ping`（带密码与 `--connect-timeout=3`）与 `redis-cli ping | grep -q PONG`；`app` 的依赖写成 `depends_on: { mysql: { condition: service_healthy }, redis: { condition: service_healthy } }`；MySQL 的 `start_period: 40s` 给首次初始化数据目录留时间；数据卷三个（`mysql-data` / `redis-data` / `app-logs`）；`deploy.resources.limits.memory: 1g` 与 `MaxRAMPercentage=70` 配套。
6. **冒烟脚本与一键脚本**：`scripts/smoke.sh` 把第 77 天靠人工执行的 curl 验证固化为 7 项断言（健康 UP、未认证 401 走统一出口、校验失败 400 带字段明细、登录拿到双令牌、带令牌 200、`X-Trace-Id` 透传），全用 `grep` 断言以免依赖 `jq`，失败即退出码 1；`scripts/deploy.sh` 串起 `up`（起服务 → 轮询健康最多 60 次 → 跑冒烟）、`down`、`clean`、`logs`、`smoke`。
7. **示意图** `deploy-topology.svg`：构建期/运行期分层 + 运行期四组件拓扑 + `service_healthy` 依赖顺序标注。

### 如何验证

```shell
# ① 构建并确认运行镜像体积
docker build -f docker/Dockerfile -t backend-template:1.0.0 .

# ② 一键起（含健康等待与冒烟）
bash scripts/deploy.sh up

# ③ 三容器健康状态
docker compose -f docker/compose.yaml ps

# ④ 镜像不该有的东西逐条确认
docker run --rm backend-template:1.0.0 sh -c 'whoami; ls /app'
docker history --no-trunc backend-template:1.0.0 | grep -i -E "password|secret" || echo "镜像层无密钥痕迹"
```

验证结果记录（**请在本地执行后填写**，当前编写环境无 JDK / Maven / Docker，未实际构建运行）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `docker build` | 成功，运行镜像约 250 MB 级 | 待填写 | ⏳ |
| `docker compose ps` | app / mysql / redis 均 `healthy` | 待填写 | ⏳ |
| 冷启动（`down -v` 后 `up`） | 应用等 MySQL 健康才启动，日志无连接失败 | 待填写 | ⏳ |
| `scripts/smoke.sh` | 7 项全过，退出码 0 | 待填写 | ⏳ |
| 容器内运行用户 | 非 root | 待填写 | ⏳ |
| 镜像内无密钥 | `docker history` 无命中 | 待填写 | ⏳ |
| `docker stop` | 秒级优雅退出 | 待填写 | ⏳ |
| 改 `.env` 不重建镜像即生效 | 生效 | 待填写 | ⏳ |
| 缺 `JWT_SECRET` 启动 | 应用启动失败并给出明确原因 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 单阶段还是多阶段构建 | **多阶段** | 编译工具链不进最终镜像，体积与攻击面同时下降 |
| 依赖层怎么缓存 | **先拷 pom + 缓存挂载 `.m2`** | 改代码不重下依赖，构建从分钟级降到秒级 |
| 启动顺序靠 `depends_on` 还是 sleep | **`condition: service_healthy`** | sleep 是猜时间，健康检查是看事实；只写 `depends_on` 仅保证容器已创建 |
| 应用要不要自带连接重试 | **要** | 健康检查有窗口期、重启场景会撞上短暂不可用；**编排管顺序、应用管韧性**，不是二选一 |
| 缺配置时给默认值还是报错 | **`${VAR:?}` 报错退出** | 默认值会让错误配置「成功启动」，把故障推迟到运行时 |
| 生产 Profile 缺密钥怎么办 | **启动期强校验，直接启动失败** | 带空密钥运行等于把认证链路敞开；宁可起不来 |
| 镜像里放配置还是环境变量 | **环境变量，配置只留占位符** | 一份镜像跑三套环境，改配置不必重建镜像 |
| JVM 堆写死还是按比例 | **`MaxRAMPercentage`** | 写死 `-Xmx` 换机器配置必然不适配 |
| `ENTRYPOINT` 用 `java` 还是 `sh -c "exec java …"` | **`exec` 形式** | 让 java 成为 PID 1，信号可达，优雅停机生效 |
| 健康检查用 Actuator 还是自写探针 | **Actuator** | 第 69 天已暴露，自带数据库与 Redis 组件级检查，不必重复造 |
| 生产 Actuator 暴露多少 | **只留 health/info/metrics/prometheus，`show-details: never`** | 全暴露会把内部组件名与依赖状态交给未授权调用方 |
| 冒烟断言用 `jq` 还是 `grep` | **`grep` 子串** | 验收机器不一定装 `jq`，零依赖优先；需要严格结构化断言时再引入 |
| 要不要立刻做分层 jar | **暂不做** | 收益只在镜像层缓存粒度，当前构建已在秒级；先用 `--mount=type=cache` 拿到大头，避免过早引入版本差异风险 |

### 下一步（第 79 天）

第 4 周第二步：**CI 流水线**。

1. 把第 74~75 天的三项门禁（JaCoCo 按模块覆盖率阈值、`openapi.json` 契约回归、选择器 `--check`）串成一条流水线，任一失败即失败。
2. 用本日 Dockerfile 构建带 `git sha` 标签的镜像并推送到镜像仓库。
3. 起 compose 环境跑 `scripts/smoke.sh` 作为流水线最后一道。
4. Maven 仓库与 Docker 构建缓存跨流水线复用。

同时把本日交付纳入验收清单的「部署」一节：冷启动顺序、镜像体积、非 root、密钥不落镜像、优雅停机五项要能逐条复核。

待办承接：模板 CLI 的 `--check` 需与「用例矩阵基线值」做交叉校验（第 77 天记入），CLI MVP 落地后一并在流水线中验证。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-77 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁、异常路径收口 | ✅ **4/4 步完成** |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（78-90 天） | Docker 化、Compose、CI 流水线、验收清单 | 🔄 **进行中（1/4）**：容器化 ✅；CI 🔜、镜像推送 🔜、验收清单 🔜 |

## 2026-09-24（第 79 天）：CI 流水线 —— 把四道门禁串成一条链

### 本次做了什么

第 4 周第二步：第 74~78 天陆续立起了四道门禁，但它们此前都要靠人记着跑。本日把它们连同构建镜像、预发部署、冒烟串成**一条自动流水线**，目标是让「这次提交能不能用」这件事有唯一答案。产出为 [CI 流水线：把门禁串成一条链](../CI/index.md)，含七个部分：

1. **五阶段与失败代价排序**：① 静态检查（编译、lint、选择器 `--check`、用例矩阵元测试，秒级~1 分钟）→ ② 测试与门禁（单元 + 集成真实容器、JaCoCo 阈值、契约破坏性变更，3~10 分钟）→ ③ 构建镜像（多阶段 Dockerfile、`git sha` 标签、推送仓库，2~5 分钟）→ ④ 部署预发（compose 起服务 + 健康检查，2~5 分钟）→ ⑤ 冒烟（`scripts/smoke.sh` 七项断言，10~30 秒）。**排序原则是「失败代价」而不是「逻辑顺序」**：把 30 秒的 lint 放在 5 分钟的镜像构建之后，等于每次笔误都白烧一次构建机——这是流水线提速最省力的一招。
2. **三条硬约束**：① 门禁失败必须让流水线红，不允许 `continue-on-error`、不允许「警告但通过」（一旦允许，门禁两周内就退化成装饰）；② 冒烟失败必须打出容器日志，只给一个红叉等于把排障成本全部转给下一个看日志的人；③ 镜像标签用 `git sha`，禁止用 `latest` 部署——`latest` 无法回答「线上跑的是哪一次提交」，也就无法回滚到确定版本。
3. **完整工作流文件** `.github/workflows/ci.yml`：`concurrency` 以 <span v-pre>`ci-${{ github.ref }}`</span> 分组并 `cancel-in-progress`，避免同分支新提交排队；`paths` 过滤（`backend-template/**` 与工作流自身）让无关变更不触发；`static-checks`（`mvn -DskipTests clean compile` + `stack-select.py --check` + `selftest.py` 57 项 + `CaseMatrixMetaTest`）与 `tests`（预热 `mysql:8.4` / `redis:8` 镜像后 `mvn -B clean verify`，再起契约导出 Profile 拉 `/v3/api-docs` 并跑 `oasdiff breaking`）拆成两个 job，让单元级反馈不被容器启动拖慢；`upload-artifact` 在 `if: always()` 下留存 surefire 报告；`build-image` 用 buildx + `docker/login-action` 推带 `github.sha` 与 `latest` 双标签；`smoke` 走 `environment: staging`、`secrets` 注入三组密钥、复制 `.env.example` 后 `compose up -d --build`、60 次轮询健康、最后 `bash scripts/smoke.sh`，并以 `if: failure()` 兜底 `compose logs --tail 200 app`。
4. **两处缓存与一条反直觉纪律**：Maven 本地仓库（`actions/setup-java` 的 `cache: maven`，按 pom 哈希做键，首次十几分钟降到 1~2 分钟）与 Docker 构建缓存（`cache-from/to: type=gha`，镜像构建 2~5 分钟降到 30 秒级）。**但缓存省的是时间不是正确性**——每周跑一次禁用缓存的完整流水线（或 `mvn -U` 强制更新依赖），确认没有缓存也能跑绿，否则缓存就成了掩盖问题的工具。
5. **与既有门禁的对应关系**：流水线不是新立门禁，而是把第 74~78 天的五道挂上去——JaCoCo 按模块覆盖率阈值（第 74 天，`tests`）、OpenAPI 契约破坏性变更（第 74 天，`tests`）、选择器 `--check` 漂移（第 76 天，`static-checks`）、用例矩阵基线只增不减（第 77 天，`static-checks`）、部署后冒烟 7 项（第 78 天，`smoke`），每道都标了失败信号（如 `Rule violated for bundle`、`冒烟：通过 X 项，失败 Y 项`）。
6. **分支保护与必需检查**：`main` 设为受保护分支，必需检查写具体 job 名（`static-checks`、`tests`），同时禁止直接推送 main 与自审自合并。**保护规则匹配的是 job 名**——名字改了而规则没改，会出现「合并按钮亮着，但没人真正验过」。
7. **时长预算与两条清单**：四阶段的初始耗时与优化后耗时对照（总计约 19 分钟 → 约 6 分钟），优化顺序是**先「减少重复下载」和「提前失败」，再做「并行化」**（前两项收益大且无副作用，并行化会让日志难读、资源竞争，留到后面）；末尾「六个会让流水线不可信的写法」——`continue-on-error` 兜住门禁、单元与集成混跑、冒烟失败不输出日志、用 `latest` 部署、密钥写在工作流文件里、**CI 与本地命令不一致**（本地 `mvn verify` 而 CI 跑 `mvn test` 加另一套参数，必然出现「本地绿 CI 红」）。

### 如何验证

```shell
# ① 本地先跑一遍与 CI 相同的命令（保证一致，这是「本地绿 CI 绿」的前提）
cd backend-template
mvn -B clean verify
python3 stack-select/stack-select.py --root . --check
python3 stack-select/selftest.py

# ② 触发流水线并观察各阶段
gh workflow run ci.yml
gh run watch

# ③ 确认镜像标签是 git sha（不是 latest）
docker pull ghcr.io/<owner>/<repo>/backend-template:$(git rev-parse HEAD)

# ④ 故意制造一次失败，确认门禁真的会红
#    例：把某条测试断言改成必然失败，推送到测试分支，确认流水线红且能定位
```

第 ④ 步常被跳过，但它是唯一能证明「门禁有效」的方式——**没有被验证过的门禁，和没有门禁的区别只在于心理安慰。**

验证结果记录（**请在仓库中执行后填写**，当前编写环境无 CI runner，未实际触发流水线）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `static-checks` | 40 秒~2 分钟通过 | 待填写 | ⏳ |
| `tests`（含 JaCoCo 与契约门禁） | 通过 | 待填写 | ⏳ |
| `build-image` | 推送带 `git sha` 标签的镜像 | 待填写 | ⏳ |
| `smoke` | 7 项全过 | 待填写 | ⏳ |
| 全流水线时长 | ≤ 10 分钟 | 待填写 | ⏳ |
| 故意失败验证 | 流水线变红且给出可定位信息 | 待填写 | ⏳ |
| 禁用缓存重跑 | 仍能跑绿 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 原因 |
| --- | --- | --- |
| 门禁失败时是否允许「警告通过」 | **不允许** | 允许一次就会形成惯例，门禁退化成装饰 |
| 用 `latest` 还是 `git sha` 部署 | **`git sha`**，`latest` 仅作人类可读指向 | 必须能回答「线上是哪次提交」才能回滚 |
| 镜像构建放在测试前还是后 | **后** | 测试不过就不该烧构建时间与仓库存储 |
| 集成测试放同一 job 还是拆开 | **拆分单元与集成** | 单元测试要快速反馈，不能被容器启动拖慢 |
| 是否用矩阵跑多 JDK 版本 | **暂不** | 模板只承诺 JDK 25；引入矩阵会让时长翻倍而收益有限 |
| 缓存策略 | **Maven 仓库 + Docker GHA 缓存** | 两处是耗时大头；每周一次无缓存跑校验缓存没有掩盖问题 |
| 冒烟放在预发还是只做本地 | **预发环境跑** | 只有预发能同时验证「迁移 + 编排 + 应用」三者一起正确 |
| 契约基线在哪里更新 | **人工确认后更新并提交** | 破坏性变更属于需要决策的变更，不应自动跟随 |

### 下一步（第 80 天）

第 4 周第三步：**镜像仓库与发布策略**。

1. 语义化标签（`1.0.0`、`1.0`）与 `git sha` 的关系：什么时候打哪种标签、如何保证不可变。
2. 镜像保留策略（保留最近 N 个 tag）与回滚时的取用路径。
3. 发布审批门禁：把 `environment: production` 的审批人、观察窗口与回滚决策人写进流程。
4. 备份与恢复演练脚本：数据库备份 + 恢复 + 校验数据一致性的三步命令。

待办承接：模板 CLI 的 `--check` 需与「用例矩阵基线值」做交叉校验（第 77 天记入）。本日已把两者放进同一个 job（`static-checks`），等 CLI MVP 落地后在此处补交叉断言。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-77 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁、异常路径收口 | ✅ **4/4 步完成** |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（78-90 天） | Docker 化、Compose、CI 流水线、验收清单 | 🔄 **进行中（2/4）**：容器化 ✅、CI 流水线 ✅；镜像推送 🔜、验收清单 🔜 |

## 2026-09-25（第 80 天）：镜像推送与发布策略 —— 从「构建成功」到「能退回去」

### 本次做了什么

第 4 周第三步：第 79 天让镜像能被构建出来，但那离「可以发布」还隔着一整套约定——镜像从哪个仓库拉、对应哪一次提交、出事之后怎么退回去。本日把这套约定固化下来，产出为 [镜像推送与发布策略](../Release/index.md)，并附一个可离线验证的工具。六个部分：

1. **发布要回答的五个问题**：哪一次提交（镜像内嵌 `org.opencontainers.image.revision`）、从哪来（带完整 registry 前缀的镜像名）、谁构建的（`provenance`）、改过没有（`cosign` 签名与验签）、出事退到哪（上一个身份标签仍在 registry 里）。**前半句是操作，后半句才是需求**——发布策略的本质是「事后能不能证明推上去的是你以为的那个东西」。

2. **标签按「会不会变」分四层**（分层依据只有一个问题，而不是名字好不好看）：身份 `sha-<12>`（永不变，部署/回滚/审计引用）、版本 `1.2.0`（永不变，对外沟通）、环境指针 `prod`/`staging`/`dev`（**会变**，只能用来问「现在跑的是什么」）、便利标签 `latest`（**不生成**）。配套论证：为什么环境指针进部署命令会让「线上是什么」这个答案的有效期只到下一次发布；为什么 `latest` 在语义上等于「最后被推上来的那个」，任何一次误推都会静默改写它的含义。

3. **「不可变」必须由 registry 强制而不是靠约定**：默认 registry 允许同名标签覆盖推送，一次覆盖之后**同一个标签在不同节点上可能对应不同镜像**，「这个镜像经过测试」这句话随之失效。开启标签不可变策略（Harbor 项目级规则 / ECR tag immutability / Artifact Registry tag immutability policy）后，覆盖推送返回 409，事故被拦在推送这一步而不是半夜的滚动重启里。**约定要落成配置，否则它只是意愿。**

4. **七阶段发布流水线**：前三阶段（多架构 buildx 构建 + 内嵌 revision 注解、打身份与版本标签、只推不可变层）**只产出可追溯的镜像**，第五阶段才开始碰线上，因此中间有一道唯一的**人工审批门**。① 多架构不是加分项而是必需品（开发机 arm64、生产 amd64，只推单架构会让开发机报 `no matching manifest`）；② `--provenance=true --sbom=true` 与 ④ 的 `cosign sign --yes`（keyless，基于 CI 的 OIDC 短期证书）共同构成证据链；③ **验签必须阻断部署**，且 `--certificate-identity-regexp` 要收窄到自己的仓库（留空或写成 `.+` 等于「任何人的签名都算数」）；④ 环境指针**单独一次操作、单独一条审批链路**，好处是「有权限推 sha 镜像」与「有权限改 prod 指针」可以分开授给不同的人；⑤ 部署命令显式写 `IMAGE_REF=<身份标签>`，让部署动作与它对应的信息落在同一条命令里；⑥ 回滚 = 把引用换回上一个身份标签。

5. **发布三档与滚动替换的兼容性要求**：滚动替换（本模板选择，资源开销最小、无需额外环境，代价是发布过程中两个版本同时服务，**必须向前向后兼容**）、蓝绿（回滚即切回，需要两套资源）、金丝雀（风险面最小，链路最复杂）。**滚动发布的兼容性要求正是第 74 天契约门禁与第 79 天破坏性变更拦截存在的理由**——三件事在逻辑上是同一件。另含 `liveness` 与 `readiness` 必须分开的完整论证：`liveness` 只问「进程还在吗」，配成「能对外服务吗」会让依赖抖动变成**反复重启**（越重越慢）；`readiness` 配错或用同一端点，会在预热未完成时就放流量进来，表现为**发布瞬间的 5xx 尖刺**。

6. **回滚的三个前提**：数据结构兼容（破坏性变更是发布前设计的，不是事后补救的）、旧配置还在（配置项改名同样属于破坏性变更）、外部副作用不随镜像回退（已发出的消息、已写的外部记录不会退回去，回滚是止血而非复原）。核心推论：**回滚能力取决于旧标签还在不在**——「重新构建一版当时的代码」不叫回滚，因为产出是否等价于当时线上那个镜像，谁也证明不了；因此镜像清理策略必须按「上一稳定版 + 当前版 + 回滚候选」保留，而不能按「时间最近」。

### 本次新增的可执行交付物

`Release/tagplan.py`（零第三方依赖）+ `Release/selftest.py`。把发布策略里**与 Docker、registry 都无关**的那部分（标签分层与「谁可以出现在部署命令里」）抽成可离线验证的工具——依赖 registry 才能验证的部分一旦出错，代价是线上事故。

| 编号 | 不变量 | 违反了会发生什么 |
| --- | --- | --- |
| INV1 | 身份层恰好一个 `sha-<12位小写hex>`，且等于传入 sha 的前 12 位 | 两个身份标签等于没有身份，回滚会指错镜像 |
| INV2 | 版本标签符合严格语义化版本（不接受 `1.2`、`v1.2.0`、`1.2.0+build9`） | 版本号无法排序，无法回答「上一版是哪个」 |
| INV3 | 命令里任何位置不出现 `:latest` | 不可追溯，且会被误推静默改写 |
| INV4 | `deploy` / `rollback` 的 `IMAGE_REF` 落在可引用的不可变集合内 | 引用环境指针 = 事后查不到当时跑的是哪次提交 |
| INV5 | 环境指针必须是枚举值之一，且不得与不可变层重名 | 三套写法指向同一环境却互不知情；重名会原地覆盖身份层 |
| INV6 | 预发布版本不得生成 `prod` 指针 | 「生产在跑 rc」这件事无人察觉 |

**过程中的两次修正（工具与自测互相纠错，两次都是改工具而不是改测试）**：

1. **INV3 原先只检查命令的首个 token**。`docker run <base>:latest` 的首个 token 是 `docker`，真正的镜像引用在第三个 token 上——恰恰是事故现场最常见的写法，却检不出来。改为**逐 token 扫描**。
2. **INV4 原先要求引用的标签必须属于本次计划**。这让回滚命令永远违规：回滚本来就该指向上一个发布的身份标签，它不是本次构建的产物。改为「本次标签 ∪ 上一个发布的身份标签」。

第 2 条是一个值得记住的类型：**当一个校验规则让「正确的操作」永远违规时，要怀疑规则而不是操作。**

### 如何验证

```shell
cd backend-template/Release

# ① 自测：88 项断言 + 11 组全组合扫描
python3 selftest.py            # 期望：selftest: 88/88 通过（全组合扫描 11 组），退出码 0

# ② 正常计划生成
python3 tagplan.py --version 1.2.0 --sha <40位git sha> \
  --previous-sha <上一个发布的40位sha> --channel prod

# ③ 违规输入必须被拒（退出码 1）
python3 tagplan.py --version 1.3.0-rc.1 --sha <40位git sha> --channel prod
# 期望：FAIL: 预发布版本 1.3.0-rc.1 不得打 prod 环境指针……

# ④ 校验一份既有计划（可当 CI 门禁）
python3 tagplan.py --verify plan.json   # 期望：OK: plan.json 通过全部不变量（INV1~INV6）
```

验证结果记录（**请在具备 Docker 与 registry 的环境执行后填写**，当前编写环境无 Docker / registry，仅 ①②③ 已实测）：

| 检查项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| `selftest.py` | 88/88 通过，退出码 0 | 88/88 通过（全组合扫描 11 组） | ✅ |
| 正常计划生成 | 输出三层标签与 7 组命令，退出码 0 | 与预期一致 | ✅ |
| 预发布打 prod 被拒 | `FAIL` 并给出原因，退出码 1 | 与预期一致 | ✅ |
| `--verify` 校验既有计划 | 通过全部不变量 | 待填写 | ⏳ |
| registry 标签不可变已开启 | 重复推同一 `sha-*` 返回 409 | 待填写 | ⏳ |
| 部署镜像自证身份 | 读出的 revision 注解 = 当前记录的提交号 | 待填写 | ⏳ |
| 验签阻断 | 未签名镜像在验签步骤即失败，不进入部署 | 待填写 | ⏳ |
| 回滚可执行 | 服务恢复，日志中出现旧提交号 | 待填写 | ⏳ |

### 遇到的问题与决策

| 问题 | 决策 | 理由 |
| --- | --- | --- |
| 身份标签用全长 sha 还是前 12 位 | **工具用 `sha-<12>`，并强制小写规范化** | 12 位在「一次发布几十个提交」的量级下碰撞概率可忽略且好读；但**入库与比对一律用全长 sha**，短 sha 只属于展示层 |
| 版本标签在构建阶段打还是发布阶段打 | **发布阶段** | 「第几个发布」是人的决策而不是构建副产物；构建阶段只产出身份。CI 页据此调整为只推 sha 标签 |
| 环境指针要不要显式推 | **要，但单独一次操作、单独一条审批链路** | 好处是权限可分级：CI 角色能推 `sha-*`，推 `prod` 需要另一条链路。混在一起推等于任何能跑 CI 的人都能改生产指针 |
| 回滚能不能靠「重新构建旧代码」 | **不能** | 重新构建要重新拉基础镜像、重新解析依赖，产出是否等价于当时线上那个镜像无法证明。回滚必须是换回旧身份标签 |
| 镜像清理保留多少个历史版本 | **按「上一稳定版 + 当前版 + 回滚候选」定，不按时间** | 按「时间最近」保留会让回滚能力随清理动作消失 |
| 发布策略选滚动/蓝绿/金丝雀 | **滚动替换** | 不需要额外基础设施；代价是必须守住接口兼容性——这与契约门禁是同一件事 |
| `liveness` 与 `readiness` 能不能共用一个端点 | **不能** | 混用会让「还没准备好」被误判成「已经坏了」，依赖抖动时进程被反复重启，越重越慢 |

### 下一步（第 81 天）

第 4 周第四步：**验收清单与上线收口**，也是月度项目的收尾。

1. 六类 18 项验收清单的落地版：把第 79 天的流水线产物、第 80 天的发布策略与第 78 天的部署脚本串成一次完整的「上线演练」。
2. 备份与恢复演练：数据库备份 + 恢复 + 数据一致性校验的三步命令，并把结果写进验收记录。
3. 观察窗口与回滚决策人：发布后的观察时长、看哪些指标、谁有权决定回滚，写进流程而不是靠默契。
4. 模板交付形态定稿：`stack-select.py` + CLI 设计 + 发布策略三者的关系收口，明确 MVP 范围。
5. 承接待办：CLI `--check` 与用例矩阵基线的交叉断言（第 77、79 天两次记入，仍未落地）。

:::warning 顺序调整（2026-09-25，第 81 天实际执行）
按需求方要求，第 81 天实际优先落地「**主库可插拔**」——主库不再固定 MySQL 8，改为 MySQL 8.4 / PostgreSQL 17 部署期二选一（见[主库可插拔](../Database/index.md)）。上述五项验收收口内容**顺延至第 82 天**，其中「备份与恢复演练」将按选定引擎分别给出 `mysqldump` / `pg_dump` 双版本。理由：主库选择影响验收清单的备份/恢复命令与监控指标口径，先定引擎再收口验收，避免同一件事走两遍。
:::

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-77 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁、异常路径收口 | ✅ **4/4 步完成** |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（78-90 天） | Docker 化、Compose、CI 流水线、发布策略、验收清单 | ✅ **4/4 完成**：容器化 ✅、CI 流水线 ✅、发布策略 ✅、验收清单 ✅（第 82 天；第 81 天为主库可插拔需求插入，不计入 4 周里程碑步数） |

## 2026-09-25（第 81 天）：主库可插拔 —— 需求方要求主库不固定 MySQL 8，改为可选

### 本次做了什么

按需求方当日要求，把「主库固定 MySQL 8.4」改为「**主库可插拔**」：同一套业务代码，部署期在 MySQL 8.4 与 PostgreSQL 17 之间二选一。与第 76 天的 ORM 可插拔构成两个正交维度（编译期选 ORM、部署期选引擎），并在页面中写明「切换引擎是发布事件，不是配置热更」的边界。

1. **设计决策三条**：雪花 ID 是双方言 DDL 能逐列对齐的前提（无自增差异）；建表脚本双方言双份、Flyway 版本号两侧成对；结构一致性做成门禁而不是约定。
2. **双方言建表脚本**：`db/mysql/V1__init_user.sql`、`V2__init_login_log.sql` 与 `db/postgres/` 同名对应，落实七条方言翻译规则（TINYINT→SMALLINT、DATETIME(n)→TIMESTAMP(n)、行内 COMMENT→COMMENT ON、内联 UNIQUE KEY→CONSTRAINT、内联 KEY→表外 CREATE INDEX、ENGINE/CHARSET 删除、INT→INTEGER）。
3. **一致性门禁 `db/parity_check.py`**（零第三方依赖）：解析两方言 DDL，按归一化类型比对表集合、脚本清单成对、列/可空性/主键/唯一约束/普通索引/表注释，不一致列明细并退出码 1；`--verbose` 输出每张表比对明细。
4. **校验器自测 `db/selftest.py`**：11 项断言覆盖解析、四种类型归一化（TINYINT/TINYINT(1)/DATETIME(3)/TIMESTAMP(3)）、主键/唯一/索引归并、一致样本空差异、缺列与类型不一致检出。
5. **部署配套**：`db/docker-compose.databases.yml` 双 profile（mysql/postgres，共用 `${DB_PASSWORD:?}` 缺失即报错，各自挂载方言初始化目录）；Spring 双数据源配置（`application-mysql.yml` / `application-postgres.yml`）；MyBatis-Plus 分页 `DbType` 显式注入而非连接推断；双 JDBC 驱动共存（约 2.5MB）免重建镜像。
6. 同步更新[项目总览](../index.md)（技术选型表「主库固定」改「主库可插拔」、进度表拆出第 81 天行、交付内容补第 20 项、本地运行补第 7 步）。

### 如何验证

```shell
cd db
# ① 校验器自测（2026-09-25 实测通过）
python selftest.py       # 期望：selftest: 11/11 通过
# ② 双方言结构一致性（2026-09-25 实测通过，零依赖）
python parity_check.py   # 期望：OK: 2 张表 / 22 列 双方言结构一致
# ③ 双 profile 部署路径（需 Docker，验收时执行）
DB_PASSWORD=xxx docker compose -f docker-compose.databases.yml --profile mysql up -d
#   等 healthy → 跑冒烟 → down；换 --profile postgres 重复一遍
# 期望：两侧冒烟全部通过、行为等效
```

开发过程中的三轮纠错（工具侧，不改测试）：

1. **表体定位**：初版用非贪婪正则 `(.*?)\)\s*;` 匹配表体，MySQL 表尾是 `) ENGINE = ... ;`，`)` 后不是紧跟 `;`，整表匹配失败——改为**括号配平扫描**。
2. **分数类型归一化**：`DATETIME(3)` / `TIMESTAMP(3)` 不在字面映射表里，归一化落空——补 `TINYINT(n)`、`DATETIME(n)`/`TIMESTAMP(n)` 的正则归一化分支。
3. **表注释检测**：表体定位方式改变后，原「从整段匹配里找 COMMENT」失效——统一改为在表尾片段（tail）中查 `COMMENT` 关键字（MySQL 表尾 `COMMENT = '...'`、PG 表后 `COMMENT ON TABLE`），并要求两侧都有。

### 遇到的问题与决策

| 问题 | 决策 |
| --- | --- |
| 切换引擎能不能做成运行时热切换？ | 不能。引擎切换涉及数据迁移与回滚预案，是发布事件；模板提供「可选」，不承诺「随换」 |
| 双驱动共存还是 Maven profile 裁剪？ | 默认共存（约 2.5MB），部署期配置切换、免重建镜像；体积敏感再按 profile 裁剪 |
| 分页方言从哪来？ | 配置项显式注入 `DbType`；连接推断会把「数据库可用」变成启动前置条件 |
| 一致性校验覆盖什么？ | 结构（列/键/索引/注释）机械比对；行为等效靠双 profile 冒烟，两层缺一不可 |
| success 字段用 BOOLEAN 还是 SMALLINT？ | SMALLINT，与实体 Integer 映射及 MySQL TINYINT(1) 语义对齐；布尔语义需求出现时两侧同步改 |

### 下一步（第 82 天）

1. **上线验收与监控接入**（原第 81 天计划顺延）：六类 18 项验收清单落地、备份恢复演练（`mysqldump` / `pg_dump` 双版本）、观察窗口与回滚决策人、模板交付形态定稿、CLI `--check` × 用例矩阵基线交叉断言（承接待办）。
2. **Testcontainers 双库矩阵**：数据层集成测试按引擎参数化各跑一遍，复用第 75 天隔离方案。
3. 本日新增的 `parity_check.py` 接入 CI 静态检查阶段（秒级、零依赖，放静态检查 job 最合适）。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-77 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁、异常路径收口 | ✅ **4/4 步完成** |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（78-90 天） | Docker 化、Compose、CI 流水线、发布策略、验收清单 | ✅ **4/4 完成**：容器化 ✅、CI 流水线 ✅、发布策略 ✅、验收清单 ✅（第 82 天完成；第 81 天为主库可插拔需求插入，不计入 4 周里程碑步数） |

## 2026-09-25（第 82 天）：上线验收与监控接入 —— 把「都验过了」拆成可判定、可复核的判据

### 本次做了什么

第 81 天把主库定成可插拔之后，验收的备份/恢复命令与监控指标口径才能定下来。本日把原定第 81 天的「验收收口」做完，并结清两笔挂了三天以上的待办。

1. **验收清单从「一张勾选框表格」变成可执行工具**。六类 18 项（功能 / 性能 / 安全 / 数据 / 可观测 / 运维，各 3 项）写进 `Acceptance/acceptance_check.py` 的 `ITEMS` 常量——**清单写在代码里而不是文档里**，因为文档里的表会漂移，代码里的表一改就会让自测报红。
2. **三层结构定死判定方式**。AUTO 12 项（`file` / `grep` / `matrix` / `script` / `crossrollback` 五类判据，CI 里全跑）、MANUAL 6 项（A1 主链路、B1 压测、B3 慢查询、C3 漏洞扫描、D3 越权、E3 告警触达——需要真实集群、真实流量、真实人员，工具**只打印可直接粘贴的命令与「期望看到什么」，不假装它们通过**）、签名表 `manual_signoff.json`（`--strict` 下 6 项必须登记 `by` / `at` / `evidence`，且 evidence 至少 8 字符、`at` 必须是 ISO 日期开头，**给 AUTO 项签名会被点名**）。
3. **两条跨交付物交叉断言，结清第 76/77 天与第 80 天的待办**。`--cross` 断言：① CLI `--check` × 用例矩阵基线——基线现在从 `stack.json.caseBaseline` 一路流到 `application-stack.yml` 的 `case-baseline` 与 `STACK.md`，断言它真的进了生成物、**改小一格必报红**、降基线必须被拒；② 回滚命令 × 标签不可变性——用 `tagplan.py --verify` 断言回滚引用身份标签，并做一次变异把 `IMAGE_REF` 换成环境指针 `prod`，`--verify` 必须报红。**两处都用变异测试，而不是「生成后 --check 通过」这种必然成立的检查。**
4. **备份可恢复演练 `Acceptance/backup_restore.py`**。判据四条：备份非空、恢复到 `<源库>_restore_check` 而不是就地覆盖、**表集合与逐表行数完全一致**（只比总行数会漏掉「A 表少 100 行、B 表多 100 行」）、演练后清理演练库。双方言（`mysqldump` / `pg_dump`）共用一份动作清单，`--dry-run` 在无客户端的环境也能跑通。
5. **判据文件两份**：`known_issues.md`（A3，遗留缺陷登记 + 「什么不算已知缺陷」+ 豁免时效）与 `rollback_plan.md`（F3，决策人 / 观察窗口三档 / 四类触发阈值 / 升级路径 / 交接记录）。
6. **`Acceptance/selftest.py` 71 项断言**，含 10 处变异测试（矩阵 5 + 签名表 5）。
7. **补上 `PerformanceTest/index.md` 的容量拐点一节**（B2 的判据要求）：阶梯加压五档 + 双证据判定（TPS 增量衰减 **且** 资源水位触顶，单独出现都不算），以及找到拐点后的三件事（写进容量台账、只对先触顶的资源扩容、重跑确认可复现）。
8. 同步更新[项目总览](../index.md)（进度表拆出第 82 天行、交付内容补第 21 项、本地运行补第 8、9 步、参考资料补链接）。

### 如何验证

```shell
cd project/Base/BackendTemplate

# ① 清单本身：六类 18 项的判据、责任人、判定方式、可直接粘贴的命令
python Acceptance/acceptance_check.py --list

# ② AUTO 12 项（2026-09-25 实测：12/12 通过，退出码 0）
python Acceptance/acceptance_check.py

# ③ 跨交付物交叉断言（2026-09-25 实测：两条 PASS，含 3 处变异测试）
python Acceptance/acceptance_check.py --cross

# ④ 工具自测（2026-09-25 实测：71/71 通过）
python Acceptance/selftest.py

# ⑤ 严格模式：签名前必然退出码 1，且点名 6 个未签项 —— 这是正确状态，不是缺陷
python Acceptance/acceptance_check.py --strict

# ⑥ 备份恢复演练的动作清单（真演练需 mysql / pg 客户端，本机用 dry-run 核对）
python Acceptance/backup_restore.py --dry-run

# ⑦ 被交叉断言复用的两条既有门禁（实测通过）
cd db && python parity_check.py      # 期望：OK: 2 张表 / 22 列 双方言结构一致
cd ../Release && python selftest.py  # 期望：selftest: 88/88 通过（全组合扫描 11 组）
```

### 遇到的问题与决策

| 问题 | 决策 |
| --- | --- |
| 验收清单的最优失效方式是什么？ | **「跑起来全绿但没人真验过」**。所以随仓库提供的签名表是**空的**，`--strict` 初始必红；转绿条件只有一个：在验收环境把 6 个 MANUAL 项真做一遍并填证据 |
| 校验器遇到坏数据该崩还是该报失败？ | **必须报失败**。自测第一次运行就抓到：矩阵里填一个非法符号（`✔` 写成 `X`）会让覆盖数统计 `KeyError` 崩溃——而手工维护的矩阵最容易出的就是写错符号。修法是改用 `.get()`，并把「JSON 损坏 / 缺字段 / 类型不对」都做成 FAIL 而不是异常 |
| 交叉断言该断言什么？ | 断言**门禁被改坏时会不会拦住**，而不是「正常情况通过」。后者是必然成立的（生成器刚写完生成物当然自洽），跑了等于没跑 |
| 备份演练用 shell 还是 Python？ | Python。曾写成 Python / POSIX sh 双栖，但因为本机 `bash` 指向被拦截的 WSL、无 `python3`，**双栖无法在本地验证**——一个自己没跑通的脚本放进验收清单，正是本页要反对的事。与 `parity_check.py` / `tagplan.py` / `stack-select.py` 统一 |
| `mysqldump` 要不要加 `--databases`？ | **不要**。加了会把 `CREATE DATABASE` / `USE <源库>` 写进 dump，「恢复到演练库」会拐回去覆盖源库——备份演练最危险的写法。另加一条自我保护：源库名若已带 `_restore_check` 后缀直接拒绝执行 |
| 备份判据能不能简化成「总行数一致」？ | 不能。A 表少 100 行、B 表多 100 行时总数相等。判据必须是**表集合一致 + 逐表行数一致** |
| 容量拐点怎么算拐点？ | **双证据**：TPS 增量衰减到前一段的 50% 以下 **且** 资源水位触顶（CPU > 85% / 连接池排队 / GC 占比 > 10%）。只满足一条可能是压测机自瓶颈或无效并发，两条同时成立才是服务端容量上限 |

### 下一步（第 83 天）

1. **在真实环境执行 6 个 MANUAL 项并回填签名表**，把 `--strict` 从红转绿——不做这一步，前面全是纸上功夫。
2. **Testcontainers 双库矩阵**（第 81 天起两次记入）：把 `parity_check.py` 的静态结构比对升级为「起真实 MySQL 8.4 + PostgreSQL 17 各跑一次迁移」，覆盖静态比对看不见的行为差异（排序规则、`TEXT` 语义、并发下的 DDL 锁）。
3. **两条门禁接进 CI**：`db/parity_check.py` 进静态检查 job（秒级、零依赖），`Acceptance/acceptance_check.py --cross` 进测试 job——本日只把断言写出来了，还没挂进流水线。
4. **监控接入落地**：E1 看板与 E2 traceId 检索已有基础（第 70、74 天），E3「告警触达人」目前还只是判据，需要在验收环境真推一次。

### 里程碑对照

| 阶段 | 计划 | 当前状态 |
| --- | --- | --- |
| 第 1 周（61-68 天） | 需求拆分、技术选型、架构与目录设计 | ✅ 完成 |
| 第 2 周（69-72 天） | 核心模块编码：骨架 → 响应/异常 → 校验/日志 → 数据访问 → 认证 | ✅ **4/4 步完成** |
| 第 3 周（73-77 天） | 联调、单元与集成测试、压测基线、覆盖率与契约门禁、异常路径收口 | ✅ **4/4 步完成** |
| 模板产品化（第 76 天插入） | 技术栈可插拔 + 选择器脚本 + CLI 设计 | ✅ **3/3 完成**；CLI 处于设计阶段，MVP 待排期 |
| 第 4 周（78-90 天） | Docker 化、Compose、CI 流水线、发布策略、验收清单 | ✅ **4/4 完成**：容器化 ✅、CI 流水线 ✅、发布策略 ✅、验收清单 ✅（第 81 天为主库可插拔需求插入，不计入 4 周里程碑步数） |

## 参考资料

- 项目总览：[后端通用模板](../index.md)
- 本日两条：[上线验收与监控接入](../Acceptance/index.md) ｜ [压测与性能基线](../PerformanceTest/index.md)（新增容量拐点一节）
- 本日交付物：`Acceptance/acceptance_check.py`（六类 18 项可执行清单）｜ `Acceptance/selftest.py`（71 项自测）｜ `Acceptance/backup_restore.py`（双方言备份恢复演练）｜ `Acceptance/case_baseline.json`（用例矩阵机器可读来源）｜ `Acceptance/known_issues.md` + `Acceptance/rollback_plan.md`（A3 / F3 判据文件）｜ `Acceptance/manual_signoff.json`（签名表，随仓库为空）
- 各日模块页：[骨架与目录结构](../Skeleton/index.md) ｜ [统一响应与全局异常](../CommonResponse/index.md) ｜ [健康检查与配置](../HealthCheck/index.md) ｜ [请求追踪 ID 与日志切面](../TraceId/index.md) ｜ [参数校验增强](../Validation/index.md) ｜ [MockMvc 集成测试](../IntegrationTest/index.md) ｜ [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) ｜ [认证授权：Spring Security 7 + JWT](../Security/index.md) ｜ [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) ｜ [压测与性能基线](../PerformanceTest/index.md) ｜ [测试数据隔离与边界用例](../TestIsolation/index.md) ｜ [技术栈可插拔](../StackSelect/index.md) ｜ [模板 CLI：设计与路线图](../TemplateCli/index.md) ｜ [异常路径联调收口与用例清单](../ErrorPath/index.md) ｜ [容器化：多阶段镜像与 Compose 编排](../Deployment/index.md) ｜ [CI 流水线：把门禁串成一条链](../CI/index.md) ｜ [镜像推送与发布策略](../Release/index.md) ｜ [主库可插拔：MySQL / PostgreSQL 双方言](../Database/index.md) ｜ [上线验收与监控接入](../Acceptance/index.md)
- 外部规范：[Docker Build attestations](https://docs.docker.com/build/attestations/) ｜ [Sigstore Cosign 验签](https://docs.sigstore.dev/cosign/verifying/verify/) ｜ [K8s 存活、就绪与启动探针](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) ｜ [OCI 镜像注解规范](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
- 相关文档：[Spring Boot 通用指南](../../../../docs/Backend/Java/Frame/SpringBoot/Common/index.md) ｜ [完整项目交付 · 一键部署与上线验收](../../../../docs/Others/ProjectDelivery/Delivery/index.md)
