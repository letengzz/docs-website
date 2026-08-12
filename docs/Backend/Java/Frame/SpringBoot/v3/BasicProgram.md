# SpringBoot 构建入门程序

:::tip 环境要求

- JDK：Java17
- Maven：3.6.8
- SpringBoot：3.0.9

:::

**官方教程**：https://docs.spring.io/spring-boot/docs/3.0.9/reference/html/

## 1. 构建SpringBoot项目

**SpringBoot 项目结构**：

![image-20230722213944365](assets/202307222143259.png)

### 使用Maven父工程构建

:::warning 说明

下列操作基于模块进行开发，仅创建SpringBoot项目时，将父工程\子模块中的依赖全部添加即可。

:::

**构建basic_program_parent工程**：

![image-20230722231822302](assets/202307222318010.png)

**创建子模块`springboot_hello`**：

![image-20230722232002367](assets/202307222320525.png)

**父工程添加依赖**：

```xml
<!--    所有springboot项目都必须继承自 spring-boot-starter-parent -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.0.9</version>
</parent>
```

**子工程添加依赖**：

```xml
<!-- 导入依赖：springboot通过自动版本仲裁 不需要关注版本问题 -->
<dependencies>
    <dependency>
    	<groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
	</dependency>
</dependencies>
```

**查看依赖**：

![image-20230722210039241](assets/202307222100838.png)

### 使用Maven依赖管理器构建

:::warning 说明

下列操作仅创建SpringBoot项目，创建基于模块进行开发，可先创建空项目，再进行创建模块操作下列步骤。

:::

**构建basic_program_dM项目**：

![image-20230722233424396](assets/202307222334335.png)

**添加依赖**：

```xml
<!-- 导入依赖：springboot通过自动版本仲裁 不需要关注版本问题 -->
<dependencies>
    <dependency>
    	<groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
	</dependency>
</dependencies>
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.0.9</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 使用Spring Initailizr构建

使用 Spring Initailizr 可以大量简化SpringBoot项目的开发。

**选择开发场景**：

- 官方脚手架：https://start.spring.io/
- 阿里脚手架：https://start.aliyun.com/

常见的 Spring Boot 脚手架工具和方法：

- Spring Initializr：这是 Spring 官方提供的工具，它允许开发者选择所需的依赖、Java 版本、构建工具(Maven 或 Gradle)以及其他配置选项来生成一个新的 Spring Boot 项目。
- IntelliJ IDEA 内置支持：IntelliJ IDEA 集成了 Spring Initializr 的功能，可以在 IDE 内直接创建 Spring Boot 项目。
- Start Alibaba Cloud：阿里云提供的 Start Alibaba Cloud 增强版工具，除了基本的 Spring Boot 模块外，还集成了阿里云服务和中间件的支持。
- JHipster：JHipster 是一个流行的脚手架工具，用于生成完整的 Spring Boot 应用程序，包括前端（Angular, React 或 Vue.js）和后端。它还包括用户管理和认证等功能。
- Yeoman Generators：Yeoman 是一个通用的脚手架工具，它有一个庞大的插件生态系统，其中包括用于生成 Spring Boot 项目的插件。
- Bootify：Bootify 是另一个用于生成 Spring Boot 应用程序的脚手架工具，提供了一些预定义的应用模板。
- Spring Boot CLI：Spring Boot CLI 是一个命令行工具，允许用户通过命令行来编写和运行 Spring Boot 应用。
- Visual Studio Code 插件：Visual Studio Code 社区提供了多个插件，如 Spring Boot Extension Pack，可以帮助开发者生成 Spring Boot 项目的基本结构。
- GitHub Gist 和 Bitbucket Templates：在 GitHub 和 Bitbucket 上，有很多开发者分享了用于生成 Spring Boot 项目的脚本或模板。
- 自定义脚手架：很多开发者也会根据自己的需求定制自己的脚手架工具，比如使用 Bash 脚本、Gradle 或 Maven 插件等。

![image-20230808144710182](assets/202308081447047.png)

在网站中可构建项目来进行开发，也可在IDEA中进行开发。

**创建`springboot_initailizr`项目**：

![image-20230722234225212](assets/202307222342152.png)

**选择版本及所需依赖**：

![image-20230722233927410](assets/202307222339835.png)

**自动引入依赖**：

![image-20230722235517116](assets/202307222355431.png)

**自动创建项目结构**：

![image-20230722235620962](assets/202307222356930.png)

**项目启动器**：

```java
@SpringBootApplication
public class SpringbootInitailizrApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringbootInitailizrApplication.class, args);
    }

}
```

## 2. 创建主程序类

:::danger 注意

业务层必须在主程序类所在的包或其子包下。

:::

```java [com.hjc.demo.MainApplication]
/**
 * 主程序类
 * SpringBootApplication等同于EnableAutoConfiguration+SpringBootConfiguration+ComponentScan("com.hjc.demo")
 * scanBasePackages扫描指定包
 * 主程序所在包及其下面的所有子包里面的组件都会被默认扫描进来
 * @author hjc
 */
