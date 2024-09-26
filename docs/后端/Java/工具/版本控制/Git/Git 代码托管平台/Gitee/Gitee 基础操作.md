# Gitee 基础操作

## 注册网站会员

注册并登录Gitee：

![image-20230514001949044](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108715.png)

## 用户中心

登录成功后跳转到用户中心

![image-20230514002037048](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108200.png)

## 创建远程仓库

右上角选择新建仓库：

![image-20230514002051523](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107533.png)

填写仓库信息并创建：

![image-20230514002101335](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107562.png)

创建成功

![image-20230514002107558](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107151.png)

## 远程仓库简易操作指令

![image-20230514002127575](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107118.png)

## SSH 免密操作

同github一样Gitee支持两种同步方式“https”和“ssh”。如果使用https很简单基本不需要配置就可以使用，但是每次提交代码和下载代码时都需要输入用户名和密码。ssh模式比https模式的一个重要好处就是，每次push、pull、fetch等操作时，不用重复填写遍用户名密码。前提是必须是这个项目的拥有者或者合作者，且配好了ssh key。

- 本地生成SSH密钥：

  `ssh-keygen -t rsa -C Gitee邮箱`

  需要把邮件地址换成你自己的邮件地址，然后一路回车，使用默认值即可，由于这个Key无需设置密码。

- 执行命令完成后，在window本地用户 .ssh 目录 C:\Users\用户名\.ssh 下面生成公钥和私钥：

  ![image-20230514002244992](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107229.png)

- 集成用户公钥：将id_rsa.pub文件内容复制到Gitee仓库中

  ![image-20230514002254440](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107317.png)

  ![image-20230514002259614](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107029.png)

## 设定全局用户

```bash
git config --global user.name '202088'
# 这里的邮箱地址需要为远程仓库简易操作指令内容
git config --global user.email '202088@163.com'
```

## 创建本地库以远程地址

```bash
# 初始化本地仓库
git init
# 设置远程仓库
git remote add origin git@gitee.com:letengzz/git-repo.git
```

## 新增，提交本地仓库文件

```bash
# 新增文件
git add test.txt
# 提交文件
git commit test.txt
```

## 推送到 Gitee 远程仓库

```bash
# 推送文件
git push -u origin "master"
```

## 从远程库克隆

新建仓库，设置README文件，这样Gitee会自动创建一个README.md 文件：

![image-20230514002916289](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107271.png)

创建完毕后，可以看到 README.md 文件：

![image-20230514002921857](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107213.png)

使用命令 `git clone` 克隆一个本地库，查看文件已经存在了：

![image-20230514002925784](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140107085.png)

Gitee给出的地址不止一个，还可以用http 地址。实际上，Git支持多种协议，默认的 git:// 使用ssh，但也可以使用 https 等其他协议。

使用 https 除了速度慢以外，还有个最大的麻烦是每次推送都必须输入口令，但是在某些只开放http端口的公司内部就无法使用 ssh 协议而只能用 https 。