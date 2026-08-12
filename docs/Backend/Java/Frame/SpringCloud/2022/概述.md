##  Spring Cloud简介

Spring Cloud是Spring提供的微服务框架。它利用Spring Boot的开发特性简化了微服务开发的复杂性，例如：**服务发现注册**、**配置中心**、**消息总线**、**负载均衡**、**断路器**、**数据监控**等，这些工作都可以借助Spring Boot的开发风格做到一键启动和部署。

Spring Cloud的目标是通过一系列组件(一系列框架的有序集合)，帮助开发者快速构建出在任何环境下的分布式系统，包括开发人员自己的笔记本电脑、裸机数据中心和云计算等托管平台。Spring Cloud 是通过包装其它公司产品来实现的，比如Spring Cloud整合了开源的Netflix很多产品。Spring Cloud提供了微服务治理的诸多组件，例如：**服务注册和发现**、**配置中心**、**熔断器**、**智能路由**、**微代理**、**控制总线**、**一次性令牌**、**全局锁**、**分布式会话**、**集群状态**等。Spring Cloud组件非常多，涉及微服务开发的诸多场景。

**Git源码地址**：https://github.com/spring-cloud

**官方文档**：https://spring.io/projects/spring-cloud#overview

**Spring Cloud的架构图**：

![image-20240117224806591](https://fastly.jsdelivr.net/gh/LetengZzz/img@main/tc2/img202401172248753.png)

![image.png](https://fastly.jsdelivr.net/gh/LetengZzz/img@main/Two-C/img/Java/202303271139276.png)

![image_rR3xK4zw_I](https://fastly.jsdelivr.net/gh/LetengZzz/img@main/tc2/img/202310051300183.png)

Spring Cloud实现微服务的治理功能产品很多，Spring Cloud各个产品的作用，以及采用的原则：

![image-20240302123331979](https://fastly.jsdelivr.net/gh/LetengZzz/img@main/tc2/img202403021234040.png)

例：基于Netflix（奈飞）的开源分布式解决方案提供的组件：

- Eureka：实现服务治理(服务注册与发现)，可以对所有的微服务进行集中管理，包括他们的运行状态、信息等。
- Ribbon：为服务之间相互调用提供负载均衡算法（现在被SpringCloudLoadBalancer取代）
- Hystrix：断路器，保护系统，控制故障范围。暂时可以跟家里电闸的保险丝类比，当触电危险发生时能够防止进一步的发展。
- Zuul：api网关，路由，负载均衡等多种作用，就像路由器，可能有很多个设备都连接了路由器，但是数据包要转发给谁则是由路由器在进行（已经被SpringCloudGateway取代）
- Config：配置管理，可以实现配置文件集中管理

****

Spring Boot 为 Spring Cloud 提供了代码实现环境，使用 Spring Boot 将其它组件有机融合 到了 Spring Cloud 的体系架构中了。所以说，Spring Cloud 是基于 Spring Boot 的、微服务系统架构的一站式解决方案。

**Spring Cloud命名规则**：

Spring Cloud 采用了英国伦敦地铁站的名称来命名，并由地铁站名称字母A-Z依次类推的形式来发布迭代版本

Spring Cloud是一个由许多子项目组成的综合项目，各子项目有不同的发布节奏。为了管理Spring Cloud与各子项目的版本依赖关系，发布了一个清单，其中包括了某个Spring Cloud版本对应的子项目版本。为了避免Spring Cloud版本号与子项目版本号混淆，SpringCloud版本采用了名称而非版本号的命名，这些版本的名字采用了伦敦地铁站的名字，根据字母表的顺序来对应版本时间顺序。例如Angel是第一个版本, Brixton是第二个版本。

当SpringCloud的发布内容积累到临界点或者一个重大BUG被解决后，会发布一个"service releases"版本，简称SRX版本，比如Greenwich.SR2就是SpringCloud发布的Greenwich版本的第2个SRX版本。

![image-20240405152616569](https://fastly.jsdelivr.net/gh/LetengZzz/img@main/tc2/img202404051526584.png)

**Spring Cloud 和Spring Boot版本对应关系**：

| Spring Cloud                                                 | Spring Boot                           |
| ------------------------------------------------------------ | ------------------------------------- |
| [2022.0.x](https://github.com/spring-cloud/spring-cloud-release/wiki/Spring-Cloud-2022.0-Release-Notes) aka Kilburn | 3.0.x                                 |
| [2021.0.x](https://github.com/spring-cloud/spring-cloud-release/wiki/Spring-Cloud-2021.0-Release-Notes) aka Jubilee | 2.6.x, 2.7.x (Starting with 2021.0.3) |
| [2020.0.x](https://github.com/spring-cloud/spring-cloud-release/wiki/Spring-Cloud-2020.0-Release-Notes) aka Ilford | 2.4.x, 2.5.x (Starting with 2020.0.3) |
| [Hoxton](https://github.com/spring-cloud/spring-cloud-release/wiki/Spring-Cloud-Hoxton-Release-Notes) | 2.2.x, 2.3.x (Starting with SR5)      |
| [Greenwich](https://github.com/spring-projects/spring-cloud/wiki/Spring-Cloud-Greenwich-Release-Notes) | 2.1.x                                 |
| [Finchley](https://github.com/spring-projects/spring-cloud/wiki/Spring-Cloud-Finchley-Release-Notes) | 2.0.x                                 |
| [Edgware](https://github.com/spring-projects/spring-cloud/wiki/Spring-Cloud-Edgware-Release-Notes) | 1.5.x                                 |
| [Dalston](https://github.com/spring-projects/spring-cloud/wiki/Spring-Cloud-Dalston-Release-Notes) | 1.5.x                                 |

官网对版本进行解释：

- Spring Cloud Dalston, Edgware, Finchley, and Greenwich have all reached end of life status and are no longer supported.

  Spring Cloud Dalston、Edgware、Finchley 和 Greenwich 都已达到生命周期终止状态，不再受支持
