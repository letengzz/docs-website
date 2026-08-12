# SpringBoot 依赖管理和自动配置

## 依赖管理

### 作为父项目和作为依赖的区别

**继承父工程的优势**

- 依赖管理：可以在父工程中定义依赖的版本，子模块可以直接引用而不必指定版本号。
- 插件管理：可以在父工程中配置常用的插件及其版本，子模块可以直接使用这些配置。
- 属性设置：可以在父工程中定义一些通用的属性，如项目编码、Java 版本等。
- 统一配置：可以统一多个子模块的构建配置，确保一致性。

**直接引入依赖的局限性**（如果你不使用继承父工程的方式，而是通过直接引入依赖的方式来管理项目，那么你将失去上述的一些优势）

- 依赖版本管理：每个子模块都需要单独指定依赖的版本，这会导致大量的重复配置，并且难以维护。
- 插件配置：每个子模块都需要单独配置插件及其版本，无法共享父工程中的插件配置。
- 属性设置：每个子模块都需要单独设置通用的属性，如项目编码、Java 版本等。
- 构建配置：每个子模块的构建配置需要单独维护，难以保证一致性。

**<font style="color:#DF2A3F;">总结：选择哪种方式取决于你的具体需求。</font>**

- **<font style="color:#DF2A3F;">如果你希望多个项目之间共享构建配置，那么使用父项目是一个好的选择；</font>**
- **<font style="color:#DF2A3F;">如果你只是想在项目之间共享代码，那么应该使用依赖关系。</font>**

### 自动版本仲裁

因为配置了SpringBoot父项目(`spring-boot-starter-parent`的父项目`spring-boot-dependencies`中配置了相关信息)，所以引入父项目已有的依赖都可以不写版本，这称为**自动版本仲裁机制**。

:::danger 注意

引⼊非版本仲裁的jar，需要要写版本号，比如Mybatis。

:::

**好处**：

1. **简化依赖声明**：开发者只需要在 `pom.xml` 文件中声明需要的依赖而不需要指定其版本号，因为 Spring Boot 已经为这些依赖指定了版本。例如，如果需要使用mysql驱动，你只需要添加相应的依赖声明而不需要关心版本。

2. **避免版本冲突**：当多个库之间存在依赖关系的时候，如果手动管理版本可能会导致版本之间的冲突（即“依赖地狱”）。Spring Boot 提供的统一版本管理可以减少这种冲突的可能性。
3. **易于升级**：当 Spring Boot 发布新版本时，通常会更新其依赖库到最新稳定版。因此，当你升级 Spring Boot 版本时，它所管理的所有依赖也会随之更新到兼容的版本。
4. **减少配置错误**：由于 Spring Boot 自动处理了依赖的版本，减少了手动输入版本号可能引入的拼写或格式错误。
5. **提高开发效率**：开发者可以专注于业务逻辑的编写，而不是花费时间在解决依赖问题上。

总的来说，Spring Boot 的依赖管理功能使得开发者可以更加专注于业务逻辑的实现，同时减少了因依赖版本不一致而引发的问题，提高了项目的可维护性和开发效率。

**父项目几乎声明了所有开发中常用的依赖的版本号**：

![image-20230722222430548](assets/202307222226770.png)

![image.png](assets/202307222256042.png)

### 修改仲裁版本

利用maven的**就近原则**：

- 直接在当前项目`properties`标签中声明父项目用的版本属性的key：

  ```xml
  <properties>
  	<mysql.version>8.1.0</mysql.version>
  </properties>
  ```

- 直接在**导入依赖的时候声明版本**：

  ```xml
  <dependency>
  	<groupId>com.mysql</groupId>
      <artifactId>mysql-connector-j</artifactId>
      <version>8.1.0</version>
  </dependency>
  ```

### starter场景启动器

在 Spring Boot 中，启动器 (Starter) 本质上是一个简化依赖管理的概念。

