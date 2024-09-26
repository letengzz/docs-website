# Spring Framework介绍

Spring 框架是一个分层的、面向切面的 Java 应用程序的一站式轻量级解决方案，它是 Spring 技术栈的核心和基础，是为了解决企业级应用开发的复杂性而创建的。

## Spring 核心模块

Spring 有两个最核心模块： IoC 和 AOP。

**IoC**(控制反转，`Inverse of Control`)： 把创建对象过程交给 Spring 进行管理。

**AOP**(面向切面编程，`Aspect Oriented Programming`) ：AOP 用来封装多个类的公共行为，将那些与业务无关，却为业务模块所共同调用的逻辑封装起来，减少系统的重复代码，降低模块间的耦合度。另外，AOP 还解决一些系统层面上的问题，比如日志、事务、权限等。

## Spring 特点

- **非侵入式**：使用 Spring Framework 开发应用程序时，Spring 对应用程序本身的结构影响非常小。对领域模型可以做到零污染；对功能性组件也只需要使用几个简单的注解进行标记，完全不会破坏原有结构，反而能将组件结构进一步简化。这就使得基于 Spring Framework 开发应用程序时结构清晰、简洁优雅。

- **控制反转**：IoC——Inversion of Control，翻转资源获取方向。把自己创建资源、向环境索取资源变成环境将资源准备好，我们享受资源注入。

- **面向切面编程**：AOP——Aspect Oriented Programming，在不修改源代码的基础上增强代码功能。

- **容器**：Spring IoC 是一个容器，因为它包含并且管理组件对象的生命周期。组件享受到了容器化的管理，替程序员屏蔽了组件创建过程中的大量细节，极大的降低了使用门槛，大幅度提高了开发效率。

- **组件化**：Spring 实现了使用简单的组件配置组合成一个复杂的应用。在 Spring 中可以使用 XML 和 Java 注解组合这些对象。这使得我们可以基于一个个功能明确、边界清晰的组件有条不紊的搭建超大型复杂应用系统。

- **一站式**：在 IoC 和 AOP 的基础上可以整合各种企业应用的开源框架和优秀的第三方类库。而且 Spring 旗下的项目已经覆盖了广泛领域，很多方面的功能性需求可以在 Spring Framework 的基础上全部使用 Spring 来实现。

## Spring 模块组成

![image-20230220154255847](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202307042000510.png)

![2097896352](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202307042002409.png)

包含了 Spring 框架的所有模块，这些模块可以满足一切企业级应用开发的需求，在开发过程中可以根据需求有选择性地使用所需要的模块。

- **Spring Core(核心容器)**：

  spring core提供了IOC,DI,Bean配置装载创建的核心实现。核心概念： Beans、BeanFactory、BeanDefinitions、ApplicationContext。

  - spring-core ：IOC和DI的基本实现，在 Spring 环境下使用任何功能都必须基于 IOC 容器。


  - spring-beans：BeanFactory和Bean的装配管理(BeanFactory)

  - spring-context：Spring context上下文，即IOC容器(AppliactionContext)

  - spring-expression：spring表达式语言


- **Spring AOP**：
  - spring-aop：面向切面编程的应用模块，整合ASM，CGLib，JDK Proxy
  
  - spring-aspects：集成AspectJ，AOP应用框架
  
  - spring-instrument：动态Class Loading模块
  
- **Spring Data Access**：

  - spring-jdbc：spring对JDBC的封装，用于简化jdbc操作

  - spring-orm：java对象与数据库数据的映射框架

  - spring-oxm：对象与xml文件的映射框架

  - spring-jms： Spring对Java Message Service(java消息服务)的封装，用于服务之间相互通信

  - spring-tx：spring jdbc事务管理

- **Spring Web**：

  - spring-web：最基础的web支持，建立于spring-context之上，通过servlet或listener来初始化IOC容器

  - spring-webmvc：实现web mvc

  - spring-websocket：与前端的全双工通信协议

  - spring-webflux：Spring 5.0提供的，用于取代传统java servlet，非阻塞式Reactive Web框架，异步，非阻塞，事件驱动的服务

- **Spring Message**：
  - Spring-messaging：spring 4.0提供的，为Spring集成一些基础的报文传送服务


- **Spring test**：
  - spring-test：集成测试支持，主要是对junit的封装

## Spring 主要优势

1.  丰富的生态系统：Spring 生态系统非常丰富，支持许多模块和库，如 Spring Boot、Spring Security、Spring Cloud 等等，可以帮助开发人员快速构建高可靠性的企业应用程序。
2.  模块化的设计：框架组件之间的松散耦合和模块化设计使得 Spring Framework 具有良好的可重用性、可扩展性和可维护性。开发人员可以轻松地选择自己需要的模块，根据自己的需求进行开发。
3.  简化 Java 开发：Spring Framework 简化了 Java 开发，提供了各种工具和 API，可以降低开发复杂度和学习成本。同时，Spring Framework 支持各种应用场景，包括 Web 应用程序、RESTful API、消息传递、批处理等等。
4.  不断创新和发展：Spring Framework 开发团队一直在不断创新和发展，保持与最新技术的接轨，为开发人员提供更加先进和优秀的工具和框架。

因此，这些优点使得 Spring Framework 成为了一个稳定、可靠、且创新的框架，为企业级 Java 开发提供了一站式的解决方案。

Spring 使创建 Java 企业应用程序变得容易。它提供了在企业环境中采用 Java 语言所需的一切，支持 Groovy 和 Kotlin 作为 JVM 上的替代语言，并且可以根据应用程序的需求灵活地创建多种架构。

## Spring 版本要求

从Spring Framework 6开始，Spring 需要 Java 17+(**JDK最低版本是JDK17**)：

![image-20221201103138194](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202307042002052.png)

