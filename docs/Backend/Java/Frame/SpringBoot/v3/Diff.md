# SpringBoot3改变 & 新特性

1. 自动配置包位置变化：
   `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

2. jakata api迁移：包名：`java.*`  --> `jakarta.*`
   
3. 新特性 - 函数式Web、ProblemDetails

4. GraalVM 与 AOT

5. 响应式编程

Jakarta 依赖 Spring Boot3.x 已经将所有底层依赖从 JavaEE 迁移到了 JarkartaEE，是基于 JakartaEE9 并尽可能地兼容 JakartaEE10。 