@SpringBootApplication(scanBasePackages = "com.hjc.demo")
public class MainApplication {

    public static void main(String[] args) {
        //返回IoC容器
        ConfigurableApplicationContext run = SpringApplication.run(MainApplication.class, args);
        //查看容器中的组件
        String[] names = run.getBeanDefinitionNames();
        for (String name :
                names) {
            System.out.println("name = " + name);
        }

    }
}
```

## 3. 创建业务层

```java [com.hjc.demo.controller.HelloController]
/**
 * RestController 就是Controller 和ResponseBody的合体
 * @author hjc
 */
@RestController
public class HelloController {

    @RequestMapping("/hello")
    public String handle01() {
        return "Hello, Spring Boot!";
    }
}
```

## 4. 测试运行

执行运行主程序类中的main方法。

访问http://localhost:8080/hello即可。

![image-20230722212035522](assets/202307222120147.png)

## 5. 配置参数

在Spring Boot项目中，默认会提供一个application.properties或者application.yml文件，把一些全局性的配置或者需要动态维护的配置写入改文件，比如数据库连接，功能开关，限流阈值，服务地址等。

**配置文件名称必须为`application.properties`**：

- 集中式管理配置。只需要修改这个文件就行
- 配置基本都有默认值

**更多参数**：https://docs.spring.io/spring-boot/docs/3.0.9/reference/html/application-properties.html#appendix.application-properties

```properties [application.properties]
# 修改服务器的端口号 默认为8080
server.port=8888
```

## 6. 部署运行

Spring Boot提供了打包插件，可以将Spring Boot项目打包为可执行 jar 包。Web服务器(Tomcat)也会连同一块打入jar包中。只要安装了Java的运行环境(JDK)，就可以启动Spring Boot项目。

在pom.xml中添加插件：

```xml
<!-- 打包格式 -->
<packaging>jar</packaging>

<!-- 打包插件 -->
<build>
	<plugins>
    	<!-- 可以打成jar包：包括所有运行环境，可以直接运行jar包 -->
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                    <executable>true</executable>
                    <layout>JAR</layout>
            </configuration>
            <executions>
                <execution>
                    <goals>
                        <goal>repackage</goal>
                    </goals>
                    <configuration>
                        <attach>false</attach>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

![image-20230722212253815](assets/202307222122164.png)

把项目打成jar包，直接在目标服务器执行即可。

**项目打成可执行的jar包**：

```bash
mvn clean package
```

**运行**：

```bash
java -jar 包名.jar
```

**SpringBoot的jar包和普通jar包的区别**：Spring Boot 打包成的 JAR 文件与传统的 Java 应用程序中的 JAR 文件相比确实有一些显著的区别，主要体现在依赖管理和可执行性上。

依赖管理：

- Spring Boot 的 JAR 包通常包含了应用程序运行所需的所有依赖项，也就是说它是一个“fat jar”（胖 JAR 包），这种打包方式使得应用可以独立运行，而不需要外部的类路径或应用服务器上的其他依赖。
- 普通的 JAR 文件一般只包含一个类库的功能，并且需要依赖于特定的类路径来找到其他的类库或者框架，这些依赖项通常在部署环境中已经存在，比如在一个应用服务器中。

可执行性：

- Spring Boot 的 JAR 文件可以通过直接执行这个 JAR 文件来启动应用程序，也就是说它是一个可执行的 JAR 文件。通过 java -jar your-application.jar 命令就可以直接运行应用程序。
- 普通的 JAR 文件通常是不可直接执行的，需要通过指定主类（main class）的方式或者其他方式来启动一个应用程序，例如使用 -cp 或 -classpath 加上类路径以及主类名来执行。

Spring Boot 的这些特性使得部署和运行变得更加简单和方便，特别是在微服务架构中，每个服务都可以被打包成独立的 JAR 文件并部署到任何支持 Java 的地方。

SpringBoot的可执行jar包目录结构：

![image.png](assets/img202411161552820.webp)

普通jar包的目录结构：

![image.png](assets/img202411161552172.webp)
