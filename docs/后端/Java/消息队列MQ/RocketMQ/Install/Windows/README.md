# Windows 安装 RocketMQ

## 准备工作

**注意**：Windows必须先安装64bit的JDK1.8或以上版本

下载地址：https://rocketmq.apache.org/dowloading/releases/ 

下载解压到本地目录 bin目录下存放可运行的脚本：

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171602475.png)

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171602848.png)

- 项目目录结构：

  - Benchmark：包含一些性能测试的脚本
  - Bin：可执行文件目录
  - Conf：配置文件目录
  - Lib：第三方依赖
  - LICENSE：授权信息
  - NOTICE：版本公告

**配置环境变量**：

- 配置JAVA_HOME环境变量

- 配置ROCKETMQ_HOME环境变量：ROCKETMQ_HOME 应指向解压后的`Readme.md`文件所在目录。

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171602616.png)

## 启动NameServer

- NameServer的启动脚本是bin目录下的mqnamesrv.cmd。

- 阅读mqnamesrv.cmd脚本，发现其实际上是调用了runserver.cmd脚本来实现启动的动作。

- 在runserver.cmd脚本，java的默认启动参数中，启动时堆内存的大小为2g，可根据自己的情况来设置内存大小。

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171603759.png)

  ```shell
  rem set "JAVA_OPT=%JAVA_OPT% -server -Xms2g -Xmx2g -Xmn1g -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m"
  set "JAVA_OPT=%JAVA_OPT% -server -Xms256m -Xmx512m"
  ```

**启动NameServer**：

- 启动方式一：直接双击mqnamesrv.cmd脚本启动NameServer。

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171604155.png)

- 启动方式二：使用cmd命令启动，首先进入rocketMq的安装目录，再进入bin目录，执行`start mqnamesrv.cmd`，启动NAMESERVER

  ```shell
  start mqnamesrv.cmd 
  ```

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171604368.png)

- NameServer启动显示：看到 The Name Server boot success 字样，表示NameServer己启动成功。

- Windows环境下，可以在目录%USERPROFILE%\logs\rocketmqlogs下找到NameServer的启动日志。文件名为namesrv.log。

## 启动Broker

- Broker的启动脚本是bin目录下的mqbroker.cmd。

- 与`mqnamesrv.cmd`脚本类似，`mqbroker.cmd`是调用`runbroker.cmd`脚本启动Broker的。

- 同样的，优化一下`runbroker.cmd`的启动内存

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171604553.png)

  ```shell
  rem set "JAVA_OPT=%JAVA_OPT% -server -Xms2g -Xmx2g -Xmn1g"
  set "JAVA_OPT=%JAVA_OPT% -server -Xms256m -Xmx512m"
  ```

- Broker脚本启动之前要指定 NameServer的地址。

  NameServer默认启动端口是9876，这点可以从NameServer的启动日志中找到记录。

  - 启动方式一：修改`mqbroker.cmd`脚本，增加NameServer的地址。

    ```shell
    rem 添加此行，指定NameServer的地址
    set "NAMESRV_ADDR=localhost:9876"
     
    rem 在此行之前添加NameServer的地址
    call "%ROCKETMQ_HOME%\bin\runbroker.cmd" -Drmq.logback.configurationFile=%ROCKETMQ_HOME%\conf\rmq.broker.logback.xml org.apache.rocketmq.broker.BrokerStartup %*
    ```

    ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171605877.png)

    双击mqbroker.cmd脚本启动Broker：

    ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171605568.png)

  - 启动方式二：不修改`mqbroker.cmd`脚本，直接使用cmd命令启动

    首先跟启动NameServer一样先进入rocketmq安装目录的bin目录下面，然后执行`start mqbroker.cmd -n 127.0.0.1:9876 autoCreateTopicEnable=true`启动broker

    ```shell
    start mqbroker.cmd -n 127.0.0.1:9876 autoCreateTopicEnable=true
    ```

    ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171605589.png)

- Broker启动显示：看到 `The broker ... boot success` 字样，表示Broker己启动成功

- 与NameServer类似，可以在目录`%USERPROFILE%\logs\rocketmqlogs`下找到Broker的启动日志。文件名为`broker.log`。

## 验证功能

RocketMQ自带了恬送与接收消息的脚本`tools.cmd`，用来验证RocketMQ的功能是否正常。

tool.cmd脚本需要带参数执行，无法用简单的双击方式启动。因此，需要打开一个cmd窗口，并跳转到bin目录下。

与`mqbroker.cmd`脚本类似，启动`tool.cmd`命令之前我们要指定NameServer地址。

### 启动消费者

采用命令方式指定，并启动消费者：

```shell
set NAMESRV_ADDR=127.0.0.1:9876
tools.cmd org.apache.rocketmq.example.quickstart.Consumer
```

消费者启动成功：

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171605536.png)

### 启动生产者

采用命令方式指定，并启动生产者：

```shell
set NAMESRV_ADDR=127.0.0.1:9876
tools.cmd org.apache.rocketmq.example.quickstart.Producer
```

生产者启动成功：

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171606100.png)

启动成功后，生产者会发送1000个消息，然后自动退出

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171609580.png)

### 查看效果

在消费者界面下，就会收到刚刚生产者发出的消息。

消费者接收消息

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171609250.png)

RocketMQ最小应用已经可以正常工作，能满足开发环境下调试代码的需求

## 安装可视化控制台

Rocketmq 控制台可以可视化MQ的消息发送。

旧版本源码是在rocketmq-external里的rocketmq-console，新版本已经单独拆分成dashboard

网址： https://github.com/apache/rocketmq-dashboard 

下载地址：https://github.com/apache/rocketmq-dashboard/archive/refs/tags/rocketmq-dashboard-1.0.0.zip  

修改端口号：进入\src\main\resources下的application.properties修改端口号

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610655.png)

下载后解压出来，在跟目录下执行：`mvn clean package -Dmaven.test.skip=true`

```shell
mvn clean package -Dmaven.test.skip=true
```

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610971.png)

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610538.png)

直接运行该jar包即可，使用cmd命令进入到该目录，然后执行命令 `java -jar rocketmq-console-ng-1.0.0.jar`  命令

```sh
java -jar rocketmq-console-ng-1.0.0.jar
```

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610009.png)

使用浏览器输入 http://127.0.0.1:8080/ 即可进入rocketmq控制台

**解决连接超时问题**：

- 进入\src\main\resources下的application.properties修改即可

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610466.png)

- 重新打包运行即可