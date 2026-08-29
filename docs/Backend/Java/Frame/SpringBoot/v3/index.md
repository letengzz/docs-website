# SpringBoot 3

![image-20230722002105472](assets/202307220027897.png)

通用指南见 [Spring Boot 通用指南](../Common/index.md)。

- [SpringBoot 介绍](Overview.md)

> SpringBoot 介绍：时代背景(微服务、分布式、云原生)、Spring生态、SpringBoot优点、SpringBoot缺点、SpringBoot3介绍

- [SpringBoot 构建入门程序](BasicProgram.md)

> SpringBoot 构建入门程序：构建项目(使用Maven父工程构建、使用Maven依赖管理器构建、使用Spring Initailizr构建)、创建主程序类、创建业务层、测试运行、配置参数、部署运行

- [SpringBoot 依赖管理和自动配置](FeaturesConfiguration.md)

> SpringBoot 依赖管理：作为父项目和作为依赖的区别、自动版本仲裁、修改仲裁版本、starter场景启动器
>
> SpringBoot 自动配置：自动配置Tomcat、自动配置SpringMVC、包扫描路径、自动配置 配置默认值、按需加载所有自动配置项、自动配置流程

- [SpringBoot 常用注解](Annotation.md)

> SpringBoot 常用注解：`@SpringBootApplication`注解、组件注册(`@Configuration`、`@SpringBootConfiguration`、`@Bean`、`@Scope`、`@Controller`、 `@Service`、`@Repository`、`@Component`、`@Import`、`@ComponentScan`、`@ImportResource`)、条件注解(`@ConditionalOnXxx`)、属性绑定(`@ConfigurationProperties`、`@EnableConfigurationProperties`)

- [SpringBoot 基本操作及特性](BasisOperation.md)

> SpringBoot 基本操作及特性：配置文件、自定义Bean设置、自定义banner、自定义SpringApplication、FluentBuilder API、环境隔离 Profiles、外部化配置、日志配置、时间格式统一

- [SpringBoot Web开发](Web/index.md)

> SpringBoot web开发：SpringMVC自动配置、默认效果、WebMvcAutoConfiguration原理、静态资源资源访问、路径匹配、内容协商、Restful请求、视图解析与模板引擎、国际化、文件上传、拦截器、异常处理、嵌入式容器、全面接管SpringMVC(手动管理SpringMVC)、开发模式、Web新特性(Problemdetails、函数式Web)

- [SpringBoot 数据访问](DataAccess/index.md)

> SpringBoot 数据访问：使用Spring Data JPA、使用MyBatis、使用MyBatis-Plus

- [SpringBoot 远程调用](Remote/index.md)

> SpringBoot 远程调用：RestTemplate、WebClient、Http Interface

- [SpringBoot 核心原理](CorePrinciple.md)

> SpringBoot 核心原理：事件和监听器、自动配置原理、自定义starter

- [SpringBoot 可观测性](Observability.md)

> SpringBoot 可观测性：SpringBoot Actuator、基于Prometheus+Grafana监控

- [SpringBoot 提前编译AOT](AOT.md)

> SpringBoot 提前编译(AOT)：JIT与AOT的区别、编译器与解释器、AOT的优缺点、JVM架构、Java执行过程、JVM编译器、分层编译云原生、Native Images构建过程、GraalVM、操作过程、Linux平台测试、SpringBoot整合、常见问题

- [SpringBoot 项目打包和运行](PackageAndRun.md)

> SpringBoot 项目打包和运行：添加打包插件、执行打包、命令启动和参数说明

- [SpringBoot 整合框架](Integration/index.md)

> SpringBoot 整合框架：整合MyBatis、整合 Junit、整合Druid、整合Swagger

**拓展**：

- [SpringBoot3改变 & 新特性](Diff.md)
- [Thymeleaf 视图模板](Integration/Thymeleaf/index.md)
- [SpringBoot 邮件发送](Email.md)
- [SpringBoot Docker编排支持](DockerComposeSupport.md)
- [SpringBoot 重试](Retry.md)
