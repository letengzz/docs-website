# Maven profile

项目的每一个运行环境，相当于是项目整体的一个侧面。

![images](data:image/png;base64,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)

**项目的不同运行环境**：

通常情况下，至少有三种运行环境：

- 开发环境：供不同开发工程师开发的各个模块之间互相调用、访问；内部使用
- 测试环境：供测试工程师对项目的各个模块进行功能测试；内部使用
- 生产环境：供最终用户访问——所以这是正式的运行环境，对外提供服务

![images](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311072128299.png)

而环境仍然只是一个笼统的说法，实际工作中一整套运行环境会包含很多种不同服务器：

- MySQL
- Redis
- ElasticSearch
- RabbitMQ
- FastDFS
- Nginx
- Tomcat
- ……

就拿其中的 MySQL 来说，不同环境下的访问参数肯定完全不同：

![image-20231107213502064](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311072135362.png)

可是代码只有一套。如果在 jdbc.properties 里面来回改，那就太麻烦了，而且很容易遗漏或写错，增加调试的难度和工作量。所以最好的办法就是把适用于各种不同环境的配置信息分别准备好，部署哪个环境就激活哪个配置。

在 Maven 中，使用 profile 机制来管理不同环境下的配置信息。但是解决同类问题的类似机制在其他框架中也有，而且从模块划分的角度来说，持久化层的信息放在构建工具中配置也违反了『**高内聚，低耦合**』的原则。

**profile 声明和使用的基本逻辑**：

- 首先为每一个环境声明一个 profile
  - 环境 A：profile A
  - 环境 B：profile B
  - 环境 C：profile C
  - ……
- 然后激活某一个 profile

**默认 profile**：

其实即使在 pom.xml 中不配置 profile 标签，也已经用到 profile了。因为根标签 project 下所有标签相当于都是在设定默认的 profile。project 标签下除了 modelVersion 和坐标标签之外，其它标签都可以配置到 profile 中。

## profile 配置

### 外部视角：配置文件

从外部视角来看，profile 可以在下面两种配置文件中配置：

- settings.xml：全局生效。其中最熟悉的就是配置 JDK 1.8。
- pom.xml：当前 POM 生效

### 内部实现：具体标签

从内部视角来看，配置 profile 有如下语法要求：

#### profiles/profile 标签

- 由于 profile 天然代表众多可选配置中的一个所以由复数形式的 profiles 标签统一管理。
- 由于 profile 标签覆盖了 pom.xml 中的默认配置，所以 profiles 标签通常是 pom.xml 中的最后一个标签。

#### id 标签

每个 profile 都必须有一个 id 标签，指定该 profile 的唯一标识。这个 id 标签的值会在命令行调用 profile 时被用到。

**命令格式**：`-D<profile id>`。

#### 其它允许出现的标签

一个 profile 可以覆盖项目的最终名称、项目依赖、插件配置等各个方面以影响构建行为。

- build
  - defaultGoal
  - finalName
  - resources
  - testResources
  - plugins
- reporting
- modules
- dependencies
- dependencyManagement
- repositories
- pluginRepositories
- properties

## 激活 profile

### 默认配置默认被激活

POM 中没有在 profile 标签里的就是默认的 profile，当然默认被激活。

### 基于环境信息激活

环境信息包含：JDK 版本、操作系统参数、文件、属性等各个方面。一个 profile 一旦被激活，那么它定义的所有配置都会覆盖原来 POM 中对应层次的元素。

**例**：

```xml
<profile>
    <!-- id标签：唯一标识 -->
	<id>dev</id>
    <!-- activation 标签：激活方式 -->
    <activation>
        <!-- activeByDefault 标签：配置是否默认激活 -->
    	<activeByDefault>false</activeByDefault>
        <!-- jdk 标签：标识当前profile 可以根据 JDK 版本来激活 -->
        <jdk>1.5</jdk>
        <os>
        	<name>Windows XP</name>
            <family>Windows</family>
            <arch>x86</arch>
            <version>5.1.2600</version>
        </os>
        <property>
        	<name>mavenVersion</name>
            <value>2.0.5</value>
        </property>
        <file>
        	<exists>file2.properties</exists>
            <missing>file1.properties</missing>
        </file>
    </activation>
</profile>
```

多个激活条件的关系：

- Maven **3.2.2 之前**：遇到第一个满足的条件即可激活：**或**的关系。
- Maven **3.2.2 开始**：各条件均需满足：**且**的关系。

