# 配置与密钥：同一份镜像跑在三套环境上

这一页回答「**同一份镜像怎么在本地、预发、生产三套环境上跑起来**」——哪些值该随镜像走、哪些该随环境走、密钥放在哪一级、怎么保证它不会被打进日志。它**不回答**「编排文件本身怎么写」（那是 [环境与工程骨架](../Environment/index.md) 第三、四节的事），也**不回答**「发布时这些配置怎么变、怎么退回来」（那是 [发布与回滚手册](../ReleaseRunbook/index.md) 的事）。

![在线协作任务看板：配置三层分流与密钥四级落点](../assets/tb-config-secrets.svg)

::: warning 本仓库只有文档，没有代码
下面所有 `.env`、`application.yml`、`compose.yaml` 片段，以及 `docker compose config`、`gitleaks`、`git check-ignore` 命令，都是**读者在自己的工程里创建并执行的东西**。本仓库不存放源码、配置文件与密钥样例（`project/` 只允许 `*.md` 与配图）；「运行 `xxx`」一律指「先按本节把文件建出来，再执行」。
:::

## 一、配置三分法：先分清「谁该改它」

「配置」这个词太宽，宽到把密钥也吞进去了。**分开它们的判据不是「放在哪个文件」，而是「谁该改它、改了之后要付出什么代价」**：

| 类 | 本项目里的例子 | 落点 | 变更成本 | 泄漏 / 写错的后果 |
| --- | --- | --- | --- | --- |
| **随镜像走的**（默认值，不该变） | `server.port`、日志基线、时区、预签名有效期默认值 | `application.yml` + `application-common.yml`，**打进镜像** | 改一次要重新构建并发布镜像 | 三套环境**一起错**，而且没有「只回滚一套」的选项 |
| **随环境走的** | 连接串、Redis 主机、对外域名、CORS 来源、功能开关 | `.env` / CI 变量 / 编排 `environment` / `env_file` | 改值 + 重启，不动镜像 | **环境串味**：预发连上生产库、生产开了调试开关，且第一眼看不出 |
| **密钥** | 库口令、对象存储密钥、令牌签名密钥、SMTP 口令 | 密钥管理服务；本地退化为 `.env`；编排用 `secrets:` | 轮换要**双密钥过渡**（旧令牌在 TTL 内仍有效） | **不可逆**：只能轮换，已经泄漏的那段时间窗撤不回来 |

三类之所以要分开，是因为**失败模式不同**：随镜像走的值写错是「三套一起错」，随环境走的值写错是「一套错成另一套」，密钥泄漏是「不可撤销」。**「把密钥当配置」之所以是最常见的滑坡**，是因为它们在物理上长得一样——都是 `KEY=value`、都放在 `.env`、都由同一段代码读出来，于是「再加一行」永远最省事。但配置写错是**可回滚的**（改回一行、重启），密钥泄漏是**不可回滚的**（值可能已被复制到别处，轮换不会让已泄漏的时间窗消失）。滑坡的第一块石头通常是示例文件：`.env.example` 的职责只是**描述结构**，一旦出现真值而不是 `change-me-locally` 这类占位符，下一步就是把 `example` 复制成 `.env` 并提交。

::: tip 一句话判据
**「这个值泄漏之后，我能把它改回原状吗？」** 能 → 它是配置；不能 → 它是密钥。**分不出来的值，一律当密钥处理。**
:::

## 二、完整环境变量清单

清单必须同时回答三个问题：**有默认值吗**（没有就等于「启动期必填」）、**是密钥吗**（决定走哪条注入路径）、**该给谁**（谁持有这个值）。三列合起来才决定这个值的落点。

