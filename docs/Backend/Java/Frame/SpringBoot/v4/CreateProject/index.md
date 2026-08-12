# Spring Boot 项目搭建

本节从零创建一个 Spring Boot 4 项目：使用 Spring Initializr 生成骨架、用 IntelliJ IDEA 导入、跑通第一个接口，并解释项目结构与常用命令。

::: info 环境要求
JDK 17+（推荐 JDK 25 LTS）、Maven 3.9+ 或 Gradle 8.x+、IntelliJ IDEA 2024.3+（或 VS Code + Java 插件）。
:::

## 1. 使用 Spring Initializr 生成项目

打开 https://start.spring.io ，按下面配置生成：

| 配置项 | 建议值 |
| --- | --- |
| Project | Maven |
| Language | Java |
| Spring Boot | 4.1.x（当前稳定版） |
| Group | `com.example` |
| Artifact | `demo` |
| Java | 25（或 17/21） |
| Dependencies | Web、Validation、Actuator |

点击 Generate 下载 `demo.zip`，解压后得到标准骨架。

也可以直接使用命令行生成（需要 curl）：

```shell
curl https://start.spring.io/starter.zip \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=4.1.0 \
  -d groupId=com.example \
  -d artifactId=demo \
  -d javaVersion=25 \
  -d dependencies=web,validation,actuator \
  -o demo.zip
```

## 2. 导入 IDE

IntelliJ IDEA：

1. `File → Open` 选择解压后的目录。
2. 等待 Maven 自动导入依赖（右下角进度条完成）。
3. 打开 `DemoApplication.java`，点击 `main` 方法旁的运行按钮。

## 3. 项目结构

```text
demo/
├─ pom.xml                 # Maven 构建配置
├─ src/main/java/           # Java 源码
│  └─ com/example/demo/
│     ├─ DemoApplication.java   # 启动类
│     ├─ controller/            # 控制层
│     ├─ service/               # 业务层
│     └─ repository/            # 数据访问层
├─ src/main/resources/
│  ├─ application.properties    # 应用配置
│  └─ static/                   # 静态资源
└─ src/test/java/               # 测试代码
```

## 4. 第一个接口

```java [src/main/java/com/example/demo/controller/HelloController.java]
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot 4!";
    }
}
```

启动后访问 http://localhost:8080/hello ，页面显示 `Hello, Spring Boot 4!`。

## 5. 常用命令

```shell
# 开发运行
mvn spring-boot:run

# 打包（跳过测试）
mvn package -DskipTests

# 运行打包产物
java -jar target/demo-0.0.1-SNAPSHOT.jar

# 只运行测试
mvn test
```

## 6. pom.xml 关键内容

```xml [pom.xml]
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.1.0</version>
        <relativePath/>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <properties>
        <java.version>25</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

继承 `spring-boot-starter-parent` 后，不需要为 Spring 生态依赖写版本号，BOM 会统一管理。

## 易错点

::: danger 常见错误
1. 只装了 JDK 没配 `JAVA_HOME`，Maven 报 `Unable to locate a Java Runtime`。
2. `spring-boot-maven-plugin` 缺失，`mvn package` 打出的 jar 不是可执行 fat jar，`java -jar` 报「没有主清单属性」。
3. 端口被占用：`server.port` 或换端口后仍访问 8080。
4. 启动类位置不对，Controller 扫描不到，接口 404。
5. 依赖下载慢或失败：配置 Maven 镜像（阿里云/腾讯云）后重新导入。
:::

## 验证方式

1. `mvn -v` 确认 Maven 与 JDK 版本。
2. `mvn spring-boot:run` 控制台出现 `Started DemoApplication`。
3. 访问 `http://localhost:8080/hello` 返回预期文本。
4. `mvn package -DskipTests` 后 `java -jar target/demo-0.0.1-SNAPSHOT.jar` 能独立启动。
5. 访问 `http://localhost:8080/actuator/health` 返回 `{"status":"UP"}`。

## 参考资料

- Spring Initializr：https://start.spring.io/
- Spring Boot Maven 插件：https://docs.spring.io/spring-boot/maven-plugin/index.html
- Spring Boot 快速开始：https://spring.io/quickstart
