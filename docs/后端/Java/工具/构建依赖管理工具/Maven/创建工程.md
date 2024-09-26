````
# Maven 创建工程

## 创建普通工程

1. 创建目录作为后面操作的工作空间：例如：D:\maven-workspace\space

2. 在工作空间目录下打开命令行窗口：

   ![image-20231023184923742](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231849310.png)

3. 使用命令生成Maven工程：运行 `mvn archetype:generate` 命令

   ```shell
   mvn archetype:generate
   ```

   ![images](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231915838.png)

   > Choose a number or apply filter (format: [groupId:]artifactId, case sensitive contains): 7:【直接回车，使用默认值】
   >
   > Define value for property 'groupId': com.hjc.maven
   >
   > Define value for property 'artifactId': pro01-maven-java
   >
   > Define value for property 'version' 1.0-SNAPSHOT: :【直接回车，使用默认值】
   >
   > Define value for property 'package' com.hjc.maven: :【直接回车，使用默认值】
   >
   > Confirm properties configuration: groupId: com.hjc.maven artifactId: pro01-maven-java version: 1.0-SNAPSHOT package: com.hjc.maven Y: :【直接回车，表示确认。如果前面有输入错误，想要重新输入，则输入 N 再回车。】

   ![image-20231023185406627](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231854501.png)

自动生成的 pom.xml 解读：

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <!-- 当前Maven工程的坐标 -->
  <groupId>com.hjc.maven</groupId>
  <artifactId>pro01-maven-java</artifactId>
  <version>1.0-SNAPSHOT</version>
    
  <!-- 当前Maven工程的打包方式，可选值有下面三种： -->
  <!-- jar：表示这个工程是一个Java工程  -->
  <!-- war：表示这个工程是一个Web工程 -->
  <!-- pom：表示这个工程是“管理其他工程”的工程 -->
  <packaging>jar</packaging>

  <name>pro01-maven-java</name>
  <url>http://maven.apache.org</url>

  <properties>
    <!-- 工程构建过程中读取源码时使用的字符集 -->
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <!-- 依赖信息配置 -->
  <!-- 当前工程所依赖的jar包 -->
  <!-- dependencies复数标签：里面包含dependency单数标签 -->
  <dependencies>
    <!-- dependency单数标签:使用dependency配置一个具体的依赖 -->
    <dependency>
      <!-- 在dependency标签内使用具体的坐标来依赖其他jar包 -->
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <!-- scope标签配置依赖的范围 -->
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
```

### 调整工程

- Maven 默认生成的工程，对 junit 依赖的是较低的 3.8.1 版本，可以改成较适合的 4.12 版本。

  ```xml
  <dependencies>
  	<dependency>
  		<groupId>junit</groupId>
  		<artifactId>junit</artifactId>
  		<version>4.12</version>
  		<scope>test</scope>
  	</dependency>
  </dependencies>
  ```

- 自动生成的 App.java 和 AppTest.java 可以删除。

### 编写代码

#### 主体程序

![image-20231023190441593](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231904220.png)

主体程序指的是被测试的程序，同时也是将来在项目中真正要使用的程序。

```java
package com.hjc.maven;
	
public class Calculator {
	
	public int sum(int i, int j){
		return i + j;
	}
	
}
```

#### 测试程序

![image-20231023190722219](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231907713.png)

```java
package com.hjc.maven;
	
import org.junit.Test;
import com.hjc.maven.Calculator;
	
// 静态导入的效果是将Assert类中的静态资源导入当前类
// 这样一来，在当前类中就可以直接使用Assert类中的静态资源，不需要写类名
import static org.junit.Assert.*;
	
public class CalculatorTest{
	