| 变量 | 用途 | 有默认值？ | 是密钥？ | 该给谁 |
| --- | --- | --- | --- | --- |
| `SPRING_PROFILES_ACTIVE` | 生效的配置档 | 有（`local`） | 否 | 部署平台 |
| `APP_PORT` | 后端宿主端口 | 有（`8080`） | 否 | 本地开发者 |
| `POSTGRES_DB` | 库名 | 有（`teamboard`） | 否 | 部署平台 |
| `POSTGRES_USER` | 库用户 | 有（`teamboard`） | 否 | 部署平台 |
| `POSTGRES_PASSWORD` | 库口令 | **无（必填）** | **是** | 密钥管理服务 |
| `SPRING_DATASOURCE_URL` | JDBC 连接串 | 本地有、生产**无** | 否 | 部署平台 |
| `SPRING_DATA_REDIS_HOST` | Redis 主机 | 本地有、生产**无** | 否 | 部署平台 |
| `JWT_SIGNING_KEY` | 访问令牌签名密钥 | **无（必填）** | **是** | 密钥管理服务 |
| `JWT_ACCESS_TTL` / `JWT_REFRESH_TTL` | 访问 / 刷新令牌有效期 | 有（`15m` / `14d`） | 否 | 部署平台 |
| `S3_ENDPOINT` | 对象存储端点 | 本地有、生产**无** | 否 | 部署平台 |
| `S3_ACCESS_KEY` | 对象存储访问键 | 有（仅本地固定值） | 否 | 部署平台 |
| `S3_SECRET_KEY` | 对象存储密钥 | **无（必填）** | **是** | 密钥管理服务 |
| `S3_BUCKET` | 附件桶名 | 有（`teamboard-attachments`） | 否 | 部署平台 |
| `S3_PRESIGN_TTL_SECONDS` | 附件预签名有效期 | 有（`300`） | 否 | 部署平台 |
| `SMTP_HOST` / `SMTP_USERNAME` | 通知邮件出口与账号 | 有（本地为空即不发信） | 否 | 部署平台 |
| `SMTP_PASSWORD` | 邮件口令 | **无（启用邮件时必填）** | **是** | 密钥管理服务 |
| `CORS_ALLOWED_ORIGINS` | 允许的前端来源 | 本地有、生产**无** | 否 | 部署平台 |
| `APP_PUBLIC_BASE_URL` | 对外域名（票据与预签名回跳） | **无** | 否 | 部署平台 |

::: tip 这张表怎么用
1. **「无默认值」的变量就是第六节启动期断言的必填清单**（`POSTGRES_PASSWORD`、`JWT_SIGNING_KEY`、`S3_SECRET_KEY`、`SMTP_PASSWORD`，以及生产档位下的 `SPRING_DATASOURCE_URL`、`SPRING_DATA_REDIS_HOST`、`S3_ENDPOINT`、`APP_PUBLIC_BASE_URL`）。
2. `S3_ACCESS_KEY` 与 `S3_SECRET_KEY` 的「是密钥」判定**不对称**：访问键本身不是秘密（它要出现在请求里），密钥才是；本地值一律写成 `change-me-locally` 这类**不可用**的占位符，保证「忘了配值」在启动期炸，而不是连上某台恰好存在的数据库。
:::

## 三、`application.yml` 的多环境分层与 `env_file`

### 3.1 入口文件：档位组 + 三种导入来源

```yaml [app/src/main/resources/application.yml]
spring:
  application:
    name: teamboard
  profiles:
    group:                                # 档位组：一次激活一组，避免 local 与 prod 同时生效
      local:   [common, local]
      staging: [common, staging]
      prod:    [common, prod]
  config:
    import:
      - classpath:application-common.yml  # 基线：随镜像走的那一类
      - optional:file:.env[.properties]   # 本地开发：从工程根读 .env（[.properties] 是格式提示）
      - configtree:/run/secrets/          # 编排挂载：文件名即配置键名
server:
  port: ${APP_PORT:8080}                  # 有默认值 → 属于「随镜像走」的那一类
app:
  public-base-url: ${APP_PUBLIC_BASE_URL:}
```

三处要读懂的地方：① **`profiles.group` 把「档位」变成「一组文件」**，`SPRING_PROFILES_ACTIVE=prod` 实际激活 `common` + `prod`，基线放 `common`、各档只写差异，否则三份文件必然各自漂移；② **`.env` 用 `file:` 前缀导入**，只在本地开发成立，`optional:` 让它缺失时不报错（CI 与生产走另一条路）；③ **`configtree:/run/secrets/` 的文件名就是配置键名**，容器里出现 `/run/secrets/app.jwt.signing-key` 就等价于设置了 `app.jwt.signing-key`。

### 3.2 各档只写差异

