# Docker 安装

1. 拉取镜像：

   ```shell
   docker pull rabbitmq:3.12.0-management
   ```

2. 使用容器启动服务：

   ```shell
   docker run -d --name=rabbitmq --restart=always -p 5672:5672 -p 15672:15672 rabbitmq:3.12.0-management  
   ```