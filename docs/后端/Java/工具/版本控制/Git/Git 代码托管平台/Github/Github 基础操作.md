# GitHub 基础操作

首先需要访问[官网](https://github.com/)，注册登录账号。

## 创建新的仓库

- 两种方式，任选其一：

  ![image-20230513235452404](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104273.png)

- 输入仓库的相关信息：

  ![image-20230513235459573](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104185.png)

## 基本操作指令

![image-20230513235613316](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140105568.png)

## SSH 免密操作

github支持两种同步方式"https"和"ssh"。如果使用https很简单基本不需要配置就可以使用，但是每次提交代码和下载代码时都需要输入用户名和密码。ssh模式比https模式的一个重要好处就是，每次push、pull、fetch等操作时，不用重复填写遍用户名密码。前提是必须是这个项目的拥有者或者合作者，且配好了ssh key。

- 本地生成SSH密钥：`ssh-keygen -t rsa -C GitHub邮箱`

  ```sh
  ssh-keygen -t rsa -C GitHub邮箱
  ```

  需要把邮件地址换成你自己的邮件地址，然后一路回车，使用默认值即可，由于这个Key无需设置密码。

- 执行命令完成后，在window本地用户 .ssh 目录 `C:\Users\用户名\.ssh` 下面生成公钥和私钥：

  ![image-20230513235656181](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140105198.png)

- 集成用户公钥：将id_rsa.pub文件内容复制到GitHub仓库中

  ![image-20230513235711239](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140105423.png)

  ![image-20230513235716328](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140105262.png)

## 设定全局用户

```bash
git config --global user.name '202088'
# 这里的邮箱地址需要为GitHub网站的注册账号
git config --global user.email '202088@163.com'
```

## 创建本地库以远程地址

```bash
# 初始化本地仓库
git init
# 设置远程仓库
git remote add origin git@github.com:Joe-Clion/git-study.git
```

## 新增，提交本地仓库文件

```bash
# 新增文件
git add test.txt
# 提交文件
git commit test.txt
```

## 推送到GitHub远程仓库

```bash
# 推送文件
git push origin master
```

SSH警告：

当第一次使用Git的 clone 或者 push 命令连接GitHub时，会得到一个警告：

> The authenticity of host 'github.com (xx.xx.xx.xx)' can't be established.
> RSA key fingerprint is xx.xx.xx.xx.xx.
> Are you sure you want to continue connecting (yes/no)?

这是因为Git使用SSH连接，而SSH连接在第一次验证GitHub服务器的Key时，需要确认GitHub的Key的指纹信息是否真的来自GitHub的服务器，输入 yes 回车即可。
Git会输出一个警告，告诉已经把GitHub的Key添加到本机的一个信任列表里了：这个警告只会出现一次，后面的操作就不会有任何警告了。

## 从远程库克隆

- 新建仓库，勾选Add a README file，这样GitHub会自动创建一个README.md 文件：

  ![image-20230514000030061](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140106249.png)

- 创建完毕后，可以看到 README.md 文件：

  ![image-20230514000038799](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140106846.png)

- 使用命令 git clone 克隆一个本地库，查看文件已经存在了：

  ![image-20230514000043963](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140106585.png)

- GitHub给出的地址不止一个，还可以用http 地址。实际上，Git支持多种协议，默认的 git:// 使用ssh，但也可以使用 https 等其他协议。

  使用 https 除了速度慢以外，还有个最大的麻烦是每次推送都必须输入口令，但是在某些只开放http端口的公司内部就无法使用 ssh 协议而只能用 https 。