```yaml [app/src/main/resources/application-local.yml]
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/teamboard
  data:
    redis:
      host: localhost
app:
  s3:
    endpoint: http://localhost:9000
logging:
  level:
    com.teamboard: DEBUG                  # 只有这一档是 DEBUG，基线在 application-common.yml
```

```yaml [app/src/main/resources/application-prod.yml]
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}          # 无默认值：生产不许「猜一个」
  data:
    redis:
      host: ${SPRING_DATA_REDIS_HOST}
server:
  forward-headers-strategy: framework      # 生产在反向代理之后，必须显式声明
```

::: warning 生产档不写默认值，是**故意的**
`${SPRING_DATASOURCE_URL}` 没有 `:默认值` 尾巴，所以变量缺失时 Spring 直接报 `Could not resolve placeholder` 并拒绝启动。这不是「配置没写全」，而是把「必须由外部提供」这件事**写进配置结构里**——比写一句注释可靠得多。
:::

### 3.3 编排侧：`env_file` 与 `secrets:`

```yaml [compose.yaml（只列与配置、密钥有关的部分）]
services:
  app:
    image: registry.example.com/teamboard-app@sha256:${APP_DIGEST}
    env_file:
      - .env                               # 普通配置：值来自文件
    environment:
      SPRING_PROFILES_ACTIVE: ${SPRING_PROFILES_ACTIVE:-local}  # 行内取值优先于 env_file
    secrets:
      - app.jwt.signing-key
      - app.s3.secret-key
secrets:
  app.jwt.signing-key:
    file: ./secrets/jwt_signing_key.txt
  app.s3.secret-key:
    file: ./secrets/s3_secret_key.txt
```

::: danger 这一节最容易被写错的四件事
1. **在 `environment:` 里写死档位名。** 写成 `SPRING_PROFILES_ACTIVE: local` 之后，`.env` 里的值再也覆盖不了它——`environment` 的显式常量优先级高于 `env_file`。正确写法是 `${SPRING_PROFILES_ACTIVE:-local}`：`.env` 有值就用 `.env` 的，没有才回落默认。
2. **把密钥写在 `environment:` 里而不是 `secrets:` 里。** 环境变量会同时出现在 `docker inspect`、`docker compose config` 与进程的 `/proc/<pid>/environ` 三处。正确写法：密钥只走 `secrets:`，挂载成 `/run/secrets/<键名>` 文件。
3. **用 `.env` 当密钥源。** `env_file: .env` 里的密钥同样进环境变量，且 `.env` 一旦被误提交就是全环境失守。正确写法：`.env` 只放非密钥值，密钥单独放 `secrets/` 目录，并同时写进 `.gitignore` 与 `.dockerignore`。
4. **生产档位给 `configtree:` 加了 `optional:`。** 目录不存在时它被静默跳过，「密钥为空」也能启动成功，直到第一次签发令牌才报错。正确写法：生产档位写 `- configtree:/run/secrets/`（**不加** `optional:`），目录缺失即启动失败。
:::

## 四、`docker compose config` 会把密钥打印到标准输出

这条值得单独一节，因为它的后果与它的日常程度完全不匹配：**一条命令就能把三套环境的密钥写进 CI 日志并长期留存**，而「校验编排文件」是每个流水线都会做的事。`docker compose config` 的职责是「渲染最终配置」——它把 `.env` 的值**插值展开**进 `environment` 段再打印，所以只要密钥在 `environment` 或 `env_file` 里，最常见的 CI 步骤就会把明文吐进日志。

::: danger 四处会让密钥进日志的写法
1. **CI 里直接跑 `docker compose config` 并把输出打进日志。** 正确写法：`docker compose config --no-interpolate -q`——`--no-interpolate` 不展开变量，`-q` 不打印渲染结果，只校验编排文件本身是否合法。
2. **把 `--no-interpolate` 的输出当成「变量也都对」。** 它只查 YAML 结构与引用关系，**不查变量是否存在、是否有值**。正确写法：结构用 `--no-interpolate` 查，取值是否就绪用第六节的启动期断言查，两者分工、互不替代。
3. **把「日志脱敏」当成第一道防线。** 脱敏是第二道；第一道是**让密钥根本不进入被打印的那个结构**。正确写法：密钥走 `secrets:`（文件挂载），于是渲染结果里只有 `file:` 路径，没有值。
4. **在脚本里 `echo` 出密钥之后手动加掩码。** 掩码只对**之后**的输出生效，抓不到已经写进同一行的内容。正确写法：不 `echo`，需要判断「值是否为空」时只打印变量名与长度。
:::

