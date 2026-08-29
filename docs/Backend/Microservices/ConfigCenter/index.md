# 配置中心

配置中心（Config Center）把**配置从代码里抽离出来集中管理，并在运行时动态下发**。微服务数量一多，散落在每个服务里的 `application.yml` 会成为噩梦：改一个数据库地址要逐个服务改、逐个重启；线上问题排查时不知道线上到底跑的是什么配置。配置中心就是解决这个问题的统一配置管理系统。

## 为什么需要配置中心

单体时代一个配置文件就够；微服务时代配置管理面临：

| 问题 | 说明 |
| --- | --- |
| 配置分散 | 几十个服务各自维护配置文件，口径不一致 |
| 修改成本高 | 改一处公共配置要改 N 个服务 |
| 不能动态生效 | 改配置必须重启，线上成本高 |
| 环境混乱 | dev/test/prod 配置容易串 |
| 无审计 | 谁改了什么、什么时候改的没有记录 |
| 安全风险 | 数据库密码、密钥明文躺在代码仓库里 |

## 配置中心的核心能力

1. **集中存储**：所有服务的配置放在一起，按服务 + 环境 + 分组管理。
2. **动态下发**：配置变更后推送到客户端，**无需重启**即可生效。
3. **环境隔离**：dev / test / prod 环境配置隔离，避免串环境。
4. **版本回滚**：每次变更留版本，出错一键回滚。
5. **权限与审计**：谁改的、改了什么有记录；敏感配置加密。
6. **灰度发布**：先推给部分实例验证，再全量推送。

## 主流实现

| 组件 | 特点 | 说明 |
| --- | --- | --- |
| Nacos Config | 注册中心 + 配置中心一体 | 中文文档全、动态刷新开箱即用，国内主流 |
| Spring Cloud Config | 配合 Git 仓库存配置 | 基于 Git 做版本管理，天然可审计可回滚 |
| Apollo（携程） | 专做配置中心 | 功能强大（灰度、权限、审计），Java 生态 |
| Consul KV | 分布式 KV | 与 Consul 注册中心一起用 |
| K8s ConfigMap/Secret | 容器平台原生 | 与 Helm/Kustomize 配合，云原生标配 |

## Nacos Config 快速上手

沿用注册中心章节的 Nacos 环境，加入配置中心依赖：

```xml [pom.xml]
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

### 配置 Data ID 规则

Nacos 中一个配置的唯一标识 Data ID 默认规则：

```text
${spring.application.name}-${spring.profiles.active}.${file-extension}
示例：order-service-prod.yaml
```

### 在 Nacos 控制台新建配置

Data ID：`order-service.yaml`

```yaml
server:
  port: 8081
order:
  timeout: 30
  max-retry: 3
```

### 服务端读取

```yaml [application.yml]
spring:
  application:
    name: order-service
  config:
    import: optional:nacos:order-service.yaml   # Spring Cloud 2020+ 写法
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        file-extension: yaml
```

::: info 关于 bootstrap.yml
Spring Cloud 2020.x 起默认不再使用 `bootstrap.yml` 加载配置，推荐用 `spring.config.import`。若使用旧版（2020 之前）或显式开启，才需要 `bootstrap.yml` + `spring-cloud-starter-bootstrap`。
:::

### 动态刷新

配置变更默认推送给客户端，但**已经注入到 Bean 的属性不会自动更新**，需要加 `@RefreshScope`：

```java
@RestController
@RefreshScope
public class OrderConfigController {
    @Value("${order.timeout:30}")
    private int timeout;

    @GetMapping("/config/timeout")
    public int timeout() {
        return timeout;
    }
}
```

在 Nacos 控制台把 `order.timeout` 从 30 改为 60 并发布，**不重启服务**，请求 `/config/timeout` 应返回 60。

## 配置分层与优先级

Spring Cloud 的配置优先级（从高到低）：

```text
命令行参数 > Java 系统属性 > 环境变量 > Nacos 远端配置 > 本地 application.yml > 默认值
```

推荐实践：

- **常变配置**（开关、阈值、灰度比例）放 Nacos，动态刷新。
- **环境相关**（数据源地址、日志级别）放 Nacos 按环境隔离。
- **稳定配置**（应用名、端口等）保留在本地文件兜底。

## 敏感配置加密

::: danger 禁止明文密钥入库
1. 数据库密码、Redis 密码、私钥不要明文写在 Nacos/配置文件里。
2. 方案一：Jasypt 加密配置值，启动时解密。
3. 方案二：对接 KMS/Vault 动态取密钥。
4. 方案三：K8s 场景用 Secret + 外部 Secrets Operator。
:::

Jasypt 示例：

```yaml
spring:
  datasource:
    password: ENC(加密后的密文)
jasypt:
  encryptor:
    password: ${JASYPT_SECRET}   # 解密密钥来自环境变量，不进代码库
```

## 配置灰度与回滚

### Nacos 灰度

1. 发布配置时勾选「Beta 发布」。
2. 填写 Beta IP 列表（如 10.0.0.11）。
3. 只有该 IP 的实例收到新配置，验证通过后全量发布。

### 回滚

1. 在配置详情页查看「历史版本」。
2. 选择要回滚的版本，执行回滚。
3. 客户端会自动收到旧版本配置（如果 `@RefreshScope` 生效）。

## 易错点与最佳实践

::: danger 常见错误
1. **只存不刷**：配置放上去了，但 Bean 没加 `@RefreshScope`，改了不生效。
2. **不配置兜底**：`spring.config.import` 不带 `optional:` 时，Nacos 不可用服务起不来；应评估是否需要启动兜底。
3. **本地配置覆盖远端**：以为在 Nacos 改了，实际本地 `application.yml` 优先级高，改了不生效。
4. **全量配置都放 Nacos**：启动依赖远端、本地无兜底，注册中心抖动整站起不来。
5. **密钥明文入库**：密码直接写配置，泄露即事故。
6. **不同环境共用 Data ID**：dev 和 prod 用一个配置，改一次全部生效，线上事故隐患。
:::

::: tip 最佳实践
1. 按 `服务-环境.yaml` 命名，配置内容分组：业务开关 / 中间件连接 / 日志级别。
2. 公共配置（如公共 Redis）用 shared-configs 共享，避免重复。
3. 上线前做「配置演练」：改配置 → 观察动态生效 → 回滚。
4. 把配置变更纳入发布单，回滚应用和回滚配置要能联动。
5. 敏感配置单独管理并加密，密钥放环境变量或 KMS。
:::

## 验证方式

1. 启动服务，确认控制台日志显示从 Nacos 拉取配置成功。
2. 修改 Nacos 配置并发布，不重启调用接口验证新值生效。
3. 模拟 Nacos 不可用（停容器），确认服务按兜底配置启动或明确失败，符合预期。
4. 做一次 Beta 发布 + 全量发布 + 回滚演练。

## 参考资料

- Nacos 配置管理文档：https://nacos.io/en/docs/latest/configuration/
- Spring Cloud Config 文档：https://docs.spring.io/spring-cloud-config/reference/
- Spring Cloud 外部化配置：https://docs.spring.io/spring-boot/reference/features/external-config.html
- Apollo 配置中心：https://www.apolloconfig.com/
- Jasypt Spring Boot：https://github.com/ulisesbocchio/jasypt-spring-boot
