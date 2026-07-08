# Linux 安装 Docker

## 检查环境

Docker 要求 CentOS 系统的内核版本高于 3.10

查看当前的内核版本：

```sh
uname -r
```

## 使用yum安装

1. 卸载旧版本：

   ```sh
   sudo yum remove docker \
                     docker-client \
                     docker-client-latest \
                     docker-common \
                     docker-latest \
                     docker-latest-logrotate \
                     docker-logrotate \
                     docker-engine
   ```

2. 确保 yum 包更新到最新：

   ```sh
   sudo yum update
   ```

3. 安装所需的软件包：

   ```sh
   sudo yum install -y yum-utils device-mapper-persistent-data lvm2
   ```

4. 设置yum源：

   ```sh
   sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
   ```

   阿里源：

   ```shell
   sudo yum-config-manager \
   --add-repo \
   http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
   ```

5. 查看所有仓库中所有docker版本，并选择特定版本安装：

   ```sh
   yum list docker-ce --showduplicates | sort -r
   ```

6. 安装Docker：

   - 安装指定版本：

     **注意**：`--setopt=obsoletes=0`，否则yum会自动安装更高版本

     ```sh
     sudo yum install <FQPN>
     ```

     例：

     ```sh
     yum install --setopt=obsoletes=0 -y docker-ce-19.03.10-3.el7 docker-ce-cli-19.03.10-3.el7 containerd.io
     ```

   - 安装最新稳定版(由于repo中默认只开启stable仓库)：

     ```sh
     sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
     ```

7. 启动并加入开机启动：

   ```sh
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

   也可以使用：启动& 开机启动docker； enable + start 二合一

   ```shell
   systemctl enable docker --now
   ```

8. 验证安装是否成功(有client和service两部分表示docker安装启动都成功)：

   ```sh
   docker version
   ```

   ![image-20240401222521119](assets/img202404012225981-174296611088311.png)

## 使用安装脚本自动安装

1. 安装curl：

   - Ubuntu/Debian安装curl：

     ```sh
     true > /etc/apt/sources.list.d/mobian.list
     sudo apt-get update
     apt-get install curl
     apt-get install wget
     ```

   - CentOS安装curl：CentOS系统自带的curl

     安装最新版本：

     - 安装所需的软件包：

       ```sh
       yum install wget gcc openssl-devel -y
       ```

     - 下载最新的cURL源：

       ```sh
       wget https://curl.se/download/curl-7.76.1.tar.gz
       ```

     - 安装：

       ```sh
       # 解压
       tar -zxvf curl-7.76.1.tar.gz
       cd curl-7.76.1
       ./configure --with-ssl
       make
       make install
       ```

   - 查看curl版本：

     ```sh
     curl --version
     ```

2. 安装所需的软件包：

   ```sh
   sudo yum install -y yum-utils device-mapper-persistent-data lvm2
   ```

3. 命令(任选其一)：

   ```sh
   curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
   ```

   ```sh
   curl -sSL https://get.daocloud.io/docker | sh
   ```

   提示curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to get.docker.com:443错误解决办法：

   Ubuntu 系统下操作:

   ```sh
   apt-get install libnss3
   ```

   Centos 系统下操作:

   ```sh
   yum install nss && yum update nss
   ```

   执行完安装nss步骤后再次执行`curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun`即可

   如果不想安装nss也可以在浏览器打开https://get.docker.com,然后把内容保存为install_docker，在执行`bash -s install_docker --mirror Aliyun`即可

4. 启动并加入开机启动：

   ```sh
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

5. 也可以使用：启动& 开机启动docker； enable + start 二合一

   ```shell
   systemctl enable docker --now
   ```

6. 验证安装是否成功(有client和service两部分表示docker安装启动都成功)：

   ```sh
   docker version
   ```

   ![image-20240401222521119](assets/img202404012225981.png)

## Docker镜像加速

### 配置阿里镜像

阿里云镜像获取：https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors

登陆后，左侧菜单选中镜像加速器就可以看到专属地址，选中粘贴即可。

![image-20240401222805165](assets/img202404012228630.png)

查看是否新增了阿里云的地址：

```sh
docker info
```

![image-20240401224219492](assets/img202404012242145.png)

### 配置网易云加速

配置网易云加速器：无需注册网易云用户。只需将前面的 daemon.json 文件中的那个URL 替换URL 即可。

```sh
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
      "registry-mirrors": ["http://hub-mirror.c.163.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

![image-20240401224659949](assets/img202404012257197.png)

查看是否新增了网易云的地址：

```sh
docker info
```

![image-20240401224734219](assets/img202404012247498.png)
