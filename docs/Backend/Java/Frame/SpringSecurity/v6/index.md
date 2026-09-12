# Spring Security 6

Spring Security 是一个功能强大且高度可定制的**认证与授权框架**，核心能力包括：**认证（用户登录）、授权（能做什么）与攻击防护（防伪造身份等）**。6.x 是当前**上一代主线**，对应 **Spring Boot 3.x**，在企业存量与新建项目中都很常见。

![img](assets/202309201637507.jpeg)

::: info 版本状态
6.x 属**上一代主线**（仍在维护与广泛使用）；新项目建议直接使用 [Spring Security 7](../v7/index.md)（对应 Spring Boot 4.x）。概念层面的认证授权知识见 [认证与授权专题](../../../../Auth/index.md)。
:::

## 目录

- [Spring Security 概述](Overview.md)
- 基于 Spring 创建
  - [Spring Security 构建入门程序](Spring/BasicProgram/index.md)
  - [Spring Security 认证](Spring/Authentication/index.md)
  - [Spring Security 授权](Spring/Authorization/index.md)
  - [Spring Security 其他配置](Spring/Other/index.md)
  - [Spring Security 原理](Spring/Principle/index.md)
- 基于 Spring Boot 创建
  - [Spring Security 构建入门程序](SpringBoot/BasicProgram/index.md)
  - [Spring Security 认证](SpringBoot/Authentication/index.md)
  - [Spring Security 授权](SpringBoot/Authorization/index.md)
  - [Spring Security 其他配置](SpringBoot/Other/index.md)
  - [Spring Security 原理](SpringBoot/Principle/index.md)
  - [会话（Session）](SpringBoot/Session/index.md)
- 专项
  - [JWT](JWT/index.md)
  - [OAuth2](OAuth2/index.md)
  - [Spring Security 常见错误](Errors.md)

## 学习顺序建议

| 顺序 | 内容 | 说明 |
| --- | --- | --- |
| 1 | 认证授权基础概念 | 先读 [认证与授权专题](../../../../Auth/index.md)，区分认证与授权 |
| 2 | 入门程序 | 跑通默认配置与登录流程 |
| 3 | 认证 | 内存/数据库/自定义认证，前后端分离 |
| 4 | 授权 | 角色、权限点与注解式授权 |
| 5 | 专项 | JWT、OAuth2（资源服务器/客户端） |
| 6 | 其他配置 | CSRF、跨域、会话并发、记住我 |

## 常见错误

- [Spring Security 常见错误](Errors.md)：配置类写法、过滤器链顺序、跨域与 CSRF 的高频问题
