// .Net
export const DotNet = [
  {
    text: ".NET",
    link: "/docs/Backend/DotNet/index.md",
    items: [
      {
        "link": "/docs/Backend/DotNet/Basic/index.md",
        "text": ".NET 基础语法"
      },
      {
        "link": "/docs/Backend/DotNet/Advanced/index.md",
        "text": "进阶语法"
      },
      {
        "link": "/docs/Backend/DotNet/DotNet5/index.md",
        "text": ".Net5"
      },
      {
        "link": "/docs/Backend/DotNet/WebApiNet6/index.md",
        "text": "WebApi-Net6"
      },
    ]
  }
];
export const Java = [
  {
    text: "Java",
    link: "/docs/Backend/Java/index.md",
    items: [
      {
        text: "JavaSE",
        link: "/docs/Backend/Java/JavaSE/index.md",
        collapsed: true,
        items: [
          { text: "Java 概述", link: "/docs/Backend/Java/JavaSE/Overview/index.md" },
          { text: "环境搭建", link: "/docs/Backend/Java/JavaSE/Environment/index.md" },
          { text: "基础语法", link: "/docs/Backend/Java/JavaSE/BasicSyntax/index.md" },
          { text: "面向对象", link: "/docs/Backend/Java/JavaSE/ObjectOriented/index.md" },
          { text: "面向对象核心（OOP）", link: "/docs/Backend/Java/JavaSE/OOP/index.md" },
          { text: "常用类", link: "/docs/Backend/Java/JavaSE/CommonClasses/index.md" },
          {
            text: "集合框架",
            link: "/docs/Backend/Java/JavaSE/Collection/index.md",
            collapsed: true,
            items: [
              { text: "集合框架总览", link: "/docs/Backend/Java/JavaSE/Collection/Overview/index.md" },
              { text: "List 接口与实现", link: "/docs/Backend/Java/JavaSE/Collection/List/index.md" },
              { text: "Set 接口与实现", link: "/docs/Backend/Java/JavaSE/Collection/Set/index.md" },
              { text: "Map 接口与实现", link: "/docs/Backend/Java/JavaSE/Collection/Map/index.md" },
              { text: "迭代与遍历", link: "/docs/Backend/Java/JavaSE/Collection/Iteration/index.md" },
              { text: "排序与比较器", link: "/docs/Backend/Java/JavaSE/Collection/SortCompare/index.md" },
              { text: "并发集合", link: "/docs/Backend/Java/JavaSE/Collection/Concurrent/index.md" },
              { text: "源码要点", link: "/docs/Backend/Java/JavaSE/Collection/Source/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/Backend/Java/JavaSE/Collection/FAQ/index.md" },
            ],
          },
          {
            text: "IO / NIO",
            link: "/docs/Backend/Java/JavaSE/IO/index.md",
            collapsed: true,
            items: [
              { text: "文件 IO：File 与 Path/Files", link: "/docs/Backend/Java/JavaSE/IO/FileIO/index.md" },
              { text: "字节流：InputStream 与 OutputStream", link: "/docs/Backend/Java/JavaSE/IO/ByteStream/index.md" },
              { text: "字符流：Reader 与 Writer", link: "/docs/Backend/Java/JavaSE/IO/CharacterStream/index.md" },
              { text: "NIO 核心概念", link: "/docs/Backend/Java/JavaSE/IO/NIO/index.md" },
              { text: "Channel 与 Buffer 详解", link: "/docs/Backend/Java/JavaSE/IO/ChannelBuffer/index.md" },
              { text: "Selector 与多路复用", link: "/docs/Backend/Java/JavaSE/IO/Selector/index.md" },
              { text: "网络 IO 模型：BIO/NIO/AIO", link: "/docs/Backend/Java/JavaSE/IO/NetworkIO/index.md" },
              { text: "实战：NIO 文件传输服务器", link: "/docs/Backend/Java/JavaSE/IO/Practice/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/Backend/Java/JavaSE/IO/FAQ/index.md" },
            ],
          },
          {
            text: "反射与注解",
            link: "/docs/Backend/Java/JavaSE/Reflection/index.md",
            collapsed: true,
            items: [
              { text: "反射概述与 Class 对象", link: "/docs/Backend/Java/JavaSE/Reflection/Overview/index.md" },
              { text: "字段与方法反射", link: "/docs/Backend/Java/JavaSE/Reflection/FieldsMethods/index.md" },
              { text: "构造器与对象创建", link: "/docs/Backend/Java/JavaSE/Reflection/Constructor/index.md" },
              { text: "动态代理", link: "/docs/Backend/Java/JavaSE/Reflection/DynamicProxy/index.md" },
              { text: "注解：定义与使用", link: "/docs/Backend/Java/JavaSE/Reflection/Annotation/index.md" },
              { text: "注解处理器（APT）", link: "/docs/Backend/Java/JavaSE/Reflection/AnnotationProcessor/index.md" },
              { text: "实战：注解驱动简易 ORM", link: "/docs/Backend/Java/JavaSE/Reflection/Practice/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/Backend/Java/JavaSE/Reflection/FAQ/index.md" },
            ],
          },
          {
            text: "函数式编程",
            link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/index.md",
            collapsed: true,
            items: [
              { text: "Lambda 表达式", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/Lambda/index.md" },
              { text: "函数式接口与方法引用", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/FunctionalInterface/index.md" },
              { text: "Stream 基础：创建与流水线", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/StreamBasic/index.md" },
              { text: "Stream 进阶：映射、归约与并行", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/StreamAdvanced/index.md" },
              { text: "Optional：优雅处理空值", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/Optional/index.md" },
              { text: "Collectors 收集器详解", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/Collectors/index.md" },
              { text: "实战：订单统计与数据处理", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/Practice/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/Backend/Java/JavaSE/FunctionalProgramming/FAQ/index.md" },
            ],
          },
          {
            text: "Java 并发",
            link: "/docs/Backend/Java/JavaSE/Multithreading/index.md",
            collapsed: true,
            items: [
              { text: "线程基础", link: "/docs/Backend/Java/JavaSE/Multithreading/ThreadBasic/index.md" },
              { text: "线程池", link: "/docs/Backend/Java/JavaSE/Multithreading/ThreadPool/index.md" },
              { text: "synchronized 与 Lock", link: "/docs/Backend/Java/JavaSE/Multithreading/SynchronizedLock/index.md" },
              { text: "volatile 与内存可见性", link: "/docs/Backend/Java/JavaSE/Multithreading/Volatile/index.md" },
              { text: "并发工具类", link: "/docs/Backend/Java/JavaSE/Multithreading/ConcurrentUtils/index.md" },
              { text: "CompletableFuture 异步编排", link: "/docs/Backend/Java/JavaSE/Multithreading/CompletableFuture/index.md" },
              { text: "ThreadLocal 详解", link: "/docs/Backend/Java/JavaSE/Multithreading/ThreadLocal/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/Backend/Java/JavaSE/Multithreading/FAQ/index.md" },
            ],
          },
          {
            text: "JVM 基础",
            link: "/docs/Backend/Java/JavaSE/JVM/index.md",
            collapsed: true,
            items: [
              { text: "内存结构", link: "/docs/Backend/Java/JavaSE/JVM/MemoryStructure/index.md" },
              { text: "对象创建与内存布局", link: "/docs/Backend/Java/JavaSE/JVM/ObjectLayout/index.md" },
              { text: "类加载机制", link: "/docs/Backend/Java/JavaSE/JVM/ClassLoading/index.md" },
              { text: "GC 算法", link: "/docs/Backend/Java/JavaSE/JVM/GcAlgorithm/index.md" },
              { text: "垃圾收集器", link: "/docs/Backend/Java/JavaSE/JVM/GcCollector/index.md" },
              { text: "JVM 调优参数", link: "/docs/Backend/Java/JavaSE/JVM/Tuning/index.md" },
              { text: "故障排查", link: "/docs/Backend/Java/JavaSE/JVM/Troubleshoot/index.md" },
              { text: "常见问题与最佳实践", link: "/docs/Backend/Java/JavaSE/JVM/FAQ/index.md" },
            ],
          },
        ],
      },
      {
        text: "框架",
        link: "/docs/Backend/Java/Frame/index.md",
        collapsed: true,
        items: [
          { text: "框架基本概念", link: "/docs/Backend/Java/Frame/BasicConcept/index.md" },
          {
            text: "Spring",
            link: "/docs/Backend/Java/Frame/Spring/index.md",
            collapsed: true,
            items: [
              { text: "Spring 5", link: "/docs/Backend/Java/Frame/Spring/Spring5/index.md" },
              { text: "Spring 6", link: "/docs/Backend/Java/Frame/Spring/Spring6/index.md", collapsed: true, items: [
                { text: "Spring 整合 Druid", link: "/docs/Backend/Java/Frame/Spring/Spring6/Integration/Druid/index.md" },
                { text: "单元测试：JUnit", link: "/docs/Backend/Java/Frame/Spring/Spring6/Integration/Junit/index.md" },
                { text: "SSM 整合", link: "/docs/Backend/Java/Frame/Spring/Spring6/Integration/SSM/index.md" },
                { text: "Spring 整合框架", link: "/docs/Backend/Java/Frame/Spring/Spring6/Integration/index.md" },
              ] },
            ],
          },
          { text: "Spring MVC", link: "/docs/Backend/Java/Frame/SpringMVC/index.md" },
          {
            text: "Spring Boot（版本总览）",
            link: "/docs/Backend/Java/Frame/SpringBoot/index.md",
            collapsed: true,
            items: [
              {
                text: "通用指南",
                link: "/docs/Backend/Java/Frame/SpringBoot/Common/index.md",
                collapsed: true,
                items: [
                  { text: "Spring Boot 概述与版本", link: "/docs/Backend/Java/Frame/SpringBoot/Common/Overview/index.md" },
                  { text: "项目搭建", link: "/docs/Backend/Java/Frame/SpringBoot/Common/CreateProject/index.md" },
                  { text: "配置与 Profile", link: "/docs/Backend/Java/Frame/SpringBoot/Common/Configuration/index.md" },
                  { text: "Web 开发", link: "/docs/Backend/Java/Frame/SpringBoot/Common/Web/index.md" },
                  { text: "数据访问", link: "/docs/Backend/Java/Frame/SpringBoot/Common/DataAccess/index.md" },
                  { text: "REST API", link: "/docs/Backend/Java/Frame/SpringBoot/Common/RestAPI/index.md" },
                  { text: "异常处理", link: "/docs/Backend/Java/Frame/SpringBoot/Common/Exception/index.md" },
                  { text: "测试", link: "/docs/Backend/Java/Frame/SpringBoot/Common/Testing/index.md" },
                  { text: "部署", link: "/docs/Backend/Java/Frame/SpringBoot/Common/Deploy/index.md" },
                  { text: "常见问题与最佳实践", link: "/docs/Backend/Java/Frame/SpringBoot/Common/FAQ/index.md" },
                ],
              },
              { text: "Spring Boot 2.x", link: "/docs/Backend/Java/Frame/SpringBoot/v2/index.md", collapsed: true, items: [
                { text: "SpringBoot 自定义Starter", link: "/docs/Backend/Java/Frame/SpringBoot/v2/CustomStarter/index.md" },
                { text: "SpringBoot整合Mybatis", link: "/docs/Backend/Java/Frame/SpringBoot/v2/Integration/MyBatis/index.md" },
                { text: "SpringBoot集成knife4j", link: "/docs/Backend/Java/Frame/SpringBoot/v2/Integration/Swagger/index.md" },
                { text: "SpringBoot 整合框架", link: "/docs/Backend/Java/Frame/SpringBoot/v2/Integration/index.md" },
              ] },
              { text: "Spring Boot 3.x", link: "/docs/Backend/Java/Frame/SpringBoot/v3/index.md", collapsed: true, items: [
                { text: "SpringBoot 数据访问", link: "/docs/Backend/Java/Frame/SpringBoot/v3/DataAccess/index.md" },
                { text: "SpringBoot 整合 AOP", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/AOP/index.md" },
                { text: "SpringBoot 整合 Druid", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Druid/index.md" },
                { text: "SpringBoot 整合 Elasticsearch", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Elasticsearch/index.md" },
                { text: "SpringBoot 整合 JDBC", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/JDBC/index.md" },
                { text: "SpringBoot 整合 Junit", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Junit/index.md" },
                { text: "SpringBoot 整合 Kafka", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Kafka/index.md" },
                { text: "SpringBoot 整合 MyBatis", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/MyBatis/index.md" },
                { text: "SpringBoot 整合 PageHelper", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/PageHelper/index.md" },
                { text: "SpringBoot 整合 RabbitMQ", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/RabbitMQ/index.md" },
                { text: "SpringBoot 整合 Redis", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Redis/index.md" },
                { text: "SpringBoot 整合 RocketMQ", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/RocketMQ/index.md" },
                { text: "SpringBoot 整合 spring-retry", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/SpringRetry/index.md" },
                { text: "SpringBoot 整合 Spring Security", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/SpringSecurity/index.md" },
                { text: "SpringBoot 整合 Swagger", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Swagger/index.md" },
                { text: "SpringBoot 整合 Thymeleaf", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/Thymeleaf/index.md" },
                { text: "SpringBoot 整合框架", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/index.md" },
                { text: "SpringBoot 整合 screw", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Integration/screw/index.md" },
                { text: "SpringBoot 远程调用", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Remote/index.md" },
                { text: "SpringBoot Web开发", link: "/docs/Backend/Java/Frame/SpringBoot/v3/Web/index.md" },
              ] },
              { text: "Spring Boot 4.x（当前稳定版）", link: "/docs/Backend/Java/Frame/SpringBoot/v4/index.md" },
            ],
          },
          {
            text: "Spring Security",
            link: "/docs/Backend/Java/Frame/SpringSecurity/index.md",
            collapsed: true,
            items: [
              { text: "Spring Security 7.x（当前主线）", link: "/docs/Backend/Java/Frame/SpringSecurity/v7/index.md" },
              { text: "Spring Security 6.x（上一代）", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/index.md", collapsed: true, items: [
                { text: "Spring Security 认证", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/Spring/Authentication/index.md" },
                { text: "Spring Security 授权", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/Spring/Authorization/index.md" },
                { text: "Spring Security 构建入门程序", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/Spring/BasicProgram/index.md" },
                { text: "Spring Security 其他配置", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/Spring/Other/index.md" },
                { text: "Spring Security 内部机制", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/Spring/Principle/index.md" },
                { text: "Spring Security6-Spring", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/Spring/index.md" },
              ] },
              { text: "Spring Security 6 · 基于 SpringBoot", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/index.md", collapsed: true, items: [
                { text: "Spring Security 认证", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/Authentication/index.md" },
                { text: "Spring Security 授权", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/Authorization/index.md" },
                { text: "Spring Security 构建入门程序", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/BasicProgram/index.md" },
                { text: "Spring Security 其他配置", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/Other/index.md" },
                { text: "Spring Security 内部机制", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/Principle/index.md" },
              ] },
              { text: "Spring Security 6 · 会话（Session）", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/SpringBoot/Session/index.md" },
              { text: "Spring Security 6 · JWT", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/JWT/index.md" },
              { text: "Spring Security 6 · OAuth2", link: "/docs/Backend/Java/Frame/SpringSecurity/v6/OAuth2/index.md" },
              { text: "Spring Security 5.x（仅存量）", link: "/docs/Backend/Java/Frame/SpringSecurity/v5/index.md" },
            ],
          },
          {
            text: "Spring Cloud",
            link: "/docs/Backend/Java/Frame/SpringCloud/index.md",
            collapsed: true,
            items: [
              { text: "Spring Cloud 2020（仅存量）", link: "/docs/Backend/Java/Frame/SpringCloud/SpringCloud2020/Overview/index.md" },
              { text: "Spring Cloud 2020 · Alibaba", link: "/docs/Backend/Java/Frame/SpringCloud/SpringCloud2020/Alibaba/index.md" },
              { text: "Spring Cloud 2022（仅存量）", link: "/docs/Backend/Java/Frame/SpringCloud/SpringCloud2022/Overview/index.md" },
              { text: "Spring Cloud 2022 · Alibaba", link: "/docs/Backend/Java/Frame/SpringCloud/SpringCloud2022/Alibaba/index.md" },
            { text: "Spring Cloud 2020（Ilford）· 历史版本入口", link: "/docs/Backend/Java/Frame/SpringCloud/SpringCloud2020/index.md" },
            { text: "Spring Cloud 2022（Kilburn）· 历史版本入口", link: "/docs/Backend/Java/Frame/SpringCloud/SpringCloud2022/index.md" },
          ],
          },
          { text: "MyBatis", link: "/docs/Backend/Java/Frame/MyBatis/index.md", collapsed: true, items: [
            { text: "MyBatis 表结构专题", link: "/docs/Backend/Java/Frame/MyBatis/Table/index.md" },
          ] },
          { text: "MyBatis-Plus", link: "/docs/Backend/Java/Frame/MyBatisPlus/index.md", collapsed: true, items: [
            { text: "listObjs() 方法", link: "/docs/Backend/Java/Frame/MyBatisPlus/Methods/ListObjs/index.md" },
            { text: "常用方法解析", link: "/docs/Backend/Java/Frame/MyBatisPlus/Methods/index.md" },
            { text: "Mybatis-Plus简介", link: "/docs/Backend/Java/Frame/MyBatisPlus/Overview/index.md" },
            { text: "Mybatis-Plus", link: "/docs/Backend/Java/Frame/MyBatisPlus/Spring/index.md" },
            { text: "Mybatis-Plus (SpringBoot)", link: "/docs/Backend/Java/Frame/MyBatisPlus/SpringBoot/index.md" },
          ] },
          { text: "MyBatis-Flex", link: "/docs/Backend/Java/Frame/MyBatis-Flex/index.md" },
          { text: "Sa-Token", link: "/docs/Backend/Java/Frame/Sa-token/index.md" },
          {
            text: "LangChain4j",
            link: "/docs/Backend/Java/Frame/Langchain4j/index.md",
            collapsed: true,
            items: [
              { text: "LangChain4j 概述", link: "/docs/Backend/Java/Frame/Langchain4j/Overview/index.md" },
              { text: "快速开始", link: "/docs/Backend/Java/Frame/Langchain4j/QuickStart/index.md" },
              { text: "大模型平台", link: "/docs/Backend/Java/Frame/Langchain4j/Platform/index.md" },
              { text: "构建入门程序", link: "/docs/Backend/Java/Frame/Langchain4j/BasicProgram/index.md" },
              { text: "核心概念", link: "/docs/Backend/Java/Frame/Langchain4j/Concepts/index.md" },
              { text: "大语言模型集成", link: "/docs/Backend/Java/Frame/Langchain4j/LlmIntegration/index.md" },
              { text: "国产大模型集成", link: "/docs/Backend/Java/Frame/Langchain4j/NationalModels/index.md" },
              { text: "提示词模板", link: "/docs/Backend/Java/Frame/Langchain4j/PromptTemplate/index.md" },
              { text: "内存管理", link: "/docs/Backend/Java/Frame/Langchain4j/MemoryManagement/index.md" },
              { text: "链式调用", link: "/docs/Backend/Java/Frame/Langchain4j/Chain/index.md" },
              { text: "工具调用", link: "/docs/Backend/Java/Frame/Langchain4j/Tools/index.md" },
              { text: "流式响应", link: "/docs/Backend/Java/Frame/Langchain4j/Streaming/index.md" },
              { text: "检索增强生成 RAG", link: "/docs/Backend/Java/Frame/Langchain4j/Rag/index.md" },
              { text: "整合 Spring Boot", link: "/docs/Backend/Java/Frame/Langchain4j/SpringBoot/index.md" },
              { text: "常见错误", link: "/docs/Backend/Java/Frame/Langchain4j/Error/index.md" },
            ],
          },
        ],
      },
      { text: "其他", link: "/docs/Backend/Java/Others/index.md" },
    ],
  },
];
export const Auth = [
  {
    text: "认证与授权",
    link: "/docs/Backend/Auth/index.md",
    items: [
      { text: "认证与授权概述", link: "/docs/Backend/Auth/index.md" },
      { text: "会话与 Cookie", link: "/docs/Backend/Auth/Session/index.md" },
      { text: "JWT 深入", link: "/docs/Backend/Auth/Jwt/index.md" },
      { text: "OAuth 2.1 与 OIDC", link: "/docs/Backend/Auth/Oauth2/index.md" },
      { text: "单点登录（SSO）", link: "/docs/Backend/Auth/Sso/index.md" },
      { text: "权限模型", link: "/docs/Backend/Auth/Authorization/index.md" },
      { text: "服务端落地", link: "/docs/Backend/Auth/Implementation/index.md" },
      { text: "安全最佳实践", link: "/docs/Backend/Auth/Security/index.md" },
      { text: "版本与兼容矩阵", link: "/docs/Backend/Auth/Version/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/Auth/FAQ/index.md" },
    ],
  },
];
export const MessageQueue = [
  {
    text: "消息队列",
    link: "/docs/Backend/MessageQueue/index.md",
    items: [
      { text: "概念与选型", link: "/docs/Backend/MessageQueue/Overview/index.md" },
      {
        text: "Kafka 深入",
        link: "/docs/Backend/MessageQueue/Kafka/index.md",
        collapsed: true,
        items: [
          { text: "Kafka 概述", link: "/docs/Backend/MessageQueue/Kafka/index.md" },
          { text: "版本演进与迁移", link: "/docs/Backend/MessageQueue/Kafka/Version/index.md" },
          { text: "架构与存储原理", link: "/docs/Backend/MessageQueue/Kafka/Architecture/index.md" },
          { text: "分区与副本机制", link: "/docs/Backend/MessageQueue/Kafka/PartitionReplica/index.md" },
          { text: "生产者深入", link: "/docs/Backend/MessageQueue/Kafka/Producer/index.md" },
          { text: "消费者与消费组深入", link: "/docs/Backend/MessageQueue/Kafka/Consumer/index.md" },
          { text: "可靠性与 Exactly-Once", link: "/docs/Backend/MessageQueue/Kafka/Reliability/index.md" },
          { text: "集群部署、运维与监控", link: "/docs/Backend/MessageQueue/Kafka/Cluster/index.md" },
          { text: "实战：订单事件管道", link: "/docs/Backend/MessageQueue/Kafka/Practice/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Backend/MessageQueue/Kafka/FAQ/index.md" },
        ],
      },
      { text: "RabbitMQ 入门", link: "/docs/Backend/MessageQueue/RabbitMQ/index.md" },
      { text: "可靠投递", link: "/docs/Backend/MessageQueue/Reliability/index.md" },
      { text: "消费幂等", link: "/docs/Backend/MessageQueue/Idempotency/index.md" },
      { text: "集群部署", link: "/docs/Backend/MessageQueue/Cluster/index.md" },
      { text: "对比总结", link: "/docs/Backend/MessageQueue/Comparison/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/MessageQueue/FAQ/index.md" },
    ],
  },
];
export const Microservices = [
  {
    text: "微服务",
    link: "/docs/Backend/Microservices/index.md",
    items: [
      { text: "概述与服务拆分", link: "/docs/Backend/Microservices/Overview/index.md" },
      { text: "注册中心", link: "/docs/Backend/Microservices/Registry/index.md" },
      { text: "配置中心", link: "/docs/Backend/Microservices/ConfigCenter/index.md" },
      { text: "API 网关", link: "/docs/Backend/Microservices/Gateway/index.md" },
      { text: "负载均衡", link: "/docs/Backend/Microservices/LoadBalance/index.md" },
      { text: "熔断限流与降级", link: "/docs/Backend/Microservices/CircuitBreaker/index.md" },
      { text: "链路追踪", link: "/docs/Backend/Microservices/Tracing/index.md" },
      {
        text: "分布式事务",
        link: "/docs/Backend/Microservices/DistributedTransaction/index.md",
        collapsed: true,
        items: [
          { text: "分布式事务概述", link: "/docs/Backend/Microservices/DistributedTransaction/index.md" },
          { text: "一致性基础与事务边界", link: "/docs/Backend/Microservices/DistributedTransaction/Consistency/index.md" },
          { text: "2PC 与 XA", link: "/docs/Backend/Microservices/DistributedTransaction/TwoPhaseCommit/index.md" },
          { text: "TCC", link: "/docs/Backend/Microservices/DistributedTransaction/TCC/index.md" },
          { text: "SAGA", link: "/docs/Backend/Microservices/DistributedTransaction/Saga/index.md" },
          { text: "本地消息表与事务消息", link: "/docs/Backend/Microservices/DistributedTransaction/MessageTable/index.md" },
          { text: "Seata 事务框架", link: "/docs/Backend/Microservices/DistributedTransaction/Seata/index.md" },
          { text: "Seata 1.x 存档（仅存量）", link: "/docs/Backend/Microservices/DistributedTransaction/Seata/Seata1/index.md" },
          { text: "实战：订单-库存-账户一致性", link: "/docs/Backend/Microservices/DistributedTransaction/Practice/index.md" },
          { text: "常见问题与最佳实践", link: "/docs/Backend/Microservices/DistributedTransaction/FAQ/index.md" },
        ],
      },
      { text: "实战：订单库存账户微服务", link: "/docs/Backend/Microservices/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/Microservices/FAQ/index.md" },
    ],
  },
];
export const GatewayDeep = [
  {
    text: "网关深入",
    link: "/docs/Backend/GatewayDeep/index.md",
    items: [
      { text: "概述：四条边界", link: "/docs/Backend/GatewayDeep/Overview/index.md" },
      { text: "Kong 深入", link: "/docs/Backend/GatewayDeep/Kong/index.md" },
      { text: "APISIX 深入", link: "/docs/Backend/GatewayDeep/APISIX/index.md" },
      { text: "插件开发", link: "/docs/Backend/GatewayDeep/Plugin/index.md" },
      { text: "流量治理与灰度", link: "/docs/Backend/GatewayDeep/TrafficManagement/index.md" },
      { text: "网关可观测", link: "/docs/Backend/GatewayDeep/Observability/index.md" },
      { text: "网关安全", link: "/docs/Backend/GatewayDeep/Security/index.md" },
      { text: "实战：生产级网关", link: "/docs/Backend/GatewayDeep/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/GatewayDeep/FAQ/index.md" },
    ],
  },
];
export const SpringCloud = [
  {
    text: "Spring Cloud",
    link: "/docs/Backend/SpringCloud/index.md",
    items: [
      { text: "Spring Cloud 概述", link: "/docs/Backend/SpringCloud/Overview/index.md" },
      { text: "版本选择与演进", link: "/docs/Backend/SpringCloud/Version/index.md", collapsed: true, items: [
        { text: "Spring Cloud 2025.1.x（Oakwood，当前稳定版）", link: "/docs/Backend/SpringCloud/Version/2025-1/index.md" },
      ] },
      { text: "环境搭建与项目脚手架", link: "/docs/Backend/SpringCloud/Environment/index.md" },
      { text: "服务注册与发现", link: "/docs/Backend/SpringCloud/Discovery/index.md" },
      { text: "服务调用：OpenFeign 与负载均衡", link: "/docs/Backend/SpringCloud/OpenFeign/index.md" },
      { text: "API 网关：Spring Cloud Gateway", link: "/docs/Backend/SpringCloud/Gateway/index.md" },
      { text: "配置中心与动态刷新", link: "/docs/Backend/SpringCloud/ConfigCenter/index.md" },
      { text: "熔断限流与降级", link: "/docs/Backend/SpringCloud/CircuitBreaker/index.md" },
      { text: "链路追踪与可观测性", link: "/docs/Backend/SpringCloud/Tracing/index.md" },
      { text: "消息驱动：Spring Cloud Stream", link: "/docs/Backend/SpringCloud/Stream/index.md" },
      { text: "实战：Nacos + 网关 + OpenFeign", link: "/docs/Backend/SpringCloud/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/SpringCloud/FAQ/index.md" },
    ],
  },
];
export const DesignPatterns = [
  {
    text: "设计模式",
    link: "/docs/Backend/DesignPatterns/index.md",
    items: [
      { text: "设计原则", link: "/docs/Backend/DesignPatterns/Principles/index.md" },
      { text: "创建型模式", link: "/docs/Backend/DesignPatterns/Creational/index.md" },
      { text: "结构型模式", link: "/docs/Backend/DesignPatterns/Structural/index.md" },
      { text: "行为型模式", link: "/docs/Backend/DesignPatterns/Behavioral/index.md" },
      { text: "框架中的应用", link: "/docs/Backend/DesignPatterns/FrameworkUsage/index.md" },
      { text: "JDK 源码中的设计模式", link: "/docs/Backend/DesignPatterns/JdkPatterns/index.md" },
      { text: "现代 Java 与设计模式", link: "/docs/Backend/DesignPatterns/ModernJava/index.md" },
      { text: "反模式与过度设计", link: "/docs/Backend/DesignPatterns/AntiPatterns/index.md" },
      { text: "重构实战：安全地改代码", link: "/docs/Backend/DesignPatterns/RefactorPractice/index.md" },
      { text: "实战案例", link: "/docs/Backend/DesignPatterns/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/DesignPatterns/FAQ/index.md" },
    ],
  },
];
export const NetworkProgramming = [
  {
    text: "网络编程",
    link: "/docs/Backend/NetworkProgramming/index.md",
    items: [
      { text: "网络分层与 TCP/IP 基础", link: "/docs/Backend/NetworkProgramming/Overview/index.md" },
      { text: "TCP 与 UDP 详解", link: "/docs/Backend/NetworkProgramming/TCPUDP/index.md" },
      { text: "HTTP 与 HTTPS 协议", link: "/docs/Backend/NetworkProgramming/HttpHttps/index.md" },
      { text: "Socket 与 IO 模型", link: "/docs/Backend/NetworkProgramming/SocketIO/index.md" },
      { text: "Netty 入门", link: "/docs/Backend/NetworkProgramming/Netty/index.md" },
      { text: "Netty 进阶：线程模型与性能调优", link: "/docs/Backend/NetworkProgramming/NettyAdvanced/index.md" },
      { text: "虚拟线程与高并发模型", link: "/docs/Backend/NetworkProgramming/VirtualThread/index.md" },
      { text: "自定义协议设计", link: "/docs/Backend/NetworkProgramming/ProtocolDesign/index.md" },
      { text: "粘包拆包与编解码", link: "/docs/Backend/NetworkProgramming/StickyHalf/index.md" },
      { text: "性能基准与压测", link: "/docs/Backend/NetworkProgramming/BenchmarkPractice/index.md" },
      { text: "实战：Netty 聊天服务器", link: "/docs/Backend/NetworkProgramming/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/NetworkProgramming/FAQ/index.md" },
    ],
  },
];
export const HighPerformanceJava = [
  {
    text: "高性能 Java",
    link: "/docs/Backend/HighPerformanceJava/index.md",
    items: [
      { text: "性能工程全景：指标口径与优化决策", link: "/docs/Backend/HighPerformanceJava/Overview/index.md" },
      { text: "JMH 基准测试", link: "/docs/Backend/HighPerformanceJava/JmhBenchmark/index.md" },
      { text: "JIT 与分层编译", link: "/docs/Backend/HighPerformanceJava/JitCompiler/index.md" },
      { text: "对象布局：从对象头到紧凑对象头", link: "/docs/Backend/HighPerformanceJava/MemoryLayout/index.md" },
      { text: "分配与内存效率", link: "/docs/Backend/HighPerformanceJava/AllocationOptimize/index.md" },
      { text: "锁与并发原语的性能", link: "/docs/Backend/HighPerformanceJava/LockOptimize/index.md" },
      { text: "剖析工具链：JFR 与 async-profiler", link: "/docs/Backend/HighPerformanceJava/Profiling/index.md" },
      { text: "实战：把慢接口的 P99 打下来", link: "/docs/Backend/HighPerformanceJava/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/HighPerformanceJava/FAQ/index.md" },
    ],
  },
];
export const Go = [
  {
    text: "Go",
    link: "/docs/Backend/Go/index.md",
    items: [
      { text: "Go 概述", link: "/docs/Backend/Go/Overview/index.md" },
      { text: "Go 环境搭建", link: "/docs/Backend/Go/Environment/index.md" },
      { text: "Go 基础语法", link: "/docs/Backend/Go/BasicSyntax/index.md" },
      { text: "Go 函数、方法与接口", link: "/docs/Backend/Go/Functions/index.md" },
      { text: "Go 集合：数组、切片与映射", link: "/docs/Backend/Go/Collections/index.md" },
      {
        text: "语言进阶",
        collapsed: true,
        items: [
          { text: "Go 泛型", link: "/docs/Backend/Go/Generics/index.md" },
          { text: "Go 并发模型", link: "/docs/Backend/Go/Concurrency/index.md" },
          { text: "Go 错误处理与 panic", link: "/docs/Backend/Go/ErrorHandling/index.md" },
          { text: "Go 包与模块管理", link: "/docs/Backend/Go/Modules/index.md" },
        ],
      },
      {
        text: "应用与交付",
        collapsed: true,
        items: [
          { text: "Go Web 开发", link: "/docs/Backend/Go/WebDev/index.md" },
          { text: "实战：短链服务", link: "/docs/Backend/Go/Practice/index.md" },
          { text: "Go 常见问题与最佳实践", link: "/docs/Backend/Go/FAQ/index.md" },
        ],
      },
    ],
  },
];
export const GoMicroservices = [
  {
    text: "Go 微服务",
    link: "/docs/Backend/GoMicroservices/index.md",
    items: [
      { text: "Go 微服务概述与选型", link: "/docs/Backend/GoMicroservices/Overview/index.md" },
      { text: "gRPC 与 Protobuf 工程化", link: "/docs/Backend/GoMicroservices/GRPC/index.md" },
      { text: "服务治理：注册发现到可观测", link: "/docs/Backend/GoMicroservices/Governance/index.md" },
      { text: "实战：订单服务", link: "/docs/Backend/GoMicroservices/Practice/index.md" },
    ],
  },
];
export const PythonWeb = [
  {
    text: "Python Web 框架",
    link: "/docs/Backend/PythonWeb/index.md",
    items: [
      { text: "框架选型：FastAPI / Django / Flask", link: "/docs/Backend/PythonWeb/Overview/index.md" },
      { text: "FastAPI 进阶：类型、异步与依赖注入", link: "/docs/Backend/PythonWeb/FastAPI/index.md" },
      { text: "数据层：SQLAlchemy 2.0 与 Alembic", link: "/docs/Backend/PythonWeb/DataLayer/index.md" },
      { text: "实战：可部署的 API 服务", link: "/docs/Backend/PythonWeb/Practice/index.md" },
    ],
  },
];
export const Python = [
  {
    text: "Python",
    link: "/docs/Backend/Python/index.md",
    items: [
      { text: "环境管理", link: "/docs/Backend/Python/Environment/index.md" },
      { text: "装饰器", link: "/docs/Backend/Python/Decorator/index.md" },
      { text: "异步编程", link: "/docs/Backend/Python/Async/index.md" },
      { text: "常用第三方库", link: "/docs/Backend/Python/CommonLibs/index.md" },
    ],
  },
];
export const Ecommerce = [
  {
    text: "电商系统设计",
    link: "/docs/Backend/Ecommerce/index.md",
    items: [
      { text: "电商系统全景与核心链路", link: "/docs/Backend/Ecommerce/Overview/index.md" },
      { text: "商品与领域建模", link: "/docs/Backend/Ecommerce/DomainModeling/index.md" },
      { text: "购物车与价格计算", link: "/docs/Backend/Ecommerce/Cart/index.md" },
      { text: "订单状态机", link: "/docs/Backend/Ecommerce/OrderStateMachine/index.md" },
      { text: "库存模型与超卖防护", link: "/docs/Backend/Ecommerce/Inventory/index.md" },
      { text: "支付、幂等与对账", link: "/docs/Backend/Ecommerce/Payment/index.md" },
      { text: "秒杀与流量治理", link: "/docs/Backend/Ecommerce/FlashSale/index.md" },
      { text: "常见问题与排错", link: "/docs/Backend/Ecommerce/FAQ/index.md" },
    ],
  },
];
export const DDD = [
  {
    text: "领域驱动设计",
    link: "/docs/Backend/DDD/index.md",
    items: [
      { text: "DDD 概述", link: "/docs/Backend/DDD/Overview/index.md" },
      { text: "战略设计", link: "/docs/Backend/DDD/StrategicDesign/index.md" },
      { text: "战术设计", link: "/docs/Backend/DDD/TacticalDesign/index.md" },
      { text: "聚合设计", link: "/docs/Backend/DDD/Aggregate/index.md" },
      { text: "仓储与持久化", link: "/docs/Backend/DDD/Repository/index.md" },
      { text: "领域事件", link: "/docs/Backend/DDD/DomainEvent/index.md" },
      { text: "落地架构", link: "/docs/Backend/DDD/Architecture/index.md" },
      { text: "实战：博客平台文章发布域", link: "/docs/Backend/DDD/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/DDD/FAQ/index.md" },
    ],
  },
];
export const WorkflowEngine = [
  {
    text: "工作流与规则引擎",
    link: "/docs/Backend/WorkflowEngine/index.md",
    items: [
      { text: "总览：三层能力与选型边界", link: "/docs/Backend/WorkflowEngine/Overview/index.md" },
      { text: "BPMN 2.0 建模", link: "/docs/Backend/WorkflowEngine/Modeling/index.md" },
      { text: "Flowable 引擎深入", link: "/docs/Backend/WorkflowEngine/Flowable/index.md" },
      { text: "审批流设计", link: "/docs/Backend/WorkflowEngine/ApprovalFlow/index.md" },
      { text: "Drools 规则引擎", link: "/docs/Backend/WorkflowEngine/Drools/index.md" },
      { text: "规则引擎选型与轻量替代", link: "/docs/Backend/WorkflowEngine/RuleEngine/index.md" },
      { text: "与业务系统集成", link: "/docs/Backend/WorkflowEngine/Integration/index.md" },
      { text: "实战：投稿—审核—发布", link: "/docs/Backend/WorkflowEngine/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/WorkflowEngine/FAQ/index.md" },
    ],
  },
];

export const DistributedCache = [
  {
    text: "分布式缓存深入",
    link: "/docs/Backend/DistributedCache/index.md",
    items: [
      { text: "总览：缓存的四条边界", link: "/docs/Backend/DistributedCache/Overview/index.md" },
      { text: "拓扑与路由", link: "/docs/Backend/DistributedCache/Topology/index.md" },
      { text: "多级缓存深入", link: "/docs/Backend/DistributedCache/MultiLevel/index.md" },
      { text: "一致性方案深入", link: "/docs/Backend/DistributedCache/Consistency/index.md" },
      { text: "热点与倾斜治理", link: "/docs/Backend/DistributedCache/HotKey/index.md" },
      { text: "缓存层韧性", link: "/docs/Backend/DistributedCache/Availability/index.md" },
      { text: "可观测与容量治理", link: "/docs/Backend/DistributedCache/Observability/index.md" },
      { text: "实战：博客平台内容缓存体系", link: "/docs/Backend/DistributedCache/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/DistributedCache/FAQ/index.md" },
    ],
  },
];

export const ReactiveProgramming = [
  {
    text: "响应式编程",
    link: "/docs/Backend/ReactiveProgramming/index.md",
    items: [
      { text: "总览：响应式的四条边界", link: "/docs/Backend/ReactiveProgramming/Overview/index.md" },
      { text: "Reactor 核心", link: "/docs/Backend/ReactiveProgramming/Reactor/index.md" },
      { text: "背压", link: "/docs/Backend/ReactiveProgramming/Backpressure/index.md" },
      { text: "WebFlux 落地", link: "/docs/Backend/ReactiveProgramming/WebFlux/index.md" },
      { text: "响应式数据访问", link: "/docs/Backend/ReactiveProgramming/DataAccess/index.md" },
      { text: "调试与排障", link: "/docs/Backend/ReactiveProgramming/Debugging/index.md" },
      { text: "实战：一次聚合查询的改造", link: "/docs/Backend/ReactiveProgramming/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/ReactiveProgramming/FAQ/index.md" },
    ],
  },
];

export const Ledger = [
  {
    text: "账务与清结算",
    link: "/docs/Backend/Ledger/index.md",
    items: [
      { text: "总览：账务系统的四条边界", link: "/docs/Backend/Ledger/Overview/index.md" },
      { text: "复式记账与账本模型", link: "/docs/Backend/Ledger/DoubleEntry/index.md" },
      { text: "账户、余额与流水", link: "/docs/Backend/Ledger/AccountModel/index.md" },
      { text: "记账幂等与一致性", link: "/docs/Backend/Ledger/Idempotency/index.md" },
      { text: "清分与结算", link: "/docs/Backend/Ledger/Settlement/index.md" },
      { text: "对账体系与差错处理", link: "/docs/Backend/Ledger/Reconciliation/index.md" },
      { text: "实战：从一笔支付到日终打平", link: "/docs/Backend/Ledger/Practice/index.md" },
      { text: "常见问题与排错", link: "/docs/Backend/Ledger/FAQ/index.md" },
    ],
  },
];

export const HighConcurrency = [
  {
    text: "高并发系统设计",
    link: "/docs/Backend/HighConcurrency/index.md",
    items: [
      { text: "总览：高并发的四条边界", link: "/docs/Backend/HighConcurrency/Overview/index.md" },
      { text: "分层防御与预算分配", link: "/docs/Backend/HighConcurrency/LayeredDefense/index.md" },
      { text: "限流：算法与分布式实现", link: "/docs/Backend/HighConcurrency/RateLimit/index.md" },
      { text: "排队与削峰", link: "/docs/Backend/HighConcurrency/QueueShaping/index.md" },
      { text: "热点识别与拆分", link: "/docs/Backend/HighConcurrency/HotspotSplit/index.md" },
      { text: "过载行为与有损服务", link: "/docs/Backend/HighConcurrency/OverloadBehavior/index.md" },
      { text: "资源隔离与并发控制", link: "/docs/Backend/HighConcurrency/Isolation/index.md" },
      { text: "实战：写接口的过载治理", link: "/docs/Backend/HighConcurrency/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/HighConcurrency/FAQ/index.md" },
    ],
  },
];

export const LegacyModernization = [
  {
    text: "遗留系统改造",
    link: "/docs/Backend/LegacyModernization/index.md",
    items: [
      { text: "总览：四条边界与改造判据", link: "/docs/Backend/LegacyModernization/Overview/index.md" },
      { text: "绞杀者模式：把替换拆成可回退的步骤", link: "/docs/Backend/LegacyModernization/Strangler/index.md" },
      { text: "防腐层：让旧模型停在一层里", link: "/docs/Backend/LegacyModernization/AntiCorruption/index.md" },
      { text: "数据迁移：双写、追平与三档校验", link: "/docs/Backend/LegacyModernization/DataMigration/index.md" },
      { text: "灰度切换：把流量当成开关", link: "/docs/Backend/LegacyModernization/TrafficCutover/index.md" },
      { text: "共存期工程：两套系统同时活着时的约束", link: "/docs/Backend/LegacyModernization/Coexistence/index.md" },
      { text: "实战：从单体到新服务的一次完整改造", link: "/docs/Backend/LegacyModernization/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/LegacyModernization/FAQ/index.md" },
    ],
  },
];

export const RealtimeCollaboration = [
  {
    text: "实时协作与冲突解决",
    link: "/docs/Backend/RealtimeCollaboration/index.md",
    items: [
      { text: "概述：三类冲突与五种一致性", link: "/docs/Backend/RealtimeCollaboration/Overview/index.md" },
      { text: "OT：操作变换与定序", link: "/docs/Backend/RealtimeCollaboration/OT/index.md" },
      { text: "CRDT：收敛的代价", link: "/docs/Backend/RealtimeCollaboration/CRDT/index.md" },
      { text: "同步协议与状态向量", link: "/docs/Backend/RealtimeCollaboration/SyncProtocol/index.md" },
      { text: "Presence：在线状态与光标", link: "/docs/Backend/RealtimeCollaboration/Presence/index.md" },
      { text: "离线优先与重放", link: "/docs/Backend/RealtimeCollaboration/Offline/index.md" },
      { text: "权限、审计与内容安全", link: "/docs/Backend/RealtimeCollaboration/Security/index.md" },
      { text: "实战：卡片描述的协作编辑", link: "/docs/Backend/RealtimeCollaboration/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/RealtimeCollaboration/FAQ/index.md" },
    ],
  },
];

export const IdempotencyStateMachine = [
  {
    text: "幂等与状态机工程",
    link: "/docs/Backend/IdempotencyStateMachine/index.md",
    items: [
      { text: "概述：两条铁律与五种失败模式", link: "/docs/Backend/IdempotencyStateMachine/Overview/index.md" },
      { text: "幂等键设计：让同一个请求只发生一次", link: "/docs/Backend/IdempotencyStateMachine/IdempotencyKey/index.md" },
      { text: "状态机建模：状态只能沿合法的边迁移", link: "/docs/Backend/IdempotencyStateMachine/StateMachine/index.md" },
      { text: "并发护栏：乐观锁、条件更新与 fencing", link: "/docs/Backend/IdempotencyStateMachine/ConcurrencyGuard/index.md" },
      { text: "补偿与对账：回不去的时候往前修", link: "/docs/Backend/IdempotencyStateMachine/Compensation/index.md" },
      { text: "重放：把历史事件再跑一遍", link: "/docs/Backend/IdempotencyStateMachine/Replay/index.md" },
      { text: "怎么测：属性测试与模型测试", link: "/docs/Backend/IdempotencyStateMachine/Testing/index.md" },
      { text: "实战：支付回调到日终对账", link: "/docs/Backend/IdempotencyStateMachine/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/IdempotencyStateMachine/FAQ/index.md" },
    ],
  },
];

export const DistributedLock = [
  {
    text: "分布式锁与选主",
    link: "/docs/Backend/DistributedLock/index.md",
    items: [
      { text: "概述：三性质与五种失效", link: "/docs/Backend/DistributedLock/Overview/index.md" },
      { text: "三种实现与安全性来源", link: "/docs/Backend/DistributedLock/Implementations/index.md" },
      { text: "租约与续期：TTL 三角", link: "/docs/Backend/DistributedLock/Lease/index.md" },
      { text: "fencing token：失锁后的闸门", link: "/docs/Backend/DistributedLock/Fencing/index.md" },
      { text: "选主与领导权", link: "/docs/Backend/DistributedLock/LeaderElection/index.md" },
      { text: "脑裂与分区", link: "/docs/Backend/DistributedLock/SplitBrain/index.md" },
      { text: "运行面：指标、演练与排查", link: "/docs/Backend/DistributedLock/Operations/index.md" },
      { text: "实战：单例任务、库存扣减与主备切换", link: "/docs/Backend/DistributedLock/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/DistributedLock/FAQ/index.md" },
    ],
  },
];

export const ContractEvolution = [
  {
    text: "契约演进与兼容",
    link: "/docs/Backend/ContractEvolution/index.md",
    items: [
      { text: "总览：四类契约面与三种破坏", link: "/docs/Backend/ContractEvolution/Overview/index.md" },
      { text: "兼容性判定：加法、语义与时序", link: "/docs/Backend/ContractEvolution/Compatibility/index.md" },
      { text: "消费者清单：谁在调用我", link: "/docs/Backend/ContractEvolution/ConsumerInventory/index.md" },
      { text: "服务端承载多版本", link: "/docs/Backend/ContractEvolution/ServerVersions/index.md" },
      { text: "库表演进：expand-contract 四阶段", link: "/docs/Backend/ContractEvolution/SchemaEvolution/index.md" },
      { text: "异步契约：消息与兼容模式", link: "/docs/Backend/ContractEvolution/AsyncContract/index.md" },
      { text: "契约门禁：让 CI 拦住破坏", link: "/docs/Backend/ContractEvolution/ContractGate/index.md" },
      { text: "下线：可执行的倒计时", link: "/docs/Backend/ContractEvolution/Sunset/index.md" },
      { text: "实战：v1 演进成 v2", link: "/docs/Backend/ContractEvolution/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/ContractEvolution/FAQ/index.md" },
    ],
  },
];

export const ObjectStorage = [
  {
    text: "文件与对象存储工程",
    link: "/docs/Backend/ObjectStorage/index.md",
    items: [
      { text: "总览：三条硬约束与四维成本", link: "/docs/Backend/ObjectStorage/Overview/index.md" },
      { text: "键空间与命名", link: "/docs/Backend/ObjectStorage/KeysLayout/index.md" },
      { text: "上传路径与预签名", link: "/docs/Backend/ObjectStorage/UploadPaths/index.md" },
      { text: "完整性校验", link: "/docs/Backend/ObjectStorage/IntegrityChecksum/index.md" },
      { text: "去重与内容寻址", link: "/docs/Backend/ObjectStorage/DedupCAS/index.md" },
      { text: "一致性与并发写", link: "/docs/Backend/ObjectStorage/ConsistencyModel/index.md" },
      { text: "生命周期与分层成本", link: "/docs/Backend/ObjectStorage/LifecycleCost/index.md" },
      { text: "访问控制与合规", link: "/docs/Backend/ObjectStorage/SecurityAccess/index.md" },
      { text: "实战：一个附件服务的端到端", link: "/docs/Backend/ObjectStorage/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/Backend/ObjectStorage/FAQ/index.md" },
    ],
  },
];

export const EmailDeliverability = [
  {
    text: "邮件送达工程",
    link: "/docs/Backend/EmailDeliverability/index.md",
    items: [
      { text: "总览：三层送达与五个必失点", link: "/docs/Backend/EmailDeliverability/Overview/index.md" },
      { text: "身份三件套：SPF/DKIM/DMARC 与对齐", link: "/docs/Backend/EmailDeliverability/Authentication/index.md" },
      { text: "DNS 与密钥：记录形状与轮换", link: "/docs/Backend/EmailDeliverability/DnsAndKeys/index.md" },
      { text: "发信链路：组装、队列与投递", link: "/docs/Backend/EmailDeliverability/SendingPipeline/index.md" },
      { text: "退信与投诉：分类与重试阶梯", link: "/docs/Backend/EmailDeliverability/BounceComplaint/index.md" },
      { text: "声誉与预热：投诉率算术", link: "/docs/Backend/EmailDeliverability/ReputationWarmup/index.md" },
      { text: "收信侧：MX、网关与会话", link: "/docs/Backend/EmailDeliverability/InboundMail/index.md" },
      { text: "观测与分诊：五个口径与四张表", link: "/docs/Backend/EmailDeliverability/Observability/index.md" },
      { text: "实战：邀请邮件的端到端验收", link: "/docs/Backend/EmailDeliverability/Practice/index.md" },
      { text: "常见问题与排错", link: "/docs/Backend/EmailDeliverability/FAQ/index.md" },
    ],
  },
];

export const DistributedScheduling = [
  {
    text: "分布式调度与任务编排",
    link: "/docs/Backend/DistributedScheduling/index.md",
    items: [
      { text: "总览：四种触发语义与五个必失点", link: "/docs/Backend/DistributedScheduling/Overview/index.md" },
      { text: "Cron 语义：时区、DST 与下一次触发时间", link: "/docs/Backend/DistributedScheduling/CronSemantics/index.md" },
      { text: "调度内核：扫描、认领与执行三段式", link: "/docs/Backend/DistributedScheduling/SchedulerCore/index.md" },
      { text: "高可用：选主、分片、脑裂与 fencing", link: "/docs/Backend/DistributedScheduling/LeaderSharding/index.md" },
      { text: "misfire 与补跑：停机之后补几次", link: "/docs/Backend/DistributedScheduling/MisfireCatchup/index.md" },
      { text: "幂等与重试：一次到底算几次", link: "/docs/Backend/DistributedScheduling/IdempotentRetry/index.md" },
      { text: "依赖编排：DAG、扇出与背压", link: "/docs/Backend/DistributedScheduling/DagDependency/index.md" },
      { text: "可观测：五个口径与静默停摆", link: "/docs/Backend/DistributedScheduling/Observability/index.md" },
      { text: "实战：TeamBoard 的六类定时任务验收", link: "/docs/Backend/DistributedScheduling/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/Backend/DistributedScheduling/FAQ/index.md" },
    ],
  },
];

export const EventSourcing = [
  {
    text: "事件溯源与 CQRS",
    link: "/docs/Backend/EventSourcing/index.md",
    items: [
      { text: "总览：三种事件、两条路径与五个必失点", link: "/docs/Backend/EventSourcing/Overview/index.md" },
      { text: "事件存储：追加、顺序与并发", link: "/docs/Backend/EventSourcing/EventStore/index.md" },
      { text: "聚合重建与快照：把「从头」往后挪", link: "/docs/Backend/EventSourcing/Replay/index.md" },
      { text: "投影与读模型：位点、幂等与重建", link: "/docs/Backend/EventSourcing/Projection/index.md" },
      { text: "读写一致性：水位、滞后与读己之写", link: "/docs/Backend/EventSourcing/Consistency/index.md" },
      { text: "事件版本与兼容：只增不改的翻译链", link: "/docs/Backend/EventSourcing/Versioning/index.md" },
      { text: "实战：订单中心的事件时间线与三个读模型", link: "/docs/Backend/EventSourcing/Practice/index.md" },
      { text: "运维：分区、归档与重放演练", link: "/docs/Backend/EventSourcing/Ops/index.md" },
      { text: "常见问题与分诊", link: "/docs/Backend/EventSourcing/FAQ/index.md" },
    ],
  },
];

export const ServiceMesh = [
  {
    text: "服务网格与东西向流量",
    link: "/docs/Backend/ServiceMesh/index.md",
    items: [
      { text: "概述：四个问题、三段链路与五档成熟度", link: "/docs/Backend/ServiceMesh/Overview/index.md" },
      { text: "架构形态：Sidecar、Ambient 与 xDS 下发", link: "/docs/Backend/ServiceMesh/Architecture/index.md" },
      { text: "身份与 mTLS：SPIFFE、证书轮换与授权策略", link: "/docs/Backend/ServiceMesh/Identity/index.md" },
      { text: "东西向流量治理：路由、灰度、超时与重试预算", link: "/docs/Backend/ServiceMesh/Traffic/index.md" },
      { text: "可观测性：指标基数、访问日志与链路", link: "/docs/Backend/ServiceMesh/Observability/index.md" },
      { text: "性能账本：每跳延迟、每 Pod 资源与节点密度", link: "/docs/Backend/ServiceMesh/Performance/index.md" },
      { text: "网格自身故障：控制面宕机、证书过期与升级事故", link: "/docs/Backend/ServiceMesh/Failure/index.md" },
      { text: "从 SDK 治理到网格：双栈迁移与回退", link: "/docs/Backend/ServiceMesh/Migration/index.md" },
      { text: "实战：本地集群跑通 mTLS、灰度与故障注入", link: "/docs/Backend/ServiceMesh/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/Backend/ServiceMesh/FAQ/index.md" },
    ],
  },
];

export const MultiTenantSaaS = [
  {
    text: "多租户 SaaS 架构",
    link: "/docs/Backend/MultiTenantSaaS/index.md",
    items: [
      { text: "四个维度与五个必失点", link: "/docs/Backend/MultiTenantSaaS/Overview/index.md" },
      { text: "隔离三档：成本、体积与迁移路径", link: "/docs/Backend/MultiTenantSaaS/IsolationModel/index.md" },
      { text: "租户上下文：六段链与三个断点", link: "/docs/Backend/MultiTenantSaaS/TenantContext/index.md" },
      { text: "噪声邻居：公平排队的代价与收益", link: "/docs/Backend/MultiTenantSaaS/NoisyNeighbor/index.md" },
      { text: "配额执行：扣在哪一步决定超不超卖", link: "/docs/Backend/MultiTenantSaaS/QuotaEnforcement/index.md" },
      { text: "大租户与热点：倾斜、分片与单元化", link: "/docs/Backend/MultiTenantSaaS/HotTenant/index.md" },
      { text: "计量与账单：从事件到一行可解释的账", link: "/docs/Backend/MultiTenantSaaS/MeteringBilling/index.md" },
      { text: "生命周期：八个状态与一条没有入边的迁移", link: "/docs/Backend/MultiTenantSaaS/Lifecycle/index.md" },
      { text: "实战：一套可验收的多租户基线", link: "/docs/Backend/MultiTenantSaaS/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/Backend/MultiTenantSaaS/FAQ/index.md" },
    ],
  },
];

export const RecommenderSystems = [
  {
    text: "推荐系统工程",
    link: "/docs/Backend/RecommenderSystems/index.md",
    items: [
      { text: "总览：一条推荐请求穿过的四段", link: "/docs/Backend/RecommenderSystems/Overview/index.md" },
      { text: "数据与样本：曝光日志怎么变成训练集", link: "/docs/Backend/RecommenderSystems/DataSamples/index.md" },
      { text: "召回：多路候选、ANN 损失与融合", link: "/docs/Backend/RecommenderSystems/Recall/index.md" },
      { text: "特征：训练与服务必须是同一个数", link: "/docs/Backend/RecommenderSystems/Features/index.md" },
      { text: "排序：AUC、校准与位置偏差", link: "/docs/Backend/RecommenderSystems/Ranking/index.md" },
      { text: "冷启动与探索：不探索就永远不知道", link: "/docs/Backend/RecommenderSystems/ColdStart/index.md" },
      { text: "在线服务：延迟预算、降级与兜底", link: "/docs/Backend/RecommenderSystems/Serving/index.md" },
      { text: "评估与实验：什么时候可以停", link: "/docs/Backend/RecommenderSystems/Evaluation/index.md" },
      { text: "实战：一个能跑起来的最小推荐服务", link: "/docs/Backend/RecommenderSystems/Practice/index.md" },
      { text: "常见问题与分诊", link: "/docs/Backend/RecommenderSystems/FAQ/index.md" },
    ],
  },
];