Spring Boot 的启动器本质上就是一组预定义的依赖集合，它们被组织成一个个 Maven的依赖，以方便开发者快速集成特定的功能模块。

**启动器实现原理**：

1. **依赖聚合**：每个启动器通常对应一个特定的功能集或者一个完整的应用模块，如 `spring-boot-starter-web` 就包含了构建 Web 应用所需的所有基本依赖项，如 Spring MVC, Tomcat 嵌入式容器等。
2. **依赖传递**：当你在项目中引入一个启动器时，它不仅会把自身作为依赖加入到你的项目中，还会把它的所有直接依赖项（transitive dependencies）也加入进来。这意味着你不需要单独声明这些依赖项，它们会自动成为项目的一部分。
3. **版本管理**：启动器内部已经指定了所有依赖项的具体版本，这些版本信息存储在一个公共的 BOM（Bill of Materials，物料清单）文件中，通常是 `spring-boot-dependencies`。当引入启动器时，实际上也间接引用了这个 BOM，从而确保了所有依赖项版本的一致性。
4. **自动配置**：许多启动器还提供了自动配置（Auto-configuration），这是一种机制，允许 Spring Boot 根据类路径上的可用组件自动设置你的应用程序。例如，如果类路径上有 Spring MVC 和嵌入式 Tomcat，则 Spring Boot 会自动配置它们，并准备好一个 web 应用程序。

`spring-boot-starter-*`：`*`代表某种场景，比如：`spring-boot-starter-web`表示web开发场景

只要引入starter，这个场景的所有常规需要的依赖都会自动的引入，所有场景启动器最底层的依赖：`spring-boot-starter`

- 官方提供简化开发的场景启动器：命名为：`spring-boot-starter-*`

  ![](assets/img202411172030764.png)

- 第三方提供简化开发的场景启动器：命名为：`*-spring-boot-starter`

  ![](assets/img202411172030855.png)

默认支持的所有场景：https://docs.spring.io/spring-boot/docs/current/reference/html/using.html#using.build-systems.starters

## 自动配置

### 自动配置Tomcat

SpringBoot能够自动引入Tomcat依赖，同时自动进行Tomcat配置

**Tomcat依赖**：

![image-20230723202609497](assets/202307232027310.png)

### 自动配好SpringMVC

SpringBoot能够自动引入SpringMVC全套组件并配置好SpringMVC的常用组件，如：字符编码问题

![image-20230723203327808](assets/202307232033251.png)

在启动器中查看容器中的组件：

```java
public static void main(String[] args) {

        //var: 局部变量类型的自动推断
        var ioc = SpringApplication.run(MainApplication.class, args);

        //1、获取容器中所有组件的名字
        String[] names = ioc.getBeanDefinitionNames();
        //2、挨个遍历：
        // dispatcherServlet、beanNameViewResolver、characterEncodingFilter、multipartResolver
        // SpringBoot把配置的核心组件现在都给自动配置好了。
        for (String name : names) {
            System.out.println(name);
        }
}
```

### 包扫描路径

#### 默认的包扫描规则

`@SpringBootApplication` 标注的类就是主程序类。

**SpringBoot只会扫描主程序所在的包及其下面的所有子包里面的组件，都会被默认扫描进来。**

**改变扫描路径**：

- `@SpringBootApplication(scanBasePackages="com.hjc")`

- 指定扫描路径：`@ComponentScan("com.hjc")`

### 自动配置 配置默认值

**配置文件**的所有配置项是和某个**类的对象**值进行一一绑定的。

绑定了配置文件中每一项值的类： **属性类**。

**例**：

- `ServerProperties`绑定了所有Tomcat服务器有关的配置
- `MultipartProperties`绑定了所有文件上传相关的配置

