# GitHub 客户端

官方地址：https://desktop.github.com/

## 安装GitHub Desktop

下载链接：https://central.github.com/deployments/desktop/desktop/latest/win32

无安装过程，安装完成后，弹出应用界面

## 配置

### 配置用户名及邮箱

点击软件得File菜单后，选择Options, 设定软件得操作用户名称及对应得邮箱地址：

![image-20230514000745901](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109517.png)

### 设置主题样式

可以根据自己得偏好设定软件主题样式：

![image-20230514000756689](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109455.png)

### 设置全屏

如果觉得软件界面比较小，可以适当进行调整或全屏：

![image-20230514000801530](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109293.png)

## 本地仓库操作

### 新建仓库

![image-20230514000934583](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109134.png)

![image-20230514000937969](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109045.png)

### 操作区域

![image-20230514000942375](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109268.png)

### 切换仓库

![image-20230514000946745](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109071.png)

### 删除仓库

![image-20230514000951015](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109131.png)

![image-20230514000954863](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109453.png)

## 文件操作

### 新增文件

当工作区域创建了一份新文件，工具可以自动识别并进行对应得显示：

![image-20230514001002555](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109746.png)

此时Git仓库中并没有这份文件，所以需要执行commit操作，将文件保存到Git仓库中：

![image-20230514001009106](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109527.png)

### 忽略文件

如果某一个文件或某一类得文件，不想被Git软件进行管理。可以在忽略文件中进行设定：

![image-20230514001017278](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109488.png)

### 修改文件

修改文件只是将工作区域得文件进行修改，但是对于Git软件来讲，其实本质上还是提交，因为底层会生成新得文件

![image-20230514001026194](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109392.png)

### 删除文件

删除文件对于Git软件来讲，依然是一个提交

![image-20230514001037001](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109287.png)

提交后，最新版本得文件也会被"删除"

### 历史记录

如果存在多次得提交操作得话，可以查看提交得历史记录

![image-20230514000903123](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109024.png)

## 分支操作

### 默认分支

软件创建仓库时，默认创建得分支为main

![image-20230514001148016](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109564.png)

点击右键可以改名

![image-20230514001154841](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109056.png)

### 创建分支

![image-20230514001159121](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109439.png)

![image-20230514001203414](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140109815.png)

### 切换分支

![image-20230514001207595](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108632.png)

### 删除分支

![image-20230514001211116](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108623.png)

### 合并分支

![image-20240330185840594](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202403301858488.png)

![image-20230514001219782](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108708.png)

## 标签操作

### 创建标签

![image-20230514001226860](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108494.png)

![image-20230514001232010](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108106.png)

![image-20230514001236866](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108716.png)

### 删除标签

![image-20230514001240933](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108740.png)

## 远程仓库

### 克隆仓库

- 选择克隆仓库：

  ![image-20230514001248813](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108189.png)

- 可以选择登录GitHub账号，也可以使用GitHub企业版 同时也可以使用URL：

  ![image-20230514001412701](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108373.png)

  ![image-20230514001417272](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108823.png)

- ![image-20230514001420934](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108073.png)

- ![image-20230514001424800](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108952.png)

### 拉取文件

- 远程仓库更新了文件：

  ![image-20230514001429120](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108014.png)

- 拉取远程仓库文件：

  ![image-20230514001434216](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108114.png)

- ![image-20230514001439590](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108092.png)

- ![image-20230514001442657](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108463.png)

- ![image-20230514001447106](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140112960.png)

### 推送文件

- 本地创建新文件：

  ![image-20230514001455569](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108899.png)

- 提交新文件到本都仓库：

  ![image-20230514001459645](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108118.png)

- 向远程仓库推送文件：

  ![image-20230514001505855](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108853.png)

- ![image-20230514001539897](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140108208.png)