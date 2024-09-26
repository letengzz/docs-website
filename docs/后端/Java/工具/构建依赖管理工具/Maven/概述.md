# Maven 概述

Maven 是 Apache 软件基金会组织维护的一款专门为 Java 项目提供**构建**和**依赖**管理支持的工具。

![img](https://maven.apache.org/images/maven-logo-black-on-white.png)

- 官方网站：https://maven.apache.org/

**Maven 作为依赖工具**：

- jar 包的**规模**：

  - 随着使用越来越多的框架，或者框架封装程度越来越高，项目中使用的jar包也越来越多。项目中，一个模块里面用到上百个jar包是非常正常的。
  - 使用 Maven 来引入jar 包只需要配置**依赖**即可。

- jar 包的**来源**：

  - 当从jar包所属技术的官网下载。官网通常是英文界面，网站的结构又不尽相同，甚至找到下载链接还发现需要通过特殊的工具下载。

  - 第三方网站提供下载。问题是不规范，在使用过程中会出现各种问题。
    - jar包的名称
    - jar包的版本
    - jar包内的具体细节
  - 使用 Maven 后，依赖对应的 jar 包能够**自动下载**，方便、快捷又规范。

- jar 包之间的**依赖关系**：

  - 框架中使用的 jar 包，不仅数量庞大，而且彼此之间存在错综复杂的依赖关系。依赖关系的复杂程度，已经上升到了完全不能靠人力手动解决的程度。另外，jar 包之间有可能产生冲突。进一步增加了在 jar 包使用过程中的难度。

    实际上 jar 包之间的依赖关系是普遍存在的，如果要由程序员手动梳理无疑会增加极高的学习成本，而这些工作又对实现业务功能毫无帮助。

  - 使用 Maven 则几乎不需要管理这些关系，极个别的地方调整一下即可，极大的减轻了我们的工作量。

**Maven 作为构建管理工具**：

- 可以不使用 Maven，但是构建必须要做。当使用 IDEA 进行开发时，构建是 IDEA 替我们做的。

- 脱离 IDE **环境仍需构建**

  ![images](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231610779.png)

## 构建问题

Java 项目开发过程中，构建指的是使用**原材料生产产品**的过程。

构建过程包含的**主要环节**：

- **清理**：删除上一次构建的结果，为下一次构建做好准备
- **编译**：Java 源程序编译成 *.class 字节码文件
- **测试**：运行提前准备好的测试程序
- **报告**：针对刚才测试的结果生成一个全面的信息
- **打包**：
  - Java工程：jar包
  - Web工程：war包

- **安装**：把一个 Maven 工程经过打包操作生成的 jar 包或 war 包存入 Maven 仓库

- **部署**：

  - 部署 jar 包：把一个 jar 包部署到 Nexus 私服服务器上

  - 部署 war 包：借助相关 Maven 插件 (例如 cargo)，将 war 包部署到 Tomcat 服务器上

## 依赖问题

如果 A 工程里面用到了 B 工程的类、接口、配置文件等等这样的资源，那么就可以说 A 依赖 B

**例**：

- junit-4.12 依赖 hamcrest-core-1.3
- thymeleaf-3.0.12.RELEASE 依赖 ognl-3.1.26
  - ognl-3.1.26 依赖 javassist-3.20.0-GA
- thymeleaf-3.0.12.RELEASE 依赖 attoparser-2.0.5.RELEASE
- thymeleaf-3.0.12.RELEASE 依赖 unbescape-1.1.6.RELEASE
- thymeleaf-3.0.12.RELEASE 依赖 slf4j-api-1.7.26

依赖管理中要解决的**具体问题**：

- **jar 包的下载**：使用 Maven 之后，jar 包会从规范的远程仓库下载到本地
- **jar 包之间的依赖**：通过依赖的传递性自动完成
- **jar 包之间的冲突**：通过对依赖的配置进行调整，让某些jar包不会被导入

## Maven 的工作机制

![./images](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231612848.png)