```shell
# ① 只校验结构：不展开、不打印任何一个值（CI 里唯一该跑的那条）
docker compose config --no-interpolate -q && echo "编排结构 OK"

# ② 本地排查：不插值地看「哪些位置引用了变量」，用来核对清单是否漏项
docker compose config --no-interpolate | grep -nE '\$\{[A-Z_][A-Z0-9_]*\}' | head -20

# ③ 值级判据：CI 日志里不得出现任何密钥字面值（期望 0）
grep -cF "$(cat secrets/jwt_signing_key.txt)" ci-log.txt
```

第 ③ 条测的不是「有没有脱敏成功」，而是「**密钥字面值有没有进入日志文件**」——一个能被 `grep -c` 数出来的事实，而不是一句「我们做了脱敏」的承诺。

## 五、密钥的四级落点

四级不是「更好的四级」，而是**四种代价结构**：越往下越难泄漏，也越难轮换。选哪一级取决于「这个密钥泄漏的后果」与「它多久要换一次」。

| 级 | 形态 | 最小可用形态 | 轮换要做什么 | 不该用的场景 |
| --- | --- | --- | --- | --- |
| **L1** | 本地 `.env`（不入库） | `.env` + `.env.example` + `.gitignore` 首行 | 改文件、重启本地服务 | 任何**多人共享**的环境 |
| **L2** | CI 变量（仓库 / 环境级 Secrets） | 平台 Secrets + 输出掩码 | 平台里改值、重跑流水线 | 需要**双人审批与审计**的生产主密钥 |
| **L3** | 编排 secrets 挂载 `/run/secrets` | `secrets:` + `configtree:/run/secrets/` | 换文件 + **重建容器** | 需要**不重启就轮换**的场景 |
| **L4** | 密钥管理服务（Vault / KMS / SSM） | 启动时按角色拉取、只驻内存、不落盘 | 服务侧改版本，应用按 TTL 重取 | 30 天周期的本地开发（过度设计且无人维护） |

落地的第一步不是选级别，而是**堵住入库这条路**。下面五条命令是 `CF-E` 的可执行部分：

```shell
# ① .gitignore 必须挡住的三类（结构文件用 ! 放行）
printf '.env\n.env.*\n!.env.example\nsecrets/\n' >> .gitignore
# ② 确认它们真的被挡住了（期望：每条都命中一条规则，规则行号可读）
git check-ignore -v .env secrets/jwt_signing_key.txt
# ③ 历史里从未提交过（期望：无输出）
git log --oneline -- .env secrets/ | head
# ④ 提交前扫描：命中即阻断（gitleaks 2.x）
gitleaks detect --source . --redact --no-banner     # 期望：no leaks found
gitleaks protect --staged --redact                  # 只扫暂存区（pre-commit 钩子同样用 git-secrets --install）
```

::: danger 四级落法里最容易做错的三个地方
1. **把「文件路径」当成「已经安全」。** 密钥在 `secrets/` 目录里，但只要镜像构建上下文包含它（没有 `.dockerignore`），它就会被 `COPY` 进镜像层——**镜像层是永久的**，删掉文件也不会从历史层里消失。正确写法：`secrets/` 同时写进 `.gitignore` 与 `.dockerignore`。
2. **轮换时直接换值。** 访问令牌还有 15 分钟有效期、刷新令牌 14 天，直接换签名密钥等于**把所有在线用户踢下线**。正确写法：双密钥过渡——验签时新旧都接受、签发只用新的，等超过 `JWT_REFRESH_TTL` 之后再摘掉旧密钥。
3. **把「密钥管理服务」当成一次性开关。** L4 的代价是「多了一个必须可用的依赖」：它挂掉时应用能不能启动、能不能降级，必须先答出来。正确写法：在第七节的表里明确写出 L4 的失败场景（拉取超时、权限被撤），**答不出来就先停在 L3**。
:::

## 六、启动期拒绝：四类必须写成断言的配置错误

