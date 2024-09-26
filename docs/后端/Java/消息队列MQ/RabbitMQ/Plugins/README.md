# RabbitMQ 插件

## 延迟队列插件

1. 首先下载[rabbitmq_delayed_message_exchange-3.12.0.ez](https://www.rabbitmq.com/community-plugins.html)文件上传到RabbitMQ所在服务器：https://github.com/rabbitmq/rabbitmq-delayed-message-exchange

2. 上传下载延迟队列插件到Linux操作系统中，切换到插件所在目录，执行 `docker cp rabbitmq_delayed_message_exchange-3.12.0.ez rabbitmq:/plugins` 命令，将刚插件拷贝到容器内plugins目录下

   ```shell
   docker cp rabbitmq_delayed_message_exchange-3.12.0.ez rabbitmq:/plugins
   ```

3. 执行 `docker exec -it rabbitmq /bin/bash` 命令进入到容器内部，并 `cd plugins` 进入plugins目录

   ```shell
    docker exec -it rabbitmq /bin/bash
    cd plugins
   ```

   执行 `ls -l|grep delay`  命令查看插件是否copy成功

   ```shell
   ls -l|grep delay
   ```

   在容器内plugins目录下，执行 `rabbitmq-plugins enable rabbitmq_delayed_message_exchange`  命令启用插件

   ```shell
   rabbitmq-plugins enable rabbitmq_delayed_message_exchange
   ```

4. exit命令退出RabbitMQ容器内部，然后执行 `docker restart rabbitmq` 命令重启RabbitMQ容器

   ```shell
   docker restart rabbitmq
   ```

   