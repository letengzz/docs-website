# Spring Boot 数据访问

数据访问是后端应用的标配：连接数据库、定义实体、编写 Repository、管理事务。本节以 Spring Data JPA + MySQL 为例，并说明连接池与常见 ORM 的选型。

::: info 适用版本
本节基于 Spring Boot 4.1.x + Spring Data JPA + Hibernate + HikariCP；数据库以 MySQL 8.4 LTS 为例。
:::

## 引入依赖

```xml [pom.xml]
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

## 数据源配置

```yaml [application.yml]
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: ${DB_USER:root}
    password: ${DB_PASSWORD:root}
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 10
      minimum-idle: 2
      connection-timeout: 30000
  jpa:
    hibernate:
      ddl-auto: update     # 开发环境用 update，生产建议 validate 或关闭
    show-sql: true
    open-in-view: false
```

`ddl-auto` 取值：

| 值 | 行为 | 适用 |
| --- | --- | --- |
| `none` | 不做任何 DDL | 生产 |
| `validate` | 校验表结构与实体一致 | 生产 |
| `update` | 更新表结构 | 开发 |
| `create-drop` | 启动建表、停止删表 | 测试 |

生产环境建议用 Flyway 或 Liquibase 管理表结构，而不是依赖 Hibernate 自动建表。

## 实体与 Repository

```java [User.java]
package com.example.demo.entity;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    @Column(unique = true, nullable = false)
    private String email;

    private LocalDateTime createdAt = LocalDateTime.now();

    // getter / setter
}
```

```java [UserRepository.java]
package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);

    List<User> findByNameContaining(String keyword);

    boolean existsByEmail(String email);
}
```

方法名会自动翻译成查询：`findByNameContaining` → `WHERE name LIKE %keyword%`。复杂查询用 `@Query`：

```java
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface UserRepository extends JpaRepository<User, Long> {
    @Query("select u from User u where u.email like concat('%', :keyword, '%')")
    List<User> searchByEmail(@Param("keyword") String keyword);
}
```

## Service 与事务

```java [UserService.java]
package com.example.demo.service;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Transactional
    public User create(User user) {
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new IllegalArgumentException("邮箱已存在");
        }
        return userRepository.save(user);
    }

    @Transactional
    public void updateEmail(Long id, String email) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        user.setEmail(email);
        // 事务提交时自动 flush 更新
    }
}
```

`@Transactional` 保证方法内多个数据库操作要么全部成功、要么全部回滚。查询方法可加 `readOnly = true` 提升性能。

## 连接池 HikariCP

Spring Boot 默认使用 HikariCP，无需额外引入。关键参数：

| 参数 | 建议 | 说明 |
| --- | --- | --- |
| `maximum-pool-size` | 与并发量匹配（如 10~50） | 过大反而浪费数据库连接 |
| `minimum-idle` | 2~5 | 空闲保底连接 |
| `connection-timeout` | 30000 | 获取连接超时 |
| `max-lifetime` | 1800000 | 连接最大存活时间，建议小于数据库 wait_timeout |

## ORM 选型

| 方案 | 特点 | 适合 |
| --- | --- | --- |
| Spring Data JPA | 自动 CRUD、方法名查询、对象模型 | 领域模型复杂、快速开发 |
| MyBatis / MyBatis-Plus | SQL 可控、贴近数据库 | 复杂 SQL、已有 DBA 文化 |
| JdbcTemplate | 轻量、无 ORM 负担 | 简单查询、性能敏感 |
| Querydsl | 类型安全动态查询 | JPA 复杂查询 |

## 易错点

::: danger 常见错误
1. `open-in-view: true`（默认）导致 Controller 层仍持有会话，容易 N+1 和连接泄漏，生产建议关闭。
2. 实体间关联不设 `fetch = LAZY`，查询全表时级联加载全部数据。
3. 生产用 `ddl-auto: update`，上线时自动改表结构，风险高。
4. 密码写死在 `application.yml` 并提交 Git。
5. 大列表用 `findAll()` 一次性加载，应该用分页（`Pageable`）。
6. 事务方法内捕获异常后不重抛，事务可能不会回滚（默认只对 RuntimeException 回滚）。
:::

## 验证方式

1. 启动前在 MySQL 建库：`CREATE DATABASE demo CHARACTER SET utf8mb4;`。
2. `mvn spring-boot:run` 启动后，`show-sql` 能在控制台看到建表与查询 SQL。
3. 通过接口创建用户，MySQL 中能查到记录。
4. 重复创建相同邮箱返回「邮箱已存在」，且事务回滚不留脏数据。
5. 生产环境把 `ddl-auto` 改为 `validate`，实体与表结构不一致时启动失败并提示。

## 参考资料

- Spring Data JPA：https://docs.spring.io/spring-data/jpa/reference/
- HikariCP：https://github.com/brettwooldridge/HikariCP
- Flyway：https://documentation.red-gate.com/flyway
- MyBatis-Plus：https://baomidou.com/
