````
# MacOS 安装 RabbitMQ

## brew 命令安装

安装 erlang

```sh
# 终端输入
brew install erlang
```

安装 rabbitmq

```sh
# 终端输入
brew install rabbitmq
```

配置 RabbitMQ 环境变量：

```sh
# 终端输入
vi ~/.bash_profile
```

添加配置 终端输入：

```sh
vim ~/.bash_profile

export RABBIT_HOME=/usr/local/Cellar/rabbitmq/3.13.0
export PATH=$PATH:$RABBIT_HOME/sbin 
```

更新配置 终端输入：

```sh
source ~/.bash_profile
```

安装 RabiitMQ 的可视化监控插件：

```sh
# 终端输入
sudo /usr/local/Cellar/rabbitmq/3.13.0/sbin/rabbitmq-plugins enable rabbitmq_management
```

Mac 后台启动 RabbitMQ：

1. 后台启动：

   ```sh
   # 终端输入
   sudo rabbitmq-server -detached 
   ```

2. 查看状态：

   ```sh
   # 终端输入
   sudo rabbitmqctl status
   ```

3. 访问可视化监控插件的界面：浏览器内输入 http://localhost:15672

默认的用户名密码都是 guest，登录后可以在 Admin 那一列菜单内添加自己的用户

## 添加用户

在 RabbitMQ 中添加新用户：您需要使用 RabbitMQ 提供的命令行工具或者管理界面进行操作

- 使用 RabbitMQ 命令行工具：

  - 创建`admin`用户：

    ```sh
    sudo rabbitmqctl add_user admin admin
    ```

  - 将管理员权限给予`admin`用户：

    ```sh
    sudo rabbitmqctl set_user_tags admin administrator
    ```

    设置用户权限：

    ```sh
    rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
    ```

    说明：此操作是设置admin用户拥有操作虚拟主机/下的所有权限

    查看用户权限：

    ```sh
    rabbitmqctl list_permissions
    ```

- 使用 RabbitMQ 管理界面 (只能搭建在本地操作)：

  - 打开您的浏览器并访问 RabbitMQ 管理界面。默认地址为 `http://localhost:15672`

  - 使用默认的管理员账号和密码（通常是 `guest`/`guest`）登录到管理界面

  - 在管理界面上导航到 "Admin" -> "Users" 选项卡

  - 单击 "Add a user" 按钮

  - 输入用户名和密码，并选择 "Tag" 为 "Administrator"

  - 单击 "Add user" 按钮以创建新用户。

  - 注意，此处需要进行一次授权，否则在代码中连接RabbitMQ会失败

    ![image-20230616194600354](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img202403171903826.png)

    ![image-20230616194636865](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img202403171903294.png)

创建完成之后，登录一下页面：

![image-20240310233156858](https://cdn.jsdelivr.net/gh/letengzz/tc2@main/img202403171903995.png)

进入了之后会显示当前的消息队列情况，包括版本号、Erlang版本等。
````