口径是：**配置错了要在启动期炸，不要留到运行期**。区别很具体——启动期炸的表现是**容器起不来**（`docker compose up` 直接报错，编排层可见），运行期才炸的表现是「服务 `health` 是 `UP`，第一次登录返回 `500`」。

| 类 | 运行期才炸的样子 | 启动期断言 | 拒绝启动时的输出 |
| --- | --- | --- | --- |
| **变量缺失** | 服务 `UP`，第一次落库 `500` | `${VAR}` 不写默认值 + `@NotBlank` | `Could not resolve placeholder 'SPRING_DATASOURCE_URL'` |
| **端口格式错** | 容器起来但监听在意外端口 | `@Min(1) @Max(65535)` | `Property: app.port ... must be less than or equal to 65535` |
| **签名密钥不足 32 字节** | 签发时报弱密钥异常，或签出短密钥 | 自定义断言（HS256 要求 ≥ 256 bit） | `IllegalStateException: JWT_SIGNING_KEY 不足 32 字节……拒绝启动` |
| **生产档位指向本机** | 生产库里出现「本地测试数据」 | `@Profile("prod")` 的启动断言 | `IllegalStateException: 生产档位不允许指向本机 / 开发服务名` |

```java [app/src/main/java/com/teamboard/config/AppProperties.java]
@ConfigurationProperties(prefix = "app")
@Validated
public record AppProperties(
    @Min(1) @Max(65535) int port,
    @NotBlank String publicBaseUrl,
    @Valid Jwt jwt,
    @Valid S3 s3) {
  public record Jwt(@NotBlank String signingKey, Duration accessTtl, Duration refreshTtl) {}
  public record S3(@NotBlank String endpoint, @NotBlank String bucket, @NotBlank String secretKey) {}
}
```

```java [app/src/main/java/com/teamboard/config/ConfigGuard.java]
@Configuration
@EnableConfigurationProperties(AppProperties.class)
public class ConfigGuard {
  /** ① 密钥长度：HS256 要求 ≥ 256 bit（32 字节），不足即拒绝启动 */
  @Bean
  ApplicationRunner assertSigningKey(AppProperties props) {
    return args -> {
      int bytes = props.jwt().signingKey().getBytes(StandardCharsets.UTF_8).length;
      if (bytes < 32) {
        throw new IllegalStateException(
            "JWT_SIGNING_KEY 不足 32 字节（HS256 需要 ≥ 256 bit）：当前 " + bytes + " 字节，拒绝启动");
      }
    };
  }
  /** ② 档位与取值的矛盾：生产档位不允许指向本机或开发服务名 */
  @Bean
  ApplicationRunner assertProdIsNotLocal(Environment env) {
    return args -> {
      if (!env.matchesProfiles("prod")) {
        return;
      }
      String url = env.getProperty("spring.datasource.url", "");
      if (url.contains("localhost") || url.contains("127.0.0.1") || url.contains("//db:")) {
        throw new IllegalStateException("生产档位不允许指向本机 / 开发服务名：url=" + url);
      }
    };
  }
}
```

失败时的预期输出（**结构示例，包名与行号以你自己的工程为准**）：

```text
***************************
APPLICATION FAILED TO START
***************************
Description:
Failed to bind properties under 'app' to com.teamboard.config.AppProperties:
    Property: app.jwt.signing-key   Value: ""   Reason: 必须提供令牌签名密钥
    Origin: class path resource [application-prod.yml] - 8:16
# 另一类断言的表现（包名以你的工程为准）：
# java.lang.IllegalStateException: JWT_SIGNING_KEY 不足 32 字节：当前 13 字节，拒绝启动
```

::: warning 为什么这四条不能靠「运行期发现」
一个 `UP` 但配置错的服务是最难被发现的一类故障：健康检查绿、容器在跑、日志没有 `ERROR`，直到有人做第一次真实操作。把它变成「容器起不来」之后，**所有既有流程（编排、冒烟、告警）都会替你抓住它**——这就是启动期断言的全部价值。
:::

## 七、配置漂移：三套环境怎么对账

漂移分两种，危险程度不同：**「某个变量只在一套环境里有」最危险**（另一套会静默回落到默认值），**「同一个非密钥变量在三套里取值不同」次之**（可能是故意的，也可能不是）。

