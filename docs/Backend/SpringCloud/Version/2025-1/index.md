# Spring Cloud 2025.1.x（Oakwood，当前稳定版）

Spring Cloud **2025.1.x（代号 Oakwood）** 是 2026 年 9 月当前稳定版，配套 Spring Boot 4.0.x/4.1.x 与 Spring Framework 7。新项目、新功能一律面向此版本；除非团队生态明确不支持 Boot 4，不建议再以 2025.0.x 为基线。

::: info 版本现状（2026-09 核对）
2025.1.0 于 2025-11 发布，2025.1.2 起支持 Spring Boot 4.1.x，当前补丁版本已到 2025.1.3+。示例 BOM 版本建议取用发布页的最新 SR（Service Release）。
:::

## 与上一代（2025.0.x）的关键差异

| 维度 | 2025.0.x（Northfields） | 2025.1.x（Oakwood） |
| --- | --- | --- |
| Spring Boot | 3.5.x | 4.0.x / 4.1.x |
| Spring Framework | 6.2.x | 7.x |
| 主要组件版本 | Gateway 4.x、OpenFeign 4.x、Commons 4.x | Gateway 5.x、OpenFeign 5.x、Commons 5.x、LoadBalancer 5.x |
| JSON 默认库 | Jackson 2 | Jackson 3 |
| Jakarta | jakarta.*（与 Boot 3 相同） | jakarta.*，但内部 API 变化较多 |
| 已知注意点 | OSS 已结束（2026-06-30） | 部分三方 Starter 尚未适配 Boot 4，需先查兼容性 |

## 使用方式

在 Spring Boot 4.x 项目中引入 BOM 与所需启动器，组件版本一律不写：

```xml [pom.xml]
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.1.0</version>
    <relativePath/>
</parent>

<properties>
    <spring-cloud.version>2025.1.3</spring-cloud.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <!-- 示例：只引入用到的组件 -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-loadbalancer</artifactId>
    </dependency>
</dependencies>
```

## 本 Train 组件版本速查（以 2025.1.0 发布说明为准）

| 组件 | 版本线 | 说明 |
| --- | --- | --- |
| Spring Cloud Commons | 5.0.x | 公共抽象，含 LoadBalancer API |
| Spring Cloud OpenFeign | 5.0.x | 声明式 HTTP 客户端 |
| Spring Cloud Gateway | 5.0.x | 基于 Spring WebFlux/Netty |
| Spring Cloud Config | 5.0.x | 集中配置服务端/客户端 |
| Spring Cloud LoadBalancer | 5.0.x | 客户端负载均衡 |
| Spring Cloud Circuit Breaker | 3.x | Resilience4j 集成 |
| Spring Cloud Stream | 5.0.x | 函数式消息驱动 |
| Spring Cloud Bus | 5.0.x | 消息广播刷新 |
| Spring Cloud Consul / Zookeeper / Netflix | 5.0.x | 注册发现适配 |

::: warning 与 Boot 4.1 的配合
Spring Cloud 官方文档说明：**2025.1.2 起**才支持 Spring Boot 4.1.x。若项目锁定 Boot 4.1，请使用 2025.1.2 及之后的 BOM，不要停留在 2025.1.0。
:::

## Spring Cloud Alibaba 配套

使用 Nacos/Sentinel/Seata 时，版本以 **Spring Cloud Alibaba（SCA）官方映射**为准，而非直接按 Spring Cloud Train 判断：

| SCA 版本 | Spring Cloud | Spring Boot | Nacos | Sentinel | Seata |
| --- | --- | --- | --- | --- | --- |
| 2025.1.0.0 | 2025.1.0 | 4.0.0 | 3.1.1（客户端） | 1.8.9 | 2.5.0 |
| 2025.0.0.0 | 2025.0.0 | 3.5.0 | 3.0.3（客户端） | 1.8.9 | 2.5.0 |

来源：阿里云 Spring Cloud Alibaba 官方版本说明（2026-09 核对）。

::: danger SCA 与 Boot 4.1 注意点
1. SCA 2025.1.0.0 的官方映射目前标注 Spring Boot 4.0.0；若升级 Boot 4.1，请先在官方 Issue/发布说明确认对应 SCA 补丁，再整体升级。
2. **bootstrap 配置已移除**：SCA 2025.x 起不再读取 `bootstrap.yml`，Nacos 配置改由 `spring.config.import` 导入（详见 [配置中心](../../ConfigCenter/index.md)）。
3. Nacos 配置默认关闭 actuator 健康指示器，注册健康状态需自行检查，别误以为“没输出就是没连上”。
:::

## 从 2025.0.x 升级到 2025.1.x

升级路径建议先升 Spring Cloud，再升 Spring Boot：

1. 全量替换 BOM：`spring-cloud.version` 从 2025.0.x 改为 2025.1.2+。
2. 更新 Spring Boot 父 POM/依赖到 4.0.x（再逐步 4.1.x）。
3. 编译器升级：JDK 17 起步，推荐 JDK 25 LTS（见本库 [Java 版本现状](../../../Java/JavaSE/Overview/index.md)）。
4. 检查依赖冲突：Gateway 5.x / OpenFeign 5.x 内部 API 变化，若有自定义 Filter、`RequestInterceptor` 等扩展点，重点回归测试。
5. 若用 Jackson 3：检查 `ObjectMapper` 相关配置与自定义序列化器。
6. 跑全量测试并灰度：优先在分支环境验证，再逐步上线。

## 验证方式

1. `mvn dependency:tree | findstr spring-cloud`：确认所有 `spring-cloud-*` 都由 2025.1.x BOM 管理且无重复版本。
2. 启动应用，观察日志出现 `Spring Cloud ... 2025.1.x` 与对应的自动配置生效信息。
3. 通过网关调用业务接口，并用 `/actuator/health`、`/actuator/gateway/routes` 确认组件健康。

## 参考资料

- Spring Cloud 官方发布页：https://spring.io/projects/spring-cloud
- Spring Cloud 2025.1.0 发布公告：https://spring.io/blog/2025/11/25/spring-cloud-2025-1-0-aka-oakwood-has-been-released
- Spring Cloud Alibaba 版本说明：https://sca.aliyun.com/docs/2025.x/overview/version-explain/
