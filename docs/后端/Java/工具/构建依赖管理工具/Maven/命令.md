# Maven 命令

运行 Maven 中和构建操作相关的命令时，必须进入到 pom.xml 所在的目录。如果没有在 pom.xml 所在的目录运行 Maven 的构建命令，那么会看到下面的错误信息：

> The goal you specified requires a project to execute but there is no POM in this directory

**说明**：

`mvn -v` 命令和构建操作无关，只要正确配置了 PATH，在任何目录下执行都可以。而构建相关的命令要在 pom.xml 所在目录下运行——操作哪个工程，就进入这个工程的 pom.xml 目录。

## 清理操作

操作命令：

```shell
mvn clean
```

效果：删除 target 目录

![image-20231023192502697](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231925679.png)

## 编译操作

主程序编译：

```shell
mvn compile
```

测试程序编译：

```shell
mvn test-compile
```

**存放目录**：

- 主体程序编译结果存放的目录：`target/classes`

  ![image-20231023192556095](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231925999.png)

- 测试程序编译结果存放的目录：`target/test-classes`

  ![image-20231023192658702](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231927431.png)

## 测试操作

```shell
mvn test
```

测试的报告存放的目录：`target/surefire-reports`

![image-20231023192817092](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231928623.png)

## 打包操作

```shell
mvn package
```

打包的结果——jar 包，存放的目录：target

![image-20231023193004726](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231930928.png)

## 安装操作

```shell
mvn install
```

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051643778.png)

> [INFO] Installing D:\maven-workspace\space\pro01-maven-java\target\pro01-maven-java-1.0-SNAPSHOT.jar to D:\Data\Maven\com\hjc\maven\pro01-maven-java\1.0-SNAPSHOT\pro01-maven-java-1.0-SNAPSHOT.jar
> [INFO] Installing D:\maven-workspace\space\pro01-maven-java\pom.xml to D:\Data\Maven\com\hjc\maven\pro01-maven-java\1.0-SNAPSHOT\pro01-maven-java-1.0-SNAPSHOT.pom

安装的效果是将本地构建过程中生成的 jar 包存入 Maven 本地仓库。这个 jar 包在 Maven 仓库中的路径是根据它的坐标生成的。

坐标信息：

```xml
  <groupId>com.hjc.maven</groupId>
  <artifactId>pro01-maven-java</artifactId>
  <version>1.0-SNAPSHOT</version>
```

在 Maven 仓库中生成的路径：

```log
D:\repo\maven-repository\com\hjc\maven\pro01-maven-java\1.0-SNAPSHOT\pro01-maven-java-1.0-SNAPSHOT.jar
```

另外，安装操作还会将 pom.xml 文件转换为 XXX.pom 文件一起存入本地仓库。所以在 Maven 的本地仓库中想看一个 jar 包原始的 pom.xml 文件时，查看对应 XXX.pom 文件即可，它们是名字发生了改变，本质上是同一个文件。

## 查看当前 Web 工程所依赖的 jar 包的列表

```shell
mvn dependency:list
```

![image-20231105162923957](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051629710.png)

> [INFO] The following files have been resolved:
> [INFO] org.hamcrest:hamcrest-core:jar:1.3:test
> [INFO] javax.servlet:javax.servlet-api:jar:3.1.0:provided
> [INFO] com.hjc.maven:pro01-maven-java:jar:1.0-SNAPSHOT:compile
> [INFO] junit:junit:jar:4.12:test

**说明**：javax.servlet:javax.servlet-api:jar:3.1.0:provided 格式显示的是一个 jar 包的坐标信息。格式是：`groupId:artifactId:打包方式:version:依赖的范围`

这样的格式虽然和 XML 配置文件中坐标的格式不同，但是本质上还是坐标信息，将来从 Maven 命令的日志或错误信息中看到这样格式的信息，就能够识别出来这是坐标。进而根据坐标到Maven 仓库找到对应的jar包，用这样的方式解决遇到的报错的情况。

## 以树形结构查看当前 Web 工程的依赖信息

```shell
mvn dependency:tree
```

![image-20231105163356579](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051634512.png)

> [INFO] com.hjc.maven:pro02-maven-web:war:1.0-SNAPSHOT
> [INFO] +- junit:junit:jar:4.12:test
> [INFO] | \- org.hamcrest:hamcrest-core:jar:1.3:test
> [INFO] +- javax.servlet:javax.servlet-api:jar:3.1.0:provided
> [INFO] \- com.hjc.maven:pro01-maven-java:jar:1.0-SNAPSHOT:compile

在 pom.xml 中并没有依赖 hamcrest-core，但是它却被加入了依赖的列表。

**原因**：junit 依赖了hamcrest-core，然后基于依赖的传递性，hamcrest-core 被传递到工程了。

## 查看Maven版本

```xml
mvn -v
```

![image-20231105132734015](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051327939.png)