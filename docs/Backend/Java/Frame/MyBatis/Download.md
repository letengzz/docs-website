# MyBatis 下载

在 MyBatis 的官方网站 [http://mybatis.org](http://mybatis.org/)下载。

如果打不开网站或下载进度较慢，可以通过 https://github.com/mybatis/mybatis-3/releases 网址下载。

**MyBatis文件目录结构**：

下载完成后，mybatis-3.5.5.zip 解压后目录结构：

![mybatis目录结构](assets/143IRD4-0.png)

mybatis-3.5.5.jar 是 MyBatis 的核心包，mybatis-3.5.5.pdf 是 MyBatis 官方使用手册，lib 文件夹下的 jar 文件是 MyBatis 的依赖包：

![lib文件夹内容](assets/143IU3W-1.png)

JAR 文件说明：

| 名称                     | 说明                                             |
| ------------------------ | ------------------------------------------------ |
| asm-7.1.jar              | 操作Java字节码的类库                             |
| cglib-3.3.0.jar          | 用来动态继承Java类或实现接口                     |
| commons-logging-1.2.jar  | 用于通用日志处理                                 |
| javassist-3.27.0-GA.jar  | 分析、编码和创建Java类库                         |
| log4j-1.2.17.jar         | 日志系统                                         |
| log4j-api-2.13.3.jar     | log4j到log4j2的桥接包                            |
| log4j-core-2.13.3.jar    | log4j到log4j2的桥接包                            |
| ognl-3.2.14.jar          | OGNL的类库                                       |
| slf4j-api-1.7.30.jar     | 日志系统的封装，对外提供统一的API接口            |
| slf4j-log4j12-1.7.30.jar | slf4j 对 log4j 的相应驱动，完成 slf4j 绑定 log4j |

在使用 MyBatis 框架时，需要把它的核心包和依赖包引入到应用程序中。如果是 Web 应用，只需将核心包和依赖包复制到 /WEB-INF/lib 目录中。
