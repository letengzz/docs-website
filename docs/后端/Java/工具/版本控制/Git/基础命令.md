# Git 基础命令

## Linux 操作命令

最初Git软件是为辅助 Linux 内核开发的一套软件，所以在使用时，简单常用的linux系统操作指令是可以直接使用的

<img src="https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140057353.png" alt="图片1" style="zoom: 67%;" />

## 获取软件的配合信息

```bash
git config -l
```

配置文件位置为：Git安装路径/etc/gitconfig

![image-20230513223745598](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140057770.png)

## 设置用户名/邮箱

```bash
git config --global user.name 用户名
git config --global user.email test@hjc.com
```

- --global表示全局配置，后续的所有文件操作都会使用该用户名称及邮箱

- 在操作系统的用户目录，会产生新的配置文件.gitconfig：

  ![image-20230513223835884](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140057689.png)

  ![image-20230513223841153](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140057664.png)

## 查看用户名/邮箱

```bash
git config user.name
git config user.email
```

## 查看全局配置

```shell
git config --list # 查看全局配置
```

## 初始化版本库

```bash
git init
```

- 需要指定某一个文件目录作为软件的管理目录。因为这个目录主要就作为Git软件的管理文件的版本变化信息，所以这个目录也称之为Git软件的版本仓库目录。

- 创建成功后，会在目录中创建 .git 目录，这个目录是Git来跟踪管理版本库的，切勿破坏。

  ![image-20230513223949030](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058656.png)

- 如果没有看到 .git 目录，那是因为这个目录默认是隐藏的，用 `ls -ah` 命令就可以看见。

## 查看版本库状态

```bash
git status
```

**说明**：


- 分支中没有需要提交的数据：

  ![image-20230513224028483](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058056.png)

- 分支中有需要提交的数据：

  ![image-20230513224034940](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058924.png)

- 分支中新提交的数据：

  ![image-20230513224040752](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058274.png)

- 分支中的数据有修改内容：

  ![image-20230513224045264](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058230.png)

## 添加到版本库

```bash
git add 文件名
```

添加所有文件到版本库：

```shell
git add .
```

使用通配符*指定多个文件：

```shell
git add a*
```

**操作步骤**：

- 手动创建文件：test.txt：

  ![image-20230513224149120](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058246.png)

- 通过软件的指令查看版本库状态：

  ![image-20230513224155457](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058393.png)

  test.txt文件属于untracked files（未追踪文件），这里表示当前的test.txt文件虽然放置到了版本库的文件目录中，被Git软件识别到了，但是未纳入到版本库管理中。所以属于未追踪文件。通过这个现象可以认为，系统文件夹物理目录和版本库管理目录的含义是不一样的。只有文件被纳入到版本库管理后，Git软件才能对文件修改后的不同版本内容进行追踪处理，也就是所谓的tracked files了。

- 添加到版本库中： `git add test.txt`

- 再次查看版本库状态：

  ![image-20230513224245856](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058489.png)

  此时文件状态为cached file，是Git管理文件时的一种状态：暂存状态。就是我们生活中常说的草稿状态。也就是说对于Git来讲，它认为此时文件只是一种临时草稿状态，随时可能会进行修改或删除，并不算真正的操作完成状态。所以并不会把文件纳入到版本库管理中。


## 提交到版本库

```bash
git commit -m "my first git file"
```

- -m 表示提交时的信息 (message)，是必须输入的。用于描述不同版本之间的差别信息
- -a 表示在提交前执行添加操作 相当于先将文件git add 添加后 git commit 提交。一步完成。

提交之后，查看Git状态：

![image-20230513224330811](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058961.png)

## 比较工作区与暂存区差异

**说明**：显示的格式是Unix通用的diff格式

```bash
git diff 文件名
```

## 比较暂存区与本地库差异

```bash
git diff --cached 文件名
```

## 查看当前提交数据

```bash
git show
```

![image-20230513224437143](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058406.png)


- Git会对当前的操作进行Hash计算，通过计算后的值将数据保存下来，保存的位置为版本库.git文件目录的objects中

  ![image-20230513224448492](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058934.png)

- 文件内容进行了转换处理

  ![image-20230513224455261](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058914.png)

## 查看版本库文件历史

通过 git log 查看文件的版本信息就会发生变化

```bash
git log
```

- 使用 git log --pretty=oneline 美化显示方式：

  ```bash
  git log --pretty=oneline
  ```

