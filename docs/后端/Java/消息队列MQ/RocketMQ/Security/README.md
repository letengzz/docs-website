# RocketMQ ACL安全

ACL (Access Control List)访问控制列表，是一种**细粒度**的权限管理策略，可以针对任意用户与组进行权限控制。目前大多数Unix系统和Linux 2.6版本已经支持ACL了。Unix和Linux系统默认使用UGO (User、Group、Other)权限控制策略。其是一个**粗粒度**的权限管理策略。

1. 开启acl的控制 在broker.conf中开启：

   ```bash
   vi /root/rocketmq/conf/broker.conf
   aclEnable=true
   ```

   ![image-20240318090012541](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403180900922.png)

2. 配置账号密码 (当使用RocketMQ时，需要指定账户和密码)：修改plain_acl.yml

   ```shell
   vi /root/rocketmq/conf/plain_acl.yml
   ```

   ![image-20240318090703306](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403181903015.png)

   将rocketmq2的白名单地址 改为 `192.168.*.*`

   ```shell
   whiteRemoteAddress: 192.168.*.*
   ```

3. 修改控制面板的配置文件：将源码中的application.yaml 放开52/53行 把49行改为true，将application.yaml 上传到服务器的jar包平级目录下即可

   ![image-20240318101006697](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403181906730.png)

   ![image-20240318100629311](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403181906025.png)

4. 在users.properties中修改可视化控制台的账号密码：

   ![image-20240318191426657](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403181914296.png)