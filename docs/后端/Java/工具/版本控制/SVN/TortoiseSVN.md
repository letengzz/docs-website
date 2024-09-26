# TortoiseSVN

## 上传本地文件至SVN Server

1. 在本地新建测试文件夹【test】，在文件夹内新建3份文档：

   ![image-20230706150437082](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061727762.png)

2. 上传文件：右击文件夹，选择【Import】：

   ![image-20230706150729659](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730753.png)

   首次上传，可能会弹出如下窗口，选择任一选项均可

   ![在这里插入图片描述](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730608.png)

3. 填写正确的URL后点击【OK】开始上传：

   ![image-20230706151136694](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730991.png)

   上述URL可直接copy仓库下test文件夹的URL

4. 输入上面创建的用户名和密码，点击【OK】继续：

   ![image-20230706151227790](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730180.png)

5. 上传完成后，点击【OK】关闭：

   ![image-20230706151250587](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730388.png)

6. 刷新文件夹test1，可看到上传的文件：

   ![image-20230706151339710](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730529.png)

   ![image-20230706151400715](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730216.png)

## 下载SVN Server 文件

1. 想下载test1 中的3个文档至本地文件夹Hou：

   ![image-20230706151400715](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730331.png)

2. 右击待存放下载文件的文件夹，选择SVN Checkout…：

   ![image-20230706151617515](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730901.png)

   第一个框内填写待下载文件地址，第二个框填写待存放下载文件的目录，另外可以根据实际需求下载对应文件版本，这里选择最新版本。配置完成后，点击【OK】开始下载：

   ![image-20230706151824952](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061730671.png)

3. 下载完成后，点击【OK】关闭窗口：

   ![image-20230706151856398](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729617.png)

## 检出(checkout)

检出就是将远程建立的代码仓库同步到本地。

1. 进入[SVNBucket](SVNBucket.md)项目中，复制右侧的项目的地址：

   ![image-20230706154340245](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729378.png)

2. 在本地新建一个文件夹TestSVN，右键选择**SVN checkout**：

   ![image-20230706155229934](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729304.png)

3. ![image-20230706155344241](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729157.png)

4. 弹出认证框，输入登录[SVNBucket](SVNBucket.md)网址的用户名和密码，点击确定后会弹出一个检出完成的框，代表成功，这时可以看到TestSVN文件夹下会生成一个.svn的隐藏文件，同时TestSVN文件夹会有一个绿色对勾的标志(若没有，重启电脑可看见)：

   ![image-20230706155502510](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729342.png)

   ![image-20230706155519962](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729331.png)

   ![image-20230706155643776](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729912.png)

## 提交(commit)

提交，可以将本地新建的文件提交到远程仓库，也可以将已修改的文件提交到仓库

1. 在TestSVN文件下新建一个aaa.txt：

   ![image-20230706155855475](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729510.png)

2. 右击空白处，选择**SVN提交**后，输入提交信息并选择提交的文件，点击确定，提交完成后会弹出提示框，且文件会出现一个绿色对勾的标志：

   ![image-20230706155956082](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729418.png)

   ![image-20230706160111154](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729570.png)

   ![image-20230706160210184](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729460.png)

   ![image-20230706160228580](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729083.png)

3. 在SVNBucket网站上查看提交的文件：

   ![image-20230706160252111](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729359.png)

4. 当修改了本地文件后，选择**SVN提交**可以实现修改文件的同步更新。

## 更新(update)

更新，将别人提交的代码同步到本地。

1. 当远程仓库中的aaa.txt文件被其他人更新了，加了一行代码。本地需要写代码时，需要先更新本地文件：

   ![image-20230706160948790](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729101.png)

2. 在TestSVN文件夹下右击，选择**SVN Update**，完成后可以看到aaa.txt文件与远程仓库保存一致：

   ![image-20230706161211120](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729455.png)

   ![image-20230706161231975](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729421.png)

   ![image-20230706161300098](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729776.png)

## 忽略文件(ignore)

当本地有的文件或目录不用提交到远程仓库时，可以选择忽略这些文件或目录。

1. .右击选择忽略的文件或文件夹，选择**TortorseSVN**->**Add to ignore list**->**iiiii**，成功后会弹出一个聊天框：

   ![image-20230706161704201](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061729505.png)

   ![image-20230706161801900](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728593.png)

2. 撤销忽略，可选择从忽略列表中移除：

   ![image-20230706161850102](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728513.png)

   ![image-20230706161950572](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728337.png)

## 撤销本地已提交的代码

1. 修改aaa文件并进行提交：

   ![image-20230706162027173](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728970.png)

   ![image-20230706162055928](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728747.png)

2. 点击aaa文件，可以查看本地与仓库aaa文件的差异：

   ![image-20230706162220880](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728387.png)

3. 提交完成：

   ![image-20230706162248487](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728250.png)

## 撤销与恢复

### 修改后未提交

将aaa.txt内容进行修改，文件就变成红色的，此时如果想撤销刚刚的修改操作，可以直接在修改的文件上鼠标右键，单击 TortoiseSVN——>Revert… 就可以撤销了：

![image-20230706163613736](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728141.png)

![image-20230706163646216](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728826.png)

![image-20230706163709313](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728649.png)

![image-20230706163727656](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728575.png)

### 修改后已提交

1. 想回退到某个版本！右击aaa文件，选择**TortoiseSVN**->**show log**：

   ![image-20230706162323979](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728362.png)

2. 选择想要回退的版本，右击**Revert to this revision**，点击还原即可;

   ![image-20230706162737525](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728680.png)

   ![image-20230706162830250](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728034.png)

   ![image-20230706162851624](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728828.png)

3. .对还原的文件再次更新：

   ![image-20230706162911206](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728600.png)

   ![image-20230706162942914](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728109.png)

## 代码暂存

使用**代码暂存**的场景：

- 代码修改了很多，突然需要紧急修复一个bug，但是代码并没有写完，不能提交
- 代码重构了很多，突然需要发布新版本，但是代码还跑不起来，不能提交

将文件内容进行修改，然后将文件暂存起来：

![image-20230706164730196](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728340.png)

![image-20230706165418085](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728862.png)

**取消暂存**：

![image-20230706165609680](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061728056.png)

![image-20230706165641005](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/202307061727289.png)

