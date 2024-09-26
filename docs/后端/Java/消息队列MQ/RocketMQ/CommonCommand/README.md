# 常用命令

启动NameServer：

```bash
nohup sh mqnamesrv &
```

启动Broker：

```bash
nohup sh mqbroker -n localhost:9876 &
```

查看NameServer和Broker运行状态：

```bash
sh mqadmin clusterList -n localhost:9876
```

查看所有Topic：

```bash
sh mqadmin topicList -n localhost:9876
```

查看某个Topic信息：

```bash
sh mqadmin topicStatus -t TopicTest -n localhost:9876
```

查看某个Consumer Group信息：

```bash
sh mqaadmin consumerProgress -g ConsumerGroupTest -n localhost:9876
```