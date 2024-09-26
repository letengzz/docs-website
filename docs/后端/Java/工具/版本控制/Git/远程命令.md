# Git 远程命令

## 本地仓库推送到远程仓库

```bash
git push 远程仓库别名 分支名称
```

`git push origin master`：

- 远程仓库默认有个别名叫 origin，将本地仓库的文件推送（push）到远程仓库

- -u 参数：第一次推送 master 分支时，Git不但会把本地的 master 分支内容推送的远程新的 master 分支，还会把本地的 master 分支和远程的 master 分支关联起来，在以后的推送或者拉取时就可以简化命令。

  ```bash
  git push -u origin master 
  ```

## 克隆远程仓库到本地仓库

```bash
git clone git地址
```

- GitHub给出的地址不止一个，还可以用http 地址。实际上，Git支持多种协议，默认的 `git://` 使用ssh，但也可以使用 https 等其他协议。
- 使用 https 除了速度慢以外，还有个最大的麻烦是每次推送都必须输入口令，但是在某些只开放http端口的公司内部就无法使用 ssh 协议而只能用 https 。

# 搭建Git服务器

Git软件本身就是用于Linux系统开发所设计的版本管理软件，所以项目中搭建的共享版本库也应该以linux系统为主。

## 在CentsOS服务器中搭建Git服务器。

### 下载Git软件（linux版本）

- 官网下载地址：https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.9.5.tar.gz

  将下载后的压缩文件上传到Linux系统中

  ![image-20230513232500399](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140103304.png)

- 解压Git：

  ```bash
  # 将压缩文件解压到自定义位置
  mkdir /opt/module
  tar -zxvf git-2.9.5.tar.gz -C /opt/module/
  # 可以更改名字，变得简短一些，好操作
  cd /opt/module
  mv git-2.9.5/ git
  ```

- 安装依赖：解压后，需要编译源码，不过在此之前需要安装编译所需要的依赖，耐心等待安装完成，中途出现提示的时候输入y并按回车。

  ```bash
  yum install curl-devel expat-devel gettext-devel openssl-devel zlib-devel gcc perl-ExtUtils-MakeMaker
  ```

- 删除旧版Git：安装编译源码所需依赖的时候，yum操作回自动安装旧版本的Git：

  ```bash
  # 删除旧版本的Git
  yum -y remove git
  ```

- 编译、安装Git：

  ```bash
  # 进入到Git软件的解压目录
  cd /opt/module/git
  # 编译时，prefix设定为Git软件安装目录
  make prefix=/usr/local/git all
  # 安装Git
  make prefix=/usr/local/git install
  ```

- 配置环境变量：

  - 修改linux系统中/etc/profile文件：

    ```bash
    # 配置环境变量
    export PATH=$PATH:/usr/local/git/bin
    ```

  - 刷新环境，让环境变量立即生效：

    ```bash
    source /etc/profile
    ```

- 建立链接文件：

  git安装路径是/usr/local/git，不是默认路径

  ```bash
  ln -s /usr/local/git/bin/git-upload-pack /usr/bin/git-upload-pack
  ln -s /usr/local/git/bin/git-receive-pack /usr/bin/git-receive-pack
  ```

- 测试安装：

  ```bash
  git --version
  ```

### 创建Git用户

因为Git服务器需要安装在linux系统上，当使用远程客户端操作时，就需要提供相应的Git账号进行提交的，如果你的仓库文件的用户不是git的话，是root用户或者别的用户，那么你git push ,它是不允许的，因为你的git用户没有权限。你可以给这个文件创立git用户，或者修改文件夹的权限让所有用户都可以更改

```bash
# 增加用户
adduser git
# 设定密码
passwd git
```

### SSH免密登录

- 服务器端操作：

  ```bash
  # 进入用户目录
  cd /home/git
  # 在git用户根目录创建.ssh目录
  sudo mkdir .ssh
  sudo touch .ssh/authorized_keys
  # 设定.ssh目录，authorized_keys的权限
  sudo chmod -R 700 /home/git/.ssh
  sudo chmod 600 /home/git/.ssh/authorized_keys
  ```

- 客户端操作：

  ```bash
  # 在客户端生成SSH密钥
  # 默认生成的密钥用户就是当前用户，需要和之前的全局配置保持一致
  user.name=18801@LAPTOP-J9IRK5BM
  user.email=18801@LAPTOP-J9IRK5BM
  # 按照提示三次回车即可
  ssh-keygen -t rsa 
  ```

- 将客户端公钥复制到服务器端的.ssh/authorized_keys文件中

### 创建Git版本库

- 创建文件目录

  ```bash
  # 进入用户目录
  cd /home/git
  # 创建版本库目录
  mkdir git-rep 
  # 设定文件所属用户
  sudo chown git:git git-rep
  ```

- 初始化版本库：

  ```bash
  # 进入仓库目录
  cd /home/git/git-rep
  # 初始化仓库，和前面的git init略有不同
  git init -bare test.git
  # 设定文件所属用户
  sudo chown -R git:git test.git
  ```

### 远程访问Git版本库

- 将远程仓库克隆到本地：

  ```bash
  # 将远程仓库克隆到本地，形成本地仓库
  # 克隆远程仓库 => 用户@主机名:仓库地址
  git clone git@linux1:/home/git/git-rep/test.git
  ```

- 提交文件到本地仓库：

  ```bash
  # 增加文件
  git add client.txt
  # 提交文件
  git commit -m 'client'
  ```

- 将本地仓库同步到远程仓库：

  ```bash
  # 同步远程仓库
  # 远程仓库默认有个别名叫origin，将本地仓库的文件推送（push）到远程仓库
  # git push 远程仓库别名 分支名称
  git push origin master
  ```

- 查看远程仓库：

  ```bash
  # 服务器端切换用户
  su git
  # 进入仓库
  cd /home/git/git-rep/test.git
  # 切换到主干分支
  git checkout master
  # 查看git日志
  git log 
  ```

  