	@Test
	public void testSum(){
		
		// 1.创建Calculator对象
		Calculator calculator = new Calculator();
		
		// 2.调用Calculator对象的方法，获取到程序运行实际的结果
		int actualResult = calculator.sum(5, 3);
		
		// 3.声明一个变量，表示程序运行期待的结果
		int expectedResult = 8;
		
		// 4.使用断言来判断实际结果和期待结果是否一致
		// 如果一致：测试通过，不会抛出异常
		// 如果不一致：抛出异常，测试失败
		assertEquals(expectedResult, actualResult);
		
	}
	
}
```

### 执行Maven命令

#### 清理操作

操作命令：

```shell
mvn clean
```

效果：删除 target 目录

![image-20231023192502697](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231925679.png)

#### 编译操作

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

#### 测试操作

```shell
mvn test
```

测试的报告存放的目录：`target/surefire-reports`

![image-20231023192817092](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231928623.png)

#### 打包操作

```shell
mvn package
```

打包的结果——jar 包，存放的目录：target

![image-20231023193004726](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231930928.png)

#### 安装操作

```shell
mvn install
```

![image-20231105164336210](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051643778.png)

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

## 创建Web工程

使用 `mvn archetype:generate` 命令生成 Web 工程时，需要使用一个专门的 archetype。这个专门生成 Web 工程骨架的 archetype 可以参照官网看到它的用法：

![./images](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051402034.png)

参数 archetypeGroupId、archetypeArtifactId、archetypeVersion 用来指定现在使用的 maven-archetype-webapp 的坐标。

**操作**：

1. 创建目录作为后面操作的工作空间：例如：D:\maven-workspace\space

2. 在工作空间目录下打开命令行窗口：

   ![image-20231023184923742](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img/202310231849310.png)

3. 使用命令生成Maven工程：运行 `mvn archetype:generate` 命令

   ```shell
   mvn archetype:generate -DarchetypeGroupId=org.apache.maven.archetypes -DarchetypeArtifactId=maven-archetype-webapp -DarchetypeVersion=1.4
   ```

   > Define value for property 'groupId': com.hjc.maven 
   >
   > Define value for property 'artifactId': pro02-maven-web 
   >
   > Define value for property 'version' 1.0-SNAPSHOT: :【直接回车，使用默认值】
   >
   > Define value for property 'package' com.hjc.maven: :【直接回车，使用默认值】 
   >
   > Confirm properties configuration: 
   >
   > groupId: com.hjc.maven 
   >
   > artifactId: pro02-maven-web 
   >
   > version: 1.0-SNAPSHOT 
   >
   > package: com.hjc.maven Y: :【直接回车，表示确认】

   ![image-20231105142916781](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051429691.png)

**生成的pom.xml**：确认打包的方式是war包形式

```xml
<packaging>war</packaging>
```

**生成的Web工程的目录结构**：

![image-20231105144955469](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051449468.png)

- webapp 目录下有 index.jsp


- WEB-INF 目录下有 web.xml


### 创建 Servlet

在 main 目录下创建 java 目录：

![image-20231105145237818](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051452028.png)

在 java 目录下创建 Servlet 类所在的包的目录：

![image-20231105150000237](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051500404.png)

在包下创建 Servlet 类：

```java
package com.hjc.maven;
	
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletException;
import java.io.IOException;
	
public class HelloServlet extends HttpServlet{
	
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		
		response.getWriter().write("hello maven web");
		
	}
	
}
```

### 注册 Servlet

在 web.xml 中注册 Servlet：

```xml
  <servlet>
	<servlet-name>helloServlet</servlet-name>
	<servlet-class>com.hjc.maven.HelloServlet</servlet-class>
  </servlet>
  <servlet-mapping>
	<servlet-name>helloServlet</servlet-name>
	<url-pattern>/helloServlet</url-pattern>
  </servlet-mapping>
```

### 编写超链接

JSP全称是 Java Server Page，和 Thymeleaf 一样，是服务器端页面渲染技术。这里我们不必关心 JSP 语法细节，编写一个超链接标签即可。

在 index.jsp 页面编写超链接：

```html
<html>
<body>
<h2>Hello World!</h2>
<a href="helloServlet">Access Servlet</a>
</body>
</html>
```

### 编译

此时直接执行 `mvn compile` 命令出错：

![image-20231105151740878](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051517438.png)

错误信息说明：Web 工程用到了 HttpServlet 这个类，而 HttpServlet 这个类属于 servlet-api.jar 这个 jar 包。此时Web 工程需要依赖 servlet-api.jar 包。

![./images](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051518271.png)

### 配置依赖

详细信息依赖查询：https://mvnrepository.com/。使用关键词搜索，然后在搜索结果列表中选择适合的使用。

配置对 servlet-api.jar 包的依赖：

![image-20231105152412761](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051524917.png)

比如：servlet-api 的依赖信息：

```xml
<!-- https://mvnrepository.com/artifact/javax.servlet/javax.servlet-api -->
<dependency>
    <groupId>javax.servlet</groupId>
    <artifactId>javax.servlet-api</artifactId>
    <version>3.1.0</version>
    <scope>provided</scope>
