### Linux安装
1. 下载安装包：wget [https://download.redis.io/releases/redis-7.0.0.tar.gz](https://download.redis.io/releases/redis-7.0.0.tar.gz) 
2. 在opt目录下解压redis： tar -zxvf redis-7.0.0.tar.gz
3. 进入解压目录：cd redis-7.0.0/
4. 在redis-7.0.0目录下执行make命令：make && make install
5. 安装完成后，将默认的redis.conf拷贝到自己定义好的路径下，/myredis
6. 修改拷贝好的配置
   1. 默认daemonize no            ==>   daemonize yes  # 开启后台启动
   2. 默认protected-mode  yes ==>   rotected-mode no  # 将受保护模式关闭
   3. 默认bind 127.0.0.1            ==>  直接注释掉(默认bind 127.0.0.1只能本机访问)或改成本机IP地址，否则影响远程IP连接
   4. 添加redis密码                    ==>   requirepass 你自己设置的密码
7. 指定配置文件启动 redis-server /opt/redis/myredis.conf
8. 连接测试   redis-cli -p 6379


redis开启key过期提醒
开启配置：
```bash
配置文件：
notify-keyspace-events Ex

订阅channel：  __keyevent@0__:expired
那么索引为0的数据库中所有的key都会在过期时发布一个事件
```
