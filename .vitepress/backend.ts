// .Net
export const DotNet = [
  {
    text: ".Net",
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
              { text: "Spring 6", link: "/docs/Backend/Java/Frame/Spring/Spring6/index.md" },
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
              { text: "Spring Boot 2.x", link: "/docs/Backend/Java/Frame/SpringBoot/v2/index.md" },
              { text: "Spring Boot 3.x", link: "/docs/Backend/Java/Frame/SpringBoot/v3/index.md" },
              { text: "Spring Boot 4.x（当前稳定版）", link: "/docs/Backend/Java/Frame/SpringBoot/v4/index.md" },
            ],
          },
          { text: "Spring Security", link: "/docs/Backend/Java/Frame/SpringSecurity/index.md" },
          { text: "Spring Cloud", link: "/docs/Backend/Java/Frame/SpringCloud/index.md" },
          { text: "MyBatis", link: "/docs/Backend/Java/Frame/MyBatis/index.md" },
          { text: "MyBatis-Plus", link: "/docs/Backend/Java/Frame/MyBatisPlus/index.md" },
          { text: "MyBatis-Flex", link: "/docs/Backend/Java/Frame/MyBatis-Flex/index.md" },
          { text: "Sa-Token", link: "/docs/Backend/Java/Frame/Sa-token/index.md" },
        ],
      },
      { text: "其他", link: "/docs/Backend/Java/Others/index.md" },
    ],
  },
];
export const MessageQueue = [
  {
    text: "消息队列",
    link: "/docs/Backend/MessageQueue/index.md",
    items: [
      { text: "概念与选型", link: "/docs/Backend/MessageQueue/Overview/index.md" },
      { text: "Kafka 入门", link: "/docs/Backend/MessageQueue/Kafka/index.md" },
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
      { text: "分布式事务", link: "/docs/Backend/Microservices/DistributedTransaction/index.md" },
      { text: "实战：订单库存账户微服务", link: "/docs/Backend/Microservices/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/Microservices/FAQ/index.md" },
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
      { text: "粘包拆包与编解码", link: "/docs/Backend/NetworkProgramming/StickyHalf/index.md" },
      { text: "实战：Netty 聊天服务器", link: "/docs/Backend/NetworkProgramming/Practice/index.md" },
      { text: "常见问题与最佳实践", link: "/docs/Backend/NetworkProgramming/FAQ/index.md" },
    ],
  },
];
export const Go = [{ text: "Go", link: "/docs/Backend/Go/index.md" }];
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
