# Spring Boot 测试

测试是 Spring Boot 项目质量的底线。本节覆盖单元测试、切片测试（Web 层/数据层）、MockMvc 接口测试和 Testcontainers 数据库测试。

::: info 适用版本
本节为 Spring Boot 通用指南，示例基于 4.1.x；测试依赖 `spring-boot-starter-test`（包含 JUnit 5、AssertJ、Mockito、MockMvc）。
:::

## 引入测试依赖

```xml [pom.xml]
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

## 测试分层

| 测试类型 | 注解 | 加载范围 | 速度 |
| --- | --- | --- | --- |
| 单元测试 | 无（纯 JUnit） | 单个类 | 最快 |
| Web 切片 | `@WebMvcTest` | Controller + MVC | 快 |
| 数据切片 | `@DataJpaTest` | Repository + JPA | 较快 |
| 集成测试 | `@SpringBootTest` | 完整上下文 | 慢 |

## 单元测试 Service

用 Mockito 模拟 Repository：

```java [UserServiceTest.java]
package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void findById_用户不存在_抛出异常() {
        given(userRepository.findById(1L)).willReturn(Optional.empty());

        assertThatThrownBy(() -> userService.findById(1L))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("用户不存在");
    }

    @Test
    void updateEmail_用户存在_更新邮箱() {
        User user = new User();
        user.setId(1L);
        user.setEmail("old@example.com");
        given(userRepository.findById(1L)).willReturn(Optional.of(user));

        userService.updateEmail(1L, "new@example.com");

        assertThat(user.getEmail()).isEqualTo("new@example.com");
    }
}
```

## Web 切片测试 MockMvc

```java [UserControllerTest.java]
package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.service.UserService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserService userService;

    @Test
    void detail_返回用户JSON() throws Exception {
        User user = new User();
        user.setId(1L);
        user.setName("张三");
        given(userService.findById(1L)).willReturn(user);

        mockMvc.perform(get("/api/users/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("张三"));
    }
}
```

## 数据切片测试

```java [UserRepositoryTest.java]
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_能查到() {
        User user = new User();
        user.setName("张三");
        user.setEmail("zhangsan@example.com");
        userRepository.save(user);

        Optional<User> found = userRepository.findByEmail("zhangsan@example.com");

        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("张三");
    }
}
```

`@DataJpaTest` 默认使用内存数据库（如 H2），需要在测试 classpath 加 H2：

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

## 集成测试 + Testcontainers

需要真实 MySQL 时用 Testcontainers：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-testcontainers</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>mysql</artifactId>
    <scope>test</scope>
</dependency>
```

```java [UserIntegrationTest.java]
package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class UserIntegrationTest {

    @Container
    @ServiceConnection
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.4");

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void 健康检查返回UP() {
        ResponseEntity<String> response =
                restTemplate.getForEntity("/actuator/health", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("\"UP\"");
    }
}
```

`@ServiceConnection`（Spring Boot 3.1+）会自动把容器的地址注入数据源配置，无需手写属性。

## 覆盖率

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.13</version>
</plugin>
```

```shell
mvn test jacoco:report
```

打开 `target/site/jacoco/index.html` 查看覆盖率。团队可以约定核心业务模块覆盖率不低于 80%。

## 易错点

::: danger 常见错误
1. `@SpringBootTest` 启动完整上下文，测试慢且依赖外部服务，能用切片测试就不用集成测试。
2. 测试里访问真实数据库，数据互相污染；用 `@DataJpaTest` + 内存库或 Testcontainers。
3. MockMvc 测试没加 `@WebMvcTest`，加载了完整上下文。
4. 忘记 `@MockBean`（或 `@MockitoBean`）模拟依赖，测试连真实 Service 一起跑。
5. 异步代码（线程池、定时任务）在测试中难以断言，需要注入时钟或等待条件。
6. 只测「成功路径」，不测异常和边界。
:::

## 验证方式

1. `mvn test` 全部通过。
2. `mvn test jacoco:report` 生成覆盖率报告并打开查看。
3. 故意改坏一个 Service 逻辑，对应测试失败，确认测试真的有效。
4. Testcontainers 测试需要本机 Docker，运行前确认 `docker ps` 可用。
5. CI 中 `mvn verify` 作为发布前置检查。

## 相关专题

- [CI/CD 自动化测试与质量门禁](../../../../../../Tools/CICD/Testing/index.md)：覆盖率统计、SonarQube 门禁与 E2E 在流水线中的组织
- [CI/CD 概念与流水线设计](../../../../../../Tools/CICD/Overview/index.md)：测试在流水线阶段的定位

## 参考资料

- Spring Boot 测试文档：https://docs.spring.io/spring-boot/reference/testing/index.html
- JUnit 5：https://junit.org/junit5/
- Testcontainers：https://testcontainers.com/
- MockMvc：https://docs.spring.io/spring-framework/reference/testing/spring-mvc-test-framework.html
