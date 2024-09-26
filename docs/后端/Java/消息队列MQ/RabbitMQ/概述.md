# RabbitMQ 概述

RabbitMQ拥有数万计的用户，是最受欢迎的开源消息队列之一，从[T-Mobile](https://www.youtube.com/watch?v=1qcTu2QUtrU)到[Runtastic](https://medium.com/@runtastic/messagebus-handling-dead-letters-in-rabbitmq-using-a-dead-letter-exchange-f070699b952b)，RabbitMQ在全球范围内用于小型初创企业和大型企业。

RabbitMQ轻量级，易于在本地和云端部署，它是开源的实现AMQP(高级消息队列协议)的消息中间件。RabbitMQ可以部署在分布式和联合配置中，以满足大规模、高可用性要求。

RabbitMQ在许多操作系统和云环境中运行，并为[大多数流行语言](https://www.rabbitmq.com/devtools.html)提供了[广泛的开发者工具](https://www.rabbitmq.com/devtools.html)。

**官方网站：** https://www.rabbitmq.com

**GitHub**：https://github.com/rabbitmq

![image-20220415163559986](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403092347385.jpg)

## RabbitMQ 工作模型

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403120049831.jpg) 

broker 相当于mysql服务器，virtual host相当于数据库（可以有多个数据库）

queue相当于表，消息相当于记录。

消息队列有三个核心要素： **消息生产者**、**消息队列**、**消息消费者**；

- **生产者** (`Producer`)：发送消息的应用

- **消费者** (`Consumer`)：接收消息的应用

- **代理** (`Broker`)：就是消息服务器，RabbitMQ Server就是Message Broker

- **连接** (`Connection`)：连接RabbitMQ服务器的TCP长连接

- **信道** (`Channel`)：连接中的一个虚拟通道，消息队列发送或者接收消息时，都是通过信道进行的(客户端连接都会使用一个Channel，再通过Channel去访问到RabbitMQ服务器，注意通信协议不是http，而是amqp协议)

- **虚拟主机** (`Virtual host`)：一个虚拟分组，在代码中就是一个字符串，当多个不同的用户使用同一个RabbitMQ服务时，可以划分出多个Virtual host，每个用户在自己的Virtual host创建exchange/queue等(分类比较清晰、相互隔离，每个Virtual Host相互之间不影响)

- **交换机** (`Exchange`)：交换机负责从生产者接收消息，并根据交换机类型分发到对应的消息队列中，起到一个路由的作用，根据请求，转发给相应的消息队列，每个队列都可以绑定到Exchange上，这样Exchange就可以将数据转发给队列了，可以存在很多个，不同的Exchange类型可以用于实现不同消息的模式。

- **路由键** (`Routing Key`)：交换机根据路由键来决定消息分发到哪个队列，路由键是消息的目的地址

- **绑定** (`Binding`)：绑定是队列和交换机的一个关联连接 (关联关系)

- **队列** (`Queue`)：存储消息的缓存，消息队列本体，生产者所有的消息都存放在消息队列中，等待消费者取出。

- **消息** (`Message`)：由生产者通过RabbitMQ发送给消费者的信息 (消息可以任何数据，字符串、user对象，json串等等)

## RabbitMQ 优缺点

- RabbitMQ的单机吞吐量能达到万级，但是对于需要支持特别高的并发的情况，它是无法担当重任的。

- 在高可用上，它使用的是镜像集群模式，可以保证高可用。

- 在消息可靠性上，它是可以保证数据不丢失的，这也是它的一大优点。

- 同时它也支持一些消息中间件的高级功能，如：消息重试、死信队列等。

- RabbitMQ 开发语言是`erlang`，国内很少有人精通`erlang`，所以导致无法阅读源码。