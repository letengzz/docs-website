### 版本选择
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

### 注册中心Nacos
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

### 配置中心Nacos
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


### SpringCloudGateway
[Gateway官网](https://spring.io/projects/spring-cloud-gateway)

> POM

```xml
 <dependency>
     <groupId>org.springframework.cloud</groupId>
     <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
```

### Sentinel
