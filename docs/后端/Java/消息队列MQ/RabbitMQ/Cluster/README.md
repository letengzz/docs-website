### 集群搭建

前面我们对于RabbitMQ的相关内容已经基本讲解完毕了，最后我们来尝试搭建一个集群，让RabbitMQ之间进行数据复制（镜像模式）稍微有点麻烦，跟着视频走吧。

可能会用到的一些命令：

```sh
sudo rabbitmqctl stop_app
sudo rabbitmqctl join_cluster rabbit@ubuntu-server
sudo rabbitmqctl start_app
```

实现复制即可。