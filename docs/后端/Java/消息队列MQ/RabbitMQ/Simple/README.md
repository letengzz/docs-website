## RabbitMQ 简单使用

### 新建虚拟主机

通过web页面新建虚拟主机：

![image-20240312002430351](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403120025676.png)

添加新的虚拟主机之后，当前admin用户的主机访问权限中新增了刚刚添加的环境：

![image-20240312002500485](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403120025545.png)

![image-20240312200156098](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122001504.png)

点击用户名，可以进行更多的操作：

![image-20240312205335781](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122053064.png)

### 新建消息

![image-20240312204020463](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122040470.png)

可以看到消息队列列表中没有任何的消息队列，可以来尝试添加一个新的消息队列：

![image-20240312204243554](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122042477.png)

选择刚刚创建好的虚拟主机，在这个虚拟主机下创建此消息队列，接着将其类型定义为`Classic`类型(经典类型)，名称随便起一个，然后持久化选择`Transient`暂时的(当然也可以持久化)，自动删除选择`No` (需要至少有一个消费者连接到这个队列，之后，一旦所有与这个队列连接的消费者都断开时，就会自动删除此队列)，最下面的参数暂时不进行任何设置

这样就创建好了一个经典的消息队列：

![image-20240312204727254](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122047768.png)

点击此队列的名称，可以查看详细信息：

![image-20240312211248320](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122112128.png)

详细相信中包括队列的当前负载状态、属性、消息队列占用的内存，消息数量等。

### 绑定交换机

现在需要将此消息队列绑定到上面的第二个直连交换机，这样就可以通过此交换机向此消息队列发送消息了：填写之前第二个交换机的名称还有自定义的`routingKey` (最好还是和消息队列名称一致)，直接点击绑定即可

![image-20240312211628676](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122118404.png)

![image-20240312211808317](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122118299.png)



绑定之后可以看到当前队列已经绑定对应的交换机了，现在可以前往交换机对此消息队列发送一个消息：

![image-20240312213443887](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122134317.png)

直接向此消息队列发送信息：

![image-20240312213644304](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130002912.png)

点击发送之后，回到刚刚的交换机详细页面，可以看到已经有一条新的消息在队列中了：

![image-20240312213745218](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122137830.png)

### 获取消息

可以直接在消息队列这边获取消息队列中的消息，找到下方的Get message选项：

![image-20220419145936160](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403122144515.jpg)

可以看到有三个选择

- Ack Mode(**应答模式选择**)，一共有4个选项：

  ![image-20240312214811598](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003953.png)

  * Nack message requeue true：拒绝消息，也就是说不会将消息从消息队列取出，并且重新排队，一次可以拒绝多个消息。

  * Ack message requeue false：确认应答，确认后消息会从消息队列中移除，一次可以确认多个消息。

  * Reject message requeue true/false：拒绝此消息，但是可以指定是否重新排队。

- Encoding(编码格式)，使用默认的就可以
- Messages(要生效的操作数量)，选择1就行

这样只会查看消息是啥，但是不会取出，消息依然存在于消息队列中：刚刚的消息已经成功读取到。

![image-20240312220344828](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003425.png)

现在再去第一个默认交换机中尝试发送消息试试看：

![image-20240312221716974](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003947.png)

如果使用之前自定义的`routingKey`，会显示没有路由，这是因为默认的交换机只会找对应名称的消息队列，现在向`testQueue`发送发现消息成功发布：

![image-20240312221830813](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003187.png)

来接收一下消息可以看到成功发送到此消息队列中了：

![image-20240312222035280](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003421.png)

当然除了在交换机发送消息给消息队列之外，也可以直接在消息队列这里发：

![image-20240312222842263](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003441.png)

效果是一样的，可以选择是否将消息持久化，如果是持久化消息，那么就算服务器重启，此消息也会保存在消息队列中。

如果不需要再使用此消息队列了，可以手动对其进行删除或是清空：

![image-20220419151548923](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403130003966.jpg)

点击Delete Queue删除刚刚创建好的队列。
