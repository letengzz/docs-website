# Git 分支命令

## 主干分支

默认情况下，Git软件就存在分支的概念，而且就是一个分支，称之为 master 分支，也称之为**主干分支**。

![image-20230513230951276](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101160.png)

这就意味着，所有文件的版本管理操作都是在 master 这一个分支路线上进行完成的。

**默认的所有操作本身就都是基于master分支完成的**。而master主干分支在创建版本库时，也就是 `git init` 时默认就会创建。

## 其他分支

如果仅仅是一个分支，在某些情况并不能满足实际的需求，那么就需要创建多个不同的分支。

## 创建分支

创建分支都是基于当前分支为基础的。

```bash
git branch 分支名称
```

## 创建分支，并直接切换到新的分支

```bash
git checkout -b 分支名称
```

## 查看分支

```bash
git branch -v
```

## 切换分支

```bash
git checkout 分支名称
```

## 删除分支

**删除本地分支**：

```bash
git branch -d 分支名称
```

**删除远程分支**：

```bash
 git push origin --delete 分支名称
```

## 合并分支

```bash
git merge 分支名称
```

## 查看操作日志

```bash
git log --graph
```

## Git 分支操作

### 分支基础操作

- 默认使用主干分支master 默认的所有操作本身就都是基于master分支完成的。而master主干分支在创建版本库时，也就是 `git init` 时默认就会创建：

  ![image-20230513231204972](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101422.png)

- 创建两个b1 b2分支(基于master主干分支为基础的)：

  ![image-20230513231227342](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101063.png)

- 使用 `git branch -v` 查看所有分支：

  ![image-20230513231239907](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101074.png)

- 使用 `git checkout` 切换到b1，并在b1分支中提交新文件，查看分支信息，会发现不同分支的版本进度信息发生了改变：

  ![image-20230513231253989](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101047.png)

- 此时切换回到主干分支的话，那么b1.txt文件就不存在了，因为对应版本信息不一样：

  ![image-20230513231303278](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101872.png)

- 如果觉得某一个分支建立的不太理想或已经没有必要在使用了，那么是可以将这个分支删除的：

  ![image-20230513231309161](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101913.png)

### 分支合并操作

无论创建多少个分支，都是因为需要在不同的工作环境中进行工作，但是，最后都应该将所有的分支合在一起。形成一个整体。作为项目的最终结果。

![image-20230513231322646](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101568.png)

- 清空主干分支所有文件，并创建一个文件master.txt，并提交：

  ![image-20230513231336916](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101867.png)

- 创建分支，并直接切换到新的分支，在新分支中添加新文件branch.txt，并提交：

  ![image-20230513231344036](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101416.png)

- 此时切换回主干分支，只有master.txt文件。再切换回new_branch分支，branch文件就又回来了：

  ![image-20230513231350320](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101730.png)

- 切回到主干分支，执行 `git merge` 命令合并分支。再次查看文件，就会发现branch.txt文件已经在master分支中：

  ![image-20230513231403360](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140101572.png)

### 解决冲突操作

在多分支并行处理时，每一个分支可能是基于不同版本的主干分支创建的。如果每隔分支都独立运行而不进行合并，就没有问题，但是如果在后续操作过程中进行合并的话，就有可能产生冲突。比如B1, B2的两个分支都是基于master分支创建出来的。B1分支如果和B2分支修改了同一份文件的话，那么在合并时，以哪一个文件为准呢，这就是所谓的**冲突**。

![image-20230513231437501](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102375.png)

- 将主干分支的所有文件清空，并添加文件test.txt，文件内容为空：

  ![image-20230513231452048](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102612.png)

  - ![image-20230513231457043](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102568.png)

- 基于主干分支，创建两个分支b1, b2：

  ![image-20230513231512664](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102498.png)

  - ![image-20230513231632311](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102511.png)

- 切换到分支b1 并修改文件内容：

  ![image-20230513231521727](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102713.png)

  - ![image-20230513231640262](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102087.png)

- 切换到分支b2 并修改文件内容：

  ![image-20230513231527855](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102416.png)

  - ![image-20230513231649137](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102670.png)

- 合并分支 b1：

  ![image-20230513231532467](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102988.png)

  - ![image-20230513231655724](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102011.png)

- 合并分支 b2 因为b2分支也对文件进行了修改，所以如果此时合并b2分支,就会提示冲突：

  ![image-20230513231538319](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102137.png)

  - ![image-20230513231726063](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102188.png)

- 使用 `git diff` 查看文件内容差异：

  ![image-20230513231543001](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102952.png)

- 此冲突，软件是无法判断该如何出来处理的，所以需要人工进行判断，将冲突的文件内容进行修正。

  ![image-20230513231549234](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102343.png)

- 重新提交到master主干分支中

  ![image-20230513231553537](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102216.png)

  - ![image-20230513231743428](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102277.png)

- 使用git log 查看操作日志

  ![image-20230513231601061](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102039.png)

- ![image-20230513231605097](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140102995.png)

## 分支功能介绍

![img](assets/wps13111.jpg)

### 主干分支 master

主要负责管理正在运行的生产环境代码，永远保持与正在运行的生产环境完全一致。为了保持稳定性一般不会直接在这个分支上修改代码，都是通过其他分支合并过来的。

### 开发分支 develop

主要负责管理正在开发过程中的代码。一般情况下应该是最新的代码。

### 功能分支 feature

为了不影响较短周期的开发工作，一般把中长期开发模块，会从开发分支中独立出来。 开发完成后会合并到开发分支。

### 准生产分支（预发布分支） release

较大的版本上线前，会从开发分支中分出准生产分支，进行最后阶段的集成测试。该版本上线后，会合并到主干分支。生产环境运行一段阶段较稳定后可以视情况删除。

### bug 修理分支 hotfix

主要负责管理生产环境下出现的紧急修复的代码。 从主干分支分出，修复完毕并测试上线后，并回主干分支和开发分支。并回后，视情况可以删除该分支。