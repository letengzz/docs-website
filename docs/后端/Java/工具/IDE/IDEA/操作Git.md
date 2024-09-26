# IDEA 操作 Git

## 基本操作

在IDEA中创建一个空的项目：

![image-20240612213746551](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122137987.png)

![image-20240612213831972](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122138889.png)

编写程序：

![image-20240612214008324](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122140212.png)

右击文件进行Git操作：

![image-20240612214209495](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122142288.png)

选择.idea文件夹，忽略该文件夹：

![image-20240612214337857](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122143967.png)

对未添加版本的项目进行添加：

![image-20240612214529196](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122145640.png)

提交到仓库：

![image-20240612214628675](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122146526.png)

或者通过上方进行提交：

![image-20240612214732610](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122147780.png)

查看历史：

![image-20240612214930263](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122149989.png)

![image-20240612215125335](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122151334.png)

## 远程仓库操作

### 提交到远程仓库

点击Push：

![image-20240612222236842](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122222151.png)

点击 Define remote，添加URL：

![image-20240612222310250](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122223211.png)

![image-20240612222404360](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122224367.png)

输入用户名和密码：

![image-20240612222446426](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122224349.png)

点击PUSH即可

![image-20240612222527770](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122225462.png)

### 拉取远程仓库

点击New - Project from Version Control..：

![image-20240612222630974](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122226762.png)

![image-20240612222734887](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122227859.png)

![image-20240612222759998](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122228629.png)

## 单分支冲突

在IDEA中添加一行：

![image-20240612223913674](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122239404.png)

在页面中添加一行：

![image-20240612223957024](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122239161.png)

提交到远程仓库：

![image-20240612224059812](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122241701.png)

此时会出现：

![image-20240612224122584](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122241527.png)

点击MERGE：

![image-20240612224216218](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122242582.png)

点击 ACCEPT YOURS：使用当前提交的代码

点击 ACCEPT THEIRS：使用远程仓库的代码

点击MERGE：查看差异，并解决冲突

![image-20240612225420271](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122254890.png)

点击解决冲突：

![image-20240612225703802](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122257240.png)

提交即可：

![image-20240612225807070](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122258056.png)

文件已经更新：

![image-20240612225836993](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406122258065.png)

## 多分支使用

在实际项目中，一般使用多分支将不同模块开发的代码提交到不同的分支来管理项目。

创建新分支：此分支会基于创建前分支的状态进行创建

![image-20240613122709816](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131227767.png)

![image-20240613122740294](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131227136.png)

修改文件并提交：

![image-20240613124106866](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131241968.png)

提交到远程分支：

![image-20240613124537748](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131245846.png)

切换会master分支：

![image-20240613124155439](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131241039.png)

发现master 分支并没有记录：

![image-20240613124250712](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406131242677.png)

## 集成 GitLab

进入File-Settings-Version Control-GitLab：添加地址，点击Generate生成个人令牌

![image-20240613215653787](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132156787.png)

创建个人访问令牌：

![image-20240613211629000](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132116134.png)

![image-20240613213915625](assets/image-20240613213915625.png)

输入Gitlab地址：

![image-20240613211554214](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132116590.png)

![image-20240613215821545](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132158050.png)

点击创建合并请求：

![image-20240613215908619](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132159564.png)

合并分支：

![image-20240613220003117](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132200979.png)

![image-20240613220023160](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132200931.png)

## 冲突提交

实际单个模块的开发往往不是单独一个人来进行操作，当多个人协同开发相同的一个项目时，就会涉及到提交冲突的问题。

### 不同人修改不同文件

在远程仓库添加gitLab.txt

![image-20240614231556091](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142315658.png)

在本地IDEA中添加代码，进行模块的开发

```java
public class Module {
    public static void main(String[] args) {
        System.out.println("开始进行模块的开发");
    }
}
```

提交代码到远程仓库，此时会有报错信息

![image-20240614231702658](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142317113.png)

Git会智能识别，采用merge合并命令，拉取远端文件到本地进行合并。

查看Git提交的全部历史记录，可以看到中间有拉取Gitee日志的部分

![image-20240614231735599](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142317917.png)

### 不同人修改同文件的不同区域

远程仓库修改module代码

```java
public class Module {
    public static void main(String[] args) {
        System.out.println("没完成模块的开发");
    }
}
```

本地IDEA继续添加代码

```java
//添加注释
public class Module1 {
    public static void main(String[] args) {
        System.out.println("完成模块的开发");
    }
}
```

提交代码，之后push到远程仓库

![image-20240614231906444](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142319750.png)

同样可以采用merge命令，git会自动合并不同的区域代码。

![image-20240614230808424](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142308942.png)

![image-20240614231936055](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142319359.png)

### 不同人修改同文件的相同区域

源文件代码：

![image-20240614232409891](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142324806.png)

远程仓库修改：

![image-20240614232514065](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142325674.png)

本地IDEA添加模块开发遇到了bug

```java
public class Module1 {
    public static void main(String[] args) {
        System.out.println("完成第一个模块的开发");
        System.out.println("继续进行第一个模块的二次开发");
        System.out.println("模块开发继续!!!");
        System.out.println("模块开发遇到了bug!");
    }
}
```

![image-20240614232605596](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142326150.png)

点击MERGE选择代码，点击左下角选择使用哪个版本：

![image-20240614232702220](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142327286.png)

无法直接采用merge命令，需要人为判断哪些作为最终的结果来保留

之后需要重新提交到远程仓库

![image-20240614232753249](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142327733.png)

### 同时变更文件名和文件内容

本地IDEA修改原先的文件名称为Module1plus，之后重新开发实现功能

```java
//添加注释
public class Module1plus {
    public static void main(String[] args) {
        System.out.println("没完成模块1的开发");
        System.out.println("模块1的开发遇到了bug");
        System.out.println("完成了模块1的开发");
        System.out.println("进一步完成了模块1的拓展开发");
    }
}
```

提交代码修改到远程仓库

![image-20240614232901465](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142329195.png)

可以直接提交成功。

### 不同人把同一文件改成不同的文件名

远程仓库把文件名称改为module1

本地IDEA修改文件名称为module3

提交到远程仓库

![image-20240614231906444](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142319750.png)

需要手动选择使用哪一个

![image-20240614233302519](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142333174.png)

push会导致报错，之后需要用户自己解决保留哪些文件。

使用命令解决最终的冲突

```shell
git status
#删除掉报红找不到的文件
git rm src/main/java/com/hjc/demo/Module1plus.java
```

最后重新选择正确的代码提交到仓库

![1706151049392](assets/5C1706151049392.png)

最后NERGE即可：

![image-20240614231906444](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406142319750.png)
