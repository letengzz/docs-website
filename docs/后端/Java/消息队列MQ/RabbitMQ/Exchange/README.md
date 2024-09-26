# RabbitMQ 交换机

Exchange (X)：交换机/交换器/路由器

**RabbitMQ交换器 (`Exchange`)类型**：

1. **扇形交换机** (`Fanout Exchange`)
2. **直连交换机** (`Direct Exchange`)
3. **主题交换机** (`Topic Exchange`)
4. **头部交换机** (`Headers Exchange`)

## 扇形交换机

扇形交换机(Fanout 扇形的，散开的)：投递到所有绑定的队列，不需要路由键，不需要进行路由键的匹配，相当于广播、群发

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403121253391.jpg) 

## 直连交换机

根据路由键精确匹配进行路由消息队列

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403121253208.jpg) 

## 主题交换机

通配符匹配，相当于模糊匹配；

- `#`匹配多个单词，用来表示任意数量 (零个或多个)单词

- `*`匹配一个单词 (必须有一个，而且只有一个)，用`.`隔开的为一个单词

`beijing.# == beijing.queue.abc, beijing.queue.xyz.xxx`

`beijing.* == beijing.queue, beijing.xyz`

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403121253179.jpg)

发送时指定的路由键：`lazy.orange.rabbit`

## 头部交换机

基于消息内容中的headers属性进行匹配

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403121253242.jpg) 

## 预设的交换机

每个虚拟主机都会自动新增七个相关的预设交换机：

![image-20240312200532522](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122020427.png)

前面两个`direct`类型的交换机，一个是`AMQP default`还有一个是`amq.direct`，它们都是直连模式的交换机：

- `AMQP default`：是所有虚拟主机都会自带的一个默认交换机，并且此交换机不可删除。

  此交换机默认绑定到所有的消息队列，如果是通过默认交换机发送消息，那么会根据消息的`routingKey`（之后发消息都会指定）决定发送给哪个同名的消息队列，同时也不能显示地将消息队列绑定或解绑到此交换机。

  可以看到，详细信息中，当前交换机特性是持久化的，也就是说就算机器重启，那么此交换机也会保留，如果不是持久化，那么一旦重启就会消失。

  ![image-20240312202319665](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122023094.png)

- `amq.direct`：普通的直连交换机。和`AMQP default`默认交换机类型一致，并且也是持久化的，但是可以看到它是具有绑定关系的，如果没有指定的消息队列绑定到此交换机上，那么这个交换机无法正常将信息存放到指定的消息队列中，也是根据`routingKey`寻找消息队列 (但是可以自定义)

  ![image-20240312202421340](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122024096.png)

实际上在列表中看到`D`的字样，就表示此交换机是持久化的，**所有自动生成的交换机都是持久化的**。