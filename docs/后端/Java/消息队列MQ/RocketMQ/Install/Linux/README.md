# Linux 安装 RocketMQ

## 准备工作

**注意**：必须先安装64bit的JDK1.8或以上版本

下载地址：https://rocketmq.apache.org/dowloading/releases/ 

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171602475.png)

**上传服务器并解压**：

- 在root目录下创建文件夹，将下载后的压缩包上传到服务器：

  ```shell
  cd ~
  mkdir rocketmq
  ```

- 解压：

  ```shell
  unzip rocketmq-all-4.9.2-bin-release.zip
  ```

  如果没有unzip 命令，则下载安装一个：`yum install unzip`

  ```shell
  yum install unzip
  ```

  项目目录结构：

  - Benchmark：包含一些性能测试的脚本
  - Bin：可执行文件目录
  - Conf：配置文件目录
  - Lib：第三方依赖
  - LICENSE：授权信息
  - NOTICE：版本公告

**配置环境变量**：

```shell
vim /etc/profile
# 末尾添加
export NAMESRV_ADDR=公网IP:9876
```

## 修改运行脚本

### 修改nameServer

进入bin目录下，修改runserver.sh文件,将71行和76行的Xms和Xmx等改小一点，保存并退出

```shell
vim runserver.sh
```

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171618106.png)

### 修改broker

进入bin目录下，修改runbroker.sh文件,修改67行，保存并退出

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171618859.png)

## 修改broker的配置文件

进入conf目录下，修改broker.conf文件：

```shell
brokerClusterName = DefaultCluster
brokerName = broker-a
brokerId = 0
deleteWhen = 04
fileReservedTime = 48
brokerRole = ASYNC_MASTER
flushDiskType = ASYNC_FLUSH
namesrvAddr=localhost:9876
autoCreateTopicEnable=true
brokerIP1=公网IP 
```

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171618462.png)

- namesrvAddr：nameSrv地址 可以写localhost因为nameSrv和broker在一个服务器
- autoCreateTopicEnable：自动创建主题，不然需要手动创建出来
- brokerIP1：broker也需要一个公网ip，如果不指定，那么是内网地址，在本地无法连接使用

## 启动运行

**配置环境变量变量**：

```shell
vim /etc/profile

# 在文件末尾添加以下内容:
export ROCKETMQ_HOME=/root/rocketmq
export PATH=$ROCKETMQ_HOME/bin:$PATH
```

**启动并添加日志**：首先在安装目录下创建一个logs文件夹，用于存放日志：

![image-20240317171739652](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171717295.png)

```shell
mkdir logs
```

**运行命令**：

- 启动nameSrv：

  ```shell
  nohup sh bin/mqnamesrv > ./logs/namesrv.log &
  ```

  查看日志：

  ```
  tail -f ./logs/namesrv.log
  ```

- 启动broker 这里的-c是指定使用的配置文件：

  ```shell
  nohup sh bin/mqbroker -c conf/broker.conf > ./logs/broker.log &
  ```

  查看日志：

  ```
  tail -f ./logs/broker.log
  ```

- 查看启动结果：

  ```shell
  jps
  ```

  ![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171717639.png)


## 安装可视化控制台

Rocketmq 控制台可以可视化MQ的消息发送。

旧版本源码是在rocketmq-external里的rocketmq-console，新版本已经单独拆分成dashboard

网址： https://github.com/apache/rocketmq-dashboard 

下载地址：https://github.com/apache/rocketmq-dashboard/archive/refs/tags/rocketmq-dashboard-1.0.0.zip  

修改端口号：进入\src\main\resources下的application.properties修改端口号

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610655.png)

下载后解压出来，在跟目录下执行：

```shell
mvn clean package -Dmaven.test.skip=true
```

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610971.png)

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171610538.png)

将jar包上传到服务器上去：

![](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403171720311.png)

运行：

```shell
nohup java -jar ./rocketmq-dashboard-1.0.0.jar rocketmq.config.namesrvAddr=127.0.0.1:9876 > ./logs/dashboard.log & 
```

- --server.port：指定运行的端口

- --rocketmq.config.namesrvAddr=127.0.0.1:9876：指定namesrv地址

## 防火墙操作

1. 登录到服务器上，以具有管理员权限的用户身份。

2. 检查防火墙状态，确认是否已安装 firewalld 防火墙：

   ```sh
   systemctl status firewalld
   ```

3. 如果防火墙处于开启状态，可以直接跳转到第 6 步。如果防火墙停止运行，则需要启动，请继续执行以下步骤。

4. 启动 firewalld 服务：

   ```sh
   systemctl start firewalld
   ```

5. 设置 firewalld 开机自启：

   ```sh
   systemctl enable firewalld
   ```

6. 添加端口规则，允许在防火墙上开放  rocketmq-console的端口和9876端口：

   ```sh
   firewall-cmd --zone=public --add-port=8080/tcp --permanent
   firewall-cmd --zone=public --add-port=9876/tcp --permanent
   ```

7. 重新加载防火墙配置，使更改生效：

   ```sh
   firewall-cmd --reload
   ```

防火墙应该已经放行了 rocketmq-console的端口和9876端口，允许对 RocketMQ 管理界面进行访问。

**注意**：为了安全起见，建议仅在需要时才开放必要的端口，并在完成使用后关闭不必要的端口。