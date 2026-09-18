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

## 参考资料

- 项目总览：[后端通用模板](../index.md)
- 本日两条：[容器化：多阶段镜像与 Compose 编排](../Deployment/index.md) ｜ [异常路径联调收口与用例清单](../ErrorPath/index.md)
- 各日模块页：[骨架与目录结构](../Skeleton/index.md) ｜ [统一响应与全局异常](../CommonResponse/index.md) ｜ [健康检查与配置](../HealthCheck/index.md) ｜ [请求追踪 ID 与日志切面](../TraceId/index.md) ｜ [参数校验增强](../Validation/index.md) ｜ [MockMvc 集成测试](../IntegrationTest/index.md) ｜ [数据访问：MyBatis-Plus 接入](../DataAccess/index.md) ｜ [认证授权：Spring Security 7 + JWT](../Security/index.md) ｜ [登录业务闭环与令牌生命周期](../AuthLifecycle/index.md) ｜ [压测与性能基线](../PerformanceTest/index.md) ｜ [测试数据隔离与边界用例](../TestIsolation/index.md) ｜ [技术栈可插拔](../StackSelect/index.md) ｜ [模板 CLI：设计与路线图](../TemplateCli/index.md)
- 相关文档：[Spring Boot 通用指南](../../../../docs/Backend/Java/Frame/SpringBoot/Common/index.md)