</dependency>
```

这样就可以把上面的信息加入 pom.xml。重新执行 `mvn compile` 命令。

![image-20231105152655328](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051526463.png)

### 打包为 war 包

运行 `mvn package` 命令将 Web 工程打包为 war 包：

![image-20231105153030473](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051530347.png)

生成 war 包的位置：

![image-20231105153123938](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051531258.png)

### 部署运行

将 war 包复制到 Tomcat/webapps 目录下：

![image-20231105153827284](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051538053.png)

启动 Tomcat：

![image-20231105153905761](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051539326.png)

![image-20231105154141005](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051541532.png)

通过浏览器尝试访问：http://localhost:8080/pro02-maven-web/index.jsp

![image-20231105154954931](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051549893.png)

## 让 Web 工程依赖 Java 工程

**注意**：从来只有 Web 工程依赖 Java 工程，没有反过来 Java 工程依赖 Web 工程。本质上来说，Web 工程依赖的 Java 工程其实就是 Web 工程里导入的 jar 包。最终 Java 工程会变成 jar 包，放在 Web 工程的 WEB-INF/lib 目录下。

**配置Java工程**：在 pro02-maven-web 工程的 pom.xml 中，找到 dependencies 标签，在 dependencies 标签中配置

```xml
<!-- 配置对Java工程pro01-maven-java的依赖(需要将java工程安装到本地:mvn install) -->
<!-- 具体的配置方式：在dependency标签内使用坐标实现依赖 -->
<dependency>
	<groupId>com.hjc.maven</groupId>
	<artifactId>pro01-maven-java</artifactId>
	<version>1.0-SNAPSHOT</version>
</dependency>
```

## 在 Web 工程中，编写测试代码

1. 补充创建目录：pro02-maven-web\src\test\java\com\hjc\maven

2. 确认 Web 工程依赖了 junit

   ```xml
   <dependency>
       <groupId>junit</groupId>
       <artifactId>junit</artifactId>
       <version>4.12</version>
       <scope>test</scope>
   </dependency>
   ```

3. 创建测试类：

   ```java
   package com.hjc.maven;
   	
   import org.junit.Test;
   import com.hjc.maven.Calculator;
   	
   // 静态导入的效果是将Assert类中的静态资源导入当前类
   // 这样一来，在当前类中就可以直接使用Assert类中的静态资源，不需要写类名
   import static org.junit.Assert.*;
   	
   public class CalculatorTest{
   	
   	@Test
   	public void testSum(){
   		
   		// 1.创建Calculator对象
   		Calculator calculator = new Calculator();
   		
   		// 2.调用Calculator对象的方法，获取到程序运行实际的结果
   		int actualResult = calculator.sum(5, 3);
   		
   		// 3.声明一个变量，表示程序运行期待的结果
   		int expectedResult = 8;
   		
   		// 4.使用断言来判断实际结果和期待结果是否一致
   		// 如果一致：测试通过，不会抛出异常
   		// 如果不一致：抛出异常，测试失败
   		assertEquals(expectedResult, actualResult);
   		
   	}
   	
   }
   ```

## 执行Maven命令

### 测试命令

```shell
mvn test
```

**说明**：测试操作中会提前自动执行编译操作，测试成功就说明编译也是成功的。

![image-20231105160900061](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051609384.png)

### 打包命令

```shell
mvn package
```

![image-20231105162226896](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051622056.png)

通过查看 war 包内的结构，可以看到被 Web 工程依赖的 Java 工程确实是会变成 Web 工程的 WEB-INF/lib 目录下的 jar 包。

![image-20231105162301154](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202311051623077.png)

### 查看当前 Web 工程所依赖的 jar 包的列表

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

### 以树形结构查看当前 Web 工程的依赖信息

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
````