**例**：假设有如下 profile 配置，在 JDK 版本为 1.6 时被激活：

```xml
<profiles>
	<profile>
    	<id>JDK1.6</id>
        <activation>
            <!-- 指定激活条件为：JDK 1.6 -->
        	<jdk>1.6</jdk>
        </activation>
        ……
    </profile>
</profiles>
```

Maven 会自动检测当前环境安装的 JDK 版本，只要 JDK 版本是以 1.6 开头都算符合条件。下面几个例子都符合：

- 1.6.0_03
- 1.6.0_02
- ……

### 命令行激活

#### 列出活动的 profile

```sh
# 列出所有激活的 profile，以及它们在哪里定义
mvn help:active-profiles
```

#### 指定某个具体 profile

```xml
mvn compile -P<profile id>
```

## 操作

### 编写 Lambda 表达式代码

Lambda 表达式代码要求 JDK 版本必须是 1.8，可以以此来判断某个指定更低 JDK 版本的 profile 是否被激活生效。

```java
@Test
public void test() {
    new Thread(()->{
        System.out.println(Thread.currentThread().getName() + " is working");
    }).start();
}
```

以目前配置运行这个测试方法：

![image-20231107230311037](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311072303378.png)

### 配置 profile

```xml
<profiles>
    <profile>
        <id>myJDKProfile</id>
        <!-- build 标签：定制构建行为 -->
        <build>
            <!-- plugins 标签：构建的时候要用到的插件 -->
            <plugins>
                <!-- plugin 标签：指定具体的插件 -->
                <plugin>
                    <!-- 插件的坐标。此处引用的 maven-compiler-plugin 插件不是第三方的，是一个 Maven 自带的插件。 -->
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>3.1</version>

                    <!-- configuration 标签：配置 maven-compiler-plugin 插件 -->
                    <configuration>
                        <!-- 具体配置信息会因为插件不同、需求不同而有所差异 -->
                        <source>1.6</source>
                        <target>1.6</target>
                        <encoding>UTF-8</encoding>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

### 执行构建命令

```sh
mvn clean test -PmyJDKProfile
```

![image-20231107230702526](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311072307196.png)

## 资源属性过滤

Maven 为了能够通过 profile 实现各不同运行环境切换，提供了一种『资源属性过滤』的机制。通过属性替换实现不同环境使用不同的参数。

### 配置 profile

```xml
<profiles>
    <profile>
        <id>devJDBCProfile</id>
        <properties>
            <dev.jdbc.user>root</dev.jdbc.user>
            <dev.jdbc.password>hjc</dev.jdbc.password>
            <dev.jdbc.url>http://localhost:3306/db_good</dev.jdbc.url>
            <dev.jdbc.driver>com.mysql.jdbc.Driver</dev.jdbc.driver>
        </properties>
        <build>
            <resources>
                <resource>
                    <!-- 表示为这里指定的目录开启资源过滤功能 -->
                    <directory>src/main/resources</directory>

                    <!-- 将资源过滤功能打开 -->
                    <filtering>true</filtering>
                </resource>
            </resources>
        </build>
    </profile>
</profiles>
```

### 创建待处理的资源文件

```properties
dev.user=${dev.jdbc.user}
dev.password=${dev.jdbc.password}
dev.url=${dev.jdbc.url}
dev.driver=${dev.jdbc.driver}
```

### 执行处理资源命令

```sh
mvn clean resources:resources -PdevJDBCProfile
```

### 找到处理得到的资源文件

![image-20231107233255085](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311072332406.png)

#### 延伸

在 resource 标签下includes 和 excludes 标签作用：

- includes：指定执行 resource 阶段时要包含到目标位置的资源
- excludes：指定执行 resource 阶段时要排除的资源

**例**：

```xml
<build>
    <resources>
        <resource>
            <!-- 表示为这里指定的目录开启资源过滤功能 -->
            <directory>src/main/resources</directory>

            <!-- 将资源过滤功能打开 -->
            <filtering>true</filtering>

            <includes>
                <include>*.properties</include>
            </includes>

            <excludes>
                <exclude>happy.properties</exclude>
            </excludes>
        </resource>
    </resources>
</build>
```

执行处理资源命令：

```sh
mvn clean resources:resources -PdevJDBCProfile
```

执行效果：

![image-20231107233805709](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311072338632.png)

当然这里只是以 properties 文件为例，并不是只能处理 properties 文件。