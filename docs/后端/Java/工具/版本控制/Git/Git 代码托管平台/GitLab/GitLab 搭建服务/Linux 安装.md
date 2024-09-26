# Linux 安装

**注意**：安装所需最小配置内存至少4G

**官方文档**：https://docs.gitlab.cn/jh/install/requirements.html

## 安装方式一

### 下载GitLab

下载地址：https://packages.gitlab.com/gitlab/gitlab-ce

如果下载不了，或下载比较慢，可以根据提示在在linux系统中直接采用wget指令下载：

![image-20230514003127782](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107182.png)

### 开启ssh

**说明**：已开启ssh可跳过。

```shell
sudo systemctl status sshd
sudo systemctl enable sshd
sudo systemctl start sshd
```

### 安装配置依赖

```sh
sudo yum install -y curl policycoreutils-python openssh-server perl
sudo yum install -y postfix
sudo systemctl enable postfix
sudo systemctl start postfix
```

### 安装GitLab

安装GitLab：直接采用下载的RPM软件包安装即可：

```sh
sudo rpm -ivh /opt/module/software/gitlab-ce-15.7.0-ce.0.el7.x86_64.rpm
```

![image-20230514003143828](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107080.png)

## 安装方式二

### 开启ssh

**说明**：已开启ssh可跳过。

```shell
sudo systemctl status sshd
sudo systemctl enable sshd
sudo systemctl start sshd
```

### 配置软件镜像

> 中文镜像库

```
curl -fsSL https://packages.gitlab.cn/repository/raw/scripts/setup.sh | /bin/bash
```

> 清华大学镜像库

```sh
vi /etc/yum.repos.d/gitlab-ce.repo
```

```sh
[gitlab-ce]
name=Gitlab CE Repository
baseurl=https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el$releasever/
gpgcheck=0
enabled=1
```

### 安装

注意上述的镜像库中的版本

> 社区版：

```bash
sudo EXTERNAL_URL="https://centos" yum install -y gitlab-ce
```

> 极狐版：

```bash
sudo EXTERNAL_URL="http://192.168.84.137" yum install -y gitlab-jh
```

## 初始化GitLab

```bash
sudo gitlab-ctl reconfigure
```

## 修改GitLab配置文件

1. 修改GitLab的访问地址和端口

   ```sh
   vi  /etc/gitlab/gitlab.rb
   ```

   ![image-20240330223603898](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403302236309.png)

   访问地址，如果出现502的问题，基本上是端口被占用，需要修改puma['port']=8080。默认是8080端口，修改为其他的端口，且不能和gitlab访问端口一样。

   ![image-20240330223909728](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403302239678.png)

2. 修改host：

   编辑gitlab.yml：

   ```shell
   sudo vim /opt/gitlab/embedded/service/gitlab-rails/config/gitlab.yml.example
   ```

   修改gitlab.host，保存并退出：

   ```yaml  gitlab:
     gitlab:
   
       \## Web server settings (**note:** host is the FQDN, do not include http://)
   
       host: gitlabtest
   
       port: 80
   
       https: false
   ```

   修改文件名称：

   ```shell
   sudo mv /opt/gitlab/embedded/service/gitlab-rails/config/gitlab.yml.example /opt/gitlab/embedded/service/gitlab-rails/config/gitlab.yml
   ```

## 启动GitLab

  - 启动：

    ```bash
    gitlab-ctl start
    ```

  - 停止：

    ```bash
    gitlab-ctl stop
    ```

## 配置防火墙

在CentOS 7上，下面的命令也会在系统防火墙中打开HTTP、HTTPS和SSH访问。这是一个可选步骤，如果您打算仅从本地网络访问极狐GitLab，则可以跳过它

- **firewall http 服务开启**：

  ```bash
  sudo systemctl status firewalld
  firewall-cmd --query-service http ##查看http服务是否支持，返回yes或者no
  firewall-cmd --add-service=http ##临时开放http服务
  firewall-cmd --add-service=http --permanent ##永久开放http服务
  firewall-cmd --reload ##重启防火墙生效
  ```

- **firewall https 服务开启**：

  ```bash
  sudo systemctl status firewalld
  firewall-cmd --add-service=https --permanent
  sudo systemctl reload firewalld
  ```

## 访问

访问GitLab 进入：http://centos/users/sign_in

![image-20240330235420340](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403302354872.png)

**注意**：当URL为主机名时在host中设置主机名及ip

![image-20230514003740918](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107910.png)

初始化时，软件会提供默认管理员账户：root，但是密码是随机生成的。在/etc/gitlab/initial_root_password文件中查找密码

```sh
cat /etc/gitlab/initial_root_password
```

![image-20240330235610219](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403302356640.png)



## 修改密码

在安装过程中指定了自定义密码，否则将随机生成一个密码并存储在 `/etc/gitlab/initial_root_password` 文件中(出于安全原因，24 小时后，此文件会被第一次 `gitlab-ctl reconfigure` 自动删除，因此若使用随机密码登录，建议安装成功初始登录成功之后，立即修改初始密码）

使用此密码和用户名 `root` 登录，修改一下密码

![image-20230514003756915](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107749.png)

![image-20230514003802544](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107587.png)

## 设置简体中文

点击右上角个人头像 -> preferences -> preferences-> Localization更改简体中文：

![wps223](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131328090.jpg)

回到首页，可以看到变成中文。

## 重装GitLab

1. 卸载GitLab：

   ```shell
   sudo rpm -e gitlab-jh-16.6.1
   ```

2. 删除GitLab文件：

   ```shell
   sudo rm -rf /etc/gitlab
   sudo rm -rf /var/opt/gitlab
   sudo rm -rf /opt/gitlab
   ```

3. 重装如果卡在sudo gitlab-ctl reconfigure配置命令上，可以使用另外一个窗口执行：

   ```shell
   sudo systemctl restart gitlab-runsvdir
   ```