```shell
# ① 变量名清单对账（最危险的一类：某套环境少了一个变量）
grep -oE '^[A-Z_][A-Z0-9_]*=' .env          | sort > /tmp/names.local
grep -oE '^[A-Z_][A-Z0-9_]*=' .env.staging  | sort > /tmp/names.staging
grep -oE '^[A-Z_][A-Z0-9_]*=' .env.prod     | sort > /tmp/names.prod
diff /tmp/names.local /tmp/names.staging    # 期望：无输出
diff /tmp/names.local /tmp/names.prod       # 期望：无输出
# ② 非密钥变量的值对账（密钥一律只比「存在性」，绝不打印值）
for k in APP_PORT S3_BUCKET SPRING_PROFILES_ACTIVE CORS_ALLOWED_ORIGINS APP_PUBLIC_BASE_URL; do
  printf '%-24s local=%s staging=%s prod=%s\n' "$k" \
    "$(grep -E "^$k=" .env         | cut -d= -f2-)" \
    "$(grep -E "^$k=" .env.staging | cut -d= -f2-)" \
    "$(grep -E "^$k=" .env.prod    | cut -d= -f2-)"
done
# ③ 密钥只比「有没有」：只数长度，不打印值（期望：三套都不是 0）
for f in .env .env.staging .env.prod; do
  printf '%-16s JWT_SIGNING_KEY 字节数=%s\n' "$f" \
    "$(grep -E '^JWT_SIGNING_KEY=' "$f" | cut -d= -f2- | wc -c)"
done
```

三处差异是**允许且应当**存在的，其余差异都要能说出理由：`SPRING_PROFILES_ACTIVE`（它本身就是档位选择器）、`SPRING_DATASOURCE_URL`（连接目标按环境不同，这正是「随环境走」的定义）、`S3_ENDPOINT`（同上，且**生产必须是 https**，否则预签名 URL 会被浏览器拦）。

第 ① 条 diff 一旦有输出，说明两套环境**连变量集合都不一样**——它意味着「预发跑通」推不出「生产能跑」，所以必须在发布前修掉，放进发布检查单（见 [发布与回滚手册](../ReleaseRunbook/index.md) 第三节的 T-1 阶段）。

## 八、判据族声明（`CF-A` ~ `CF-H`）

八条判据分两组：七条**文档级**（验「口径是否自洽、命令是否可执行」），一条**运行期**（验「三套环境真的各起过一次」）。逐条的判法与期望见第十节。
| 判据 | 一句话声明：它回答什么 | 级别 |
| --- | --- | --- |
| **`CF-A`** | 配置三分法写死，且三类的落点、变更成本、泄漏后果各不相同 | 文档级 |
| **`CF-B`** | 环境变量清单齐全，每行给出「有默认值 / 是密钥 / 该给谁」 | 文档级 |
| **`CF-C`** | 多环境分层用 `profiles.group` + `config.import`，编排侧用 `env_file` 与 `secrets:` | 文档级 |
| **`CF-D`** | `docker compose config` 的泄漏风险写死，并给出 `--no-interpolate` 的正确排查写法 | 文档级 |
| **`CF-E`** | 密钥四级落点齐全，每级给出最小可用形态与不该用的场景 | 文档级 |
| **`CF-F`** | 四类启动期断言齐全（变量缺失 / 端口格式 / 密钥长度 / 生产指向本机） | 文档级 |
| **`CF-G`** | 三套环境的对账命令可执行（变量名集合、非密钥取值、密钥存在性） | 文档级 |
| **`CF-H`** | 三套环境各真起一次：同一 digest、启动期断言有效、CI 日志里密钥字面值命中 0 次 | 运行期 |

## 九、当日做了什么