- 使用 `git log --oneline` 简单方式显示：

  ```bash
  git log --oneline
  ```

- 使用 `git log --pretty=oneline --abbrev-commit` 查看历史提交：

  ```bash
  git log --pretty=oneline --abbrev-commit
  ```

**说明**：当git log日志命令显示的内容太多，无法在一页内显示完毕所有内容时，其最后一行会出现一个冒号，让输入命令：

![未命名绘图](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202308171426498.png)

## 记录每一次命令

```bash
git reflog
```

```shell
git reflog -n 数量
```

## 把文件从缓存区撤销，回到未被追踪的状态

```bash
git restore 文件名
```

包括对文件自身的操作，如添加文件、删除文件

## 丢弃工作区的修改

```bash
git checkout -- 文件名
```

- 文件自修改后还没有被放到暂存区，现在，撤销修改就回到和版本库一模一样的状态
- 文件已经添加到暂存区后，又作了修改，现在，撤销修改就回到添加到暂存区后的状态。
- git checkout 是用版本库里的版本替换工作区的版本，无论工作区是修改还是删除，都可以“一键还原”。

**注意**：从来没有被添加到版本库就被删除的文件，是无法恢复的

## 将暂存区的修改撤销掉(unstage)，重新放回工作区

```bash
git reset HEAD 文件名
```

- git reset 命令既可以回退版本，也可以把暂存区的修改回退到工作区。当我们用 HEAD 时，表示最新的版本。
- 相当于撤销git add 操作，不影响上一次commit后对本地文件的修改。

## 将版本库文件回退到某一版本

```bash
git reset --hard 版本值
```

`git reset --hard f2f113f`：

- 这里的f2f113f就是版本Hash值，用于唯一确定版本库中此版本的标记

如果不记得具体的版本值，版本值也可以使用HEAD值，比如最新的上一个版本：`HEAD^`：

```bash
git reset --hard HEAD^
```

如果后退更多的版本,可以使用 `HEAD~N`：

```bash
git reset --hard HEAD~2
```

远程仓库回退：这个命令将强制推送本地上一个提交的版本到远程仓库，覆盖当前的代码。需要注意的是，这种方法会改变远程仓库的历史记录，因此在团队协作中需要谨慎使用。

```
git push -f origin HEAD^:branch_name
```

## 从版本库中删除文件

```bash
git rm 文件名
```

# Git 基础操作

## 首次使用相关配置

如果首次使用Git软件，需要告诉Git软件你的名称和邮箱，否则是无法将文件纳入到版本库中进行版本管理的。这是因为在多人协作时，不同的用户可能对同一个文件进行操作，所以Git软件必须区分不同用户的操作，区分的方式就是名称和邮箱。

只用本地库，不需要进行多人协作，也需要配置，因为Git软件的设计初衷本身就是针对于linux系统的分布式开发协同工作，所以它天生就是用于分布式协同工作的，所以无论是否使用这个功能，它本身就是这么设计的。所以是一定要配置的，否则就会出现如下提示：

![image-20230513225056292](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058324.png)

**注意**：这里设置用户签名和将来登录GitHub (或其他代码托管中心) 的账号没有任何关系。

### 设置用户名和邮箱

```bash
git config --global user.name 用户名
git config --global user.email test@hjc.com
```

设置用户名和邮箱后，在操作系统的用户目录，会产生新的配置文件.gitconfig：

![image-20230513225108750](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058557.png)

![image-20230513225112478](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058517.png)

查看用户名和密码：

![image-20230513225120476](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058805.png)

## 创建版本库并添加文件到版本库

需要指定某一个文件目录作为软件的管理目录。因为这个目录主要就作为Git软件的管理文件的版本变化信息，所以这个目录也称之为Git软件的版本仓库目录。

 1. 通过指令进入到指定文件目录：

    ![image-20230513225353888](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058528.png)

 2. 执行指定的命令，创建文件版本库：

    ![image-20230513225404770](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058677.png)

 3. 创建成功后，会在目录中创建.git 目录，用于管理当前版本库：

    ![image-20230513225412714](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058061.png)

 4. 手动创建文件：test.txt：

    ![image-20230513225421274](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058025.png)

    所有的版本控制系统，其实只能跟踪文本文件的改动，比如TXT文件，网页，所有的程序代码等等，Git也不例外。版本控制系统可以告诉你每次的改动，比如在第5行加了一个单词“Linux”，在第8行删了一个单词“Windows”。而图片、视频这些二进制文件，虽然也能由版本控制系统管理，但没法跟踪文件的变化，只能把二进制文件每次改动串起来，也就是只知道图片从100KB改成了120KB，但到底改了啥，版本控制系统不知道，也没法知道。

 5. 通过软件的指令查看版本库状态：

    ![image-20230513225510554](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140058908.png)

 6. 添加到版本库中： git add test.txt

 7. 再次查看版本库状态：

    ![image-20230513225517691](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059843.png)

