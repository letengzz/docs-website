# Git 标签命令

## 创建标签

```bash
git tag <name> 
```

**说明**：

- 需要切换到需要打标签的分支上

- 给历史打标签：`git tag v0.9 f52c633`

- 创建带有说明的标签，用 `-a` 指定标签名， `-m` 指定说明文字：

  ```bash
  git tag -a v0.1 -m "version 0.1 released" 1094adb 
  ```

## 查看所有标签

```bash
git tag
```

## 查看标签信息

```bash
git show <tagname>
```

## 查看说明文字

```bash
git show <tagname>
```

## 指定标签信息

```bash
git tag -a <tagname> -m "标签信息"
```

## 删除标签

```bash
git tag -d <tagname>
```

**说明**：因为创建的标签都只存储在本地，不会自动推送到远程。所以，打错的标签可以在本地安全删除。

## 推送标签到远程库

```bash
git push origin <tagname>
```

## 一次性推送全部尚未推送到远程的本地标签

```bash
git push origin --tags
```

## 从远程删除标签

```bash
git push origin :refs/tags/v0.9
```

# Git 标签操作

## 创建标签

- 切换到需要打标签的分支上：

  ![image-20230513234935268](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140103711.png)

- 使用  `git tag <名称>` 创建标签，用命令 `git tag` 查看所有标签：

  ![image-20230513234941679](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140103067.png)

- 默认标签是打在最新提交的commit上的，可以给之前的操作打上标签：

  - 使用 `git log --pretty=oneline --abbrev-commit` 查看历史提交的commit id 提交打上标签

    ![image-20230513235047457](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104833.png)

- 标签不是按时间顺序列出，而是按字母排序的。可以用 `git show <tagname>` 查看标签信息：

  ![image-20230513235057534](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104652.png)

- 创建带有说明的标签：用 `-a` 指定标签名， `-m` 指定说明文字

  `git tag -a v0.1 -m "version 0.1 released" 1094adb` 

  ![image-20230513235110847](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104416.png)

## 推送标签到远程库

- 推送单个标签：

  ![image-20230513235140930](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104114.png)

- 推送全部尚未推送到远程库的本地标签：

  ![image-20230513235148404](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104064.png)

- ![image-20230513235135933](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104009.png)

## 删除标签

- 当本地标签打错了，可以删除本地标签：

  ![image-20230513235158453](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104886.png)

- 因为创建的标签都只存储在本地，不会自动推送到远程。所以，打错的标签可以在本地安全删除。

- 删除远程库：

  - 首先从本地删除标签：

    ![image-20230513235207521](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104759.png)

  - 从远程库中删除：

    ![image-20230513235210767](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104556.png)

  - ![image-20230513235230186](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140104461.png)