1. 产出**配置三分法**（随镜像走 / 随环境走 / 密钥），逐类给出落点、变更成本与泄漏后果，并论证**「把密钥当配置」是最常见的滑坡**（判据：这个值泄漏后能不能改回原状）；点出滑坡的第一块石头是「示例文件里出现真值」。
2. 产出**完整环境变量清单**（18 行），三列分别是「有默认值 / 是密钥 / 该给谁」，并标出八个「无默认值」的变量构成第六节的必填清单。
3. 产出**多环境分层写法**：`profiles.group` 的档位组、`spring.config.import` 的三种来源（基线 / `.env` / `configtree`）、各档只写差异的两份档位文件，以及编排侧的 `env_file` + `secrets:` 片段。
4. 论证**`docker compose config` 会把展开后的密钥打印到标准输出**，给出四处不良写法与正确写法（`--no-interpolate` 查结构、`-q` 不打印），并产出**密钥四级落点表**（本地 `.env` / CI 变量 / 编排 secrets / 密钥管理服务）——每级给最小可用形态、轮换动作与不该用的场景，附 `.gitignore` + `git check-ignore` + `gitleaks` 三条可执行的前置检查。
5. 产出**四类启动期断言**（变量缺失 / 端口格式 / 密钥不足 32 字节 / 生产指向本机）与 Java 侧校验片段、失败时的预期输出，并论证「`UP` 但配置错」是最难被发现的一类故障。
6. 产出**三套环境的配置漂移对账命令**（变量名集合 / 非密钥取值 / 密钥存在性），列出三处「允许且应当不同」的差异，并产出 **`CF-A` ~ `CF-H` 八条判据**：七条文档级、本机可判，一条运行期如实标 `⏳`。

## 十、如何验证

### 10.1 判据定义表（`CF-A` ~ `CF-H`）

| 判据 | 判什么 | 怎么判 | 级别 | 状态 |
| --- | --- | --- | --- | --- |
| **`CF-A`** | 三分法三行齐全，且「泄漏后能否改回原状」这句判据在 | 10.2 第 1 组 `grep` | 文档级 | ✅ 本机可判 |
| **`CF-B`** | 环境变量清单 18 行，五列表头齐全 | 10.2 第 2 组 | 文档级 | ✅ 本机可判 |
| **`CF-C`** | 分层三要素齐全（档位组 / 导入来源 / `env_file` 与 `secrets:`） | 10.2 第 3 组 | 文档级 | ✅ 本机可判 |
| **`CF-D`** | `--no-interpolate` 与「日志里密钥字面值 0 命中」两条判据都在 | 10.2 第 4 组 | 文档级 | ✅ 本机可判 |
| **`CF-E`** | 四级落点四行齐全，且前置检查命令齐全 | 10.2 第 5 组 | 文档级 | ✅ 本机可判 |
| **`CF-F`** | 四类启动期断言齐全，Java 片段与预期输出都在 | 10.2 第 6 组 | 文档级 | ✅ 本机可判 |
| **`CF-G`** | 对账三组命令齐全，且密钥只比存在性 | 10.2 第 7 组 | 文档级 | ✅ 本机可判 |
| **`CF-H`** | 三套环境各起一次，且 CI 日志中密钥字面值命中为 0 | 10.3 的命令序列 | 运行期 | `⏳ 未跑 · 原因：本仓库无工程代码（BL-2），无法起本项目自己的栈` |

### 10.2 本机可判的部分

以下命令在 `ConfigSecrets/` 目录内执行，期望值均为本机实跑后回填：

```shell
# 1) CF-A：三分法三行 + 一句话判据
grep -cE '^\| \*\*(随镜像走的|随环境走的|密钥)' index.md           # 期望 3
grep -c '分不出来的值，一律当密钥处[理]' index.md                  # 期望 1
# 2) CF-B：清单表体行数（含表头与分隔行，第二节的表）
sed -n '/^## 二、/,/^::: tip/p' index.md | grep -c '^|'   # 期望 20
# 3) CF-C：分层三要素
grep -c '^    group:' index.md                                     # 期望 1
grep -c 'configtre[e]:/run/secrets/' index.md                      # 期望 4
grep -c '^    env_file:' index.md                                  # 期望 1
# 4) CF-D：两条判据都在
grep -c 'no-interpolat[e]' index.md                                # 期望 8
grep -c '密钥字面[值]' index.md                                     # 期望 6
# 5) CF-E：四级落点 + 前置检查
grep -cE '^\| \*\*L[1-4]\*\* \|' index.md                          # 期望 4
grep -c 'git check-ignore [-]v' index.md                           # 期望 1
grep -c 'gitleak[s]' index.md                                      # 期望 5
# 6) CF-F：四类断言 + 拒绝启动
grep -cE '^\| \*\*(变量缺失|端口格式错|签名密钥不足 32 字节|生产档位指向本机)' index.md   # 期望 4
grep -c '拒绝启[动]' index.md                                        # 期望 8
# 7) CF-G：对账三组命令（三份变量名清单 + 两次 diff）
grep -c '/tmp/names\.' index.md                                    # 期望 5
# 配图、判据族（声明表 8 行 + 定义表 8 行）
grep -c 'assets/tb-config-secrets.sv[g]' index.md                  # 期望 1
grep -cE '^\| \*\*`CF-[A-H]`\*\*' index.md                         # 期望 16
```

