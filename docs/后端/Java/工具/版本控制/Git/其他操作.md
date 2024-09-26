# Git 其他操作

## git config 自定义配置颜色

Git会适当地显示不同的颜色，比如 git status 命令

```bash
git config --global color.ui true
```

![image-20230514004027556](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140113887.png)

## 忽略特殊文件

一般情况下工作区中的文件都是要交给Git管理的，但有些文件并不想交给Git管理。但是又由于该文件处理工作区，所有在执行git status命令的时候会给出xx文件Untracked (未被跟踪)

在Git工作区的根目录下创建一个特殊的 .gitignore 文件，然后把要忽略的文件名填进去，Git就会自动忽略这些文件。 

GitHub已经准备了各种配置文件，只需要组合一下就可以使用了。

所有配置文件可以直接在线浏览：https://github.com/github/gitignore

### 添加文件，用 -f 强制添加到Git

```bash
git add -f App.class
```

### 检查忽略文件

```bash
git check-ignore 
```

### 忽略文件的原则

- 忽略操作系统自动生成的文件，比如缩略图等
- 忽略编译生成的中间文件、可执行文件等，也就是如果一个文件是通过另一个文件自动生成的，那自动生成的文件就没必要放进版本库，比如Java编译产生的 .class 文件；
- 忽略你自己的带有敏感信息的配置文件，比如存放口令的配置文件。

### 忽略文件的案例

假设在Windows下进行Python开发，Windows会自动在有图片的目录下生成隐藏的缩略图文件，如果有自定义目录，目录下就会有 Desktop.ini 文件，因此需要忽略Windows自动生成的垃圾文件：

```bash
# Windows: 
Thumbs.db 
ehthumbs.db 
Desktop.ini 
```

继续忽略Python编译产生的 .pyc 、 .pyo 、 dist 等文件或目录：

```bash
# Python:
*.py[cod]
*.so
*.egg
*.egg-info
dist
build
```

加上你自己定义的文件，最终得到一个完整的 .gitignore 文件：

```bash
# Windows:
Thumbs.db
ehthumbs.db
Desktop.ini
# Python:
*.py[cod]
*.so
*.egg
*.egg-info
dist
build
# My configurations:
db.ini
deploy_key_rsa
```

 最后一步就是把 .gitignore 也提交到Git，就完成了

## 配置别名

- 将 `status` 设 st 为别名： 

  ```bash
  git config --global alias.st status
  ```

- 配置一个 unstage 别名： 

  ```bash
  git config --global alias.unstage 'reset HEAD'
  ```

  当使用 `git unstage test.py` 实际上是  `git reset HEAD test.py`

- 配置一个 `git last` ，让其显示最后一次提交信息

  ```bash
  git config --global alias.last 'log -1'
  ```

配置Git的时候，加上 `--global` 是针对当前用户起作用的，如果不加，那只针对当前的仓库起作用。

每个仓库的Git配置文件都放在 .git/config 文件中

- 当前用户的Git配置文件放在用户主目录下的一个隐藏文件 .gitconfig 中

- 配置别名也可以直接修改这个文件，如果改错了，可以删掉文件重新通过命令配置。

## 高效使用GitHub

### 如何找项目

#### 搜索spring boot

##### 根据名字搜索

名字含有spring boot的项目：`in:name spring boot`

![image-20230514005018629](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140113480.png)

##### 根据 starts和forks搜索

搜索名字含有spring boot同时starts > 3000，forks>3000：`in:name spring boot stars:>3000 forks:>3000`

![image-20230514005047099](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140113519.png)

##### 根据 readme和language和pushed搜索

搜索readme中含有微服务 语言为java push时间为2019-09-01之后的：`in:readme 微服务 language:java pushed:>2019-09-01`

![image-20230514005106159](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140113396.png)

##### 根据 description 搜索

搜索描述包含爬虫，语言为python，stars >1000 ,2020-1-1有更新的：`in:description 爬虫 language:python stars:>1000 pushed:>2020-01-01`

![image-20230514005136561](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140113112.png)

#### 组合搜索

搜索文档中包含spring security的开源项目

![image-20230514004955567](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140113040.png)
