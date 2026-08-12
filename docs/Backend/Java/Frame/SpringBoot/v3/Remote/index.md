# SpringBoot 远程调用

![image.png](assets/202308181530050.png)

**本地过程调用**： `a();` `b();` `a() { b();}`： 不同方法都在同一个JVM运行

**远程过程调用** (RPC:Remote Procedure Call)：通过连接对方服务器进行请求\响应交互，来实现调用效果：

- 服务提供者：
- 服务消费者：

**API/SDK区别**：

- api：接口 (Application Programming Interface)

  - 远程提供功能

- sdk：工具包 (Software Development Kit)
  - 导入jar包，直接调用功能即可

开发过程中，需要经常调用别人写的功能：

- 如果是内部微服务，可以通过依赖cloud、注册中心、openfeign等进行调用
- 如果是外部暴露的，可以发送 http 请求、或遵循外部协议进行调用

**SpringBoot 整合提供了很多方式进行远程调用**：

- 轻量级客户端方式：
  - [RestTemplate](RestTemplate.md)： 普通开发
  - [WebClient](WebClient.md)： 响应式编程开发
  - [Http Interface](HttpInterface.md)： 声明式编程
- Spring Cloud分布式解决方案方式：
  - [Spring Cloud OpenFeign](../../../SpringCloud/2022/SpringCloud/OpenFeign.md)
- 第三方框架：
  - Dubbo
  - gRPC
  - ...
