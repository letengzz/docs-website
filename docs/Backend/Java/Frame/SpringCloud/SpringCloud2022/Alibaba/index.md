::: info 版本与维护状态

本页是 **Spring Cloud 2022（Kilburn 线，配套 Spring Boot 3.x / Spring Cloud Alibaba 2022.x）** 对应的 Spring Cloud Alibaba 组件速览（Nacos / Sentinel / Seata），为存量教程内容（**仅存量项目使用**）。版本号以页面内表格为准，不再随新版本更新；新项目请阅读 [Spring Cloud 完整专题](../../../index.md)。

:::

# 版本选择
- [SpringCloud](https://spring.io/projects/spring-cloud/#learn)
- [SpringCloud与SpringCloudAlibaba 版本选择](https://github.com/alibaba/spring-cloud-alibaba/wiki/%E7%89%88%E6%9C%AC%E8%AF%B4%E6%98%8E)
- [SpringCloud与SpringBoot版本选型](https://start.spring.io/actuator/info)

| type | version |
| --- | --- |
| SpringCloud | 2020.0.6 |
| SpringCloudAlibaba | 2021.1 |
| SpringBoot | 2.4.13 |
| Nacos | 1.4.1 |
| Sentinel | 1.8.0 |
| Seate | 1.3.0 |

## 注册中心Nacos
[Nacos](https://nacos.io/zh-cn/)
> POM

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
<!--当使用服务名作为域名来调用其他服务的接口时，当前版本需要引入loadbalancer，无论是使用feign或者时RestTemplate-->
<!--当注入RestTemplate时需要在方法上添加注解@LoadBalanced-->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-loadbalancer</artifactId>
</dependency>
```
> 配置

```yaml
spring:
  cloud:
    nacos:
      server-addr: localhost:8848
      discovery:
        namespace: alibaba
        group: shop-server
```

## 配置中心Nacos
> POM

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
<!--配置中心的配置需要再bootstrap中配置才能生效，而bootstrap需要添加以下依赖才能生效-->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-bootstrap</artifactId>
</dependency>
```
> 配置

```yaml
spring:
  application:
    name: order-server
  profiles:
    active: dev  
  cloud:
    nacos:
      server-addr: localhost:8848
      discovery:
        namespace: alibaba
        group: shop-server
      config:
        namespace: alibaba
        group: shop-server
        file-extension: yaml    # 默认配置项：order-server-dev.yaml
        refresh-enabled: true   # 开启配置动态刷新 需要配合注解@RefreshScope使用
        extension-configs:
          - data-id: all-config.yaml
            group: common-server
            refresh: true #单独配置该配置项 是否开启动态刷新机制，需要配置注解@RefreshScope使用
        shared-configs:
          - data-id: shared-config.yaml
            group: common-server
            refresh: true
```
> **本地配置优先**
> 原因：使用配置中心时，如果配置中心的配置和本地配置重复，默认使用配置中心的配置，要是需要本地配置优先，则需要在配置中设置spring.cloud.config.override-none=true

```yaml
#配置本地优先
spring:
 cloud:
  config:
    override-none: true
```
> **动态刷新配置**
①配置项 spring.cloud.nacos.config.refresh-enabled设置为true 影响所有的配置项是否可以动态刷新，且需要@RefreshScope配置使用
②@RefreshScope注解标识在类上可以让该类中通过@Value获取的配置动态刷新
③@ConfigurationProperties注解标识的类无需使用@RefreshScope注解即可动态刷新配置
**注意**：在配置文件中有all-config时，则@Value("${all-config}")可取得配置内容，而@ConfigurationProperties注解标识的类则可以通过属性allConfig获取配置内容


> **同一服务不同环境的公共配置**
假设服务名为order-server,扩展名为yaml，
则同一服务不同环境下的公共配置为order-server.yaml
即：spring.application.name.yaml 为同一服务在不同环境下的公共配置


> **如果配置了spring.profile.active，有一个配置项在三种配置文件（demo-dev.yaml 、common.yaml 、demo.yaml）中存在且值不同，最终哪一个生效？**
配置了spring.profile.active，则demo-${spring.profile.active}.yaml生效


> **跨服务公共配置**
跨服务公共配置可以通过spring.cloud.nacos.config.extension-configs 和 spring.cloud.nacos.config.shared-configs配置
extension-configs和shared-configs都需要设置三个属性(dataId,group,refresh)


> **配置文件优先级**
`bootstrap.properties > bootstrap.yaml > application.properties > application.yaml`


> **如果多个shared-configs(extension-configs)的文件中存在相同的配置，最终会以哪个配置文件中的值为准？**
以列表中最后一个有相同配置的文件为准


> **如果同时在extension-configs和shared-configs存在相同配置，最终会以哪个文件中的值为准？**
以extension-configs中的配置为准


> **总结下demo.yaml、demo-dev.yaml和shared-configs、extension-configs读取优先级**
demo-dev.yaml > demo.yaml > extension-configs > shared-configs


## SpringCloudGateway
[Gateway官网](https://spring.io/projects/spring-cloud-gateway)

> POM

```xml
 <dependency>
     <groupId>org.springframework.cloud</groupId>
     <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

## Sentinel

> 本页配套 **Spring Boot 3.x / Spring Cloud 2022**，命名空间为 `jakarta.*`。
>
> **升级提示**：Boot 3 下务必使用 `spring-cloud-alibaba 2022.x` 提供的 Sentinel starter，**不要手动引入旧版 `sentinel-core` / `sentinel-spring-webmvc-adapter`**。旧版适配器依赖 `javax.servlet.*`，与 Boot 3 的 `jakarta.servlet.*` 不兼容，会在启动时抛 `ClassNotFoundException` 或拦截器不生效。

Sentinel 是阿里开源的**流量治理**组件，核心作用是把「不稳定」挡在业务代码之外。它与网关的职责边界是：

- 网关（SpringCloudGateway / Nginx）做**南北向**入口的限流与路由
- Sentinel 做**东西向**服务间调用的限流、熔断、系统自适应保护

### 三个核心概念

| 概念 | 含义 |
| --- | --- |
| 资源（Resource） | 被保护的逻辑单元，可以是一个方法、一个接口，也可以是整段代码块 |
| 规则（Rule） | 作用在资源上的策略，包括流控、熔断降级、系统保护、热点参数、授权 |
| 插槽链（Slot Chain） | 责任链模式，每个 Slot 负责一类职责（统计、限流、熔断……），按固定顺序执行 |

### 接入步骤

1. 引入依赖（版本由父 `pom` 的 `spring-cloud-alibaba-dependencies` 统一管理，**不要手写版本号**）：

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
```

2. 配置控制台地址：

```yaml
spring:
  cloud:
    sentinel:
      transport:
        dashboard: 127.0.0.1:8858   # Sentinel 控制台地址
        port: 8719                  # 与控制台通信的本地端口，被占用会自动 +1
      eager: true                   # 取消懒加载，启动即注册到控制台
```

Sentinel 控制台需要单独下载启动：

```bash
# 下载 sentinel-dashboard-1.8.6.jar 后启动
java -Dserver.port=8858 -Dcsp.sentinel.dashboard.server=localhost:8858 \
     -jar sentinel-dashboard-1.8.6.jar
# 默认账号密码均为 sentinel
```

> **注意**：`dashboard` 是「上报 + 规则下发」的地址。`eager: false`（默认）时资源要**被访问过一次**才会出现在控制台里，新手常误以为接入失败。

### 代码方式定义资源

```java
@RestController
public class OrderController {

    // value 即资源名；blockHandler 处理被限流/降级后的返回
    @SentinelResource(value = "createOrder", blockHandler = "handleBlock")
    @GetMapping("/order/{id}")
    public String createOrder(@PathVariable Long id) {
        return "order-" + id;
    }

    // 方法签名 = 原方法参数 + BlockException，返回值类型一致
    public String handleBlock(Long id, BlockException ex) {
        return "请求过于频繁，请稍后再试";
    }
}
```

### 流控（限流）规则四种模式

| 模式 | 说明 |
| --- | --- |
| 直接 | 资源自身达到阈值就限流 |
| 关联 | 关联资源达到阈值时，限流当前资源（如「下单」压力大时限制「查询」） |
| 链路 | 只统计从指定入口进来的调用（需配置 `web-context-unify: false`） |
| 热点参数 | 对参数中的某个值单独限流（如某个商品 ID 被刷接口） |

**QPS 还是线程数**：Web 场景通常用 QPS；对「慢调用」敏感的场景用线程数更准确，因为线程被占满才是真正的过载。阈值类型选错，限流会「看起来生效但没保护住」。

### 熔断降级三种策略

| 策略 | 触发条件 |
| --- | --- |
| 慢调用比例 | 响应时间超过阈值的请求占比达标，且请求数超过最小请求数 |
| 异常比例 | 异常请求占比达标 |
| 异常数 | 异常数量达标 |

熔断器有三个状态：`CLOSED`（正常）→ `OPEN`（熔断，直接拒绝）→ `HALF_OPEN`（试探，放一个请求过去看是否恢复）。半开状态下试探成功则闭合，失败则继续熔断。

### 规则持久化

控制台默认把规则存在**内存**里，重启即丢失。生产必须做持久化：

```yaml
spring:
  cloud:
    sentinel:
      datasource:
        flow:
          nacos:
            server-addr: 127.0.0.1:8848
            data-id: ${spring.application.name}-flow-rules
            group-id: SENTINEL_GROUP
            rule-type: flow
        degrade:
          nacos:
            server-addr: 127.0.0.1:8848
            data-id: ${spring.application.name}-degrade-rules
            group-id: SENTINEL_GROUP
            rule-type: degrade
```

### 与 Spring Cloud Gateway 协作时的一个坑

Gateway 基于 WebFlux（响应式），与 Spring MVC 的 Servlet 拦截器不是同一套。在网关里接入 Sentinel 要用 **`spring-cloud-alibaba-sentinel-gateway`**，它提供的是 `SentinelGatewayFilter` 与 `GatewayFlowRule`，而**不是** `@SentinelResource` 注解那一套。

```xml
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-alibaba-sentinel-gateway</artifactId>
</dependency>
```

### 常见坑

1. **`blockHandler` 方法必须在同一个类里**，且参数列表 = 原方法参数 + `BlockException`，返回值类型一致，否则会走 `NoSuchMethodException` 兜底。
2. **同时标注 `@SentinelResource` 与 `@GetMapping` 时，生效的资源名是 `@SentinelResource` 的 `value`**；只标 `@GetMapping` 也能被保护，但资源名是 URL 路径，规则不好维护。
3. **`exceptionsToIgnore`**：不配置的话，业务异常也会被计入统计，导致熔断误触发。
4. **滑动窗口边界**：默认 1 秒窗口，秒杀类场景流量在窗口交界处「双倍通过」属于正常现象；需要更严格时改用匀速排队（漏桶）模式。

### 与网关限流的分工

| 位置 | 组件 | 解决的问题 |
| --- | --- | --- |
| 南北向入口 | SpringCloudGateway + `RequestRateLimiter` | 抵挡外部洪峰，保护整个集群 |
| 东西向服务间 | Sentinel | 保护单个服务不被下游拖垮，防止雪崩 |

两者不冲突：网关限流是「第一道闸门」，Sentinel 是「每个服务自己的保险丝」。网关侧更完整的流量治理见 [GatewayDeep 网关深入](../../../../../GatewayDeep/index.md)。
