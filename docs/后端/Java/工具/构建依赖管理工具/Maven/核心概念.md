# Maven 核心概念

## 坐标

Maven使用三个**向量**在**Maven的仓库**中**唯一**的定位到一个**jar**包。

- **groupId**：公司或组织的 id
- **artifactId**：一个项目或者是项目中的一个模块的 id
- **version**：版本号

### 取值方式

三个向量的取值方式

- groupId：公司或组织域名的倒序，通常也会加上项目名称
  - 例如：com.hjc.maven
- artifactId：模块的名称，将来作为 Maven 工程的工程名
- version：模块的版本号，根据自己的需要设定
  - SNAPSHOT 表示快照版本，正在迭代过程中，不稳定的版本
  - RELEASE 表示正式版本

**例**：

- groupId：com.hjc.maven
- artifactId：pro01-hjc-maven
- version：1.0-SNAPSHOT

### 坐标与存储路径对应关系

坐标和仓库中 jar 包的存储路径之间的对应关系：

坐标：

```xml
  <groupId>javax.servlet</groupId>
  <artifactId>servlet-api</artifactId>
  <version>2.5</version>
```

上面坐标对应的 jar 包在 Maven 本地仓库中的位置：

> Maven本地仓库根目录\javax\servlet\servlet-api\2.5\servlet-api-2.5.jar

一定要学会根据坐标到本地仓库中找到对应的 jar 包。

## POM

POM(**P**roject **O**bject **M**odel)项目对象模型。

和 POM 类似的是：DOM（Document Object Model），文档对象模型。

它们都是模型化思想的具体体现。

**模型化思想**：

POM 表示将工程抽象为一个模型，再用程序中的对象来描述这个模型。这样就可以用程序来管理项目了。在开发过程中，最基本的做法就是将现实生活中的事物抽象为模型，然后封装模型相关的数据作为一个对象，这样就可以在程序中计算与现实事物相关的数据。

**对应的配置文件**：

POM 理念集中体现在 Maven 工程根目录下 **pom.xml** 这个配置文件中。所以这个 pom.xml 配置文件就是 Maven 工程的核心配置文件。

## 目录结构

### 各个目录的作用

![./images](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231845410.png)

另外还有一个 target 目录专门存放构建操作输出的结果。

### 约定目录结构的意义

Maven 为了让构建过程能够尽可能自动化完成，所以必须约定目录结构的作用。例如：Maven 执行编译操作，必须先去 Java 源程序目录读取 Java 源代码，然后执行编译，最后把编译结果存放在 target 目录。

### 约定大于配置

Maven 对于目录结构这个问题，没有采用配置的方式，而是基于约定。这样会在开发过程中非常方便。如果每次创建 Maven 工程后，还需要针对各个目录的位置进行详细的配置，那肯定非常麻烦。

目前开发领域的技术发展趋势就是：**约定大于配置，配置大于编码**。
