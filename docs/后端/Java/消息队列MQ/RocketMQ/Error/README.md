# RocketMQ 常见问题

RocketMQ 控制台点击生产者时，出现如下异常：

![image-20240318210108962](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403182101736.png)

在写demo测试RocketMQ，把代码中的`producer.shutdown()`去掉，因为生产者调用`shutdown()`方法，会自动将这个组删掉。

RocketMQ控制台再次点击生产者，就不报错了