### 10.3 需要真实环境的部分

`CF-H` 的判据对象是**三套环境各自的容器栈**。本仓库按约定只有文档，因此如实标 `⏳ 未跑`，只给命令。注意原因**不是**「本机没有容器运行时」——本机 `docker` 客户端与服务端可用（`27.1.1`，compose `v2.29.1`，2026-10-17 复验，见 [第 3 周验收结论](../Week3Acceptance/index.md) 第三节）；真实原因是**本仓库无工程代码，无法起本项目自己的栈**。

```shell
# CF-H（需要：容器运行时 + 读者自己搭好的工程 + 三份取值不同的 .env）
for env in local staging prod; do
  docker compose --env-file ".env.$env" config --no-interpolate -q && echo "$env 编排结构 OK"
  docker compose --env-file ".env.$env" up -d db cache app
  curl -sf localhost:8080/actuator/health                       # 期望 {"status":"UP"}
  docker inspect --format '{{index .Config.Image}}' teamboard-app-1   # 三套应为同一 digest
done
JWT_SIGNING_KEY=short-key docker compose up app                 # 断言有效性：期望起不来（拒绝启动）
grep -cF "$(cat secrets/jwt_signing_key.txt)" ci-log.txt        # 日志里密钥字面值 0 命中
```

::: warning 状态列的读法
`CF-A` ~ `CF-G` 的期望值是**本机 `grep -c` 数出来的**，不是从模式里反推的。`CF-H` 的状态不是「结论」而是「当前可执行性」，它唯一的阻塞项与 [验收](../Acceptance/index.md) 的 `BL-2` 是同一条：**本仓库只有文档，没有可执行的工程**。**不把「设计完成」写成「跑过了」，也不把期望值抄进状态列。**
:::

## 十一、下一步

1. **配置怎么变，是发布动作的一部分**：[发布与回滚手册](../ReleaseRunbook/index.md) 会把「配置回退与镜像回退必须成对」写进回滚动作——`.env` 也是发布产物，只回滚镜像会把两套不一致的取值拼在一起。
2. **密钥轮换要有一次演练**：双密钥过渡的窗口（超过 `JWT_REFRESH_TTL` 才能摘旧密钥）是一条**必须实测**的判据，它与回滚演练同一批次做。
3. **配置项要进监控**：`resync_required`、出站队列深度、outbox 积压这几个量的采集口依赖配置（间隔、上限），相关接线落在 [监控与告警接入](../Monitoring/index.md)。

## 参考资料

- [环境与工程骨架](../Environment/index.md)（`compose.yaml` 与 `.env` 的完整内容、五类启动失败排查） · [第 3 周验收结论](../Week3Acceptance/index.md)（`BL-2` 口径与「本机具备 X 必须复验一次」的纪律）
- [发布与回滚手册](../ReleaseRunbook/index.md)（发布时配置怎么变、配置回退与镜像回退为什么必须成对） · [数据库设计](../Database/index.md)（连接串指向的 14 张表与迁移三分法）
- [Docker Compose 编排](/docs/Ops/Docker/DockerCompose/index.md)（`env_file` 与 `environment` 的优先级、`secrets:` 的语义） · [Compose 进阶](/docs/Ops/Docker/ComposeAdvanced/index.md)（多文件与多档位编排） · [密钥治理](/docs/Ops/SecurityHardening/SecretGovernance/index.md)（四级落法的方法论侧） · [Kubernetes ConfigMap 与 Secret](/docs/Ops/Kubernetes/ConfigMapSecret/index.md)（`configtree` 式挂载的同源做法）
- [JWT](/docs/Backend/Auth/Jwt/index.md)（HS256 与密钥长度要求的出处） · [部署脚本](../DeployScripts/index.md)（一键起时配置与密钥的注入位置）