参照[官方文档](https://docs.spring.io/spring-boot/docs/current/reference/html/application-properties.html#appendix.application-properties.server)或者参照 绑定的 **属性类**。

### 按需加载所有自动配置项

SpringBoot所有的自动配置功能都在`spring-boot-autoconfigure`包里面。

[场景启动器](#starter场景启动器)除了会导入相关功能依赖，导入一个`spring-boot-starter`(基础核心starter)，是所有`starter`的`starter`

`spring-boot-starter`导入了一个包 `spring-boot-autoconfigure`。包里面都是各种场景的`AutoConfiguration`**自动配置类**

虽然全场景的自动配置都在 `spring-boot-autoconfigure`这个包，但是不是全都开启的，导入哪个场景就开启哪个自动配置(自动配置生效)。

**SpringBoot启动会默认加载 142个配置类**：

**142个配置类**来自于`spring-boot-autoconfigure`下 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`文件指定的。

项目启动的时候利用 [`@Import`](Annotation.md) 批量导入组件机制把 `autoconfigure` 包下的142 `xxxxAutoConfiguration`类(**自动配置类**)导入进来

![image-20230727230833628](assets/202307272308589.png)

![image-20230727231152519](assets/202307272311007.png)

虽然导入了`142`个自动配置类，并不是这`142`个自动配置类都能生效

每一个自动配置类，都有条件注解`@ConditionalOnxxx`，只有条件成立，才能生效

**例**：因为Kafka类不存在，所以KafkaAutoConfiguration自动配置不加载。

![image-20230727223448337](assets/202307272235441.png)

### 自动配置流程

1. 导入`starter-web`(导入web开发场景)：

   - 场景启动器导入了相关场景的所有依赖：`starter-json`、`starter-tomcat`、`springmvc`

   - 每个场景启动器都引入了一个**核心场景启动器**`spring-boot-starter`。

   - **核心场景启动器**引入了`spring-boot-autoconfigure`包。

     `spring-boot-autoconfigure`里面囊括了所有场景的所有配置。只要这个包下的所有类都能生效，那么相当于SpringBoot整合功能就生效了。

   - SpringBoot默认却扫描不到 `spring-boot-autoconfigure`下写好的所有**配置类**(**配置类**做了整合操作)。**默认只扫描主程序所在的包**。

2. **主程序**：`@SpringBootApplication`：`@SpringBootApplication`由三个注解组成`@SpringBootConfiguration`、`@EnableAutoConfiguration`、`@ComponentScan`

   - SpringBoot默认只能扫描自己主程序所在的包及其下面的子包，扫描不到 `spring-boot-autoconfigure`包中官方写好的**配置类**

   - `@EnableAutoConfiguration`：SpringBoot **开启自动配置的核心**。

     - 由`@Import(AutoConfigurationImportSelector.class)`提供功能：批量给容器中导入组件。

     - SpringBoot启动会默认加载 142个配置类。

     - 这**142个配置类**来自于`spring-boot-autoconfigure`下 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`文件指定的。

     - 项目启动的时候利用 [`@Import`](Annotation.md) 批量导入组件机制把 `autoconfigure` 包下的142 `xxxxAutoConfiguration`类(**自动配置类**)导入进来

   - 按需生效：

     - 虽然导入了`142`个自动配置类，并不是这`142`个自动配置类都能生效

     - 每一个自动配置类，都有条件注解`@ConditionalOnxxx`，只有条件成立，才能生效

3. `xxxxAutoConfiguration`**自动配置类**：

   - **给容器中使用@Bean 放一堆组件。**

   - 每个**自动配置类**都可能有`@EnableConfigurationProperties(ServerProperties.class)`，用来把配置文件中配的指定前缀的属性值封装到 `xxxProperties`**属性类**中

   - 以Tomcat为例：把服务器的所有配置都是以`server`开头的。配置都封装到了属性类中。

   - 给**容器**中放的所有**组件**的一些**核心参数**，都来自于`xxxProperties`**。**`xxxProperties`**都是和配置文件绑定。**

   - **只需要改配置文件的值，核心组件的底层参数都能修改**

4. 写业务，全程无需关心各种整合(底层进行整合并且生效)

![image-20230728000227586](assets/202307280002773.png)