## 提交到版本库

- 文件添加到版本库后，使用`git commit` 提交到版本库，并查看Git状态：

  ![image-20230513225627718](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059984.png)

- 提交后，Git会对当前的操作进行Hash计算，通过计算后的值将数据保存下来，保存的位置为版本库.git文件目录的objects中

- 使用 `git show` 查看提交的数据：

  ![image-20230513225635659](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059401.png)

## 修改文件

- 当修改文件后，使用 `git status` 查看状态，发现文件已经修改：

  ![image-20230513225703069](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059247.png)

- 使用 `git diff` 比较修改后的差异：

  ![image-20230513225713841](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059794.png)

- 使用 `git commit` 直接将修改数据提交：

  ![image-20230513225737047](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059215.png)

- 展示修改的内容及所提交的信息：

  ![image-20230513225744269](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059580.png)

## 删除文件

一般情况下，Git软件就是用于管理文件的版本变更，但是在一些特殊的场景中，文件可能作废或不再使用，那么就需要从版本库中删除，记住，这里说的并不是从物理文件目录中删除，而是从版本库中删除。

- 使用 `git status` 查看Git状态：

  ![image-20230513225801160](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140100307.png)

  此时Git软件会识别出来，版本库中有一份文件和当前用于临时操作文件的暂存区内的文件状态不一致：版本库中文件还在，但是操作区内的文件已经没有了。所以软件提供了两个选择：一个是将版本库中的文件也进行（提交）删除操作。另外一个就是从版本库中恢复文件。

- 使用 `git restore` 指令从版本库中恢复文件：

  ![image-20230513225818476](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059143.png)

- 使用 `git commit` 提交将版本库中同时删除：

  ![image-20230513225836593](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059484.png)

- 也可以使用 `git rm` 从版本库中删除(相当于删除后提交，不可以通过 `git restore` 恢复)：

  ![image-20230513225845128](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059788.png)

## 版本回退

如果版本库中一份文件中已经被删除了，原则上来讲，已经不能找回来了，因为文件删除本身也是一种变更操作，也算是版本库管理的一部分。所以想要将已经删除的那份文件从版本库中取出来，已经是不可能了。但是，要注意的是，版本库管理的是文件不同版本的变更操作，这个不同版本的概念还是非常重要的。也就是说，最后的那个删除的文件版本已经没有了，但是之前版本的文件其实还是存在的。所以如果我们能将文件恢复到某一个版本，那么那个版本的文件就依然存在。

- 使用 `git log --oneline` 查看版本库信息：

  ![image-20230513230019374](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059470.png)

- 使用 `git reset` 将版本库文件重置到某一个版本：

  ![image-20230513230042234](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059655.png)

- 如果不记得具体的版本值，版本值也可以使用HEAD值，比如最新的上一个版本：`HEAD^`

  ```bash
  git reset --hard HEAD^
  ```

- 如果后退更多的版本,可以使用  `HEAD~N`

  ```bash
  git reset --hard HEAD~1
  ```

## 版本库基本状态

Git的版本库里存了很多东西，其中最重要的stage(或者叫index)的暂存区，还有Git自动创建的第一个分支 master，以及指向 master 的一个指针叫 HEAD 

![image-20230513230336828](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059766.png)

当文件往Git版本库里添加的时候，是分两步执行的

- 第一步是用 `git add` 把文件添加进去，实际上就是把文件修改添加到暂存区
- 第二步是用 `git commit` 提交更改，实际上就是把暂存区的所有内容提交到当前分支

创建Git版本库时，Git自动为我们创建了唯一一个 master 分支，所以，现在， git commit 就是往 master 分支上提交更改。

git add 命令实际上就是把要提交的所有修改放到暂存区（Stage），然后，执行 git commit 就可以一次性把暂存区的所有修改提交到分支。

- add后的版本库状态：

  ![image-20230513230418656](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059591.png)

- commit后的版本库状态：

  ![image-20230513230439690](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140059351.png)